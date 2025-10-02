"""
Agent Operating System (AOS)

The foundational operating system for agent-based applications.
Refactored architecture with proper package structure.
"""

# Import from the new aos package structure  
from .aos import *

# Legacy imports for backward compatibility
try:
    from .AgentOperatingSystem import AOS
    from .AgentTeam import AgentTeam
    from .aos_auth import AOSAuth
except ImportError:
    # Legacy files may not exist after refactoring
    pass
from .aos_message import AOSMessage
from .mcp_client_manager import MCPClientManager, MCPServerConfig, MCPServerType

__version__ = "2.0.0"
__author__ = "Business Infinity AI"
__description__ = "Agent Operating System with MCP Integration"

__all__ = [
    # Core AOS components
    "AOS",
    "AgentTeam",
    "AOSAuth",
    "AOSMessage",
    
    # MCP Client integration
    "MCPClientManager",
    "MCPServerConfig", 
    "MCPServerType"
]


async def create_aos_system_with_mcp():
    """
    Factory function to create AOS system with MCP client integration
    
    Returns:
        Tuple of (AOS, MCPClientManager) - initialized and ready to use
    """
    # Initialize MCP Client Manager
    mcp_client = MCPClientManager()
    await mcp_client.initialize()
    
    # Initialize AOS with MCP integration
    aos = AOS()
    aos.mcp_client = mcp_client  # Inject MCP client into AOS
    await aos.initialize()
    
    return aos, mcp_client