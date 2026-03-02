"""
Backward-compatibility shim for purpose_driven_agent.mcp_routing.

The MCP routing implementation has been moved to the centralized
``aos-mcp-servers`` repository (``aos_mcp_servers.routing``).

This module re-exports all public symbols from that canonical location so
that existing code importing from ``purpose_driven_agent.mcp_routing`` continues
to work without modification.

New code should import directly from ``aos_mcp_servers.routing``::

    from aos_mcp_servers.routing import (
        MCPStdioTool,
        MCPStreamableHTTPTool,
        MCPWebsocketTool,
        MCPToolDefinition,
        MCPTransportType,
    )
"""

from aos_mcp_servers.routing import (  # noqa: F401
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