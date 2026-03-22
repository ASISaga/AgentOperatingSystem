"""AOS Dispatcher — Azure Functions entry point for the Agent Operating System.

Thin Azure Functions wrapper around the ``aos_dispatcher`` library.  All
business logic lives in ``aos_dispatcher.dispatcher``; this module only handles
Azure Functions-specific concerns:

    - Binding to HTTP routes and Service Bus triggers via ``azure.functions``
    - Parsing ``func.HttpRequest`` (body, route params, query params)
    - Converting ``(body, status_code)`` library responses to ``func.HttpResponse``

Receives all inbound requests and dispatches them to the AOS kernel, analogous
to the dispatcher in a traditional operating system.

All multi-agent orchestration is managed internally by the **Foundry Agent
Service**.  Agents inheriting from PurposeDrivenAgent continue to run as Azure
Functions.  Foundry is an implementation detail — clients interact only with
the standard orchestration endpoints.

AOS Function Apps (3 total — each is a separate Azure Functions deployment):
    aos-dispatcher       This function app — central HTTP/Service Bus dispatcher
    aos-mcp-servers      MCP server deployment & management (ASISaga/mcp)
    aos-realm-of-agents  Agent catalog & registry (ASISaga/realm-of-agents)

    The dispatcher proxies MCP and agent-catalog requests to the dedicated
    function apps via the environment variables MCP_SERVERS_BASE_URL and
    REALM_OF_AGENTS_BASE_URL.  When those variables are not set (e.g. in
    local development) the dispatcher falls back to in-memory stubs.

Endpoints — Orchestrations (all managed by Foundry Agent Service):
    POST /api/orchestrations              Submit an orchestration request
    GET  /api/orchestrations/{id}         Poll orchestration status
    GET  /api/orchestrations/{id}/result  Retrieve completed result
    POST /api/orchestrations/{id}/cancel  Cancel a running orchestration

Endpoints — Knowledge Base:
    POST /api/knowledge/documents         Create a document
    GET  /api/knowledge/documents         Search documents
    GET  /api/knowledge/documents/{id}    Get document by ID
    POST /api/knowledge/documents/{id}    Update document
    DELETE /api/knowledge/documents/{id}  Delete document

Endpoints — Risk Registry:
    POST /api/risks                       Register a risk
    GET  /api/risks                       List risks
    POST /api/risks/{id}/assess           Assess a risk
    POST /api/risks/{id}/status           Update risk status
    POST /api/risks/{id}/mitigate         Add mitigation plan

Endpoints — Audit Trail:
    POST /api/audit/decisions             Log a decision
    GET  /api/audit/decisions             Get decision history
    GET  /api/audit/trail                 Get audit trail

Endpoints — Covenants:
    POST /api/covenants                   Create a covenant
    GET  /api/covenants                   List covenants
    GET  /api/covenants/{id}/validate     Validate a covenant
    POST /api/covenants/{id}/sign         Sign a covenant

Endpoints — Analytics:
    POST /api/metrics                     Record a metric
    GET  /api/metrics                     Get metric series
    POST /api/kpis                        Create a KPI
    GET  /api/kpis/dashboard              Get KPI dashboard

Endpoints — MCP (proxied to aos-mcp-servers via MCP_SERVERS_BASE_URL):
    GET  /api/mcp/servers                 List MCP servers
    POST /api/mcp/servers/{s}/tools/{t}   Call an MCP tool
    GET  /api/mcp/servers/{s}/status      Get MCP server status

Endpoints — Agents:
    GET  /api/agents                      List agents (proxied to aos-realm-of-agents)
    GET  /api/agents/{id}                 Get agent descriptor (proxied to aos-realm-of-agents)
    POST /api/agents/register             Register a PurposeDrivenAgent with Foundry
    POST /api/agents/{id}/ask             Ask an agent
    POST /api/agents/{id}/send            Send to an agent
    POST /api/agents/{id}/message         Send message via Foundry bridge

Endpoints — Network:
    POST /api/network/discover            Discover peers
    POST /api/network/{id}/join           Join a network
    GET  /api/network                     List networks

Endpoints — App Registration:
    POST /api/apps/register               Register a client application
    GET  /api/apps/{app_name}             Get app registration status
    DELETE /api/apps/{app_name}           Deregister a client application

Endpoints — Health:
    GET  /api/health                      Health check

Service Bus Triggers:
    aos-orchestration-requests            Process incoming orchestration requests
"""

from __future__ import annotations

import json
import logging

import azure.functions as func

import aos_dispatcher.dispatcher as dispatcher

logger = logging.getLogger(__name__)
app = func.FunctionApp()


# ── Response helpers ──────────────────────────────────────────────────────────


def _make_response(result: tuple) -> func.HttpResponse:
    """Convert a library ``(body, status_code)`` tuple to ``func.HttpResponse``.

    - ``body is None``   → 204 No Content (no body, no Content-Type)
    - ``body`` is bytes  → raw bytes passed through (proxy responses)
    - ``body`` is dict   → JSON-serialised with ``application/json``
    """
    body, status_code = result
    if body is None:
        return func.HttpResponse(status_code=status_code)
    if isinstance(body, bytes):
        return func.HttpResponse(body, status_code=status_code, mimetype="application/json")
    return func.HttpResponse(
        json.dumps(body),
        status_code=status_code,
        mimetype="application/json",
    )


def _require_json(req: func.HttpRequest) -> tuple:
    """Parse JSON body from request.

    Returns:
        ``(body_dict, None)`` on success.
        ``(None, error_response)`` when the body is not valid JSON.
    """
    try:
        return req.get_json(), None
    except ValueError:
        return None, _make_response(({"error": "Invalid JSON body"}, 400))


# ── HTTP Endpoints — Orchestrations ──────────────────────────────────────────


@app.function_name("submit_orchestration")
@app.route(route="orchestrations", methods=["POST"])
async def submit_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    """Submit an orchestration request.

    Request body (OrchestrationRequest)::

        {
            "orchestration_id": "optional-client-id",
            "agent_ids": ["ceo", "cfo", "cmo"],
            "workflow": "collaborative",
            "task": {"type": "strategic_review", "data": {...}},
            "config": {},
            "callback_url": null
        }
    """
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.process_orchestration_request(body))


@app.function_name("get_orchestration_status")
@app.route(route="orchestrations/{orchestration_id}", methods=["GET"])
async def get_orchestration_status(req: func.HttpRequest) -> func.HttpResponse:
    """Poll the status of a submitted orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    return _make_response(dispatcher.get_orchestration_status(orch_id))


@app.function_name("get_orchestration_result")
@app.route(route="orchestrations/{orchestration_id}/result", methods=["GET"])
async def get_orchestration_result(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve the final result of a completed orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    return _make_response(dispatcher.get_orchestration_result(orch_id))


@app.function_name("cancel_orchestration")
@app.route(route="orchestrations/{orchestration_id}/cancel", methods=["POST"])
async def cancel_orchestration(req: func.HttpRequest) -> func.HttpResponse:
    """Cancel a running orchestration."""
    orch_id = req.route_params.get("orchestration_id", "")
    return _make_response(dispatcher.cancel_orchestration(orch_id))


# ── Service Bus Trigger — Orchestration Requests ─────────────────────────────


@app.function_name("service_bus_orchestration_request")
@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="aos-orchestration-requests",
    connection="SERVICE_BUS_CONNECTION",
)
async def service_bus_orchestration_request(msg: func.ServiceBusMessage) -> None:
    """Process an orchestration request received via Service Bus.

    This trigger enables scale-to-zero: AOS sleeps until a message arrives
    on the orchestration requests queue, then wakes up to process it.
    """
    body_bytes = msg.get_body()
    body_str = body_bytes.decode("utf-8")

    try:
        envelope = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Service Bus message: %s", body_str[:200])
        return

    app_name = envelope.get("app_name", "unknown")
    payload = envelope.get("payload", {})

    logger.info(
        "Received orchestration request via Service Bus from app '%s'",
        app_name,
    )

    # Process the request using the same logic as HTTP
    dispatcher.process_orchestration_request(payload, source_app=app_name)

    # TODO: Send result back via Service Bus topic to the client app
    # This would use the aos-orchestration-results topic with a subscription
    # filtered by app_name.


# ── HTTP Endpoints — App Registration ────────────────────────────────────────


@app.function_name("register_app")
@app.route(route="apps/register", methods=["POST"])
async def register_app(req: func.HttpRequest) -> func.HttpResponse:
    """Register a client application with AOS.

    Provisions Service Bus queues, topics, and subscriptions for async
    communication.  Returns connection details to the client.

    Request body::

        {
            "app_name": "business-infinity",
            "workflows": ["strategic-review", "market-analysis"],
            "app_id": "optional-azure-ad-app-id"
        }
    """
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.register_app(body))


@app.function_name("get_app_registration")
@app.route(route="apps/{app_name}", methods=["GET"])
async def get_app_registration(req: func.HttpRequest) -> func.HttpResponse:
    """Get the registration status of a client application."""
    app_name = req.route_params.get("app_name", "")
    return _make_response(dispatcher.get_app_registration(app_name))


@app.function_name("deregister_app")
@app.route(route="apps/{app_name}", methods=["DELETE"])
async def deregister_app(req: func.HttpRequest) -> func.HttpResponse:
    """Remove a client application registration."""
    app_name = req.route_params.get("app_name", "")
    return _make_response(dispatcher.deregister_app(app_name))


# ── Health ────────────────────────────────────────────────────────────────────


@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """Health check endpoint."""
    return _make_response(dispatcher.health())


# ── Knowledge Base Endpoints ─────────────────────────────────────────────────


@app.function_name("create_document")
@app.route(route="knowledge/documents", methods=["POST"])
async def create_document(req: func.HttpRequest) -> func.HttpResponse:
    """Create a knowledge document."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.create_document(body))


@app.function_name("get_document")
@app.route(route="knowledge/documents/{document_id}", methods=["GET"])
async def get_document(req: func.HttpRequest) -> func.HttpResponse:
    """Get a knowledge document by ID."""
    doc_id = req.route_params.get("document_id", "")
    return _make_response(dispatcher.get_document(doc_id))


@app.function_name("search_documents")
@app.route(route="knowledge/documents", methods=["GET"])
async def search_documents(req: func.HttpRequest) -> func.HttpResponse:
    """Search knowledge documents."""
    query = req.params.get("query") or ""
    doc_type = req.params.get("doc_type")
    limit = int(req.params.get("limit", "10"))
    return _make_response(dispatcher.search_documents(query=query, doc_type=doc_type, limit=limit))


@app.function_name("update_document")
@app.route(route="knowledge/documents/{document_id}", methods=["POST"])
async def update_document(req: func.HttpRequest) -> func.HttpResponse:
    """Update a knowledge document's content."""
    doc_id = req.route_params.get("document_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.update_document(doc_id, body))


@app.function_name("delete_document")
@app.route(route="knowledge/documents/{document_id}", methods=["DELETE"])
async def delete_document(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a knowledge document."""
    doc_id = req.route_params.get("document_id", "")
    return _make_response(dispatcher.delete_document(doc_id))


# ── Risk Registry Endpoints ──────────────────────────────────────────────────


@app.function_name("register_risk")
@app.route(route="risks", methods=["POST"])
async def register_risk(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new risk."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.register_risk(body))


@app.function_name("list_risks")
@app.route(route="risks", methods=["GET"])
async def list_risks(req: func.HttpRequest) -> func.HttpResponse:
    """List risks with optional filters."""
    status = req.params.get("status")
    category = req.params.get("category")
    return _make_response(dispatcher.list_risks(status=status, category=category))


@app.function_name("assess_risk")
@app.route(route="risks/{risk_id}/assess", methods=["POST"])
async def assess_risk(req: func.HttpRequest) -> func.HttpResponse:
    """Assess a risk."""
    risk_id = req.route_params.get("risk_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.assess_risk(risk_id, body))


@app.function_name("update_risk_status")
@app.route(route="risks/{risk_id}/status", methods=["POST"])
async def update_risk_status(req: func.HttpRequest) -> func.HttpResponse:
    """Update risk status."""
    risk_id = req.route_params.get("risk_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.update_risk_status(risk_id, body))


@app.function_name("add_mitigation_plan")
@app.route(route="risks/{risk_id}/mitigate", methods=["POST"])
async def add_mitigation_plan(req: func.HttpRequest) -> func.HttpResponse:
    """Add a mitigation plan to a risk."""
    risk_id = req.route_params.get("risk_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.add_mitigation_plan(risk_id, body))


# ── Audit Trail / Decision Ledger Endpoints ──────────────────────────────────


@app.function_name("log_decision")
@app.route(route="audit/decisions", methods=["POST"])
async def log_decision(req: func.HttpRequest) -> func.HttpResponse:
    """Log a decision."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.log_decision(body))


@app.function_name("get_decision_history")
@app.route(route="audit/decisions", methods=["GET"])
async def get_decision_history(req: func.HttpRequest) -> func.HttpResponse:
    """Get decision history."""
    orch_id = req.params.get("orchestration_id")
    agent_id = req.params.get("agent_id")
    return _make_response(dispatcher.get_decision_history(orch_id=orch_id, agent_id=agent_id))


@app.function_name("get_audit_trail")
@app.route(route="audit/trail", methods=["GET"])
async def get_audit_trail(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """Get the audit trail."""
    return _make_response(dispatcher.get_audit_trail())


# ── Covenant Management Endpoints ────────────────────────────────────────────


@app.function_name("create_covenant")
@app.route(route="covenants", methods=["POST"])
async def create_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Create a covenant."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.create_covenant(body))


@app.function_name("list_covenants")
@app.route(route="covenants", methods=["GET"])
async def list_covenants(req: func.HttpRequest) -> func.HttpResponse:
    """List covenants."""
    status = req.params.get("status")
    return _make_response(dispatcher.list_covenants(status=status))


@app.function_name("validate_covenant")
@app.route(route="covenants/{covenant_id}/validate", methods=["GET"])
async def validate_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Validate a covenant."""
    cov_id = req.route_params.get("covenant_id", "")
    return _make_response(dispatcher.validate_covenant(cov_id))


@app.function_name("sign_covenant")
@app.route(route="covenants/{covenant_id}/sign", methods=["POST"])
async def sign_covenant(req: func.HttpRequest) -> func.HttpResponse:
    """Sign a covenant."""
    cov_id = req.route_params.get("covenant_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.sign_covenant(cov_id, body))


# ── Analytics & Metrics Endpoints ────────────────────────────────────────────


@app.function_name("record_metric")
@app.route(route="metrics", methods=["POST"])
async def record_metric(req: func.HttpRequest) -> func.HttpResponse:
    """Record a metric data point."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.record_metric(body))


@app.function_name("get_metrics")
@app.route(route="metrics", methods=["GET"])
async def get_metrics(req: func.HttpRequest) -> func.HttpResponse:
    """Retrieve metric time series."""
    name = req.params.get("name", "")
    return _make_response(dispatcher.get_metrics(name=name))


@app.function_name("create_kpi")
@app.route(route="kpis", methods=["POST"])
async def create_kpi(req: func.HttpRequest) -> func.HttpResponse:
    """Create a KPI definition."""
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.create_kpi(body))


@app.function_name("get_kpi_dashboard")
@app.route(route="kpis/dashboard", methods=["GET"])
async def get_kpi_dashboard(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """Get the KPI dashboard."""
    return _make_response(dispatcher.get_kpi_dashboard())


# ── MCP Server Integration Endpoints ─────────────────────────────────────────
# These endpoints proxy to the *aos-mcp-servers* function app (ASISaga/mcp).
# Configure MCP_SERVERS_BASE_URL in App Settings to point at the deployed
# aos-mcp-servers instance.  When the variable is unset a minimal stub response
# is returned so local development stays functional.


@app.function_name("list_mcp_servers")
@app.route(route="mcp/servers", methods=["GET"])
async def list_mcp_servers(req: func.HttpRequest) -> func.HttpResponse:
    """List available MCP servers (proxied to aos-mcp-servers)."""
    server_type = req.params.get("server_type")
    return _make_response(await dispatcher.list_mcp_servers(server_type=server_type))


@app.function_name("call_mcp_tool")
@app.route(route="mcp/servers/{server}/tools/{tool}", methods=["POST"])
async def call_mcp_tool(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke a tool on an MCP server (proxied to aos-mcp-servers)."""
    server = req.route_params.get("server", "")
    tool = req.route_params.get("tool", "")
    return _make_response(await dispatcher.call_mcp_tool(server, tool, req.get_body()))


@app.function_name("get_mcp_server_status")
@app.route(route="mcp/servers/{server}/status", methods=["GET"])
async def get_mcp_server_status(req: func.HttpRequest) -> func.HttpResponse:
    """Get MCP server status (proxied to aos-mcp-servers)."""
    server = req.route_params.get("server", "")
    return _make_response(await dispatcher.get_mcp_server_status(server))


# ── Agent Catalog Endpoints ───────────────────────────────────────────────────
# GET /api/agents and GET /api/agents/{id} proxy to *aos-realm-of-agents*
# (ASISaga/realm-of-agents).  Configure REALM_OF_AGENTS_BASE_URL in App Settings.


@app.function_name("list_agents")
@app.route(route="agents", methods=["GET"])
async def list_agents(req: func.HttpRequest) -> func.HttpResponse:
    """List agents from the realm-of-agents catalog (proxied to aos-realm-of-agents)."""
    agent_type = req.params.get("agent_type")
    return _make_response(await dispatcher.list_agents(agent_type=agent_type))


@app.function_name("get_agent_descriptor")
@app.route(route="agents/{agent_id}", methods=["GET"])
async def get_agent_descriptor(req: func.HttpRequest) -> func.HttpResponse:
    """Get an agent descriptor from the realm-of-agents catalog."""
    agent_id = req.route_params.get("agent_id", "")
    return _make_response(await dispatcher.get_agent_descriptor(agent_id))


# ── Agent Interaction Endpoints ──────────────────────────────────────────────


@app.function_name("ask_agent")
@app.route(route="agents/{agent_id}/ask", methods=["POST"])
async def ask_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Direct message to an agent."""
    agent_id = req.route_params.get("agent_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.ask_agent(agent_id, body))


@app.function_name("send_to_agent")
@app.route(route="agents/{agent_id}/send", methods=["POST"])
async def send_to_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Fire-and-forget message to an agent."""
    agent_id = req.route_params.get("agent_id", "")
    return _make_response(dispatcher.send_to_agent(agent_id))


@app.function_name("register_agent")
@app.route(route="agents/register", methods=["POST"])
async def register_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Register a PurposeDrivenAgent with the Foundry Agent Service.

    Request body::

        {
            "agent_id": "ceo",
            "purpose": "Strategic leadership and executive decision-making",
            "name": "CEO Agent",
            "adapter_name": "leadership",
            "capabilities": ["strategic_planning", "decision_making"],
            "model": "gpt-4o"
        }
    """
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.register_agent(body))


@app.function_name("message_agent")
@app.route(route="agents/{agent_id}/message", methods=["POST"])
async def message_agent(req: func.HttpRequest) -> func.HttpResponse:
    """Send a message to a PurposeDrivenAgent via the Foundry message bridge.

    Request body::

        {
            "message": "What is the strategic direction?",
            "orchestration_id": "optional-orch-id",
            "direction": "foundry_to_agent"
        }
    """
    agent_id = req.route_params.get("agent_id", "")
    body, err = _require_json(req)
    if err:
        return err
    return _make_response(dispatcher.message_agent(agent_id, body))


# ── Network Discovery Endpoints ──────────────────────────────────────────────


@app.function_name("discover_peers")
@app.route(route="network/discover", methods=["POST"])
async def discover_peers(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """Discover peer applications."""
    return _make_response(dispatcher.discover_peers())


@app.function_name("join_network")
@app.route(route="network/{network_id}/join", methods=["POST"])
async def join_network(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """Join a network."""
    network_id = req.route_params.get("network_id", "")
    return _make_response(dispatcher.join_network(network_id))


@app.function_name("list_networks")
@app.route(route="network", methods=["GET"])
async def list_networks(req: func.HttpRequest) -> func.HttpResponse:  # noqa: ARG001
    """List available networks."""
    return _make_response(dispatcher.list_networks())
