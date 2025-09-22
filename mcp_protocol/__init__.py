"""
MCP Protocol package - contains protocol definitions for MCP communication
"""
from .mcp_request import MCPRequest
from .mcp_response import MCPResponse

__all__ = [
    'MCPRequest',
    'MCPResponse'
]
