"""
purpose_driven_agent — Public API.

Exports:
    PurposeDrivenAgent: Abstract base class for all purpose-driven perpetual agents.
    GenericPurposeDrivenAgent: Concrete general-purpose implementation.
    ContextMCPServer: Lightweight MCP context server for state preservation.
    MCPServerProtocol: Structural protocol for MCP servers registered with agents.
    MCPTransportType: Enum of supported MCP connection transports (from aos-mcp-servers).
    MCPToolDefinition: Metadata for a tool discovered from an MCP server (from aos-mcp-servers).
    MCPStdioTool: Local subprocess MCP transport (from aos-mcp-servers).
    MCPStreamableHTTPTool: Remote HTTP+SSE MCP transport with optional AI Gateway (from aos-mcp-servers).
    MCPWebsocketTool: Persistent WebSocket MCP transport (from aos-mcp-servers).
    IMLService: Abstract ML service interface for LoRA training and inference.
    NoOpMLService: No-operation ML service (raises NotImplementedError on use).

The MCP routing transport types are implemented centrally in the ``aos-mcp-servers``
repository (``aos_mcp_servers.routing``) and re-exported here for convenience.
New code should import transport types directly from ``aos_mcp_servers.routing``.
"""

from purpose_driven_agent.agent import (
    GenericPurposeDrivenAgent,
    MCPServerProtocol,
    PurposeDrivenAgent,
)
from purpose_driven_agent.context_server import ContextMCPServer
from aos_mcp_servers.routing import (
    MCPStdioTool,
    MCPStreamableHTTPTool,
    MCPToolDefinition,
    MCPTransportType,
    MCPWebsocketTool,
)
from purpose_driven_agent.ml_interface import IMLService, NoOpMLService

__all__ = [
    "PurposeDrivenAgent",
    "GenericPurposeDrivenAgent",
    "ContextMCPServer",
    "MCPServerProtocol",
    "MCPTransportType",
    "MCPToolDefinition",
    "MCPStdioTool",
    "MCPStreamableHTTPTool",
    "MCPWebsocketTool",
    "IMLService",
    "NoOpMLService",
]

__version__ = "1.0.0"
