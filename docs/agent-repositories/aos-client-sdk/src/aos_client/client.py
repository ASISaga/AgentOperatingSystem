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
from datetime import datetime
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, List, Optional

from aos_client.models import (
    AgentDescriptor,
    AgentResponse,
    Alert,
    AuditEntry,
    ComplianceReport,
    Covenant,
    CovenantValidation,
    Dashboard,
    DecisionChain,
    DecisionRecord,
    Document,
    KPI,
    MCPServer,
    MCPServerStatus,
    MetricsSeries,
    Network,
    NetworkMembership,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
    OrchestrationStatusEnum,
    OrchestrationUpdate,
    PeerApp,
    PeerVerification,
    Risk,
    RiskHeatmap,
    RiskSummary,
    RiskTrend,
    Subscription,
    Webhook,
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
        retry_policy: Optional[Any] = None,
        circuit_breaker: Optional[Any] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.realm_endpoint = (realm_endpoint or endpoint).rstrip("/")
        self.credential = credential
        self.service_bus_connection_string = service_bus_connection_string
        self.app_name = app_name
        self.retry_policy = retry_policy
        self.circuit_breaker = circuit_breaker
        self.tenant_id = tenant_id
        self._session: Optional[Any] = None  # aiohttp.ClientSession placeholder
        self._service_bus: Optional[Any] = None  # AOSServiceBus placeholder
        self._subscriptions: Dict[str, Callable] = {}

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

    async def _delete(self, url: str) -> None:
        if self._session is None:
            raise RuntimeError(
                "AOSClient must be used as an async context manager: "
                "async with AOSClient(...) as client: ..."
            )
        headers = await self._auth_headers()
        async with self._session.delete(url, headers=headers) as resp:
            resp.raise_for_status()

    async def _auth_headers(self) -> Dict[str, str]:
        if self.credential is None:
            return {}
        try:
            token = self.credential.get_token("https://management.azure.com/.default")
            return {"Authorization": f"Bearer {token.token}"}
        except Exception as exc:
            logger.warning("Failed to obtain auth token: %s. Proceeding without authentication.", exc)
            return {}

    # ------------------------------------------------------------------
    # Knowledge Base API
    # ------------------------------------------------------------------

    async def create_document(
        self, title: str, doc_type: str, content: dict, **kwargs: Any,
    ) -> Document:
        """Create a knowledge document.

        Args:
            title: Document title.
            doc_type: Document type (e.g. ``"policy"``, ``"decision"``).
            content: Arbitrary document content.
            **kwargs: Extra fields forwarded to the API.

        Returns:
            Created :class:`Document`.
        """
        payload: Dict[str, Any] = {"title": title, "doc_type": doc_type, "content": content}
        payload.update(kwargs)
        data = await self._post(f"{self.endpoint}/api/knowledge/documents", json=payload)
        return Document(**data)

    async def get_document(self, document_id: str) -> Document:
        """Get a knowledge document by ID."""
        data = await self._get(f"{self.endpoint}/api/knowledge/documents/{document_id}")
        return Document(**data)

    async def search_documents(
        self, query: str, doc_type: Optional[str] = None, limit: int = 10,
    ) -> List[Document]:
        """Search knowledge documents."""
        params: Dict[str, str] = {"query": query, "limit": str(limit)}
        if doc_type:
            params["doc_type"] = doc_type
        data = await self._get(f"{self.endpoint}/api/knowledge/documents", params=params)
        return [Document(**d) for d in data.get("documents", [])]

    async def update_document(self, document_id: str, content: dict) -> Document:
        """Update document content."""
        data = await self._post(
            f"{self.endpoint}/api/knowledge/documents/{document_id}",
            json={"content": content},
        )
        return Document(**data)

    async def delete_document(self, document_id: str) -> None:
        """Delete a knowledge document."""
        await self._delete(f"{self.endpoint}/api/knowledge/documents/{document_id}")

    async def create_documents_batch(self, documents: List[dict]) -> List[Document]:
        """Create multiple knowledge documents in a single batch.

        Args:
            documents: List of document data dicts.

        Returns:
            List of created :class:`Document` objects.
        """
        data = await self._post(
            f"{self.endpoint}/api/knowledge/documents/batch", json={"documents": documents},
        )
        return [Document(**d) for d in data.get("documents", [])]

    async def get_document_versions(self, document_id: str) -> List[Document]:
        """Get version history of a knowledge document."""
        data = await self._get(f"{self.endpoint}/api/knowledge/documents/{document_id}/versions")
        return [Document(**d) for d in data.get("versions", [])]

    async def restore_document_version(self, document_id: str, version: int) -> Document:
        """Restore a previous version of a knowledge document."""
        data = await self._post(
            f"{self.endpoint}/api/knowledge/documents/{document_id}/restore",
            json={"version": version},
        )
        return Document(**data)

    async def export_documents(self, query: str, format: str = "json") -> bytes:
        """Export knowledge documents matching a query.

        Args:
            query: Search query.
            format: Export format (default ``"json"``).

        Returns:
            Exported document data as bytes.
        """
        data = await self._post(
            f"{self.endpoint}/api/knowledge/documents/export",
            json={"query": query, "format": format},
        )
        if isinstance(data, bytes):
            return data
        import json as _json
        return _json.dumps(data).encode()

    # ------------------------------------------------------------------
    # Risk Registry API
    # ------------------------------------------------------------------

    async def register_risk(self, risk_data: dict) -> Risk:
        """Register a new risk.

        Args:
            risk_data: Risk information (title, description, category,
                owner, etc.).

        Returns:
            Created :class:`Risk`.
        """
        data = await self._post(f"{self.endpoint}/api/risks", json=risk_data)
        return Risk(**data)

    async def assess_risk(
        self, risk_id: str, likelihood: float, impact: float, **kwargs: Any,
    ) -> Risk:
        """Assess a risk with likelihood and impact scores.

        Args:
            risk_id: Risk identifier.
            likelihood: Likelihood score (0.0–1.0).
            impact: Impact score (0.0–1.0).

        Returns:
            Updated :class:`Risk`.
        """
        payload: Dict[str, Any] = {"likelihood": likelihood, "impact": impact}
        payload.update(kwargs)
        data = await self._post(f"{self.endpoint}/api/risks/{risk_id}/assess", json=payload)
        return Risk(**data)

    async def get_risks(
        self, status: Optional[str] = None, category: Optional[str] = None,
    ) -> List[Risk]:
        """List risks with optional filters."""
        params: Dict[str, str] = {}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        data = await self._get(f"{self.endpoint}/api/risks", params=params)
        return [Risk(**r) for r in data.get("risks", [])]

    async def update_risk_status(self, risk_id: str, status: str) -> Risk:
        """Update the status of a risk."""
        data = await self._post(
            f"{self.endpoint}/api/risks/{risk_id}/status", json={"status": status},
        )
        return Risk(**data)

    async def add_mitigation_plan(self, risk_id: str, plan: str, **kwargs: Any) -> Risk:
        """Add a mitigation plan to a risk."""
        payload: Dict[str, Any] = {"plan": plan}
        payload.update(kwargs)
        data = await self._post(f"{self.endpoint}/api/risks/{risk_id}/mitigate", json=payload)
        return Risk(**data)

    async def get_risk_heatmap(self, category: Optional[str] = None) -> RiskHeatmap:
        """Get a risk heatmap (likelihood × impact grid)."""
        params: Dict[str, str] = {}
        if category:
            params["category"] = category
        data = await self._get(f"{self.endpoint}/api/risks/heatmap", params=params)
        return RiskHeatmap(**data)

    async def get_risk_summary(self, category: Optional[str] = None) -> RiskSummary:
        """Get aggregate risk summary statistics."""
        params: Dict[str, str] = {}
        if category:
            params["category"] = category
        data = await self._get(f"{self.endpoint}/api/risks/summary", params=params)
        return RiskSummary(**data)

    async def get_risk_trends(self, period: str = "30d") -> List[RiskTrend]:
        """Get risk trends over time."""
        data = await self._get(
            f"{self.endpoint}/api/risks/trends", params={"period": period},
        )
        return [RiskTrend(**t) for t in data.get("trends", [])]

    # ------------------------------------------------------------------
    # Audit Trail / Decision Ledger API
    # ------------------------------------------------------------------

    async def log_decision(self, decision: dict) -> DecisionRecord:
        """Log a decision to the immutable ledger.

        Args:
            decision: Decision data (title, rationale, outcome, etc.).

        Returns:
            Created :class:`DecisionRecord`.
        """
        data = await self._post(f"{self.endpoint}/api/audit/decisions", json=decision)
        return DecisionRecord(**data)

    async def get_decision_history(
        self,
        orchestration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> List[DecisionRecord]:
        """Get decision history with optional filters."""
        params: Dict[str, str] = {}
        if orchestration_id:
            params["orchestration_id"] = orchestration_id
        if agent_id:
            params["agent_id"] = agent_id
        data = await self._get(f"{self.endpoint}/api/audit/decisions", params=params)
        return [DecisionRecord(**d) for d in data.get("decisions", [])]

    async def get_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        """Get the audit trail with optional time-range filter."""
        params: Dict[str, str] = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        data = await self._get(f"{self.endpoint}/api/audit/trail", params=params)
        return [AuditEntry(**e) for e in data.get("entries", [])]

    async def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        report_type: str = "decisions",
        format: str = "json",
    ) -> ComplianceReport:
        """Generate a structured compliance report.

        Args:
            start_time: Report period start.
            end_time: Report period end.
            report_type: Report type (default ``"decisions"``).
            format: Output format (default ``"json"``).

        Returns:
            :class:`ComplianceReport` with entries and summary.
        """
        data = await self._post(
            f"{self.endpoint}/api/audit/compliance-report",
            json={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "report_type": report_type,
                "format": format,
            },
        )
        return ComplianceReport(**data)

    async def get_decision_chain(self, decision_id: str) -> DecisionChain:
        """Get the chain of related decisions for an audit trail.

        Args:
            decision_id: Root decision identifier.

        Returns:
            :class:`DecisionChain` linking the decision to its rationale
            and approvals.
        """
        data = await self._get(f"{self.endpoint}/api/audit/decisions/{decision_id}/chain")
        return DecisionChain(**data)

    # ------------------------------------------------------------------
    # Covenant Management API
    # ------------------------------------------------------------------

    async def create_covenant(self, covenant_data: dict) -> Covenant:
        """Create a new covenant.

        Args:
            covenant_data: Covenant definition (title, parties, terms, etc.).

        Returns:
            Created :class:`Covenant`.
        """
        data = await self._post(f"{self.endpoint}/api/covenants", json=covenant_data)
        return Covenant(**data)

    async def validate_covenant(self, covenant_id: str) -> CovenantValidation:
        """Validate a covenant against its terms."""
        data = await self._get(f"{self.endpoint}/api/covenants/{covenant_id}/validate")
        return CovenantValidation(**data)

    async def list_covenants(self, status: Optional[str] = None) -> List[Covenant]:
        """List covenants with optional status filter."""
        params: Dict[str, str] = {}
        if status:
            params["status"] = status
        data = await self._get(f"{self.endpoint}/api/covenants", params=params)
        return [Covenant(**c) for c in data.get("covenants", [])]

    async def sign_covenant(self, covenant_id: str, signer: str) -> Covenant:
        """Sign a covenant."""
        data = await self._post(
            f"{self.endpoint}/api/covenants/{covenant_id}/sign",
            json={"signer": signer},
        )
        return Covenant(**data)

    # ------------------------------------------------------------------
    # Analytics and Metrics API
    # ------------------------------------------------------------------

    async def record_metric(
        self, name: str, value: float, tags: Optional[dict] = None,
    ) -> None:
        """Record a metric data point."""
        await self._post(
            f"{self.endpoint}/api/metrics",
            json={"name": name, "value": value, "tags": tags or {}},
        )

    async def get_metrics(
        self, name: str, start: Optional[datetime] = None, end: Optional[datetime] = None,
    ) -> MetricsSeries:
        """Retrieve a metric time series."""
        params: Dict[str, str] = {"name": name}
        if start:
            params["start"] = start.isoformat()
        if end:
            params["end"] = end.isoformat()
        data = await self._get(f"{self.endpoint}/api/metrics", params=params)
        return MetricsSeries(**data)

    async def create_kpi(self, kpi_definition: dict) -> KPI:
        """Create a KPI definition."""
        data = await self._post(f"{self.endpoint}/api/kpis", json=kpi_definition)
        return KPI(**data)

    async def get_kpi_dashboard(self) -> Dashboard:
        """Get the KPI dashboard."""
        data = await self._get(f"{self.endpoint}/api/kpis/dashboard")
        return Dashboard(**data)

    async def create_dashboard(
        self, name: str, kpi_ids: List[str], layout: Optional[dict] = None,
    ) -> Dashboard:
        """Create a custom dashboard with selected KPIs.

        Args:
            name: Dashboard name.
            kpi_ids: KPI identifiers to include.
            layout: Optional layout configuration.

        Returns:
            Created :class:`Dashboard`.
        """
        data = await self._post(
            f"{self.endpoint}/api/dashboards",
            json={"name": name, "kpi_ids": kpi_ids, "layout": layout or {}},
        )
        return Dashboard(**data)

    async def create_alert(
        self, metric_name: str, threshold: float, condition: str = "gt",
    ) -> Alert:
        """Create a threshold-based metric alert.

        Args:
            metric_name: Metric to monitor.
            threshold: Threshold value.
            condition: Condition (``"gt"``, ``"lt"``, ``"eq"``).

        Returns:
            Created :class:`Alert`.
        """
        data = await self._post(
            f"{self.endpoint}/api/alerts",
            json={"metric_name": metric_name, "threshold": threshold, "condition": condition},
        )
        return Alert(**data)

    async def list_alerts(self, status: Optional[str] = None) -> List[Alert]:
        """List metric alerts with optional status filter."""
        params: Dict[str, str] = {}
        if status:
            params["status"] = status
        data = await self._get(f"{self.endpoint}/api/alerts", params=params)
        return [Alert(**a) for a in data.get("alerts", [])]

    # ------------------------------------------------------------------
    # MCP Server Integration
    # ------------------------------------------------------------------

    async def list_mcp_servers(self) -> List[MCPServer]:
        """List available MCP servers."""
        data = await self._get(f"{self.endpoint}/api/mcp/servers")
        return [MCPServer(**s) for s in data.get("servers", [])]

    async def call_mcp_tool(self, server: str, tool: str, args: dict) -> Any:
        """Invoke a tool on an MCP server."""
        data = await self._post(
            f"{self.endpoint}/api/mcp/servers/{server}/tools/{tool}",
            json=args,
        )
        return data

    async def get_mcp_server_status(self, server: str) -> MCPServerStatus:
        """Get the status of an MCP server."""
        data = await self._get(f"{self.endpoint}/api/mcp/servers/{server}/status")
        return MCPServerStatus(**data)

    # ------------------------------------------------------------------
    # Agent Interaction API (Direct Messaging)
    # ------------------------------------------------------------------

    async def ask_agent(
        self, agent_id: str, message: str, context: Optional[dict] = None,
    ) -> AgentResponse:
        """Send a direct message to an agent and get a response.

        Args:
            agent_id: Target agent identifier.
            message: Message text.
            context: Optional context data.

        Returns:
            :class:`AgentResponse` from the agent.
        """
        payload: Dict[str, Any] = {"message": message}
        if context:
            payload["context"] = context
        data = await self._post(f"{self.endpoint}/api/agents/{agent_id}/ask", json=payload)
        return AgentResponse(**data)

    async def send_to_agent(self, agent_id: str, message: dict) -> None:
        """Send a fire-and-forget message to an agent."""
        await self._post(f"{self.endpoint}/api/agents/{agent_id}/send", json=message)

    # ------------------------------------------------------------------
    # Network Discovery API
    # ------------------------------------------------------------------

    async def discover_peers(self, criteria: Optional[dict] = None) -> List[PeerApp]:
        """Discover peer applications in the AOS network."""
        data = await self._post(
            f"{self.endpoint}/api/network/discover", json=criteria or {},
        )
        return [PeerApp(**p) for p in data.get("peers", [])]

    async def join_network(self, network_id: str) -> NetworkMembership:
        """Join an AOS network."""
        data = await self._post(
            f"{self.endpoint}/api/network/{network_id}/join", json={},
        )
        return NetworkMembership(**data)

    async def list_networks(self) -> List[Network]:
        """List available networks."""
        data = await self._get(f"{self.endpoint}/api/network")
        return [Network(**n) for n in data.get("networks", [])]

    async def create_network(
        self, name: str, covenant_id: str, description: str = "",
    ) -> Network:
        """Create a covenant-based network.

        Args:
            name: Network name.
            covenant_id: Required covenant for membership.
            description: Network description.

        Returns:
            Created :class:`Network`.
        """
        data = await self._post(
            f"{self.endpoint}/api/network",
            json={"name": name, "covenant_id": covenant_id, "description": description},
        )
        return Network(**data)

    async def request_membership(
        self, network_id: str, covenant_signature: str,
    ) -> NetworkMembership:
        """Request membership in a covenant-based network.

        Args:
            network_id: Target network.
            covenant_signature: Signed covenant proof.

        Returns:
            :class:`NetworkMembership` record.
        """
        data = await self._post(
            f"{self.endpoint}/api/network/{network_id}/request",
            json={"covenant_signature": covenant_signature},
        )
        return NetworkMembership(**data)

    async def verify_peer(self, peer_app_id: str, network_id: str) -> PeerVerification:
        """Verify a peer's membership in a covenant-based network.

        Args:
            peer_app_id: Peer application identifier.
            network_id: Network to verify against.

        Returns:
            :class:`PeerVerification` result.
        """
        data = await self._get(
            f"{self.endpoint}/api/network/{network_id}/verify/{peer_app_id}",
        )
        return PeerVerification(**data)

    # ------------------------------------------------------------------
    # Orchestration Streaming API
    # ------------------------------------------------------------------

    async def subscribe_to_orchestration(
        self,
        orchestration_id: str,
        callback: Callable[[OrchestrationUpdate], Awaitable[None]],
    ) -> Subscription:
        """Subscribe to updates from a specific orchestration instance.

        Args:
            orchestration_id: Orchestration to subscribe to.
            callback: Async callback invoked for each update.

        Returns:
            :class:`Subscription` handle.
        """
        sub_id = str(uuid.uuid4())
        self._subscriptions[sub_id] = callback
        data = await self._post(
            f"{self.endpoint}/api/orchestrations/{orchestration_id}/subscribe",
            json={"subscription_id": sub_id},
        )
        return Subscription(**data)

    async def stream_orchestration_updates(
        self, orchestration_id: str,
    ) -> AsyncIterator[OrchestrationUpdate]:
        """Async iterator over updates from a specific orchestration.

        Usage::

            async for update in client.stream_orchestration_updates(orch_id):
                process(update)
        """
        data = await self._get(
            f"{self.endpoint}/api/orchestrations/{orchestration_id}/updates",
        )
        for item in data.get("updates", []):
            yield OrchestrationUpdate(**item)

    # ------------------------------------------------------------------
    # Webhook API
    # ------------------------------------------------------------------

    async def register_webhook(self, url: str, events: List[str]) -> Webhook:
        """Register a webhook for external notifications.

        Args:
            url: Webhook target URL.
            events: Event types to subscribe to.

        Returns:
            Registered :class:`Webhook`.
        """
        data = await self._post(
            f"{self.endpoint}/api/webhooks",
            json={"url": url, "events": events},
        )
        return Webhook(**data)

    async def list_webhooks(self) -> List[Webhook]:
        """List registered webhooks."""
        data = await self._get(f"{self.endpoint}/api/webhooks")
        return [Webhook(**w) for w in data.get("webhooks", [])]


class AOSMultiTenantClient:
    """Multi-tenant wrapper that routes calls to per-tenant AOSClient instances.

    Usage::

        client = AOSMultiTenantClient(
            endpoints={"org-123": "https://org123.azurewebsites.net",
                        "org-456": "https://org456.azurewebsites.net"},
        )
        agents = await client.for_tenant("org-123").list_agents()
    """

    def __init__(self, endpoints: Dict[str, str], **kwargs: Any) -> None:
        self._endpoints = endpoints
        self._kwargs = kwargs
        self._clients: Dict[str, AOSClient] = {}

    def for_tenant(self, tenant_id: str) -> AOSClient:
        """Return an :class:`AOSClient` bound to the given tenant."""
        if tenant_id not in self._clients:
            if tenant_id not in self._endpoints:
                raise KeyError(f"No endpoint configured for tenant '{tenant_id}'")
            self._clients[tenant_id] = AOSClient(
                endpoint=self._endpoints[tenant_id],
                tenant_id=tenant_id,
                **self._kwargs,
            )
        return self._clients[tenant_id]

    async def __aenter__(self) -> "AOSMultiTenantClient":
        for tenant_id in self._endpoints:
            client = self.for_tenant(tenant_id)
            await client.__aenter__()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        for client in self._clients.values():
            await client.__aexit__(*exc)
        self._clients.clear()
