"""Tests for new AOSClient API methods."""

import pytest
from aos_client.client import AOSClient


class TestNewClientAPIs:
    """Verify new API methods exist on AOSClient."""

    def setup_method(self):
        self.client = AOSClient(endpoint="https://my-aos.azurewebsites.net")

    # Knowledge Base
    def test_has_create_document(self):
        assert hasattr(self.client, "create_document")

    def test_has_get_document(self):
        assert hasattr(self.client, "get_document")

    def test_has_search_documents(self):
        assert hasattr(self.client, "search_documents")

    def test_has_update_document(self):
        assert hasattr(self.client, "update_document")

    def test_has_delete_document(self):
        assert hasattr(self.client, "delete_document")

    # Risk Registry
    def test_has_register_risk(self):
        assert hasattr(self.client, "register_risk")

    def test_has_assess_risk(self):
        assert hasattr(self.client, "assess_risk")

    def test_has_get_risks(self):
        assert hasattr(self.client, "get_risks")

    def test_has_update_risk_status(self):
        assert hasattr(self.client, "update_risk_status")

    def test_has_add_mitigation_plan(self):
        assert hasattr(self.client, "add_mitigation_plan")

    # Audit Trail
    def test_has_log_decision(self):
        assert hasattr(self.client, "log_decision")

    def test_has_get_decision_history(self):
        assert hasattr(self.client, "get_decision_history")

    def test_has_get_audit_trail(self):
        assert hasattr(self.client, "get_audit_trail")

    # Covenant Management
    def test_has_create_covenant(self):
        assert hasattr(self.client, "create_covenant")

    def test_has_validate_covenant(self):
        assert hasattr(self.client, "validate_covenant")

    def test_has_list_covenants(self):
        assert hasattr(self.client, "list_covenants")

    def test_has_sign_covenant(self):
        assert hasattr(self.client, "sign_covenant")

    # Analytics
    def test_has_record_metric(self):
        assert hasattr(self.client, "record_metric")

    def test_has_get_metrics(self):
        assert hasattr(self.client, "get_metrics")

    def test_has_create_kpi(self):
        assert hasattr(self.client, "create_kpi")

    def test_has_get_kpi_dashboard(self):
        assert hasattr(self.client, "get_kpi_dashboard")

    # MCP
    def test_has_list_mcp_servers(self):
        assert hasattr(self.client, "list_mcp_servers")

    def test_has_call_mcp_tool(self):
        assert hasattr(self.client, "call_mcp_tool")

    def test_has_get_mcp_server_status(self):
        assert hasattr(self.client, "get_mcp_server_status")

    # Agent Interaction
    def test_has_ask_agent(self):
        assert hasattr(self.client, "ask_agent")

    def test_has_send_to_agent(self):
        assert hasattr(self.client, "send_to_agent")

    # Network Discovery
    def test_has_discover_peers(self):
        assert hasattr(self.client, "discover_peers")

    def test_has_join_network(self):
        assert hasattr(self.client, "join_network")

    def test_has_list_networks(self):
        assert hasattr(self.client, "list_networks")

    # Reliability integration
    def test_accepts_retry_policy(self):
        from aos_client.reliability import RetryPolicy
        client = AOSClient(
            endpoint="https://my-aos.azurewebsites.net",
            retry_policy=RetryPolicy(max_retries=3),
        )
        assert client.retry_policy is not None

    def test_accepts_circuit_breaker(self):
        from aos_client.reliability import CircuitBreaker
        client = AOSClient(
            endpoint="https://my-aos.azurewebsites.net",
            circuit_breaker=CircuitBreaker(failure_threshold=5),
        )
        assert client.circuit_breaker is not None
