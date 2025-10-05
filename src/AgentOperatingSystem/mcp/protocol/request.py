"""
MCP Request data model - represents MCP request messages
"""
from pydantic import BaseModel
from typing import Optional

class MCPRequest(BaseModel):
    """
    Represents an MCP (Model Context Protocol) request message
    """
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: Optional[str | int] = None