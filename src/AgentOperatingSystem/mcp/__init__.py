"""
AOS MCP Module

Model Context Protocol integration for AOS.
Includes ContextMCPServer - common infrastructure for agent context preservation.
"""

from .client import MCPClient
from .client import MCPConnectionStatus as ClientConnectionStatus
from .client_manager import (
    MCPClientManager,
    MCPConnectionStatus,
    MCPServerConfig,
    MCPServerType,
)
from .context_server import ContextMCPServer
from .protocol import MCPRequest, MCPResponse

__all__ = [
    "MCPClient",
    "MCPClientManager",
    "MCPConnectionStatus",
    "ClientConnectionStatus",
    "MCPServerType",
    "MCPServerConfig",
    "MCPRequest",
    "MCPResponse",
    "ContextMCPServer"
]
