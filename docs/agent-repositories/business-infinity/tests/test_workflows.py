"""Tests for BusinessInfinity workflows."""

import pytest

from business_infinity.workflows import (
    C_SUITE_AGENT_IDS,
    C_SUITE_TYPES,
    app,
    select_c_suite_agents,
)


class TestCSuiteSelection:
    """Test C-suite agent selection logic."""

    def test_c_suite_agent_ids(self):
        assert "ceo" in C_SUITE_AGENT_IDS
        assert "cfo" in C_SUITE_AGENT_IDS
        assert "cmo" in C_SUITE_AGENT_IDS
        assert "coo" in C_SUITE_AGENT_IDS
        assert "cto" in C_SUITE_AGENT_IDS

    def test_c_suite_types(self):
        assert "LeadershipAgent" in C_SUITE_TYPES
        assert "CMOAgent" in C_SUITE_TYPES


class TestAOSAppWorkflows:
    """Test AOSApp workflow registration."""

    def test_app_name(self):
        assert app.name == "business-infinity"

    def test_workflows_registered(self):
        names = app.get_workflow_names()
        assert "strategic-review" in names
        assert "market-analysis" in names
        assert "budget-approval" in names

    def test_workflow_count(self):
        assert len(app.get_workflow_names()) == 14

    def test_new_workflows_registered(self):
        names = app.get_workflow_names()
        assert "knowledge-search" in names
        assert "risk-register" in names
        assert "risk-assess" in names
        assert "log-decision" in names
        assert "covenant-create" in names
        assert "ask-agent" in names

    def test_update_handler_registered(self):
        assert "strategic-review" in app.get_update_handler_names()

    def test_mcp_tool_registered(self):
        assert "erp-search" in app.get_mcp_tool_names()

    def test_observability_configured(self):
        assert app.observability is not None

    def test_v5_workflows_registered(self):
        names = app.get_workflow_names()
        assert "risk-heatmap" in names
        assert "risk-summary" in names
        assert "compliance-report" in names
        assert "create-alert" in names
        assert "register-webhook" in names

    def test_covenant_event_handlers(self):
        handlers = app.get_covenant_event_handler_names()
        assert "violated" in handlers
        assert "expiring" in handlers

    def test_mcp_event_handlers(self):
        handlers = app.get_mcp_event_handler_names()
        assert "erpnext:order_created" in handlers

    def test_webhook_handlers(self):
        handlers = app.get_webhook_names()
        assert "slack-notifications" in handlers
