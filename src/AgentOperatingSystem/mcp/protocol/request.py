"""
MCP Request data model - represents MCP request messages
"""
from typing import Optional

from pydantic import BaseModel


class MCPRequest(BaseModel):
    """
    Represents an MCP (Model Context Protocol) request message
    """
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: Optional[str | int] = None
