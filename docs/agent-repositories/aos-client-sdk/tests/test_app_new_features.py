"""Tests for AOSApp new features (decorators, observability, mode)."""

import pytest
from aos_client.app import AOSApp, WorkflowRequest, workflow_template
from aos_client.observability import ObservabilityConfig


class TestAOSAppNewFeatures:
    def test_on_orchestration_update_decorator(self):
        app = AOSApp(name="test-app")

        @app.on_orchestration_update("my-workflow")
        async def handle_update(update):
            pass

        assert "my-workflow" in app.get_update_handler_names()

    def test_mcp_tool_decorator(self):
        app = AOSApp(name="test-app")

        @app.mcp_tool("erp-search")
        async def erp_search(request):
            pass

        assert "erp-search" in app.get_mcp_tool_names()

    def test_observability_config(self):
        config = ObservabilityConfig(
            structured_logging=True,
            correlation_tracking=True,
            metrics_endpoint="/metrics",
            health_checks=["aos"],
        )
        app = AOSApp(name="test-app", observability=config)
        assert app.observability is config

    def test_local_mode(self):
        app = AOSApp(name="test-app", mode="local")
        assert app.mode == "local"

    def test_multiple_update_handlers(self):
        app = AOSApp(name="test-app")

        @app.on_orchestration_update("wf-1")
        async def h1(u):
            pass

        @app.on_orchestration_update("wf-2")
        async def h2(u):
            pass

        assert len(app.get_update_handler_names()) == 2


class TestWorkflowTemplate:
    def test_decorator_marks_function(self):
        @workflow_template
        async def my_template(request, purpose):
            pass

        assert hasattr(my_template, "_is_workflow_template")
        assert my_template._is_workflow_template is True

    def test_template_is_callable(self):
        @workflow_template
        async def my_template(request):
            return "result"

        assert callable(my_template)
