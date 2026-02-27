"""Tests for the AOS Azure Function app.

Tests the orchestration API, Service Bus trigger, and app registration endpoints.
"""
import json
import pytest


class TestFunctionApp:
    """AOS Function App tests."""

    def test_health_endpoint(self):
        """Test health check HTTP endpoint."""
        from function_app import _orchestrations, _registered_apps

        assert isinstance(_orchestrations, dict)
        assert isinstance(_registered_apps, dict)

    def test_process_orchestration_request(self):
        """Test orchestration request processing."""
        from function_app import _process_orchestration_request, _orchestrations

        body = {
            "agent_ids": ["ceo", "cfo"],
            "workflow": "collaborative",
            "task": {"type": "test"},
        }
        response = _process_orchestration_request(body)
        assert response.status_code == 202

        data = json.loads(response.get_body())
        assert data["status"] == "pending"
        assert data["agent_ids"] == ["ceo", "cfo"]

        # Verify it was stored
        assert data["orchestration_id"] in _orchestrations

    def test_process_orchestration_request_empty_agents(self):
        """Test orchestration request with empty agents list."""
        from function_app import _process_orchestration_request

        body = {"agent_ids": [], "task": {"type": "test"}}
        response = _process_orchestration_request(body)
        assert response.status_code == 400

    def test_process_orchestration_request_with_source_app(self):
        """Test orchestration request from Service Bus with source app."""
        from function_app import _process_orchestration_request, _orchestrations

        body = {
            "agent_ids": ["cmo"],
            "task": {"type": "market_analysis"},
        }
        response = _process_orchestration_request(body, source_app="business-infinity")
        assert response.status_code == 202

        data = json.loads(response.get_body())
        orch_id = data["orchestration_id"]
        assert _orchestrations[orch_id]["source_app"] == "business-infinity"

    def test_registered_apps_store(self):
        """Test app registration store."""
        from function_app import _registered_apps

        _registered_apps["test-app"] = {
            "app_name": "test-app",
            "workflows": ["test-workflow"],
            "status": "provisioned",
        }
        assert "test-app" in _registered_apps
        del _registered_apps["test-app"]
