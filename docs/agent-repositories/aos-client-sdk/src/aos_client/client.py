"""AOSClient — primary client for interacting with the Agent Operating System.

Usage::

    from aos_client import AOSClient

    async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
        # Browse the agent catalog
        agents = await client.list_agents()

        # Select C-suite agents and start a perpetual orchestration
        selected = [a.agent_id for a in agents if "leadership" in a.capabilities]
        status = await client.start_orchestration(
            agent_ids=selected,
            purpose="Drive strategic growth and continuous organisational improvement",
            purpose_scope="C-suite quarterly review and ongoing alignment",
            context={"quarter": "Q1-2026"},
        )
        print(status.orchestration_id, status.status)
"""

from __future__ import annotations

import uuid
import logging
from typing import Any, Dict, List, Optional

from aos_client.models import (
    AgentDescriptor,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
    OrchestrationStatusEnum,
)

logger = logging.getLogger(__name__)


class AOSClient:
    """Lightweight client for the Agent Operating System infrastructure service.

    The client communicates with AOS over HTTP (REST) and optionally
    Azure Service Bus for event-driven workflows.

    Args:
        endpoint: Base URL of the AOS Function App
            (e.g. ``"https://my-aos.azurewebsites.net"``).
        realm_endpoint: Base URL of the RealmOfAgents Function App.
            Defaults to *endpoint* if not specified (co-located deployment).
        credential: Azure credential for authentication. When ``None``,
            anonymous access is used (suitable for local development).
        service_bus_connection_string: Optional connection string for
            event-driven orchestration submission via Azure Service Bus.
        app_name: Client application name (used for Service Bus routing).
    """

    def __init__(
        self,
        endpoint: str,
        realm_endpoint: Optional[str] = None,
        credential: Optional[Any] = None,
        service_bus_connection_string: Optional[str] = None,
        app_name: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.realm_endpoint = (realm_endpoint or endpoint).rstrip("/")
        self.credential = credential
        self.service_bus_connection_string = service_bus_connection_string
        self.app_name = app_name
        self._session: Optional[Any] = None  # aiohttp.ClientSession placeholder
        self._service_bus: Optional[Any] = None  # AOSServiceBus placeholder

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AOSClient":
        try:
            import aiohttp  # type: ignore[import-untyped]
            self._session = aiohttp.ClientSession()
        except ImportError:
            logger.warning("aiohttp not installed — HTTP calls will not work")

        if self.service_bus_connection_string:
            from aos_client.service_bus import AOSServiceBus

            self._service_bus = AOSServiceBus(
                connection_string=self.service_bus_connection_string,
                app_name=self.app_name,
            )
            await self._service_bus.__aenter__()

        return self

    async def __aexit__(self, *exc: Any) -> None:
        if self._service_bus is not None:
            await self._service_bus.__aexit__(*exc)
            self._service_bus = None
        if self._session is not None:
            await self._session.close()
            self._session = None

    # ------------------------------------------------------------------
    # Agent catalog (RealmOfAgents)
    # ------------------------------------------------------------------

    async def list_agents(self, agent_type: Optional[str] = None) -> List[AgentDescriptor]:
        """List agents available in the RealmOfAgents catalog.

        Args:
            agent_type: Optional filter by agent class name.

        Returns:
            List of :class:`AgentDescriptor` objects.
        """
        params: Dict[str, str] = {}
        if agent_type:
            params["agent_type"] = agent_type

        data = await self._get(f"{self.realm_endpoint}/api/realm/agents", params=params)
        return [AgentDescriptor(**entry) for entry in data.get("agents", [])]

    async def get_agent(self, agent_id: str) -> AgentDescriptor:
        """Get a single agent descriptor by ID.

        Args:
            agent_id: Agent identifier.

        Returns:
            :class:`AgentDescriptor` for the requested agent.

        Raises:
            KeyError: If the agent is not found.
        """
        data = await self._get(f"{self.realm_endpoint}/api/realm/agents/{agent_id}")
        return AgentDescriptor(**data)

    # ------------------------------------------------------------------
    # Orchestrations (AOS Function App)
    # ------------------------------------------------------------------

    async def submit_orchestration(
        self,
        request: OrchestrationRequest,
        *,
        via_service_bus: bool = False,
    ) -> OrchestrationStatus:
        """Submit a purpose-driven orchestration request to AOS.

        The orchestration runs perpetually until explicitly stopped or
        cancelled.

        Args:
            request: Orchestration request describing the purpose, which
                agents to include, and initial context.
            via_service_bus: When ``True``, submit via Azure Service Bus
                instead of HTTP.  Requires a Service Bus connection string.

        Returns:
            Initial :class:`OrchestrationStatus` (typically ``PENDING``).
        """
        if request.orchestration_id is None:
            request.orchestration_id = str(uuid.uuid4())

        if via_service_bus and self._service_bus is not None:
            await self._service_bus.send_orchestration_request(request)
            return OrchestrationStatus(
                orchestration_id=request.orchestration_id,
                status=OrchestrationStatusEnum.PENDING,
                agent_ids=request.agent_ids,
                purpose=request.purpose.purpose,
            )

        data = await self._post(
            f"{self.endpoint}/api/orchestrations",
            json=request.model_dump(mode="json"),
        )
        return OrchestrationStatus(**data)

    async def get_orchestration_status(self, orchestration_id: str) -> OrchestrationStatus:
        """Poll the status of a submitted orchestration.

        Args:
            orchestration_id: ID returned by :meth:`submit_orchestration`.

        Returns:
            Current :class:`OrchestrationStatus`.
        """
        data = await self._get(f"{self.endpoint}/api/orchestrations/{orchestration_id}")
        return OrchestrationStatus(**data)

    async def stop_orchestration(self, orchestration_id: str) -> OrchestrationStatus:
        """Stop a running orchestration.

        Perpetual orchestrations run until explicitly stopped.  This method
        requests a graceful stop.

        Args:
            orchestration_id: ID of the orchestration to stop.

        Returns:
            Updated :class:`OrchestrationStatus` (typically ``STOPPED``).
        """
        data = await self._post(
            f"{self.endpoint}/api/orchestrations/{orchestration_id}/stop",
            json={},
        )
        return OrchestrationStatus(**data)

    async def cancel_orchestration(self, orchestration_id: str) -> OrchestrationStatus:
        """Cancel a running orchestration.

        Args:
            orchestration_id: ID of the orchestration to cancel.

        Returns:
            Updated :class:`OrchestrationStatus`.
        """
        data = await self._post(
            f"{self.endpoint}/api/orchestrations/{orchestration_id}/cancel",
            json={},
        )
        return OrchestrationStatus(**data)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def start_orchestration(
        self,
        agent_ids: List[str],
        purpose: str,
        purpose_scope: str = "",
        context: Optional[Dict[str, Any]] = None,
        workflow: str = "collaborative",
        config: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationStatus:
        """Start a perpetual purpose-driven orchestration.

        This is a convenience method that builds an
        :class:`OrchestrationRequest` from simple parameters and submits
        it.  The orchestration runs perpetually until explicitly stopped.

        Args:
            agent_ids: Agent IDs to include.
            purpose: The overarching purpose that drives the orchestration.
            purpose_scope: Boundaries/scope for the purpose.
            context: Initial context data for the orchestration.
            workflow: Workflow pattern (default ``"collaborative"``).
            config: Optional orchestration config.

        Returns:
            :class:`OrchestrationStatus` with the orchestration ID.
        """
        request = OrchestrationRequest(
            agent_ids=agent_ids,
            workflow=workflow,
            purpose=OrchestrationPurpose(
                purpose=purpose,
                purpose_scope=purpose_scope or "General orchestration scope",
            ),
            context=context or {},
            config=config or {},
        )
        return await self.submit_orchestration(request)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Check health of the AOS Function App.

        Returns:
            Health status dictionary.
        """
        return await self._get(f"{self.endpoint}/api/health")

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------

    async def _get(self, url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if self._session is None:
            raise RuntimeError(
                "AOSClient must be used as an async context manager: "
                "async with AOSClient(...) as client: ..."
            )
        headers = await self._auth_headers()
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _post(self, url: str, json: Any) -> Dict[str, Any]:
        if self._session is None:
            raise RuntimeError(
                "AOSClient must be used as an async context manager: "
                "async with AOSClient(...) as client: ..."
            )
        headers = await self._auth_headers()
        async with self._session.post(url, json=json, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _auth_headers(self) -> Dict[str, str]:
        if self.credential is None:
            return {}
        try:
            token = self.credential.get_token("https://management.azure.com/.default")
            return {"Authorization": f"Bearer {token.token}"}
        except Exception as exc:
            logger.warning("Failed to obtain auth token: %s. Proceeding without authentication.", exc)
            return {}
