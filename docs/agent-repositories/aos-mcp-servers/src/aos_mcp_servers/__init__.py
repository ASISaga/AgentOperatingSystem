"""
aos_mcp_servers — Public API.

Centralized MCP (Model Context Protocol) routing infrastructure for the
Agent Operating System.  Every agent package imports from here rather than
implementing its own transport types.

Exports:
    MCPTransportType: Enum of supported MCP connection transports.
    MCPToolDefinition: Metadata for a tool discovered from an MCP server.
    MCPStdioTool: Local subprocess MCP transport (stdin/stdout).
    MCPStreamableHTTPTool: Remote HTTP+SSE MCP transport with optional AI Gateway.
    MCPWebsocketTool: Persistent WebSocket MCP transport.
"""

from aos_mcp_servers.routing import (
    MCPStdioTool,
    MCPStreamableHTTPTool,
    MCPToolDefinition,
    MCPTransportType,
    MCPWebsocketTool,
)

__all__ = [
    "MCPTransportType",
    "MCPToolDefinition",
    "MCPStdioTool",
    "MCPStreamableHTTPTool",
    "MCPWebsocketTool",
]

__version__ = "3.0.0"
