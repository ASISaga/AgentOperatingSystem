"""Entra Agent ID and Managed Identity support for the AOS Client SDK.

Provides identity primitives that give each agent a distinct Azure Entra ID
(formerly Azure AD) identity.  Agents can authenticate via **managed identity**
(recommended for Azure-hosted workloads) or **client credentials** (for
scenarios where a client secret is available).

The module is designed to be importable and testable without the
``azure-identity`` package installed — token acquisition is stubbed with
placeholder values when the SDK is not present.

Usage::

    from aos_client.identity import AgentIdentityProvider

    provider = AgentIdentityProvider(tenant_id="my-tenant-id")
    identity = provider.register_agent(
        agent_id="cmo-agent",
        client_id="00000000-0000-0000-0000-000000000000",
    )

    token_result = await identity.get_token()
    headers = await identity.get_agent_headers()
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_DEFAULT_SCOPES: List[str] = ["https://cognitiveservices.azure.com/.default"]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class TokenResult(BaseModel):
    """Result of a token acquisition request.

    :param token: The access token string.
    :param expires_on: Optional expiration timestamp.
    :param scope: The scope for which the token was issued.
    :param identity_type: ``"managed_identity"`` or ``"client_credentials"``.
    """

    token: str
    expires_on: Optional[datetime] = None
    scope: str
    identity_type: str


class ManagedIdentityConfig(BaseModel):
    """Configuration for Azure Managed Identity.

    :param client_id: User-assigned managed identity client ID.
        ``None`` for system-assigned managed identity.
    :param resource_id: User-assigned managed identity resource ID.
    :param identity_type: ``"system_assigned"`` or ``"user_assigned"``.
    """

    client_id: Optional[str] = Field(
        default=None,
        description="User-assigned managed identity client ID (None for system-assigned)",
    )
    resource_id: Optional[str] = Field(
        default=None,
        description="User-assigned managed identity resource ID",
    )
    identity_type: str = Field(
        default="system_assigned",
        description="Identity type: 'system_assigned' or 'user_assigned'",
    )


# ---------------------------------------------------------------------------
# Core identity class
# ---------------------------------------------------------------------------


class EntraAgentIdentity:
    """Represents an Entra ID identity for an agent.

    Each agent maps to an Azure Entra App Registration and can authenticate
    using either a **managed identity** or **client credentials** flow.

    :param agent_id: Unique agent identifier.
    :param tenant_id: Azure AD tenant ID.
    :param client_id: Client / Application ID of the agent's app registration.
    :param client_secret: Client secret for the confidential-client flow.
        ``None`` when using managed identity.
    :param managed_identity: Whether to use managed identity instead of
        client credentials.  Defaults to ``True``.
    :param scopes: Token scopes.  Defaults to
        ``["https://cognitiveservices.azure.com/.default"]``.
    """

    def __init__(
        self,
        agent_id: str,
        tenant_id: str,
        client_id: str,
        client_secret: Optional[str] = None,
        managed_identity: bool = True,
        scopes: Optional[List[str]] = None,
    ) -> None:
        self.agent_id = agent_id
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.managed_identity = managed_identity
        self.scopes = scopes or list(_DEFAULT_SCOPES)
        self._credential: Optional[Any] = None

    # -- properties ---------------------------------------------------------

    @property
    def identity_type(self) -> str:
        """Return the identity type: ``"managed_identity"`` or ``"client_credentials"``."""
        return "managed_identity" if self.managed_identity else "client_credentials"

    # -- public async API ---------------------------------------------------

    async def get_token(self, scope: Optional[str] = None) -> TokenResult:
        """Acquire an access token for this agent identity.

        Uses managed identity when :pyattr:`managed_identity` is ``True``,
        otherwise falls back to client-credentials flow.  If the
        ``azure-identity`` package is not installed a **placeholder** token is
        returned so that the module remains usable in local development.

        :param scope: Override scope.  When ``None`` the first entry from
            :pyattr:`scopes` is used.
        :returns: A :class:`TokenResult` with the token and metadata.
        """
        effective_scope = scope or (self.scopes[0] if self.scopes else "")

        if self.managed_identity:
            return await self._acquire_managed_identity_token(effective_scope)
        return await self._acquire_client_credentials_token(effective_scope)

    async def get_agent_headers(self) -> Dict[str, str]:
        """Return HTTP headers containing a Bearer token and agent identifier.

        :returns: Dictionary with ``Authorization`` and ``X-Agent-ID`` headers.
        """
        token_result = await self.get_token()
        return {
            "Authorization": f"Bearer {token_result.token}",
            "X-Agent-ID": self.agent_id,
        }

    async def validate(self) -> bool:
        """Validate that the identity is properly configured and can obtain tokens.

        :returns: ``True`` if a token was successfully obtained, ``False``
            otherwise.
        """
        try:
            result = await self.get_token()
            return bool(result.token)
        except Exception:
            logger.exception("Identity validation failed for agent '%s'", self.agent_id)
            return False

    # -- internal helpers ---------------------------------------------------

    async def _acquire_managed_identity_token(self, scope: str) -> TokenResult:
        """Attempt to acquire a token via Azure Managed Identity."""
        try:
            from azure.identity.aio import ManagedIdentityCredential  # type: ignore[import-untyped]

            if self._credential is None:
                self._credential = ManagedIdentityCredential(client_id=self.client_id)
            az_token = await self._credential.get_token(scope)
            logger.debug("Acquired managed-identity token for agent '%s'", self.agent_id)
            return TokenResult(
                token=az_token.token,
                expires_on=datetime.fromtimestamp(az_token.expires_on, tz=timezone.utc),
                scope=scope,
                identity_type="managed_identity",
            )
        except ImportError:
            logger.warning(
                "azure-identity not installed — returning placeholder token "
                "for agent '%s'",
                self.agent_id,
            )
            return self._placeholder_token(scope)

    async def _acquire_client_credentials_token(self, scope: str) -> TokenResult:
        """Attempt to acquire a token via client-credentials flow."""
        try:
            from azure.identity.aio import ClientSecretCredential  # type: ignore[import-untyped]

            if self._credential is None:
                self._credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret or "",
                )
            az_token = await self._credential.get_token(scope)
            logger.debug(
                "Acquired client-credentials token for agent '%s'",
                self.agent_id,
            )
            return TokenResult(
                token=az_token.token,
                expires_on=datetime.fromtimestamp(az_token.expires_on, tz=timezone.utc),
                scope=scope,
                identity_type="client_credentials",
            )
        except ImportError:
            logger.warning(
                "azure-identity not installed — returning placeholder token "
                "for agent '%s'",
                self.agent_id,
            )
            return self._placeholder_token(scope)

    def _placeholder_token(self, scope: str) -> TokenResult:
        """Return a non-functional placeholder token for local development."""
        return TokenResult(
            token="placeholder-token",
            expires_on=None,
            scope=scope,
            identity_type=self.identity_type,
        )


# ---------------------------------------------------------------------------
# Factory / registry
# ---------------------------------------------------------------------------


class AgentIdentityProvider:
    """Factory and registry that manages :class:`EntraAgentIdentity` instances
    for multiple agents.

    :param tenant_id: Azure AD tenant ID shared by all registered agents.
    :param default_managed_identity: Default value for
        :pyattr:`EntraAgentIdentity.managed_identity` when registering agents.
    :param default_scopes: Default token scopes applied to newly registered
        agents when no explicit scopes are provided.
    """

    def __init__(
        self,
        tenant_id: str,
        default_managed_identity: bool = True,
        default_scopes: Optional[List[str]] = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.default_managed_identity = default_managed_identity
        self.default_scopes = default_scopes or list(_DEFAULT_SCOPES)
        self._identities: Dict[str, EntraAgentIdentity] = {}

    def register_agent(
        self,
        agent_id: str,
        client_id: str,
        client_secret: Optional[str] = None,
        managed_identity: Optional[bool] = None,
        scopes: Optional[List[str]] = None,
    ) -> EntraAgentIdentity:
        """Register an agent and return its :class:`EntraAgentIdentity`.

        :param agent_id: Unique agent identifier.
        :param client_id: Azure app-registration client ID.
        :param client_secret: Optional client secret for confidential-client flow.
        :param managed_identity: Override the provider default for managed identity.
        :param scopes: Override the provider default scopes.
        :returns: The newly created :class:`EntraAgentIdentity`.
        :raises ValueError: If an agent with the same *agent_id* is already
            registered.
        """
        if agent_id in self._identities:
            raise ValueError(f"Agent '{agent_id}' is already registered")

        use_mi = managed_identity if managed_identity is not None else self.default_managed_identity
        identity = EntraAgentIdentity(
            agent_id=agent_id,
            tenant_id=self.tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            managed_identity=use_mi,
            scopes=scopes or list(self.default_scopes),
        )
        self._identities[agent_id] = identity
        logger.info("Registered agent identity '%s' (%s)", agent_id, identity.identity_type)
        return identity

    def get_agent_identity(self, agent_id: str) -> EntraAgentIdentity:
        """Retrieve a previously registered agent identity.

        :param agent_id: The agent identifier.
        :returns: The :class:`EntraAgentIdentity` for the agent.
        :raises KeyError: If no agent with the given *agent_id* is registered.
        """
        try:
            return self._identities[agent_id]
        except KeyError:
            raise KeyError(f"No identity registered for agent '{agent_id}'") from None

    def list_agents(self) -> List[str]:
        """Return the identifiers of all registered agents.

        :returns: List of agent ID strings.
        """
        return list(self._identities.keys())

    def remove_agent(self, agent_id: str) -> None:
        """Remove a registered agent identity.

        :param agent_id: The agent identifier to remove.
        :raises KeyError: If no agent with the given *agent_id* is registered.
        """
        try:
            del self._identities[agent_id]
            logger.info("Removed agent identity '%s'", agent_id)
        except KeyError:
            raise KeyError(f"No identity registered for agent '{agent_id}'") from None
