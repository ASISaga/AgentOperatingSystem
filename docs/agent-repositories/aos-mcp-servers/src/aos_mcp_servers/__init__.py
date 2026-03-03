"""
aos_mcp_servers — Public API.

MCP transport infrastructure for the Agent Operating System.

All types in this package are **internal** to AOS.  Client applications
interact only with pre-registered server names and secrets through
:class:`~aos_client.mcp.MCPServerConfig` in the AOS Client SDK.

Exports (transport implementations):
    MCPStdioTool: Local subprocess MCP transport (stdin/stdout).
    MCPStreamableHTTPTool: Remote HTTP+SSE MCP transport with optional AI Gateway.
    MCPWebsocketTool: Persistent WebSocket MCP transport.

Exports (internal contract types):
    MCPTransportType: Enum of supported MCP connection transports (internal to AOS).
    MCPToolDefinition: Tool metadata dataclass returned by MCP servers (internal to AOS).
"""

from aos_mcp_servers.routing import (
    MCPStdioTool,
    MCPStreamableHTTPTool,
    MCPToolDefinition,
    MCPTransportType,
    MCPWebsocketTool,
)

__all__ = [
    # Transport implementations
    "MCPStdioTool",
    "MCPStreamableHTTPTool",
    "MCPWebsocketTool",
    # Internal contract types
    "MCPTransportType",
    "MCPToolDefinition",
]

__version__ = "4.0.0"
