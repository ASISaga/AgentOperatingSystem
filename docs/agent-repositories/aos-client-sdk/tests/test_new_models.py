"""Tests for new AOS Client SDK models."""

import pytest
from aos_client.models import (
    Document, DocumentType, DocumentStatus,
    Risk, RiskAssessment, RiskSeverity, RiskStatus, RiskCategory,
    DecisionRecord, AuditEntry,
    Covenant, CovenantStatus, CovenantValidation,
    MetricDataPoint, MetricsSeries, KPI, Dashboard,
    MCPServer, MCPServerStatus,
    OrchestrationUpdate,
    AgentResponse,
    PeerApp, NetworkMembership, Network,
)


class TestDocument:
    def test_create_minimal(self):
        doc = Document(id="doc-1", title="Policy Doc", doc_type="policy", content={"text": "hello"})
        assert doc.id == "doc-1"
        assert doc.status == "draft"
        assert doc.tags == []

    def test_create_full(self):
        doc = Document(
            id="doc-2", title="Decision", doc_type="decision",
            content={"rationale": "growth"}, tags=["important"],
            metadata={"source": "board"}, created_by="admin",
        )
        assert doc.doc_type == "decision"
        assert doc.tags == ["important"]
        assert doc.created_by == "admin"


class TestDocumentEnums:
    def test_document_types(self):
        assert DocumentType.DECISION == "decision"
        assert DocumentType.POLICY == "policy"
        assert DocumentType.REPORT == "report"

    def test_document_status(self):
        assert DocumentStatus.DRAFT == "draft"
        assert DocumentStatus.PUBLISHED == "published"
        assert DocumentStatus.ARCHIVED == "archived"


class TestRisk:
    def test_create_minimal(self):
        risk = Risk(id="r-1", title="Supply chain", description="Disruption risk",
                    category="operational", owner="coo")
        assert risk.status == "identified"
        assert risk.assessment is None

    def test_create_with_assessment(self):
        assessment = RiskAssessment(likelihood=0.7, impact=0.9, severity="critical")
        risk = Risk(id="r-2", title="Market crash", description="Global downturn",
                    category="financial", owner="cfo", assessment=assessment)
        assert risk.assessment.severity == "critical"


class TestRiskEnums:
    def test_severity_values(self):
        assert RiskSeverity.CRITICAL == "critical"
        assert RiskSeverity.INFO == "info"

    def test_status_values(self):
        assert RiskStatus.IDENTIFIED == "identified"
        assert RiskStatus.RESOLVED == "resolved"

    def test_category_values(self):
        assert RiskCategory.FINANCIAL == "financial"
        assert RiskCategory.SECURITY == "security"


class TestDecisionRecord:
    def test_create_minimal(self):
        record = DecisionRecord(id="dec-1")
        assert record.decision_type == ""
        assert record.context == {}

    def test_create_full(self):
        record = DecisionRecord(
            id="dec-2", orchestration_id="orch-1", agent_id="ceo",
            decision_type="strategic", title="Expand to EU",
            rationale="Market opportunity", confidence=0.85,
        )
        assert record.agent_id == "ceo"
        assert record.confidence == 0.85


class TestAuditEntry:
    def test_create(self):
        entry = AuditEntry(
            id="aud-1", event_type="decision", subject_id="ceo",
            action="approved budget",
        )
        assert entry.subject_type == "system"
        assert entry.severity == "medium"


class TestCovenant:
    def test_create_minimal(self):
        cov = Covenant(id="cov-1", title="Business Ethics")
        assert cov.status == "draft"
        assert cov.version == "1.0"
        assert cov.signers == []

    def test_covenant_status_enum(self):
        assert CovenantStatus.DRAFT == "draft"
        assert CovenantStatus.ACTIVE == "active"

    def test_covenant_validation(self):
        val = CovenantValidation(covenant_id="cov-1", valid=True)
        assert val.violations == []


class TestAnalyticsModels:
    def test_metric_data_point(self):
        point = MetricDataPoint(value=42.0)
        assert point.tags == {}

    def test_metrics_series(self):
        series = MetricsSeries(name="revenue", data_points=[MetricDataPoint(value=100.0)])
        assert len(series.data_points) == 1

    def test_kpi(self):
        kpi = KPI(id="kpi-1", name="Revenue Growth", target_value=0.15, current_value=0.12, unit="%")
        assert kpi.unit == "%"

    def test_dashboard(self):
        dashboard = Dashboard(kpis=[KPI(id="kpi-1", name="Revenue")])
        assert len(dashboard.kpis) == 1


class TestMCPModels:
    def test_mcp_server(self):
        server = MCPServer(name="erpnext", tools=["search", "create"])
        assert len(server.tools) == 2

    def test_mcp_server_status(self):
        status = MCPServerStatus(name="erpnext", status="running")
        assert status.healthy is True


class TestOrchestrationUpdate:
    def test_create(self):
        update = OrchestrationUpdate(orchestration_id="orch-1", agent_id="ceo", output="analysis complete")
        assert update.update_type == "status"


class TestAgentResponse:
    def test_create(self):
        resp = AgentResponse(agent_id="ceo", message="Growth looks strong")
        assert resp.context == {}


class TestNetworkModels:
    def test_peer_app(self):
        peer = PeerApp(app_id="app-1", name="TechCorp")
        assert peer.description == ""

    def test_network_membership(self):
        mem = NetworkMembership(network_id="net-1", app_id="app-1")
        assert mem.status == "active"

    def test_network(self):
        net = Network(id="net-1", name="Global Boardroom Network")
        assert net.members == []
