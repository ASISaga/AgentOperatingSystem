"""
MCP Response data model - represents MCP response messages
"""
from pydantic import BaseModel
from typing import Any, Optional

class MCPResponse(BaseModel):
    """
    Represents an MCP (Model Context Protocol) response message
    """
    jsonrpc: str = "2.0"
    result: Any | None = None
    error: Any | None = None
    id: Optional[str | int] = None
