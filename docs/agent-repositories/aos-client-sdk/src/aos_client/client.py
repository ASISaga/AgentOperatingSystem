"""AOSClient — primary client for interacting with the Agent Operating System.

Usage::

    from aos_client import AOSClient

    async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
        # Browse the agent catalog
        agents = await client.list_agents()

        # Select C-suite agents and compose an orchestration
        selected = [a.agent_id for a in agents if "leadership" in a.capabilities]
        result = await client.run_orchestration(
            agent_ids=selected,
            task={"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
        )
        print(result.summary)
"""

from __future__ import annotations

import uuid
import logging
from typing import Any, Dict, List, Optional

from aos_client.models import (
    AgentDescriptor,
    OrchestrationRequest,
    OrchestrationResult,
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
        """Submit an orchestration request to AOS.

        Args:
            request: Orchestration request describing which agents to use
                and the task to execute.
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

    async def get_orchestration_result(self, orchestration_id: str) -> OrchestrationResult:
        """Retrieve the final result of a completed orchestration.

        Args:
            orchestration_id: ID returned by :meth:`submit_orchestration`.

        Returns:
            :class:`OrchestrationResult` with per-agent results and summary.

        Raises:
            RuntimeError: If the orchestration has not completed yet.
        """
        data = await self._get(
            f"{self.endpoint}/api/orchestrations/{orchestration_id}/result"
        )
        return OrchestrationResult(**data)

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

    async def run_orchestration(
        self,
        agent_ids: List[str],
        task: Dict[str, Any],
        workflow: str = "collaborative",
        config: Optional[Dict[str, Any]] = None,
        poll_interval_seconds: float = 2.0,
        timeout_seconds: float = 300.0,
    ) -> OrchestrationResult:
        """Submit an orchestration and wait for the result.

        This is a convenience method that submits the request, polls for
        completion, and returns the final result.

        Args:
            agent_ids: Agent IDs to include.
            task: Task payload.
            workflow: Workflow pattern (default ``"collaborative"``).
            config: Optional orchestration config.
            poll_interval_seconds: Seconds between status polls.
            timeout_seconds: Maximum seconds to wait.

        Returns:
            :class:`OrchestrationResult`.

        Raises:
            TimeoutError: If the orchestration does not complete within
                *timeout_seconds*.
            RuntimeError: If the orchestration fails.
        """
        import asyncio

        request = OrchestrationRequest(
            agent_ids=agent_ids,
            workflow=workflow,
            task=task,
            config=config or {},
        )
        status = await self.submit_orchestration(request)
        oid = status.orchestration_id

        elapsed = 0.0
        while status.status in (OrchestrationStatusEnum.PENDING, OrchestrationStatusEnum.RUNNING):
            if elapsed >= timeout_seconds:
                raise TimeoutError(
                    f"Orchestration {oid} did not complete within {timeout_seconds}s"
                )
            await asyncio.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds
            status = await self.get_orchestration_status(oid)

        if status.status == OrchestrationStatusEnum.FAILED:
            raise RuntimeError(f"Orchestration {oid} failed: {status.error}")

        return await self.get_orchestration_result(oid)

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
