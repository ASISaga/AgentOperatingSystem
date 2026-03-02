"""
aos_mcp_servers — Public API.

MCP transport connection classes for the Agent Operating System.

The MCP contract types (``MCPTransportType``, ``MCPToolDefinition``,
``MCPServerConfig``) are defined in :mod:`aos_client.mcp` and available
through the AOS Client SDK.  This package exposes the runtime transport
connection classes that implement those contracts:

Exports (transport implementations):
    MCPStdioTool: Local subprocess MCP transport (stdin/stdout).
    MCPStreamableHTTPTool: Remote HTTP+SSE MCP transport with optional AI Gateway.
    MCPWebsocketTool: Persistent WebSocket MCP transport.

Re-exports (contract types from aos-client-sdk):
    MCPTransportType: Enum of supported MCP connection transports.
    MCPToolDefinition: Pydantic model for tool metadata.
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
    # Contract types (from aos-client-sdk, re-exported for convenience)
    "MCPTransportType",
    "MCPToolDefinition",
]

__version__ = "3.0.0"
