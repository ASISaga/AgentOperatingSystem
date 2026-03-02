"""
MCP (Model Context Protocol) contract types for the AOS Client SDK.

This module defines the **client-facing** MCP types that are shared across
the Agent Operating System:

* :class:`MCPTransportType` — the three supported transport protocols.
* :class:`MCPToolDefinition` — metadata for a single tool exposed by an MCP
  server, serialisable via Pydantic.
* :class:`MCPServerConfig` — Pydantic configuration model used in
  :class:`~aos_client.models.OrchestrationRequest` so that client
  applications can select which MCP servers each agent should connect to
  when an orchestration is started.

Usage (client side — e.g. *business-infinity*)::

    from aos_client import MCPServerConfig, MCPTransportType, OrchestrationRequest

    request = OrchestrationRequest(
        agent_ids=["ceo", "cmo"],
        purpose=OrchestrationPurpose(purpose="Drive strategic growth"),
        mcp_servers={
            "ceo": [
                MCPServerConfig(
                    server_name="erp",
                    transport_type=MCPTransportType.STREAMABLE_HTTP,
                    url="https://erp.example.com/mcp",
                    gateway_url="https://my-foundry-gateway.azure.com",
                ),
            ],
            "cmo": [
                MCPServerConfig(
                    server_name="crm",
                    transport_type=MCPTransportType.WEBSOCKET,
                    url="wss://crm.example.com/mcp",
                ),
                MCPServerConfig(
                    server_name="analytics",
                    transport_type=MCPTransportType.STREAMABLE_HTTP,
                    url="https://analytics.example.com/mcp",
                ),
            ],
        },
    )
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# MCPTransportType
# ---------------------------------------------------------------------------


class MCPTransportType(str, Enum):
    """
    Supported MCP connection transports.

    Values align with the Microsoft Agent Framework's three primary transports.
    """

    STDIO = "stdio"
    """Local process using standard input/output (e.g. a Python script)."""

    STREAMABLE_HTTP = "streamable_http"
    """Remote server over HTTP with Server-Sent Events (SSE)."""

    WEBSOCKET = "websocket"
    """Persistent WebSocket connection."""


# ---------------------------------------------------------------------------
# MCPToolDefinition
# ---------------------------------------------------------------------------


class MCPToolDefinition(BaseModel):
    """
    Metadata for a single tool discovered from an MCP server.

    Pydantic model counterpart of the dataclass used by transport
    implementations.  Used for serialisable tool listings returned by the
    :meth:`~aos_client.AOSClient.list_mcp_tools` SDK method and in
    orchestration responses.

    Attributes:
        name: Unique tool name used as the routing key.
        description: Human-readable description of what the tool does.
        input_schema: JSON-schema dict describing the tool's input parameters.
    """

    name: str = Field(..., description="Unique tool name (routing key)")
    description: str = Field(default="", description="Human-readable tool description")
    input_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON-schema for tool input parameters"
    )


# ---------------------------------------------------------------------------
# MCPServerConfig
# ---------------------------------------------------------------------------


class MCPServerConfig(BaseModel):
    """
    MCP server configuration for inclusion in an
    :class:`~aos_client.models.OrchestrationRequest`.

    Client applications (e.g. *business-infinity*) create
    :class:`MCPServerConfig` instances to declare which MCP servers each
    participating agent should connect to when the orchestration starts.
    AOS resolves these configs and passes them to each agent at runtime.

    Attributes:
        server_name: Logical name identifying this MCP server (used as the
            server registry key within the agent).
        transport_type: One of :class:`MCPTransportType`
            (``"stdio"``, ``"streamable_http"``, or ``"websocket"``).
        url: Server URL.  Required for ``streamable_http`` and ``websocket``
            transports; unused for ``stdio``.
        gateway_url: Optional AI Gateway URL for ``streamable_http``
            transport.  When set, requests are routed through the gateway for
            centralised authentication, rate limiting, and audit logging.
        headers: Additional HTTP headers for ``streamable_http`` requests
            (e.g. ``{"Authorization": "Bearer ..."}``.
        command: Executable path for ``stdio`` transport.
        args: Command-line arguments for the ``stdio`` executable.
        env: Environment variables injected into the ``stdio`` subprocess.
        tags: Capability tags used for dynamic server selection within the
            agent (e.g. ``["files", "search"]``).
        enabled: Whether the server starts in an enabled state inside the
            agent.  Defaults to ``False`` so newly registered servers do not
            immediately expand the LLM context window.
    """

    server_name: str = Field(..., description="Logical name for this MCP server")
    transport_type: MCPTransportType = Field(
        ..., description="Transport protocol used to connect to the MCP server"
    )
    url: Optional[str] = Field(
        None,
        description="Server URL (required for streamable_http and websocket transports)",
    )
    gateway_url: Optional[str] = Field(
        None,
        description="AI Gateway URL for governed routing (streamable_http only)",
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="HTTP headers for streamable_http requests",
    )
    command: Optional[str] = Field(
        None, description="Executable path for stdio transport"
    )
    args: List[str] = Field(
        default_factory=list, description="Command-line arguments for stdio transport"
    )
    env: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for the stdio subprocess",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Capability tags for dynamic server selection within the agent",
    )
    enabled: bool = Field(
        default=False,
        description="Whether the server starts enabled inside the agent",
    )
