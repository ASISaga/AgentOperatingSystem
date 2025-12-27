"""
AOS MCP Module

Model Context Protocol integration for AOS.
Includes ContextMCPServer - common infrastructure for agent context preservation.
"""

from .client import MCPClient, MCPConnectionStatus as ClientConnectionStatus
from .client_manager import MCPClientManager, MCPConnectionStatus, MCPServerType, MCPServerConfig
from .protocol import MCPRequest, MCPResponse
from .context_server import ContextMCPServer

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