"""
MCP Response data model - represents MCP response messages
"""
from typing import Any, Optional

from pydantic import BaseModel


class MCPResponse(BaseModel):
    """
    Represents an MCP (Model Context Protocol) response message
    """
    jsonrpc: str = "2.0"
    result: Any | None = None
    error: Any | None = None
    id: Optional[str | int] = None
