"""MCPServers Azure Function app entry point.

Deploys and manages MCP servers based on registry configuration.
All MCP servers are registered with the Foundry Agent Service for
tool discovery and routing.  The Foundry Agent Service manages
tool connections internally — clients declare server names via
``MCPServerConfig`` and AOS handles the rest.

Endpoints:
    GET  /api/mcp/servers                           List enabled MCP servers
    GET  /api/mcp/servers/{server_id}               Get a single server descriptor
    POST /api/mcp/servers/{server_id}/tools/{tool}  Invoke a tool on an MCP server
    GET  /api/health                                Health check
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import azure.functions as func

from mcp_server_schema import MCPServerRegistry, MCPServerRegistryEntry
from aos_mcp_servers.routing import (
    MCPStdioTool,
    MCPStreamableHTTPTool,
    MCPToolDefinition,
    MCPTransportType,
    MCPWebsocketTool,
)

logger = logging.getLogger(__name__)
app = func.FunctionApp()

# ── Foundry Agent Manager (optional — works in stub mode without Azure SDK) ──

try:
    from AgentOperatingSystem.agents import FoundryAgentManager as _FoundryAgentManager

    _agent_manager: Optional[Any] = _FoundryAgentManager()
except ImportError:  # pragma: no cover
    _agent_manager = None

# ── Registry & Server State ──────────────────────────────────────────────────

_registry: Optional[MCPServerRegistry] = None
_server_instances: Dict[str, Any] = {}
_foundry_registered: bool = False


# ── Registry Loading ─────────────────────────────────────────────────────────


def _load_registry() -> MCPServerRegistry:
    """Load the MCP server registry from the JSON configuration file."""
    global _registry  # noqa: PLW0603
    if _registry is not None:
        return _registry

    registry_path = os.environ.get(
        "MCP_REGISTRY_PATH",
        str(Path(__file__).parent / "example_mcp_server_registry.json"),
    )
    logger.info("Loading MCP server registry from %s", registry_path)

    with open(registry_path, encoding="utf-8") as fh:
        data = json.load(fh)

    _registry = MCPServerRegistry(**data)
    logger.info(
        "Loaded %d MCP servers (%d enabled)",
        len(_registry.mcp_servers),
        len(_registry.get_enabled_servers()),
    )
    return _registry


def _build_server_instance(entry: MCPServerRegistryEntry) -> Any:
    """Build an MCP transport instance from a registry entry."""
    tools = [
        MCPToolDefinition(
            name=t.name,
            description=t.description,
            input_schema=t.input_schema,
        )
        for t in entry.tools
    ]

    server_type = entry.server_type.lower()
    if server_type == MCPTransportType.STDIO:
        return MCPStdioTool(
            command=entry.command or "python",
            args=entry.args,
            env=entry.env,
            tools=tools,
        )
    if server_type == MCPTransportType.STREAMABLE_HTTP:
        return MCPStreamableHTTPTool(
            url=entry.url or "",
            headers=entry.headers,
            gateway_url=entry.gateway_url,
            tools=tools,
        )
    if server_type == MCPTransportType.WEBSOCKET:
        return MCPWebsocketTool(
            url=entry.url or "",
            tools=tools,
        )
    raise ValueError(f"Unsupported server_type: {entry.server_type!r}")


def _ensure_servers_initialized(registry: MCPServerRegistry) -> None:
    """Build transport instances for enabled servers if not already done."""
    for entry in registry.get_enabled_servers():
        if entry.server_id not in _server_instances:
            try:
                _server_instances[entry.server_id] = _build_server_instance(entry)
                logger.info(
                    "Initialized MCP server '%s' (type=%s)",
                    entry.server_id,
                    entry.server_type,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Failed to initialize MCP server '%s': %s",
                    entry.server_id,
                    exc,
                )


async def _ensure_foundry_registration(registry: MCPServerRegistry) -> None:
    """Register enabled MCP servers with the Foundry Agent Service.

    Each server's tool list is registered via :class:`FoundryAgentManager`
    so the Foundry Agent Service can route tool calls to the correct server.
    When called on subsequent requests the registration is skipped (idempotent).
    """
    global _foundry_registered  # noqa: PLW0603
    if _foundry_registered:
        return

    foundry_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
    for entry in registry.get_enabled_servers():
        tools: List[Dict[str, Any]] = [
            {
                "type": "function",
                "function": {"name": t.name, "description": t.description},
            }
            for t in entry.tools
        ]
        if _agent_manager is not None:
            await _agent_manager.register_agent(
                agent_id=entry.server_id,
                purpose=entry.description or f"MCP server: {entry.server_id}",
                name=entry.server_id,
                tools=tools,
            )
        else:
            logger.info(
                "Registering MCP server '%s' (%s) with Foundry Agent Service at %s",
                entry.server_id,
                entry.server_type,
                foundry_endpoint or "<not configured>",
            )
    _foundry_registered = True


# ── HTTP Endpoints ───────────────────────────────────────────────────────────


@app.function_name("list_servers")
@app.route(route="mcp/servers", methods=["GET"])
async def list_servers(req: func.HttpRequest) -> func.HttpResponse:
    """List all enabled MCP servers in the registry.

    All servers are registered with the Foundry Agent Service on first access.

    Query parameters:
        server_type: Optional filter by transport type
            (``stdio``, ``streamable_http``, or ``websocket``).
    """
    registry = _load_registry()
    _ensure_servers_initialized(registry)
    await _ensure_foundry_registration(registry)

    server_type = req.params.get("server_type")
    servers = registry.get_enabled_servers()
    if server_type:
        servers = [s for s in servers if s.server_type == server_type]

    payload = {"servers": [s.model_dump() for s in servers]}
    return func.HttpResponse(json.dumps(payload), mimetype="application/json")


@app.function_name("get_server")
@app.route(route="mcp/servers/{server_id}", methods=["GET"])
async def get_server(req: func.HttpRequest) -> func.HttpResponse:
    """Get a single MCP server descriptor by ID."""
    server_id = req.route_params.get("server_id", "")
    registry = _load_registry()
    _ensure_servers_initialized(registry)
    await _ensure_foundry_registration(registry)

    entry = registry.get_server(server_id)
    if entry is None or not entry.enabled:
        return func.HttpResponse(
            json.dumps({"error": f"MCP server '{server_id}' not found"}),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(json.dumps(entry.model_dump()), mimetype="application/json")


@app.function_name("call_tool")
@app.route(route="mcp/servers/{server_id}/tools/{tool_name}", methods=["POST"])
async def call_tool(req: func.HttpRequest) -> func.HttpResponse:
    """Invoke a tool on an MCP server.

    Request body: JSON object of tool input parameters.
    """
    server_id = req.route_params.get("server_id", "")
    tool_name = req.route_params.get("tool_name", "")
    registry = _load_registry()
    _ensure_servers_initialized(registry)
    await _ensure_foundry_registration(registry)

    instance = _server_instances.get(server_id)
    if instance is None:
        return func.HttpResponse(
            json.dumps(
                {"error": f"MCP server '{server_id}' not found or not initialized"}
            ),
            status_code=404,
            mimetype="application/json",
        )

    try:
        params = req.get_json() if req.get_body() else {}
    except ValueError:
        params = {}

    try:
        result = await instance.call_tool(tool_name, params)
        return func.HttpResponse(
            json.dumps(result, default=str), mimetype="application/json"
        )
    except ValueError as exc:
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            status_code=404,
            mimetype="application/json",
        )


@app.function_name("health")
@app.route(route="health", methods=["GET"])
async def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    try:
        registry = _load_registry()
        status: Dict[str, Any] = {
            "app": "aos-mcp-servers",
            "status": "healthy",
            "servers_registered": len(registry.mcp_servers),
            "servers_enabled": len(registry.get_enabled_servers()),
        }
        return func.HttpResponse(json.dumps(status), mimetype="application/json")
    except Exception as exc:
        return func.HttpResponse(
            json.dumps(
                {
                    "app": "aos-mcp-servers",
                    "status": "unhealthy",
                    "error": str(exc),
                }
            ),
            status_code=503,
            mimetype="application/json",
        )
