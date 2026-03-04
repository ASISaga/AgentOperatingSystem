"""
purpose_driven_agent — Public API.

Exports:
    PurposeDrivenAgent: Abstract base class for all purpose-driven perpetual agents.
    GenericPurposeDrivenAgent: Concrete general-purpose implementation.
    ContextMCPServer: Lightweight MCP context server for state preservation.
    MCPServerProtocol: Structural protocol for MCP servers registered with agents.
    IMLService: Abstract ML service interface for LoRA training and inference.
    NoOpMLService: No-operation ML service (raises NotImplementedError on use).

MCP transport types and configuration models are available through the AOS
Client SDK (``aos_client.mcp``)::

    from aos_client import MCPServerConfig, MCPTransportType
    from aos_client.mcp import MCPToolDefinition

MCP transport connection classes (runtime implementations) are in
``aos_mcp_servers.routing``::

    from aos_mcp_servers.routing import MCPStdioTool, MCPStreamableHTTPTool, MCPWebsocketTool
"""

from purpose_driven_agent.agent import (
    A2AAgentTool,
    GenericPurposeDrivenAgent,
    MCPServerProtocol,
    PurposeDrivenAgent,
)
from purpose_driven_agent.context_server import ContextMCPServer
from purpose_driven_agent.ml_interface import IMLService, NoOpMLService

__all__ = [
    "A2AAgentTool",
    "PurposeDrivenAgent",
    "GenericPurposeDrivenAgent",
    "ContextMCPServer",
    "MCPServerProtocol",
    "IMLService",
    "NoOpMLService",
]

__version__ = "1.0.0"
