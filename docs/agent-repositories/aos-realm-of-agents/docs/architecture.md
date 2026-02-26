# aos-realm-of-agents Architecture

## Overview

RealmOfAgents is a config-driven Azure Function app that dynamically deploys and
manages AOS agents based on a JSON registry configuration.

## Component Architecture

```
┌─────────────────────────────────┐
│   Agent Registry (JSON)         │
│   • Agent definitions           │
│   • Runtime configuration       │
│   • Adapter mappings            │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   RealmOfAgents Function App    │
│   • Registry loader             │
│   • Agent factory               │
│   • Lifecycle management        │
│   • Service Bus integration     │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   Agent Instances               │
│   • PurposeDrivenAgent          │
│   • LeadershipAgent             │
│   • CMOAgent                    │
│   • Custom agents               │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   aos-kernel                    │
│   • Storage, MCP, Messaging     │
└─────────────────────────────────┘
```

## Agent Registry

The agent registry is a JSON file that defines all agents to be deployed:

```json
{
    "agents": [
        {
            "agent_id": "ceo",
            "agent_type": "LeadershipAgent",
            "purpose": "Strategic leadership",
            "adapter_name": "leadership"
        }
    ]
}
```

## Lifecycle

1. **Startup** — Function app reads agent registry
2. **Initialization** — Agent instances are created from configuration
3. **Running** — Agents respond to Service Bus messages
4. **Shutdown** — Graceful cleanup on function app stop

## Migration Path

RealmOfAgents supports migration from custom deployment to Microsoft Foundry
Agent Service. The `MIGRATION_TO_FOUNDRY.md` document covers the migration
process in detail.

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Main function app
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers
