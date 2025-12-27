# Azure Functions Infrastructure for AgentOperatingSystem

This directory contains plug-and-play Azure Functions applications for deploying agents and MCP servers.

## Overview

The AgentOperatingSystem provides two Azure Functions applications for configuration-driven deployment:

1. **GenesisAgents** - Plug-and-play infrastructure for PurposeDrivenAgent(s)
2. **MCPServers** - Plug-and-play infrastructure for MCP servers

Both applications communicate with the AOS kernel over Azure Service Bus, enabling a fully decoupled architecture.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│               AgentOperatingSystem Kernel                  │
│                                                            │
└──────────────────┬──────────────────┬──────────────────────┘
                   │                  │
                   │ Azure Service Bus│
                   │                  │
        ┌──────────▼─────────┐  ┌────▼──────────────┐
        │                    │  │                   │
        │  GenesisAgents     │  │   MCPServers      │
        │  (Functions App)   │  │   (Functions App) │
        │                    │  │                   │
        └────────────────────┘  └───────────────────┘
             │                       │
             │ Agents consume        │ Provides
             │ MCP tools             │ MCP tools
             │                       │
             └───────────────────────┘
```

## GenesisAgents

**Purpose**: Plug-and-play infrastructure for onboarding PurposeDrivenAgent(s)

**Key Features**:
- Configuration-driven agent deployment
- Automatic LoRA adapter training integration
- MCP tool integration from registry
- Zero code required to onboard new agents

**Configuration**: Agents are defined in `agent_registry.json`

**Documentation**: See [GenesisAgents/README.md](GenesisAgents/README.md)

### Quick Start

```bash
cd GenesisAgents

# Configure settings
cp local.settings.json.example local.settings.json
# Edit local.settings.json with your Azure connection strings

# Install dependencies
pip install -r requirements.txt

# Run locally
func start

# Deploy to Azure
func azure functionapp publish <your-function-app-name>
```

### Example Agent Configuration

```json
{
  "agent_id": "ceo",
  "agent_type": "purpose_driven",
  "purpose": "Strategic leadership and decision-making",
  "domain_knowledge": {
    "domain": "ceo",
    "training_data_path": "training-data/ceo/scenarios.jsonl"
  },
  "mcp_tools": [
    {"server_name": "erpnext", "tool_name": "get_company_overview"}
  ],
  "enabled": true
}
```

## MCPServers

**Purpose**: Plug-and-play infrastructure for MCP server deployment

**Key Features**:
- Configuration-driven MCP server deployment
- Automatic secret resolution from Key Vault
- Service Bus integration for request/response
- Zero code required to add new MCP servers

**Configuration**: MCP servers are defined in `mcp_server_registry.json`

**Documentation**: See [MCPServers/README.md](MCPServers/README.md)

### Quick Start

```bash
cd MCPServers

# Configure settings
cp local.settings.json.example local.settings.json
# Edit local.settings.json with your Azure connection strings

# Install dependencies
pip install -r requirements.txt

# Run locally
func start

# Deploy to Azure
func azure functionapp publish <your-function-app-name>
```

### Example MCP Server Configuration

```json
{
  "server_id": "github",
  "server_name": "GitHub MCP Server",
  "server_type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
  },
  "tools": [...],
  "enabled": true,
  "auto_start": true
}
```

## Communication Flow

### Agent Event Flow

1. **AOS Kernel** publishes event to `agent-events` topic
2. **GenesisAgents** receives event via subscription
3. **Agent** processes event and may request MCP tools
4. **GenesisAgents** sends MCP request to `mcp-requests` topic
5. **MCPServers** receives request and executes tool
6. **MCPServers** sends response to `mcp-responses` topic
7. **GenesisAgents** receives response and continues processing

### MCP Request Flow

```
Agent -> GenesisAgents -> Service Bus (mcp-requests) -> MCPServers
                                                             |
Agent <- GenesisAgents <- Service Bus (mcp-responses) <------
```

## Azure Resources Required

Both applications require the following Azure resources:

### Storage Account
- Agent configurations (GenesisAgents)
- MCP server registry (MCPServers)
- Function app storage

### Service Bus Namespace
- Topics: `agent-events`, `mcp-requests`, `mcp-responses`
- Queues: `agent-commands`, `mcp-server-commands`
- Subscriptions for each app

### Key Vault
- API keys and tokens
- Connection strings
- Secrets for MCP servers

### Function Apps
- GenesisAgents function app
- MCPServers function app

## Deployment

### Prerequisites

- Azure subscription
- Azure CLI installed
- Azure Functions Core Tools
- Python 3.8+

### Infrastructure Setup

```bash
# Clone the repository
git clone https://github.com/ASISaga/AgentOperatingSystem.git
cd AgentOperatingSystem/azure_functions

# Run the setup script (creates all Azure resources)
./setup_infrastructure.sh

# Or manually create resources (see individual README files)
```

### Deploy Both Apps

```bash
# Deploy GenesisAgents
cd GenesisAgents
func azure functionapp publish aos-genesis-agents

# Deploy MCPServers
cd ../MCPServers
func azure functionapp publish aos-mcp-servers
```

## Configuration Management

### Agent Registry

Upload agent configurations to Blob Storage:

```bash
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file agent_registry.json \
  --connection-string "$STORAGE_CONN" \
  --overwrite
```

### MCP Server Registry

Upload MCP server configurations to Blob Storage:

```bash
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file mcp_server_registry.json \
  --connection-string "$STORAGE_CONN" \
  --overwrite
```

## Monitoring

### Health Checks

Both apps expose health check endpoints:

```bash
# GenesisAgents health
curl https://aos-genesis-agents.azurewebsites.net/api/health

# MCPServers health
curl https://aos-mcp-servers.azurewebsites.net/api/health
```

### Application Insights

Both apps are integrated with Application Insights for:
- Request/response tracking
- Performance metrics
- Error logging
- Custom telemetry

### Service Bus Monitoring

Monitor Service Bus topics and queues:
- Message rates
- Queue depths
- Failed deliveries
- Latency metrics

## Development

### Local Development

Both apps can run locally using Azure Functions Core Tools:

```bash
# Start GenesisAgents locally
cd GenesisAgents
func start

# Start MCPServers locally (in another terminal)
cd MCPServers
func start
```

### Testing

Test configurations before deployment:

```bash
# Validate agent configuration
python -c "from agent_config_schema import AgentRegistry; \
           import json; \
           registry = AgentRegistry(**json.load(open('agent_registry.json'))); \
           print(f'Valid: {len(registry.agents)} agents')"

# Validate MCP server configuration
python -c "from mcp_server_schema import MCPServerRegistry; \
           import json; \
           registry = MCPServerRegistry(**json.load(open('mcp_server_registry.json'))); \
           print(f'Valid: {len(registry.servers)} servers')"
```

## Security Best Practices

1. **Use Managed Identity**: Enable managed identity for both function apps
2. **Key Vault Integration**: Store all secrets in Key Vault
3. **RBAC**: Use role-based access control for resources
4. **Network Security**: Use VNet integration and private endpoints
5. **Monitoring**: Enable security monitoring and alerts

## Troubleshooting

### Common Issues

1. **Function app not starting**: Check Application Insights logs
2. **Service Bus connection issues**: Verify connection strings
3. **Agent/Server not found**: Check registry is uploaded correctly
4. **MCP tool failures**: Verify secrets in Key Vault
5. **Performance issues**: Check scaling settings

### Logs

View logs in Application Insights:

```bash
# Query logs for errors
az monitor app-insights query \
  --app aos-genesis-insights \
  --analytics-query "traces | where severityLevel > 2 | take 100"
```

## Examples

See example configurations:
- [example_agent_registry.json](GenesisAgents/example_agent_registry.json)
- [example_mcp_server_registry.json](MCPServers/example_mcp_server_registry.json)

## Support

For detailed documentation, see:
- [GenesisAgents Documentation](GenesisAgents/README.md)
- [MCPServers Documentation](MCPServers/README.md)
- [Main AOS Documentation](../README.md)

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review Application Insights logs
