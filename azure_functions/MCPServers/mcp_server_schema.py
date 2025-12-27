"""
MCP Server Configuration Schema for MCPServers

Defines the structure for configuration-driven MCP server deployment.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MCPServerType(str, Enum):
    """Types of MCP servers"""
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPToolDefinition(BaseModel):
    """Definition of an MCP tool"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(
        ...,
        description="JSON schema for tool input"
    )


class MCPResourceDefinition(BaseModel):
    """Definition of an MCP resource"""
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: str = Field(..., description="Resource description")
    mime_type: Optional[str] = Field(
        default=None,
        description="MIME type of the resource"
    )


class MCPServerConfiguration(BaseModel):
    """
    Complete configuration for an MCP server.
    
    This is all that's needed to deploy a new MCP server - no code required!
    
    Example:
        {
            "server_id": "github",
            "server_name": "GitHub MCP Server",
            "server_type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
            },
            "tools": [
                {
                    "name": "create_issue",
                    "description": "Create a new GitHub issue",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"},
                            "title": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["owner", "repo", "title"]
                    }
                }
            ],
            "resources": [],
            "enabled": true
        }
    """
    server_id: str = Field(..., description="Unique identifier for the MCP server")
    server_name: str = Field(..., description="Human-readable name")
    server_type: MCPServerType = Field(
        default=MCPServerType.STDIO,
        description="Type of MCP server (stdio, sse, websocket)"
    )
    
    # Server execution configuration
    command: str = Field(..., description="Command to start the server")
    args: List[str] = Field(
        default_factory=list,
        description="Arguments for the command"
    )
    env: Dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables (supports ${VAR} substitution from Key Vault)"
    )
    
    # MCP protocol definitions
    tools: List[MCPToolDefinition] = Field(
        default_factory=list,
        description="Tools provided by this server"
    )
    resources: List[MCPResourceDefinition] = Field(
        default_factory=list,
        description="Resources provided by this server"
    )
    
    # Lifecycle
    enabled: bool = Field(
        default=True,
        description="Whether this server is enabled"
    )
    auto_start: bool = Field(
        default=True,
        description="Whether to start this server automatically on app startup"
    )
    
    # Configuration
    timeout_seconds: int = Field(
        default=30,
        description="Timeout for MCP operations"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed operations"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class MCPServerRegistry(BaseModel):
    """Registry of all MCP server configurations"""
    servers: List[MCPServerConfiguration] = Field(
        default_factory=list,
        description="List of all MCP server configurations"
    )
    version: str = Field(
        default="1.0",
        description="Registry schema version"
    )
    
    def get_enabled_servers(self) -> List[MCPServerConfiguration]:
        """Get all enabled servers"""
        return [server for server in self.servers if server.enabled]
    
    def get_auto_start_servers(self) -> List[MCPServerConfiguration]:
        """Get all servers that should auto-start"""
        return [server for server in self.servers if server.enabled and server.auto_start]
    
    def get_server_by_id(self, server_id: str) -> Optional[MCPServerConfiguration]:
        """Get server configuration by ID"""
        for server in self.servers:
            if server.server_id == server_id:
                return server
        return None
