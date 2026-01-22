# Azure Functions Infrastructure

AOS provides **configuration-driven Azure Functions applications** for zero-code deployment of agents and MCP servers.

## RealmOfAgents - Plug-and-Play Agent Infrastructure

**RealmOfAgents** is an Azure Functions app that enables configuration-driven deployment of PurposeDrivenAgent(s). PurposeDrivenAgent - the core architectural component of AOS - now runs on **Microsoft Foundry Agent Service** with **Llama 3.3 70B fine-tuned using domain-specific LoRA adapters**. Developers provide only configuration - no code required!

### Configuration Example

```json
{
  "agent_id": "cfo",
  "purpose": "Financial oversight and strategic planning",
  "domain_knowledge": {
    "domain": "cfo",
    "training_data_path": "training-data/cfo/scenarios.jsonl"
  },
  "mcp_tools": [
    {"server_name": "erpnext", "tool_name": "get_financial_reports"}
  ],
  "enabled": true
}
```

### Features

- ✅ Zero code required to onboard new agents
- ✅ Automatic LoRA adapter training integration
- ✅ MCP tool integration from registry
- ✅ Service Bus communication with AOS kernel
- ✅ Lifecycle management (start, stop, restart)

[📖 RealmOfAgents Documentation](../../azure_functions/RealmOfAgents/README.md)

## MCPServers - Plug-and-Play MCP Server Infrastructure

**MCPServers** is an Azure Functions app that enables configuration-driven deployment of MCP servers. Add new MCP servers with just configuration!

### Configuration Example

```json
{
  "server_id": "github",
  "server_name": "GitHub MCP Server",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
  "tools": [...],
  "enabled": true
}
```

### Features

- ✅ Zero code required to add new MCP servers
- ✅ Automatic secret resolution from Key Vault
- ✅ Service Bus communication with AOS kernel
- ✅ Tool and resource discovery
- ✅ Lifecycle management (start, stop, restart)

[📖 MCPServers Documentation](../../azure_functions/MCPServers/README.md)

## Architecture

```
┌────────────────────────────────────────────────────┐
│         AgentOperatingSystem Kernel                │
│         (Core Infrastructure)                      │
└──────────────┬──────────────┬──────────────────────┘
               │              │
    Azure Service Bus  Azure Service Bus
               │              │
    ┌──────────▼──────┐  ┌───▼──────────────┐
    │ RealmOfAgents   │  │  MCPServers      │
    │ (Config-Driven) │  │  (Config-Driven) │
    └─────────────────┘  └──────────────────┘
```

[📖 Azure Functions Infrastructure Overview](../../azure_functions/README.md)

## See Also

- [Quick Start Guide](quickstart.md) - Get started quickly
- [Deployment Guide](deployment.md) - Production deployment
- [Configuration Guide](../configuration.md) - System configuration
