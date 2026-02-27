"""Local development mocks for AOS client applications.

Provides ``MockAOSClient`` for testing workflows without a live AOS
deployment, and a ``local`` mode for :class:`AOSApp`.

Usage::

    from aos_client.testing import MockAOSClient
    from aos_client.models import AgentDescriptor

    client = MockAOSClient()
    client.add_agent(AgentDescriptor(
        agent_id="ceo", agent_type="LeadershipAgent",
        purpose="Strategic leadership", adapter_name="leadership",
    ))

    agents = await client.list_agents()
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from aos_client.models import (
    AgentDescriptor,
    AgentResponse,
    AuditEntry,
    Covenant,
    CovenantStatus,
    CovenantValidation,
    Dashboard,
    DecisionRecord,
    Document,
    DocumentStatus,
    KPI,
    MCPServer,
    MCPServerStatus,
    MetricDataPoint,
    MetricsSeries,
    Network,
    NetworkMembership,
    OrchestrationPurpose,
    OrchestrationRequest,
    OrchestrationStatus,
    OrchestrationStatusEnum,
    OrchestrationUpdate,
    PeerApp,
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskSeverity,
    RiskStatus,
)

logger = logging.getLogger(__name__)


class MockAOSClient:
    """In-memory mock of :class:`AOSClient` for local development and testing.

    All data is stored in memory — no network calls are made.
    """

    def __init__(self, endpoint: str = "http://localhost:7071", **kwargs: Any) -> None:
        self.endpoint = endpoint
        self._agents: Dict[str, AgentDescriptor] = {}
        self._orchestrations: Dict[str, OrchestrationStatus] = {}
        self._documents: Dict[str, Document] = {}
        self._risks: Dict[str, Risk] = {}
        self._decisions: List[DecisionRecord] = []
        self._audit_entries: List[AuditEntry] = []
        self._covenants: Dict[str, Covenant] = {}
        self._metrics: List[Dict[str, Any]] = []
        self._kpis: Dict[str, KPI] = {}
        self._mcp_servers: Dict[str, MCPServer] = {}
        self._networks: Dict[str, Network] = {}
        self._memberships: Dict[str, NetworkMembership] = {}

    # -- context manager --------------------------------------------------

    async def __aenter__(self) -> "MockAOSClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        pass

    # -- helpers ----------------------------------------------------------

    def add_agent(self, agent: AgentDescriptor) -> None:
        """Pre-populate the mock agent catalog."""
        self._agents[agent.agent_id] = agent

    # -- Agent catalog ----------------------------------------------------

    async def list_agents(self, agent_type: Optional[str] = None) -> List[AgentDescriptor]:
        agents = list(self._agents.values())
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        return agents

    async def get_agent(self, agent_id: str) -> AgentDescriptor:
        if agent_id not in self._agents:
            raise KeyError(f"Agent {agent_id} not found")
        return self._agents[agent_id]

    # -- Orchestrations ---------------------------------------------------

    async def submit_orchestration(
        self, request: OrchestrationRequest, *, via_service_bus: bool = False,
    ) -> OrchestrationStatus:
        if request.orchestration_id is None:
            request.orchestration_id = str(uuid.uuid4())
        status = OrchestrationStatus(
            orchestration_id=request.orchestration_id,
            status=OrchestrationStatusEnum.PENDING,
            agent_ids=request.agent_ids,
            purpose=request.purpose.purpose,
            created_at=datetime.utcnow(),
        )
        self._orchestrations[request.orchestration_id] = status
        return status

    async def start_orchestration(
        self,
        agent_ids: List[str],
        purpose: str,
        purpose_scope: str = "",
        context: Optional[Dict[str, Any]] = None,
        workflow: str = "collaborative",
        config: Optional[Dict[str, Any]] = None,
    ) -> OrchestrationStatus:
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

    async def get_orchestration_status(self, orchestration_id: str) -> OrchestrationStatus:
        if orchestration_id not in self._orchestrations:
            raise KeyError(f"Orchestration {orchestration_id} not found")
        return self._orchestrations[orchestration_id]

    async def stop_orchestration(self, orchestration_id: str) -> OrchestrationStatus:
        status = await self.get_orchestration_status(orchestration_id)
        status.status = OrchestrationStatusEnum.STOPPED
        return status

    async def cancel_orchestration(self, orchestration_id: str) -> OrchestrationStatus:
        status = await self.get_orchestration_status(orchestration_id)
        status.status = OrchestrationStatusEnum.CANCELLED
        return status

    # -- Knowledge Base ---------------------------------------------------

    async def create_document(
        self, title: str, doc_type: str, content: dict, **kwargs: Any,
    ) -> Document:
        doc_id = kwargs.get("id") or f"doc-{uuid.uuid4().hex[:8]}"
        doc = Document(
            id=doc_id,
            title=title,
            doc_type=doc_type,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **{k: v for k, v in kwargs.items() if k != "id"},
        )
        self._documents[doc_id] = doc
        return doc

    async def get_document(self, document_id: str) -> Document:
        if document_id not in self._documents:
            raise KeyError(f"Document {document_id} not found")
        return self._documents[document_id]

    async def search_documents(
        self, query: str, doc_type: Optional[str] = None, limit: int = 10,
    ) -> List[Document]:
        results = list(self._documents.values())
        q = query.lower()
        results = [d for d in results if q in d.title.lower() or q in str(d.content).lower()]
        if doc_type:
            results = [d for d in results if d.doc_type == doc_type]
        return results[:limit]

    async def update_document(self, document_id: str, content: dict) -> Document:
        doc = await self.get_document(document_id)
        doc.content = content
        doc.updated_at = datetime.utcnow()
        return doc

    async def delete_document(self, document_id: str) -> None:
        self._documents.pop(document_id, None)

    # -- Risk Registry ----------------------------------------------------

    async def register_risk(self, risk_data: dict) -> Risk:
        risk_id = risk_data.get("id") or f"risk-{uuid.uuid4().hex[:8]}"
        risk = Risk(
            id=risk_id,
            title=risk_data["title"],
            description=risk_data.get("description", ""),
            category=risk_data.get("category", "operational"),
            owner=risk_data.get("owner", "system"),
            tags=risk_data.get("tags", []),
            context=risk_data.get("context", {}),
            created_at=datetime.utcnow(),
        )
        self._risks[risk_id] = risk
        return risk

    async def assess_risk(
        self, risk_id: str, likelihood: float, impact: float, **kwargs: Any,
    ) -> Risk:
        if risk_id not in self._risks:
            raise KeyError(f"Risk {risk_id} not found")
        risk = self._risks[risk_id]
        score = likelihood * impact
        if score >= 0.8:
            severity = "critical"
        elif score >= 0.6:
            severity = "high"
        elif score >= 0.3:
            severity = "medium"
        elif score >= 0.1:
            severity = "low"
        else:
            severity = "info"
        risk.assessment = RiskAssessment(
            likelihood=likelihood,
            impact=impact,
            severity=severity,
            assessed_at=datetime.utcnow(),
            assessor=kwargs.get("assessor"),
            notes=kwargs.get("notes"),
        )
        risk.status = "assessing"
        risk.updated_at = datetime.utcnow()
        return risk

    async def get_risks(
        self, status: Optional[str] = None, category: Optional[str] = None,
    ) -> List[Risk]:
        results = list(self._risks.values())
        if status:
            results = [r for r in results if r.status == status]
        if category:
            results = [r for r in results if r.category == category]
        return results

    async def update_risk_status(self, risk_id: str, status: str) -> Risk:
        if risk_id not in self._risks:
            raise KeyError(f"Risk {risk_id} not found")
        risk = self._risks[risk_id]
        risk.status = status
        risk.updated_at = datetime.utcnow()
        return risk

    async def add_mitigation_plan(self, risk_id: str, plan: str, **kwargs: Any) -> Risk:
        if risk_id not in self._risks:
            raise KeyError(f"Risk {risk_id} not found")
        risk = self._risks[risk_id]
        risk.mitigation_plan = plan
        risk.status = "mitigating"
        risk.updated_at = datetime.utcnow()
        return risk

    # -- Audit Trail / Decision Ledger ------------------------------------

    async def log_decision(self, decision: dict) -> DecisionRecord:
        record = DecisionRecord(
            id=decision.get("id") or f"dec-{uuid.uuid4().hex[:8]}",
            orchestration_id=decision.get("orchestration_id"),
            agent_id=decision.get("agent_id"),
            decision_type=decision.get("decision_type", ""),
            title=decision.get("title", ""),
            description=decision.get("description", ""),
            rationale=decision.get("rationale"),
            outcome=decision.get("outcome"),
            confidence=decision.get("confidence"),
            context=decision.get("context", {}),
            created_at=datetime.utcnow(),
        )
        self._decisions.append(record)
        return record

    async def get_decision_history(
        self,
        orchestration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> List[DecisionRecord]:
        results = list(self._decisions)
        if orchestration_id:
            results = [d for d in results if d.orchestration_id == orchestration_id]
        if agent_id:
            results = [d for d in results if d.agent_id == agent_id]
        return results

    async def get_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditEntry]:
        results = list(self._audit_entries)
        if start_time:
            results = [e for e in results if e.timestamp and e.timestamp >= start_time]
        if end_time:
            results = [e for e in results if e.timestamp and e.timestamp <= end_time]
        return results

    # -- Covenant Management ----------------------------------------------

    async def create_covenant(self, covenant_data: dict) -> Covenant:
        cov_id = covenant_data.get("id") or f"cov-{uuid.uuid4().hex[:8]}"
        cov = Covenant(
            id=cov_id,
            title=covenant_data.get("title", ""),
            version=covenant_data.get("version", "1.0"),
            parties=covenant_data.get("parties", []),
            terms=covenant_data.get("terms", {}),
            created_at=datetime.utcnow(),
        )
        self._covenants[cov_id] = cov
        return cov

    async def validate_covenant(self, covenant_id: str) -> CovenantValidation:
        if covenant_id not in self._covenants:
            raise KeyError(f"Covenant {covenant_id} not found")
        return CovenantValidation(
            covenant_id=covenant_id,
            valid=True,
            checked_at=datetime.utcnow(),
        )

    async def list_covenants(self, status: Optional[str] = None) -> List[Covenant]:
        results = list(self._covenants.values())
        if status:
            results = [c for c in results if c.status == status]
        return results

    async def sign_covenant(self, covenant_id: str, signer: str) -> Covenant:
        if covenant_id not in self._covenants:
            raise KeyError(f"Covenant {covenant_id} not found")
        cov = self._covenants[covenant_id]
        if signer not in cov.signers:
            cov.signers.append(signer)
        cov.updated_at = datetime.utcnow()
        return cov

    # -- Analytics & Metrics ----------------------------------------------

    async def record_metric(
        self, name: str, value: float, tags: Optional[dict] = None,
    ) -> None:
        self._metrics.append({
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def get_metrics(
        self,
        name: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> MetricsSeries:
        points = [
            MetricDataPoint(value=m["value"], tags=m.get("tags", {}))
            for m in self._metrics
            if m["name"] == name
        ]
        return MetricsSeries(name=name, data_points=points, start=start, end=end)

    async def create_kpi(self, kpi_definition: dict) -> KPI:
        kpi_id = kpi_definition.get("id") or f"kpi-{uuid.uuid4().hex[:8]}"
        kpi = KPI(
            id=kpi_id,
            name=kpi_definition.get("name", ""),
            description=kpi_definition.get("description", ""),
            target_value=kpi_definition.get("target_value"),
            current_value=kpi_definition.get("current_value"),
            unit=kpi_definition.get("unit", ""),
            metadata=kpi_definition.get("metadata", {}),
        )
        self._kpis[kpi_id] = kpi
        return kpi

    async def get_kpi_dashboard(self) -> Dashboard:
        return Dashboard(
            kpis=list(self._kpis.values()),
            generated_at=datetime.utcnow(),
        )

    # -- MCP Server Integration -------------------------------------------

    async def list_mcp_servers(self) -> List[MCPServer]:
        return list(self._mcp_servers.values())

    async def call_mcp_tool(self, server: str, tool: str, args: dict) -> Any:
        return {"server": server, "tool": tool, "args": args, "result": "mock"}

    async def get_mcp_server_status(self, server: str) -> MCPServerStatus:
        return MCPServerStatus(
            name=server,
            status="running",
            healthy=True,
            last_checked=datetime.utcnow(),
        )

    # -- Agent Interaction ------------------------------------------------

    async def ask_agent(
        self, agent_id: str, message: str, context: Optional[dict] = None,
    ) -> AgentResponse:
        return AgentResponse(
            agent_id=agent_id,
            message=f"Mock response from {agent_id}",
            context=context or {},
            timestamp=datetime.utcnow(),
        )

    async def send_to_agent(self, agent_id: str, message: dict) -> None:
        logger.info("Mock send_to_agent: %s -> %s", agent_id, message)

    # -- Network Discovery ------------------------------------------------

    async def discover_peers(self, criteria: Optional[dict] = None) -> List[PeerApp]:
        return []

    async def join_network(self, network_id: str) -> NetworkMembership:
        membership = NetworkMembership(
            network_id=network_id,
            app_id="mock-app",
            joined_at=datetime.utcnow(),
        )
        self._memberships[network_id] = membership
        return membership

    async def list_networks(self) -> List[Network]:
        return list(self._networks.values())

    # -- Health -----------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "mock": True}
