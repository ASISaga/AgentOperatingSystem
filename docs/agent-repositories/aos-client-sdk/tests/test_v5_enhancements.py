"""Tests for v5.0.0 SDK enhancements."""

import pytest
from datetime import datetime, timedelta

from aos_client.testing import MockAOSClient
from aos_client.models import (
    RiskHeatmapCell,
    RiskHeatmap,
    RiskSummary,
    RiskTrend,
    CovenantEvent,
    ComplianceReport,
    DecisionChain,
    Subscription,
    Alert,
    MCPEvent,
    PeerVerification,
    Webhook,
    WebhookEvent,
    OrchestrationUpdate,
)
from aos_client.app import AOSApp
from aos_client.client import AOSMultiTenantClient
from aos_client.cli import main


# ---------------------------------------------------------------------------
# 1. TestNewModels
# ---------------------------------------------------------------------------


class TestNewModels:
    def test_risk_heatmap_cell(self):
        cell = RiskHeatmapCell(likelihood_range="0.6-0.8", impact_range="0.8-1.0", count=3, risk_ids=["r-1"])
        assert cell.count == 3
        assert cell.risk_ids == ["r-1"]

    def test_risk_heatmap(self):
        heatmap = RiskHeatmap(cells=[], total_risks=0)
        assert heatmap.total_risks == 0
        assert heatmap.cells == []

    def test_risk_summary(self):
        summary = RiskSummary(by_category={"financial": 2}, by_severity={"high": 1}, by_status={"identified": 2}, total_open=2)
        assert summary.total_open == 2
        assert summary.by_category["financial"] == 2

    def test_risk_trend(self):
        trend = RiskTrend(period="30d", new_risks=5, mitigated_risks=2, risk_score_avg=0.45)
        assert trend.period == "30d"
        assert trend.new_risks == 5

    def test_covenant_event(self):
        event = CovenantEvent(covenant_id="cov-1", event_type="violated", details={"rule": "budget"})
        assert event.event_type == "violated"

    def test_compliance_report(self):
        now = datetime.utcnow()
        report = ComplianceReport(report_type="decisions", period_start=now, period_end=now)
        assert report.report_type == "decisions"
        assert report.entries == []

    def test_decision_chain(self):
        chain = DecisionChain(decision_id="dec-1", chain=[], complete=True)
        assert chain.complete is True

    def test_subscription(self):
        sub = Subscription(id="sub-1", orchestration_id="orch-1")
        assert sub.status == "active"

    def test_alert(self):
        alert = Alert(id="alert-1", metric_name="cpu", threshold=90.0)
        assert alert.condition == "gt"
        assert alert.status == "active"

    def test_mcp_event(self):
        event = MCPEvent(server="erpnext", event_type="order_created", payload={"order_id": "123"})
        assert event.server == "erpnext"

    def test_peer_verification(self):
        pv = PeerVerification(peer_app_id="app-1", network_id="net-1", verified=True, covenant_status="active")
        assert pv.verified is True

    def test_webhook(self):
        wh = Webhook(id="wh-1", url="https://example.com/hook", events=["risk.created"])
        assert wh.status == "active"
        assert wh.events == ["risk.created"]

    def test_webhook_event(self):
        we = WebhookEvent(webhook_id="wh-1", event_type="risk.created", payload={"risk_id": "r-1"})
        assert we.event_type == "risk.created"


# ---------------------------------------------------------------------------
# 2. TestKnowledgeBatchVersioning
# ---------------------------------------------------------------------------


class TestKnowledgeBatchVersioning:
    async def test_create_documents_batch(self):
        client = MockAOSClient()
        docs = await client.create_documents_batch([
            {"title": "Policy A", "doc_type": "policy", "content": {"text": "a"}},
            {"title": "Policy B", "doc_type": "policy", "content": {"text": "b"}},
        ])
        assert len(docs) == 2
        assert docs[0].title == "Policy A"
        assert docs[1].title == "Policy B"

    async def test_get_document_versions(self):
        client = MockAOSClient()
        doc = await client.create_document("Versioned", "policy", {"v": 1})
        versions = await client.get_document_versions(doc.id)
        assert len(versions) >= 1
        assert versions[0].id == doc.id

    async def test_restore_document_version(self):
        client = MockAOSClient()
        doc = await client.create_document("Restorable", "policy", {"v": 1})
        restored = await client.restore_document_version(doc.id, 0)
        assert restored.id == doc.id

    async def test_export_documents(self):
        client = MockAOSClient()
        await client.create_document("Export Me", "report", {"data": "value"})
        data = await client.export_documents("Export")
        assert isinstance(data, bytes)
        assert b"Export Me" in data


# ---------------------------------------------------------------------------
# 3. TestRiskAggregation
# ---------------------------------------------------------------------------


class TestRiskAggregation:
    async def test_get_risk_heatmap(self):
        client = MockAOSClient()
        await client.register_risk({"title": "Risk A", "owner": "coo", "category": "operational"})
        risk = await client.register_risk({"title": "Risk B", "owner": "cfo", "category": "financial"})
        await client.assess_risk(risk.id, 0.7, 0.9)
        heatmap = await client.get_risk_heatmap()
        assert isinstance(heatmap, RiskHeatmap)
        assert heatmap.total_risks == 2

    async def test_get_risk_summary(self):
        client = MockAOSClient()
        risk = await client.register_risk({"title": "Risk C", "owner": "cto", "category": "technical"})
        await client.assess_risk(risk.id, 0.5, 0.5)
        summary = await client.get_risk_summary()
        assert isinstance(summary, RiskSummary)
        assert summary.total_open >= 1
        assert "technical" in summary.by_category

    async def test_get_risk_trends(self):
        client = MockAOSClient()
        await client.register_risk({"title": "Trend Risk", "owner": "coo"})
        trends = await client.get_risk_trends(period="30d")
        assert isinstance(trends, list)
        assert len(trends) >= 1
        assert trends[0].period == "30d"


# ---------------------------------------------------------------------------
# 4. TestComplianceReporting
# ---------------------------------------------------------------------------


class TestComplianceReporting:
    async def test_generate_compliance_report(self):
        client = MockAOSClient()
        await client.log_decision({"title": "Expand EU", "agent_id": "ceo"})
        now = datetime.utcnow()
        report = await client.generate_compliance_report(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            report_type="decisions",
        )
        assert isinstance(report, ComplianceReport)
        assert report.report_type == "decisions"
        assert len(report.entries) == 1

    async def test_get_decision_chain(self):
        client = MockAOSClient()
        record = await client.log_decision({"title": "Root Decision", "agent_id": "ceo"})
        await client.log_decision({
            "title": "Follow-up", "agent_id": "cfo",
            "context": {"parent_id": record.id},
        })
        chain = await client.get_decision_chain(record.id)
        assert isinstance(chain, DecisionChain)
        assert chain.decision_id == record.id
        assert len(chain.chain) == 2


# ---------------------------------------------------------------------------
# 5. TestAnalyticsAlerts
# ---------------------------------------------------------------------------


class TestAnalyticsAlerts:
    async def test_create_dashboard(self):
        client = MockAOSClient()
        kpi = await client.create_kpi({"name": "Revenue", "target_value": 1000000})
        dashboard = await client.create_dashboard("Exec Dashboard", kpi_ids=[kpi.id])
        assert len(dashboard.kpis) == 1
        assert dashboard.kpis[0].name == "Revenue"

    async def test_create_alert(self):
        client = MockAOSClient()
        alert = await client.create_alert("cpu_usage", threshold=90.0, condition="gt")
        assert isinstance(alert, Alert)
        assert alert.metric_name == "cpu_usage"
        assert alert.threshold == 90.0

    async def test_list_alerts(self):
        client = MockAOSClient()
        await client.create_alert("cpu_usage", threshold=90.0)
        await client.create_alert("memory", threshold=80.0)
        alerts = await client.list_alerts()
        assert len(alerts) == 2


# ---------------------------------------------------------------------------
# 6. TestNetworkFederation
# ---------------------------------------------------------------------------


class TestNetworkFederation:
    async def test_create_network(self):
        client = MockAOSClient()
        network = await client.create_network("Global Net", covenant_id="cov-1", description="A test network")
        assert network.name == "Global Net"
        assert network.metadata["covenant_id"] == "cov-1"

    async def test_request_membership(self):
        client = MockAOSClient()
        network = await client.create_network("Net", covenant_id="cov-1")
        membership = await client.request_membership(network.id, covenant_signature="sig-abc")
        assert membership.network_id == network.id
        assert membership.status == "active"

    async def test_verify_peer(self):
        client = MockAOSClient()
        network = await client.create_network("Peer Net", covenant_id="cov-1")
        verification = await client.verify_peer("app-peer", network.id)
        assert isinstance(verification, PeerVerification)
        assert verification.verified is True
        assert verification.covenant_status == "active"


# ---------------------------------------------------------------------------
# 7. TestOrchestrationStreaming
# ---------------------------------------------------------------------------


class TestOrchestrationStreaming:
    async def test_subscribe_to_orchestration(self):
        client = MockAOSClient()
        status = await client.start_orchestration(agent_ids=["ceo"], purpose="Test")

        async def callback(update):
            pass

        sub = await client.subscribe_to_orchestration(status.orchestration_id, callback)
        assert isinstance(sub, Subscription)
        assert sub.orchestration_id == status.orchestration_id
        assert sub.status == "active"

    async def test_stream_orchestration_updates(self):
        client = MockAOSClient()
        orch_id = "orch-stream"
        client._updates[orch_id] = [
            OrchestrationUpdate(orchestration_id=orch_id, agent_id="ceo", output="step 1"),
            OrchestrationUpdate(orchestration_id=orch_id, agent_id="cmo", output="step 2"),
        ]
        updates = []
        async for update in client.stream_orchestration_updates(orch_id):
            updates.append(update)
        assert len(updates) == 2
        assert updates[0].output == "step 1"
        assert updates[1].agent_id == "cmo"


# ---------------------------------------------------------------------------
# 8. TestWebhooks
# ---------------------------------------------------------------------------


class TestWebhooks:
    async def test_register_webhook(self):
        client = MockAOSClient()
        wh = await client.register_webhook("https://example.com/hook", events=["risk.created"])
        assert isinstance(wh, Webhook)
        assert wh.url == "https://example.com/hook"
        assert wh.events == ["risk.created"]
        assert wh.status == "active"

    async def test_list_webhooks(self):
        client = MockAOSClient()
        await client.register_webhook("https://a.com/hook", events=["a"])
        await client.register_webhook("https://b.com/hook", events=["b"])
        webhooks = await client.list_webhooks()
        assert len(webhooks) == 2


# ---------------------------------------------------------------------------
# 9. TestAOSAppNewDecorators
# ---------------------------------------------------------------------------


class TestAOSAppNewDecorators:
    def test_on_covenant_event_decorator(self):
        app = AOSApp(name="test-app")

        @app.on_covenant_event("violated")
        async def handle_violation(event):
            pass

        assert "violated" in app.get_covenant_event_handler_names()

    def test_on_mcp_event_decorator(self):
        app = AOSApp(name="test-app")

        @app.on_mcp_event("erpnext", "order_created")
        async def handle_order(event):
            pass

        assert "erpnext:order_created" in app.get_mcp_event_handler_names()

    def test_webhook_decorator(self):
        app = AOSApp(name="test-app")

        @app.webhook("slack-notifications")
        async def notify_slack(event):
            pass

        assert "slack-notifications" in app.get_webhook_names()

    def test_workflow_versioning(self):
        app = AOSApp(name="test-app")

        @app.workflow("strategic-review", version="1.0")
        async def v1(request):
            pass

        @app.workflow("strategic-review", version="2.0")
        async def v2(request):
            pass

        names = app.get_workflow_names()
        assert "strategic-review" in names
        assert "strategic-review@2.0" in names

    def test_traffic_split(self):
        app = AOSApp(name="test-app")
        app.set_traffic_split("strategic-review", {"1.0": 50, "2.0": 50})
        splits = app.get_traffic_splits()
        assert "strategic-review" in splits
        assert splits["strategic-review"] == {"1.0": 50, "2.0": 50}


# ---------------------------------------------------------------------------
# 10. TestMultiTenantClient
# ---------------------------------------------------------------------------


class TestMultiTenantClient:
    def test_for_tenant_creates_client(self):
        mt = AOSMultiTenantClient(endpoints={
            "org-123": "https://org123.azurewebsites.net",
            "org-456": "https://org456.azurewebsites.net",
        })
        client = mt.for_tenant("org-123")
        assert client.endpoint == "https://org123.azurewebsites.net"

    def test_for_tenant_unknown_tenant(self):
        mt = AOSMultiTenantClient(endpoints={"org-123": "https://org123.azurewebsites.net"})
        with pytest.raises(KeyError, match="org-999"):
            mt.for_tenant("org-999")


# ---------------------------------------------------------------------------
# 11. TestCLI
# ---------------------------------------------------------------------------


class TestCLI:
    def test_cli_help(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0
