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

import json
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
    CovenantStatus,
    CovenantValidation,
    Dashboard,
    DecisionChain,
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
    PeerVerification,
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskHeatmap,
    RiskHeatmapCell,
    RiskSeverity,
    RiskStatus,
    RiskSummary,
    RiskTrend,
    Subscription,
    Webhook,
    calculate_risk_severity,
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
        self._alerts: Dict[str, Alert] = {}
        self._webhooks: Dict[str, Webhook] = {}
        self._document_versions: Dict[str, List[Document]] = {}
        self._subscriptions: Dict[str, Callable[[OrchestrationUpdate], Awaitable[None]]] = {}
        self._updates: Dict[str, List[OrchestrationUpdate]] = {}
        self._dashboards: Dict[str, Dashboard] = {}

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

    async def create_documents_batch(self, documents: List[dict]) -> List[Document]:
        created: List[Document] = []
        for doc_data in documents:
            doc = await self.create_document(
                title=doc_data.get("title", ""),
                doc_type=doc_data.get("doc_type", ""),
                content=doc_data.get("content", {}),
                **{k: v for k, v in doc_data.items() if k not in ("title", "doc_type", "content")},
            )
            created.append(doc)
        return created

    async def get_document_versions(self, document_id: str) -> List[Document]:
        if document_id not in self._documents:
            raise KeyError(f"Document {document_id} not found")
        return self._document_versions.get(document_id, [self._documents[document_id]])

    async def restore_document_version(self, document_id: str, version: int) -> Document:
        versions = await self.get_document_versions(document_id)
        if version < 0 or version >= len(versions):
            raise KeyError(f"Version {version} not found for document {document_id}")
        restored = versions[version]
        self._documents[document_id] = restored
        return restored

    async def export_documents(self, query: str, format: str = "json") -> bytes:
        results = await self.search_documents(query)
        data = [doc.model_dump(mode="json") for doc in results]
        return json.dumps(data).encode("utf-8")

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
        severity = calculate_risk_severity(likelihood, impact)
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

    async def get_risk_heatmap(self, category: Optional[str] = None) -> RiskHeatmap:
        risks = list(self._risks.values())
        if category:
            risks = [r for r in risks if r.category == category]
        cells: List[RiskHeatmapCell] = []
        buckets = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
        for lb in buckets:
            for ib in buckets:
                l_lo = float(lb.split("-")[0])
                l_hi = float(lb.split("-")[1])
                i_lo = float(ib.split("-")[0])
                i_hi = float(ib.split("-")[1])
                matching = [
                    r for r in risks
                    if r.assessment
                    and l_lo <= r.assessment.likelihood < l_hi
                    and i_lo <= r.assessment.impact < i_hi
                ]
                if matching:
                    cells.append(RiskHeatmapCell(
                        likelihood_range=lb,
                        impact_range=ib,
                        count=len(matching),
                        risk_ids=[r.id for r in matching],
                    ))
        return RiskHeatmap(cells=cells, total_risks=len(risks))

    async def get_risk_summary(self, category: Optional[str] = None) -> RiskSummary:
        risks = list(self._risks.values())
        if category:
            risks = [r for r in risks if r.category == category]
        by_category: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        total_open = 0
        for r in risks:
            cat = r.category if isinstance(r.category, str) else r.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            status = r.status if isinstance(r.status, str) else r.status.value
            by_status[status] = by_status.get(status, 0) + 1
            if status != "resolved":
                total_open += 1
            if r.assessment:
                sev = r.assessment.severity if isinstance(r.assessment.severity, str) else r.assessment.severity.value
                by_severity[sev] = by_severity.get(sev, 0) + 1
        return RiskSummary(
            by_category=by_category,
            by_severity=by_severity,
            by_status=by_status,
            total_open=total_open,
        )

    async def get_risk_trends(self, period: str = "30d") -> List[RiskTrend]:
        return [RiskTrend(period=period, new_risks=len(self._risks), mitigated_risks=0, risk_score_avg=0.0)]

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

    async def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        report_type: str = "decisions",
        format: str = "json",
    ) -> ComplianceReport:
        entries = [
            d for d in self._decisions
            if d.created_at and start_time <= d.created_at <= end_time
        ]
        return ComplianceReport(
            report_type=report_type,
            period_start=start_time,
            period_end=end_time,
            entries=entries,
            summary={"total": len(entries)},
            generated_at=datetime.utcnow(),
        )

    async def get_decision_chain(self, decision_id: str) -> DecisionChain:
        chain = [d for d in self._decisions if d.id == decision_id or d.context.get("parent_id") == decision_id]
        return DecisionChain(
            decision_id=decision_id,
            chain=chain,
            complete=True,
        )

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

    async def create_dashboard(
        self, name: str, kpi_ids: List[str], layout: Optional[dict] = None,
    ) -> Dashboard:
        selected = [self._kpis[kid] for kid in kpi_ids if kid in self._kpis]
        dash_id = f"dash-{uuid.uuid4().hex[:8]}"
        dashboard = Dashboard(kpis=selected, generated_at=datetime.utcnow())
        self._dashboards[dash_id] = dashboard
        return dashboard

    async def create_alert(
        self, metric_name: str, threshold: float, condition: str = "gt",
    ) -> Alert:
        alert_id = f"alert-{uuid.uuid4().hex[:8]}"
        alert = Alert(
            id=alert_id,
            metric_name=metric_name,
            threshold=threshold,
            condition=condition,
        )
        self._alerts[alert_id] = alert
        return alert

    async def list_alerts(self, status: Optional[str] = None) -> List[Alert]:
        results = list(self._alerts.values())
        if status:
            results = [a for a in results if a.status == status]
        return results

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

    async def create_network(
        self, name: str, covenant_id: str, description: str = "",
    ) -> Network:
        net_id = f"net-{uuid.uuid4().hex[:8]}"
        network = Network(
            id=net_id,
            name=name,
            description=description,
            metadata={"covenant_id": covenant_id},
        )
        self._networks[net_id] = network
        return network

    async def request_membership(
        self, network_id: str, covenant_signature: str,
    ) -> NetworkMembership:
        membership = NetworkMembership(
            network_id=network_id,
            app_id="mock-app",
            joined_at=datetime.utcnow(),
        )
        self._memberships[network_id] = membership
        return membership

    async def verify_peer(self, peer_app_id: str, network_id: str) -> PeerVerification:
        return PeerVerification(
            peer_app_id=peer_app_id,
            network_id=network_id,
            verified=network_id in self._networks,
            covenant_status="active" if network_id in self._networks else "",
            verified_at=datetime.utcnow(),
        )

    # -- Health -----------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "mock": True}

    # -- Orchestration Streaming ------------------------------------------

    async def subscribe_to_orchestration(
        self,
        orchestration_id: str,
        callback: Callable[[OrchestrationUpdate], Awaitable[None]],
    ) -> Subscription:
        sub_id = f"sub-{uuid.uuid4().hex[:8]}"
        self._subscriptions[sub_id] = callback
        return Subscription(
            id=sub_id,
            orchestration_id=orchestration_id,
            status="active",
            created_at=datetime.utcnow(),
        )

    async def stream_orchestration_updates(
        self, orchestration_id: str,
    ) -> AsyncIterator[OrchestrationUpdate]:
        for update in self._updates.get(orchestration_id, []):
            yield update

    # -- Webhooks ---------------------------------------------------------

    async def register_webhook(self, url: str, events: List[str]) -> Webhook:
        wh_id = f"wh-{uuid.uuid4().hex[:8]}"
        webhook = Webhook(
            id=wh_id,
            url=url,
            events=events,
            status="active",
            created_at=datetime.utcnow(),
        )
        self._webhooks[wh_id] = webhook
        return webhook

    async def list_webhooks(self) -> List[Webhook]:
        return list(self._webhooks.values())
