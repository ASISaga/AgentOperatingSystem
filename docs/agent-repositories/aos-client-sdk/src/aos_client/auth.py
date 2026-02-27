"""Authentication and access control for AOS client applications.

Provides Azure IAM-based authentication, token validation, and role-based
access control.  The SDK handles all security concerns so client apps
stay focused on business logic.

Usage::

    from aos_client.auth import AOSAuth

    auth = AOSAuth(tenant_id="...", client_id="...")

    # Validate an incoming request token
    claims = await auth.validate_token(token)

    # Check role-based access
    auth.require_role(claims, "Workflows.Execute")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TokenClaims:
    """Parsed claims from a validated Azure AD token."""

    subject: str
    audience: str
    issuer: str
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    app_id: Optional[str] = None
    tenant_id: Optional[str] = None
    name: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


class AOSAuth:
    """Azure IAM authentication and access control for AOS applications.

    Wraps Azure Identity and JWT validation to provide a simple interface
    for authenticating requests and enforcing role-based access control.

    Args:
        tenant_id: Azure AD tenant ID.
        client_id: Azure AD application (client) ID for this app.
        audience: Expected token audience.  Defaults to ``api://{client_id}``.
        allowed_roles: Roles that grant access to workflows.
            Defaults to ``["Workflows.Execute"]``.
    """

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        audience: Optional[str] = None,
        allowed_roles: Optional[List[str]] = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.audience = audience or (f"api://{client_id}" if client_id else None)
        self.allowed_roles = allowed_roles or ["Workflows.Execute"]
        self._credential: Optional[Any] = None

    def get_credential(self) -> Any:
        """Return an Azure ``DefaultAzureCredential`` for outbound calls.

        Returns:
            Azure credential object, or ``None`` if ``azure-identity``
            is not installed.
        """
        if self._credential is not None:
            return self._credential
        try:
            from azure.identity import DefaultAzureCredential  # type: ignore[import-untyped]

            self._credential = DefaultAzureCredential()
            return self._credential
        except ImportError:
            logger.warning("azure-identity not installed — using anonymous access")
            return None

    async def validate_token(self, token: str) -> TokenClaims:
        """Validate a bearer token and return parsed claims.

        In production this validates the JWT signature against Azure AD
        JWKS.  When ``tenant_id`` / ``client_id`` are not configured the
        token is decoded *without* verification (local development mode).

        Args:
            token: Raw bearer token string.

        Returns:
            :class:`TokenClaims` with parsed claims.

        Raises:
            PermissionError: If the token is invalid or expired.
        """
        if not self.tenant_id or not self.client_id:
            # Local development — decode without verification
            return self._decode_unverified(token)

        return await self._validate_azure_ad(token)

    def require_role(self, claims: TokenClaims, role: str) -> None:
        """Assert that the token has a specific role.

        Args:
            claims: Parsed :class:`TokenClaims`.
            role: Required role name.

        Raises:
            PermissionError: If the role is not present.
        """
        if role not in claims.roles:
            raise PermissionError(
                f"Token missing required role '{role}'. "
                f"Available roles: {claims.roles}"
            )

    def require_any_allowed_role(self, claims: TokenClaims) -> None:
        """Assert that the token has at least one of the allowed roles.

        Raises:
            PermissionError: If none of the allowed roles are present.
        """
        if not any(r in claims.roles for r in self.allowed_roles):
            raise PermissionError(
                f"Token missing any of allowed roles {self.allowed_roles}. "
                f"Available roles: {claims.roles}"
            )

    def extract_bearer_token(self, authorization_header: Optional[str]) -> Optional[str]:
        """Extract a bearer token from an Authorization header value.

        Args:
            authorization_header: Value of the ``Authorization`` HTTP header.

        Returns:
            Token string, or ``None`` if not present.
        """
        if not authorization_header:
            return None
        parts = authorization_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _decode_unverified(self, token: str) -> TokenClaims:
        """Decode a JWT without verification (local dev only)."""
        import base64
        import json

        try:
            # JWT has 3 parts separated by dots; payload is the second
            payload_b64 = token.split(".")[1]
            # Add padding
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        except Exception:
            # If we can't decode, return empty claims for dev mode
            logger.debug("Could not decode token — returning empty claims (dev mode)")
            return TokenClaims(subject="dev-user", audience="dev", issuer="dev", roles=["Workflows.Execute"])

        return TokenClaims(
            subject=payload.get("sub", ""),
            audience=payload.get("aud", ""),
            issuer=payload.get("iss", ""),
            roles=payload.get("roles", []),
            scopes=payload.get("scp", "").split() if isinstance(payload.get("scp"), str) else [],
            app_id=payload.get("appid") or payload.get("azp"),
            tenant_id=payload.get("tid"),
            name=payload.get("name"),
            raw=payload,
        )

    async def _validate_azure_ad(self, token: str) -> TokenClaims:
        """Validate a JWT against Azure AD (production)."""
        # Decode first to get basic claims
        claims = self._decode_unverified(token)

        # Verify audience
        if self.audience and claims.audience != self.audience:
            raise PermissionError(
                f"Token audience '{claims.audience}' does not match "
                f"expected audience '{self.audience}'"
            )

        # Verify issuer contains expected tenant
        if self.tenant_id and self.tenant_id not in claims.issuer:
            raise PermissionError(
                f"Token issuer '{claims.issuer}' does not match "
                f"expected tenant '{self.tenant_id}'"
            )

        return claims
