"""MCP server configuration schema for MCPServers.

Pydantic models defining the MCP server registry schema used to configure
MCP servers for config-driven deployment.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPToolEntry(BaseModel):
    """Schema for a single MCP tool exposed by a server."""

    name: str = Field(..., description="Unique tool name")
    description: str = Field(default="", description="Human-readable description")
    input_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema for the tool's input parameters",
    )


class MCPServerRegistryEntry(BaseModel):
    """Schema for a single MCP server in the registry."""

    server_id: str = Field(..., description="Unique server identifier")
    server_type: str = Field(
        ...,
        description="Transport type: 'stdio', 'streamable_http', or 'websocket'",
    )
    description: str = Field(default="", description="Human-readable description")

    # stdio-specific fields
    command: Optional[str] = Field(default=None, description="Executable for stdio servers")
    args: List[str] = Field(default_factory=list, description="Command-line arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")

    # http/websocket-specific fields
    url: Optional[str] = Field(
        default=None, description="Endpoint URL for HTTP/WebSocket servers"
    )
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    gateway_url: Optional[str] = Field(
        default=None,
        description="AI Gateway URL for governed routing via Foundry",
    )

    tools: List[MCPToolEntry] = Field(
        default_factory=list, description="Tools exposed by this server"
    )
    enabled: bool = Field(default=True, description="Whether this server is active")


class MCPServerRegistry(BaseModel):
    """Schema for the full MCP server registry configuration."""

    mcp_servers: List[MCPServerRegistryEntry] = Field(
        default_factory=list, description="List of MCP server configurations"
    )

    def get_enabled_servers(self) -> List[MCPServerRegistryEntry]:
        """Return only servers with enabled=True."""
        return [s for s in self.mcp_servers if s.enabled]

    def get_server(self, server_id: str) -> Optional[MCPServerRegistryEntry]:
        """Look up a server by ID."""
        for server in self.mcp_servers:
            if server.server_id == server_id:
                return server
        return None
