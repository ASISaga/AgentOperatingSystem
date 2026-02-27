"""AOSApp — Azure Functions application framework for AOS client apps.

Provides all Azure Functions scaffolding so client applications focus
only on business logic.  The SDK creates HTTP triggers, Service Bus
triggers, health endpoints, authentication middleware, and registration
with the Agent Operating System automatically.

Usage::

    from aos_client import AOSApp

    app = AOSApp(name="business-infinity")

    @app.workflow("strategic-review")
    async def strategic_review(request):
        agents = await request.client.list_agents()
        c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent")]
        return await request.client.start_orchestration(
            agent_ids=c_suite,
            purpose="Drive strategic growth and continuous organisational improvement",
            context=request.body,
        )

    # function_app.py just does:
    #   from my_app.workflows import app
    #   functions = app.get_functions()
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

from aos_client.auth import AOSAuth, TokenClaims
from aos_client.models import OrchestrationStatus
from aos_client.service_bus import AOSServiceBus

logger = logging.getLogger(__name__)

# Type alias for workflow handler functions
WorkflowHandler = Callable[["WorkflowRequest"], Awaitable[Any]]


def workflow_template(func: Callable) -> Callable:
    """Decorator that marks a coroutine as a reusable workflow template.

    Templates can be called from ``@app.workflow`` handlers to factor out
    common orchestration patterns.

    Example::

        @workflow_template
        async def c_suite_orchestration(request, agent_filter, purpose, purpose_scope):
            agents = await select_c_suite_agents(request.client)
            agent_ids = [a.agent_id for a in agents if agent_filter(a)]
            return await request.client.start_orchestration(
                agent_ids=agent_ids, purpose=purpose, purpose_scope=purpose_scope,
                context=request.body,
            )
    """
    func._is_workflow_template = True  # type: ignore[attr-defined]
    return func


@dataclass
class WorkflowRequest:
    """Request object passed to workflow handler functions.

    Contains the parsed request body, the AOS client (ready to use),
    and metadata about the incoming request.

    Attributes:
        body: Parsed JSON request body.
        client: Ready-to-use :class:`AOSClient` instance.
        workflow_name: Name of the workflow being invoked.
        auth_claims: Parsed authentication claims (if auth is enabled).
        headers: HTTP request headers (for HTTP-triggered invocations).
        correlation_id: Correlation ID for distributed tracing.
    """

    body: Dict[str, Any]
    client: Any  # AOSClient — forward reference to avoid circular imports
    workflow_name: str = ""
    auth_claims: Optional[TokenClaims] = None
    headers: Dict[str, str] = field(default_factory=dict)
    correlation_id: Optional[str] = None


@dataclass
class _WorkflowRegistration:
    """Internal registration record for a workflow."""

    name: str
    handler: WorkflowHandler
    method: str = "POST"
    auth_required: bool = True
    description: str = ""


class AOSApp:
    """Azure Functions application framework for AOS client apps.

    Wraps :class:`azure.functions.FunctionApp` and provides decorators
    to register business workflows.  The SDK handles:

    - Azure Functions HTTP triggers for each workflow
    - Azure Service Bus trigger for async orchestration results
    - Health endpoint
    - Authentication and access control
    - AOS client lifecycle management
    - App registration with AOS

    Args:
        name: Application name (used for registration and Service Bus routing).
        aos_endpoint: AOS Function App URL.  Reads from ``AOS_ENDPOINT``
            env var if not provided.
        realm_endpoint: RealmOfAgents URL.  Reads from ``REALM_ENDPOINT``
            env var if not provided.
        service_bus_connection_env: Name of the environment variable holding
            the Service Bus connection string.  Defaults to
            ``"SERVICE_BUS_CONNECTION"``.
        auth: Optional :class:`AOSAuth` instance.  When ``None``, auth
            configuration is read from environment variables.
        enable_service_bus: Whether to create Service Bus triggers.
            Defaults to ``True``.
    """

    def __init__(
        self,
        name: str,
        aos_endpoint: Optional[str] = None,
        realm_endpoint: Optional[str] = None,
        service_bus_connection_env: str = "SERVICE_BUS_CONNECTION",
        auth: Optional[AOSAuth] = None,
        enable_service_bus: bool = True,
        observability: Optional[Any] = None,
        mode: Optional[str] = None,
    ) -> None:
        self.name = name
        self.aos_endpoint = aos_endpoint or os.environ.get("AOS_ENDPOINT", "http://localhost:7071")
        self.realm_endpoint = realm_endpoint or os.environ.get("REALM_ENDPOINT", self.aos_endpoint)
        self.service_bus_connection_env = service_bus_connection_env
        self.auth = auth or self._default_auth()
        self.enable_service_bus = enable_service_bus
        self.observability = observability
        self.mode = mode

        self._workflows: Dict[str, _WorkflowRegistration] = {}
        self._update_handlers: Dict[str, Callable] = {}
        self._mcp_tools: Dict[str, Callable] = {}
        self._functions_app: Optional[Any] = None  # azure.functions.FunctionApp

    # ------------------------------------------------------------------
    # Workflow registration
    # ------------------------------------------------------------------

    def workflow(
        self,
        name: str,
        *,
        method: str = "POST",
        auth_required: bool = True,
        description: str = "",
    ) -> Callable[[WorkflowHandler], WorkflowHandler]:
        """Register a business workflow.

        The decorated function receives a :class:`WorkflowRequest` and
        should return the workflow result (dict, :class:`OrchestrationStatus`,
        or any JSON-serializable object).

        The SDK automatically creates:

        - ``POST /api/workflows/{name}`` HTTP trigger
        - Service Bus trigger (if enabled) for async invocation

        Args:
            name: Workflow name (used in URL route and Service Bus routing).
            method: HTTP method (default ``"POST"``).
            auth_required: Whether authentication is required.
            description: Human-readable description.

        Example::

            @app.workflow("strategic-review")
            async def strategic_review(request: WorkflowRequest):
                ...
        """

        def decorator(func: WorkflowHandler) -> WorkflowHandler:
            self._workflows[name] = _WorkflowRegistration(
                name=name,
                handler=func,
                method=method,
                auth_required=auth_required,
                description=func.__doc__ or description,
            )
            return func

        return decorator

    def on_orchestration_update(
        self,
        workflow_name: str,
    ) -> Callable:
        """Register a handler for orchestration intermediate updates.

        Example::

            @app.on_orchestration_update("strategic-review")
            async def handle_update(update):
                logger.info("Agent %s produced: %s", update.agent_id, update.output)
        """

        def decorator(func: Callable) -> Callable:
            self._update_handlers[workflow_name] = func
            return func

        return decorator

    def mcp_tool(
        self,
        tool_name: str,
    ) -> Callable:
        """Register an MCP tool handler.

        Example::

            @app.mcp_tool("erp-search")
            async def erp_search(request):
                return await request.client.call_mcp_tool("erpnext", "search", request.args)
        """

        def decorator(func: Callable) -> Callable:
            self._mcp_tools[tool_name] = func
            return func

        return decorator

    # ------------------------------------------------------------------
    # Azure Functions app generation
    # ------------------------------------------------------------------

    def get_functions(self) -> Any:
        """Build and return the ``azure.functions.FunctionApp`` instance.

        Creates HTTP triggers for each registered workflow, a Service Bus
        trigger for async results, and a health endpoint.

        Returns:
            Configured :class:`azure.functions.FunctionApp`.
        """
        import azure.functions as func  # type: ignore[import-untyped]

        app = func.FunctionApp()
        self._functions_app = app

        # Register workflow HTTP triggers
        for wf in self._workflows.values():
            self._register_http_trigger(app, wf)

        # Register Service Bus trigger for orchestration results
        if self.enable_service_bus:
            self._register_service_bus_trigger(app)

        # Register health endpoint
        self._register_health(app)

        return app

    def _register_http_trigger(self, app: Any, wf: _WorkflowRegistration) -> None:
        """Register an HTTP trigger for a workflow."""
        import azure.functions as func  # type: ignore[import-untyped]

        route = f"workflows/{wf.name}"
        func_name = wf.name.replace("-", "_")
        handler = wf.handler
        auth_required = wf.auth_required
        workflow_name = wf.name
        aos_app = self

        async def http_handler(req: func.HttpRequest) -> func.HttpResponse:
            # Authentication
            claims = None
            if auth_required and aos_app.auth.client_id:
                token = aos_app.auth.extract_bearer_token(
                    req.headers.get("Authorization")
                )
                if token:
                    try:
                        claims = await aos_app.auth.validate_token(token)
                        aos_app.auth.require_any_allowed_role(claims)
                    except PermissionError as exc:
                        return func.HttpResponse(
                            json.dumps({"error": str(exc)}),
                            status_code=403,
                            mimetype="application/json",
                        )

            # Parse request body
            try:
                body = req.get_json()
            except ValueError:
                return func.HttpResponse(
                    json.dumps({"error": "Invalid JSON body"}),
                    status_code=400,
                    mimetype="application/json",
                )

            # Create AOS client and execute workflow
            from aos_client.client import AOSClient

            async with AOSClient(
                endpoint=aos_app.aos_endpoint,
                realm_endpoint=aos_app.realm_endpoint,
                credential=aos_app.auth.get_credential(),
            ) as client:
                request = WorkflowRequest(
                    body=body,
                    client=client,
                    workflow_name=workflow_name,
                    auth_claims=claims,
                    headers=dict(req.headers),
                    correlation_id=req.headers.get("x-correlation-id"),
                )
                try:
                    result = await handler(request)
                except Exception as exc:
                    logger.exception("Workflow '%s' failed", workflow_name)
                    return func.HttpResponse(
                        json.dumps({"error": str(exc)}),
                        status_code=500,
                        mimetype="application/json",
                    )

            # Serialize result
            if isinstance(result, OrchestrationStatus):
                result_data = result.model_dump(mode="json")
            elif hasattr(result, "model_dump"):
                result_data = result.model_dump(mode="json")
            else:
                result_data = result

            return func.HttpResponse(
                json.dumps(result_data, default=str),
                mimetype="application/json",
            )

        # Apply the route decorator
        http_handler.__name__ = func_name
        decorated = app.route(route=route, methods=[wf.method])(http_handler)
        app.function_name(func_name)(decorated)

    def _register_service_bus_trigger(self, app: Any) -> None:
        """Register a Service Bus trigger for async orchestration results."""
        import azure.functions as func  # type: ignore[import-untyped]

        aos_app = self
        topic_name = "aos-orchestration-results"
        subscription_name = self.name

        async def result_handler(msg: func.ServiceBusMessage) -> None:
            body = msg.get_body().decode("utf-8")
            logger.info(
                "Received orchestration result via Service Bus (app=%s)",
                aos_app.name,
            )
            result = AOSServiceBus.parse_orchestration_result(body)
            logger.info(
                "Orchestration %s completed — status=%s",
                result.orchestration_id,
                result.status,
            )

        result_handler.__name__ = "service_bus_result_handler"
        decorated = app.service_bus_topic_trigger(
            arg_name="msg",
            topic_name=topic_name,
            subscription_name=subscription_name,
            connection=self.service_bus_connection_env,
        )(result_handler)
        app.function_name("service_bus_result_handler")(decorated)

    def _register_health(self, app: Any) -> None:
        """Register a health-check endpoint."""
        import azure.functions as func  # type: ignore[import-untyped]

        aos_app = self

        async def health(req: func.HttpRequest) -> func.HttpResponse:
            from aos_client.client import AOSClient

            try:
                async with AOSClient(
                    endpoint=aos_app.aos_endpoint,
                    realm_endpoint=aos_app.realm_endpoint,
                ) as client:
                    aos_health = await client.health_check()
                status = {
                    "app": aos_app.name,
                    "status": "healthy",
                    "workflows": list(aos_app._workflows.keys()),
                    "aos": aos_health,
                }
                return func.HttpResponse(json.dumps(status), mimetype="application/json")
            except Exception as exc:
                return func.HttpResponse(
                    json.dumps({
                        "app": aos_app.name,
                        "status": "degraded",
                        "workflows": list(aos_app._workflows.keys()),
                        "error": str(exc),
                    }),
                    status_code=503,
                    mimetype="application/json",
                )

        health.__name__ = "health"
        decorated = app.route(route="health", methods=["GET"])(health)
        app.function_name("health")(decorated)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_workflow_names(self) -> List[str]:
        """Return the names of all registered workflows."""
        return list(self._workflows.keys())

    def get_update_handler_names(self) -> List[str]:
        """Return the names of all registered orchestration update handlers."""
        return list(self._update_handlers.keys())

    def get_mcp_tool_names(self) -> List[str]:
        """Return the names of all registered MCP tools."""
        return list(self._mcp_tools.keys())

    @staticmethod
    def _default_auth() -> AOSAuth:
        """Create default auth from environment variables."""
        return AOSAuth(
            tenant_id=os.environ.get("AZURE_TENANT_ID"),
            client_id=os.environ.get("AZURE_CLIENT_ID"),
        )
