"""Tests for AOSApp framework."""

import pytest

from aos_client.app import AOSApp, WorkflowRequest, _WorkflowRegistration


class TestAOSApp:
    """AOSApp unit tests."""

    def test_init_defaults(self):
        app = AOSApp(name="test-app")
        assert app.name == "test-app"
        assert app.enable_service_bus is True
        assert app._workflows == {}

    def test_init_custom_endpoint(self):
        app = AOSApp(
            name="test-app",
            aos_endpoint="https://my-aos.azurewebsites.net",
            realm_endpoint="https://my-realm.azurewebsites.net",
        )
        assert app.aos_endpoint == "https://my-aos.azurewebsites.net"
        assert app.realm_endpoint == "https://my-realm.azurewebsites.net"

    def test_workflow_decorator(self):
        app = AOSApp(name="test-app")

        @app.workflow("my-workflow")
        async def my_handler(request: WorkflowRequest):
            return {"result": "ok"}

        assert "my-workflow" in app._workflows
        reg = app._workflows["my-workflow"]
        assert reg.name == "my-workflow"
        assert reg.method == "POST"
        assert reg.auth_required is True

    def test_workflow_decorator_options(self):
        app = AOSApp(name="test-app")

        @app.workflow("open-workflow", method="GET", auth_required=False, description="Test")
        async def handler(request: WorkflowRequest):
            return {}

        reg = app._workflows["open-workflow"]
        assert reg.method == "GET"
        assert reg.auth_required is False
        assert reg.description == "Test"

    def test_multiple_workflows(self):
        app = AOSApp(name="test-app")

        @app.workflow("workflow-a")
        async def handler_a(request: WorkflowRequest):
            return {}

        @app.workflow("workflow-b")
        async def handler_b(request: WorkflowRequest):
            return {}

        @app.workflow("workflow-c")
        async def handler_c(request: WorkflowRequest):
            return {}

        names = app.get_workflow_names()
        assert len(names) == 3
        assert "workflow-a" in names
        assert "workflow-b" in names
        assert "workflow-c" in names

    def test_get_workflow_names_empty(self):
        app = AOSApp(name="test-app")
        assert app.get_workflow_names() == []

    def test_disable_service_bus(self):
        app = AOSApp(name="test-app", enable_service_bus=False)
        assert app.enable_service_bus is False


class TestWorkflowRequest:
    """WorkflowRequest unit tests."""

    def test_create_minimal(self):
        req = WorkflowRequest(body={"key": "value"}, client=None)
        assert req.body == {"key": "value"}
        assert req.client is None
        assert req.workflow_name == ""
        assert req.auth_claims is None
        assert req.headers == {}
        assert req.correlation_id is None

    def test_create_full(self):
        req = WorkflowRequest(
            body={"quarter": "Q1"},
            client="mock_client",
            workflow_name="strategic-review",
            headers={"Authorization": "Bearer xxx"},
            correlation_id="corr-123",
        )
        assert req.workflow_name == "strategic-review"
        assert req.correlation_id == "corr-123"
        assert req.headers["Authorization"] == "Bearer xxx"
