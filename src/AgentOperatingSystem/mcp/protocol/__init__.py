"""
MCP Protocol package - contains protocol definitions for MCP communication
"""
from .request import MCPRequest
from .response import MCPResponse

__all__ = [
    'MCPRequest',
    'MCPResponse'
]