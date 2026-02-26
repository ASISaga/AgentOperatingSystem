# aos-mcp-servers Architecture

## Overview

MCPServers is a config-driven Azure Function app that dynamically deploys and
manages MCP (Model Context Protocol) servers based on a JSON registry
configuration.

## Component Architecture

```
┌─────────────────────────────────┐
│   MCP Server Registry (JSON)    │
│   • Server definitions          │
│   • Tool configurations         │
│   • Resource mappings           │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   MCPServers Function App       │
│   • Registry loader             │
│   • Server factory              │
│   • Lifecycle management        │
│   • Service Bus integration     │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   MCP Server Instances          │
│   • ContextMCPServer            │
│   • Domain-specific servers     │
│   • Tool providers              │
│   • Resource providers          │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   aos-kernel                    │
│   • Storage, Messaging, Auth    │
└─────────────────────────────────┘
```

## MCP Server Registry

The MCP server registry is a JSON file that defines all MCP servers to deploy:

```json
{
    "mcp_servers": [
        {
            "server_id": "context-server",
            "server_type": "ContextMCPServer",
            "tools": ["get_context", "set_context"],
            "resources": ["agent_state"]
        }
    ]
}
```

## MCP Protocol Integration

MCP servers expose:

- **Tools** — Callable functions that agents invoke for actions
- **Resources** — Data sources that agents read for context
- **Prompts** — Templated prompts for agent interactions

## Lifecycle

1. **Startup** — Function app reads MCP server registry
2. **Initialization** — Server instances are created from configuration
3. **Running** — Servers respond to MCP protocol requests
4. **Shutdown** — Graceful cleanup on function app stop

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Main function app
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents
