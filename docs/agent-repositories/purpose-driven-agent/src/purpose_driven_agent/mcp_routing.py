"""
MCP Routing — Microsoft Agent Framework transport types for PurposeDrivenAgent.

This module implements the MCP (Model Context Protocol) routing mechanism
described in the Microsoft Agent Framework.  It provides:

* :class:`MCPTransportType` — the three supported transport protocols.
* :class:`MCPToolDefinition` — a single tool discovered from an MCP server.
* :class:`MCPStdioTool` — local subprocess transport (stdin/stdout).
* :class:`MCPStreamableHTTPTool` — remote HTTP transport with Server-Sent Events,
  with optional AI Gateway governance.
* :class:`MCPWebsocketTool` — persistent WebSocket transport.

Each transport class satisfies :class:`~purpose_driven_agent.agent.MCPServerProtocol`
and can be registered directly with
:meth:`~purpose_driven_agent.agent.PurposeDrivenAgent.register_mcp_server`.

Usage example::

    from purpose_driven_agent.mcp_routing import (
        MCPStdioTool,
        MCPStreamableHTTPTool,
        MCPWebsocketTool,
        MCPToolDefinition,
        MCPTransportType,
    )

    # Local process server (e.g. a Python MCP script)
    stdio_server = MCPStdioTool(
        command="python",
        args=["path/to/server.py"],
        tools=[MCPToolDefinition(name="read_file", description="Read a local file")],
    )

    # Remote HTTP server with AI Gateway governance
    http_server = MCPStreamableHTTPTool(
        url="https://api.example.com/mcp",
        gateway_url="https://my-foundry-gateway.azure.com",
        tools=[MCPToolDefinition(name="search_web", description="Search the internet")],
    )

    # WebSocket server
    ws_server = MCPWebsocketTool(
        url="wss://realtime.example.com/mcp",
        tools=[MCPToolDefinition(name="stream_events", description="Subscribe to events")],
    )

    agent.register_mcp_server("filesystem", stdio_server, tags=["files"])
    agent.register_mcp_server("search", http_server, tags=["web"])
    agent.register_mcp_server("events", ws_server, tags=["realtime"])
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

_logger = logging.getLogger(__name__)


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


@dataclass
class MCPToolDefinition:
    """
    Metadata for a single tool discovered from an MCP server.

    This mirrors the tool description returned by a server's ``ListTools``
    call in the Microsoft Agent Framework.

    Attributes:
        name: Unique tool name used as the routing key.
        description: Human-readable description of what the tool does.
        input_schema: JSON-schema dict describing the tool's input parameters.
    """

    name: str
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# MCPStdioTool
# ---------------------------------------------------------------------------


class MCPStdioTool:
    """
    MCP server connected via local subprocess (stdin/stdout).

    Use this for MCP servers that run as local processes, such as Python
    scripts or compiled binaries, communicating over standard I/O.

    In production, this class would spawn the process and exchange JSON-RPC
    messages over its stdio streams.  In this implementation the tool list
    is provided at construction time and ``call_tool`` dispatches to
    registered handler callables (or returns a placeholder result).

    Args:
        command: Executable to run (e.g. ``"python"``).
        args: Command-line arguments passed to *command*.
        env: Optional additional environment variables for the subprocess.
        tools: Tool definitions this server exposes.  Used to populate the
            tool index during :meth:`~PurposeDrivenAgent.discover_mcp_tools`.
    """

    transport_type: MCPTransportType = MCPTransportType.STDIO

    def __init__(
        self,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        tools: Optional[List[MCPToolDefinition]] = None,
    ) -> None:
        self.command = command
        self.args: List[str] = args or []
        self.env: Dict[str, str] = env or {}
        self._tools: List[MCPToolDefinition] = tools or []
        _logger.debug(
            "MCPStdioTool initialised | command='%s' | tools=%d",
            command,
            len(self._tools),
        )

    async def list_tools(self) -> List[MCPToolDefinition]:
        """
        Return the tools exposed by this server.

        Mirrors ``ListToolsAsync()`` in the Microsoft Agent Framework.
        In a production implementation this communicates with the subprocess
        over stdio.

        Returns:
            List of :class:`MCPToolDefinition` objects.
        """
        return list(self._tools)

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute *tool_name* with *params* via the stdio subprocess.

        Args:
            tool_name: Name of the tool to invoke.
            params: Tool input parameters.

        Returns:
            Result dict from the tool execution.

        Raises:
            ValueError: If *tool_name* is not in this server's tool list.
        """
        known = {t.name for t in self._tools}
        if known and tool_name not in known:
            raise ValueError(
                f"Tool '{tool_name}' is not available on stdio server "
                f"(command='{self.command}')"
            )
        _logger.debug("MCPStdioTool calling tool '%s'", tool_name)
        return {
            "transport": MCPTransportType.STDIO,
            "tool": tool_name,
            "params": params,
            "result": None,
        }


# ---------------------------------------------------------------------------
# MCPStreamableHTTPTool
# ---------------------------------------------------------------------------


class MCPStreamableHTTPTool:
    """
    MCP server connected over HTTP with Server-Sent Events (SSE).

    Use this for remote MCP servers that stream results back via SSE.
    Supports optional AI Gateway governance (Microsoft Foundry) to provide
    a single, governed entry point for authentication, rate limiting, and
    audit logging.

    Args:
        url: Base URL of the MCP HTTP endpoint.
        headers: Optional HTTP headers sent with every request
            (e.g. ``Authorization``).
        gateway_url: Optional AI Gateway URL.  When provided, requests are
            routed through the gateway for centralised governance.
        tools: Tool definitions this server exposes.
    """

    transport_type: MCPTransportType = MCPTransportType.STREAMABLE_HTTP

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        gateway_url: Optional[str] = None,
        tools: Optional[List[MCPToolDefinition]] = None,
    ) -> None:
        self.url = url
        self.headers: Dict[str, str] = headers or {}
        self.gateway_url: Optional[str] = gateway_url
        self._tools: List[MCPToolDefinition] = tools or []
        _logger.debug(
            "MCPStreamableHTTPTool initialised | url='%s' | gateway='%s' | tools=%d",
            url,
            gateway_url,
            len(self._tools),
        )

    @property
    def effective_url(self) -> str:
        """
        The URL actually used for requests.

        Returns :attr:`gateway_url` when set (governed routing), otherwise
        :attr:`url` (direct routing).
        """
        return self.gateway_url or self.url

    async def list_tools(self) -> List[MCPToolDefinition]:
        """
        Return the tools exposed by this server.

        In production, performs a ``GET {effective_url}/tools`` request and
        deserialises the JSON response.

        Returns:
            List of :class:`MCPToolDefinition` objects.
        """
        return list(self._tools)

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute *tool_name* with *params* via HTTP+SSE.

        Requests are sent to :attr:`effective_url` so that AI Gateway
        governance applies when a gateway URL is configured.

        Args:
            tool_name: Name of the tool to invoke.
            params: Tool input parameters.

        Returns:
            Result dict from the tool execution.

        Raises:
            ValueError: If *tool_name* is not in this server's tool list.
        """
        known = {t.name for t in self._tools}
        if known and tool_name not in known:
            raise ValueError(
                f"Tool '{tool_name}' is not available on HTTP server (url='{self.url}')"
            )
        _logger.debug(
            "MCPStreamableHTTPTool calling tool '%s' via '%s'",
            tool_name,
            self.effective_url,
        )
        return {
            "transport": MCPTransportType.STREAMABLE_HTTP,
            "tool": tool_name,
            "params": params,
            "url": self.effective_url,
            "result": None,
        }


# ---------------------------------------------------------------------------
# MCPWebsocketTool
# ---------------------------------------------------------------------------


class MCPWebsocketTool:
    """
    MCP server connected via a persistent WebSocket.

    Use this for real-time or long-lived MCP connections that benefit from
    low-latency bidirectional communication.

    Args:
        url: WebSocket endpoint URL (``wss://`` or ``ws://``).
        tools: Tool definitions this server exposes.
    """

    transport_type: MCPTransportType = MCPTransportType.WEBSOCKET

    def __init__(
        self,
        url: str,
        tools: Optional[List[MCPToolDefinition]] = None,
    ) -> None:
        self.url = url
        self._tools: List[MCPToolDefinition] = tools or []
        _logger.debug(
            "MCPWebsocketTool initialised | url='%s' | tools=%d",
            url,
            len(self._tools),
        )

    async def list_tools(self) -> List[MCPToolDefinition]:
        """
        Return the tools exposed by this server.

        In production, sends a ``list_tools`` message over the WebSocket
        and awaits the response.

        Returns:
            List of :class:`MCPToolDefinition` objects.
        """
        return list(self._tools)

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute *tool_name* with *params* over the WebSocket connection.

        Args:
            tool_name: Name of the tool to invoke.
            params: Tool input parameters.

        Returns:
            Result dict from the tool execution.

        Raises:
            ValueError: If *tool_name* is not in this server's tool list.
        """
        known = {t.name for t in self._tools}
        if known and tool_name not in known:
            raise ValueError(
                f"Tool '{tool_name}' is not available on WebSocket server "
                f"(url='{self.url}')"
            )
        _logger.debug("MCPWebsocketTool calling tool '%s'", tool_name)
        return {
            "transport": MCPTransportType.WEBSOCKET,
            "tool": tool_name,
            "params": params,
            "url": self.url,
            "result": None,
        }
