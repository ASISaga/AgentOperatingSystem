"""MCPServers Azure Function app entry point.

Deploys and manages MCP servers based on registry configuration.
All MCP servers are registered with the Foundry Agent Service for
tool discovery and routing.  The Foundry Agent Service manages
tool connections internally — clients declare server names via
``MCPServerConfig`` and AOS handles the rest.
"""
