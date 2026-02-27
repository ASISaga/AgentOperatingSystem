"""Tests for MockAOSClient (local development mocks)."""

import pytest
from aos_client.testing import MockAOSClient
from aos_client.models import AgentDescriptor, OrchestrationStatusEnum


class TestMockAOSClient:
    async def test_context_manager(self):
        async with MockAOSClient() as client:
            assert client.endpoint == "http://localhost:7071"

    async def test_add_and_list_agents(self):
        client = MockAOSClient()
        client.add_agent(AgentDescriptor(
            agent_id="ceo", agent_type="LeadershipAgent",
            purpose="Lead", adapter_name="leadership",
        ))
        agents = await client.list_agents()
        assert len(agents) == 1
        assert agents[0].agent_id == "ceo"

    async def test_list_agents_filter(self):
        client = MockAOSClient()
        client.add_agent(AgentDescriptor(
            agent_id="ceo", agent_type="LeadershipAgent",
            purpose="Lead", adapter_name="leadership",
        ))
        client.add_agent(AgentDescriptor(
            agent_id="cmo", agent_type="CMOAgent",
            purpose="Market", adapter_name="marketing",
        ))
        leaders = await client.list_agents(agent_type="LeadershipAgent")
        assert len(leaders) == 1

    async def test_start_and_stop_orchestration(self):
        client = MockAOSClient()
        status = await client.start_orchestration(
            agent_ids=["ceo"], purpose="Test purpose",
        )
        assert status.status == OrchestrationStatusEnum.PENDING
        stopped = await client.stop_orchestration(status.orchestration_id)
        assert stopped.status == OrchestrationStatusEnum.STOPPED

    async def test_knowledge_base_crud(self):
        client = MockAOSClient()
        doc = await client.create_document("Policy", "policy", {"text": "rules"})
        assert doc.title == "Policy"
        fetched = await client.get_document(doc.id)
        assert fetched.id == doc.id
        updated = await client.update_document(doc.id, {"text": "new rules"})
        assert updated.content["text"] == "new rules"
        results = await client.search_documents("Policy")
        assert len(results) == 1
        await client.delete_document(doc.id)
        with pytest.raises(KeyError):
            await client.get_document(doc.id)

    async def test_risk_registry(self):
        client = MockAOSClient()
        risk = await client.register_risk({"title": "Supply chain", "owner": "coo"})
        assert risk.title == "Supply chain"
        assessed = await client.assess_risk(risk.id, 0.7, 0.9)
        assert assessed.assessment is not None
        risks = await client.get_risks()
        assert len(risks) == 1
        updated = await client.update_risk_status(risk.id, "mitigating")
        assert updated.status == "mitigating"
        mitigated = await client.add_mitigation_plan(risk.id, "Diversify suppliers")
        assert mitigated.mitigation_plan == "Diversify suppliers"

    async def test_audit_trail(self):
        client = MockAOSClient()
        record = await client.log_decision({"title": "Expand EU", "agent_id": "ceo"})
        assert record.title == "Expand EU"
        history = await client.get_decision_history(agent_id="ceo")
        assert len(history) == 1
        trail = await client.get_audit_trail()
        assert isinstance(trail, list)

    async def test_covenant_management(self):
        client = MockAOSClient()
        cov = await client.create_covenant({"title": "Ethics Covenant"})
        assert cov.title == "Ethics Covenant"
        val = await client.validate_covenant(cov.id)
        assert val.valid is True
        signed = await client.sign_covenant(cov.id, "ceo")
        assert "ceo" in signed.signers
        covenants = await client.list_covenants()
        assert len(covenants) == 1

    async def test_analytics(self):
        client = MockAOSClient()
        await client.record_metric("revenue", 1000000.0)
        series = await client.get_metrics("revenue")
        assert len(series.data_points) == 1
        kpi = await client.create_kpi({"name": "Growth", "target_value": 0.15})
        assert kpi.name == "Growth"
        dashboard = await client.get_kpi_dashboard()
        assert len(dashboard.kpis) == 1

    async def test_mcp(self):
        client = MockAOSClient()
        servers = await client.list_mcp_servers()
        assert isinstance(servers, list)
        result = await client.call_mcp_tool("erpnext", "search", {"q": "test"})
        assert result["server"] == "erpnext"
        status = await client.get_mcp_server_status("erpnext")
        assert status.healthy is True

    async def test_agent_interaction(self):
        client = MockAOSClient()
        resp = await client.ask_agent("ceo", "What is the strategy?")
        assert resp.agent_id == "ceo"
        await client.send_to_agent("ceo", {"type": "update"})

    async def test_network_discovery(self):
        client = MockAOSClient()
        peers = await client.discover_peers()
        assert isinstance(peers, list)
        membership = await client.join_network("net-1")
        assert membership.network_id == "net-1"
        networks = await client.list_networks()
        assert isinstance(networks, list)

    async def test_health_check(self):
        client = MockAOSClient()
        health = await client.health_check()
        assert health["status"] == "healthy"
