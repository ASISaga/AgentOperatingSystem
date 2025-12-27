# RealmOfAgents - Plug-and-Play Agent Infrastructure

## Overview

**RealmOfAgents** is an Azure Functions application that provides plug-and-play infrastructure for onboarding PurposeDrivenAgent(s). Developers provide only configuration - Purpose, domain knowledge (for fine-tuning LoRA adapters), and MCP server tools from the registry. No code changes are required to onboard new agents.

## Key Features

- **Configuration-Driven**: All agents are defined as JSON configuration
- **Zero Code Onboarding**: Add new agents without writing code
- **Common Infrastructure**: Implements all Azure and Microsoft Agent Framework infrastructure
- **Service Bus Integration**: Communicates with AOS kernel over Azure Service Bus
- **LoRA Fine-Tuning**: Automatic LoRA adapter training from domain knowledge
- **MCP Tool Integration**: Seamless integration with MCP tools from the registry
- **Lifecycle Management**: Automatic agent start, stop, restart, and health monitoring

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         RealmOfAgents (Azure Functions)             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Agent Registry (Blob Storage)                │ │
│  │  - agent_registry.json                        │ │
│  │  - Contains all agent configurations          │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  Configuration Loader                         │ │
│  │  - Loads and validates configurations         │ │
│  │  - Resolves MCP tool references               │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  Agent Instantiation Engine                   │ │
│  │  - Creates PurposeDrivenAgent instances       │ │
│  │  - Initializes MCP context servers            │ │
│  │  - Configures LoRA adapters                   │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  Active Agent Instances                       │ │
│  │  - CEO, CFO, CMO, COO, etc.                   │ │
│  │  - Running perpetually                        │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │ Azure Service Bus
                   ↓
┌─────────────────────────────────────────────────────┐
│      AgentOperatingSystem Kernel                    │
└─────────────────────────────────────────────────────┘
```

## Configuration Schema

### Agent Configuration

Each agent is defined by a JSON configuration with the following structure:

```json
{
  "agent_id": "ceo",
  "agent_type": "purpose_driven",
  "purpose": "Strategic leadership and decision-making",
  "purpose_scope": "Strategic planning, major decisions",
  "success_criteria": [
    "Drive company growth",
    "Ensure strategic alignment"
  ],
  "domain_knowledge": {
    "domain": "ceo",
    "training_data_path": "training-data/ceo/scenarios.jsonl",
    "adapter_config": {
      "task_type": "causal_lm",
      "r": 16,
      "lora_alpha": 32,
      "target_modules": ["q_proj", "v_proj"]
    }
  },
  "mcp_tools": [
    {
      "server_name": "erpnext",
      "tool_name": "get_company_overview"
    }
  ],
  "system_message": "You are the CEO...",
  "enabled": true
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | Yes | Unique identifier for the agent |
| `agent_type` | enum | Yes | Type: `purpose_driven`, `perpetual`, or `leadership` |
| `purpose` | string | Yes | The long-term purpose of the agent |
| `purpose_scope` | string | No | Scope/boundaries of the purpose |
| `success_criteria` | array | No | List of success criteria |
| `domain_knowledge` | object | Yes | Domain knowledge for LoRA fine-tuning |
| `mcp_tools` | array | No | MCP tools from the registry |
| `system_message` | string | No | Custom system message |
| `enabled` | boolean | No | Whether agent is enabled (default: true) |

## Deployment

### Prerequisites

- Azure subscription
- Azure Functions Core Tools
- Python 3.8+
- Azure CLI

### Step 1: Create Azure Resources

```bash
# Create resource group
az group create --name aos-genesis --location eastus

# Create storage account
az storage account create \
  --name aosgenesisstore \
  --resource-group aos-genesis \
  --location eastus \
  --sku Standard_LRS

# Create Service Bus namespace
az servicebus namespace create \
  --name aos-genesis-bus \
  --resource-group aos-genesis \
  --location eastus \
  --sku Standard

# Create topics and subscriptions
az servicebus topic create \
  --name agent-events \
  --namespace-name aos-genesis-bus \
  --resource-group aos-genesis

az servicebus topic subscription create \
  --name genesis-agents \
  --topic-name agent-events \
  --namespace-name aos-genesis-bus \
  --resource-group aos-genesis

# Create queue
az servicebus queue create \
  --name agent-commands \
  --namespace-name aos-genesis-bus \
  --resource-group aos-genesis
```

### Step 2: Upload Agent Registry

```bash
# Get storage connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name aosgenesisstore \
  --resource-group aos-genesis \
  --query connectionString -o tsv)

# Create container
az storage container create \
  --name agent-configs \
  --connection-string "$STORAGE_CONN"

# Upload registry
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file example_agent_registry.json \
  --connection-string "$STORAGE_CONN"
```

### Step 3: Configure Application Settings

Update `local.settings.json` with your connection strings:

```json
{
  "Values": {
    "AZURE_SERVICE_BUS_CONNECTION_STRING": "<your-service-bus-connection>",
    "AZURE_STORAGE_CONNECTION_STRING": "<your-storage-connection>",
    "AZURE_KEY_VAULT_URL": "<your-keyvault-url>",
    "AGENT_CONFIG_BLOB_CONTAINER": "agent-configs"
  }
}
```

### Step 4: Deploy Function App

```bash
# Create Function App
az functionapp create \
  --name aos-genesis-agents \
  --resource-group aos-genesis \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account aosgenesisstore \
  --os-type Linux

# Deploy
cd azure_functions/RealmOfAgents
func azure functionapp publish aos-genesis-agents
```

## Usage

### Adding a New Agent

1. **Create Configuration**: Add a new agent configuration to `agent_registry.json`

```json
{
  "agent_id": "cto",
  "agent_type": "purpose_driven",
  "purpose": "Technology strategy and innovation",
  "domain_knowledge": {
    "domain": "cto",
    "training_data_path": "training-data/cto/tech_scenarios.jsonl"
  },
  "mcp_tools": [
    {
      "server_name": "github",
      "tool_name": "search_code"
    }
  ],
  "enabled": true
}
```

2. **Upload Registry**: Upload the updated registry to Blob Storage

```bash
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file agent_registry.json \
  --connection-string "$STORAGE_CONN" \
  --overwrite
```

3. **Reload Registry**: Send a reload command via Service Bus

```bash
# The agent will be automatically loaded on the next startup trigger
# Or send a reload command manually
```

That's it! No code changes required.

### Agent Lifecycle Commands

Send commands to agents via the Service Bus queue `agent-commands`:

```json
{
  "command": "start",
  "agent_id": "cto",
  "params": {}
}
```

Available commands:
- `start`: Start an agent
- `stop`: Stop an agent
- `restart`: Restart an agent
- `reload_registry`: Reload the entire agent registry

### Monitoring

#### Health Check

```bash
curl https://aos-genesis-agents.azurewebsites.net/api/health
```

Response:
```json
{
  "status": "healthy",
  "active_agents": 4,
  "agent_ids": ["ceo", "cfo", "cmo", "coo"]
}
```

#### Agent Status

```bash
curl https://aos-genesis-agents.azurewebsites.net/api/agents/ceo/status
```

Response:
```json
{
  "agent_id": "ceo",
  "status": "running",
  "is_running": true,
  "type": "PurposeDrivenAgent"
}
```

## Service Bus Communication

### Event Topic: `agent-events`

Agents receive events from the AOS kernel:

```json
{
  "agent_id": "ceo",
  "event_type": "DecisionRequested",
  "payload": {
    "context": "Q4 strategic planning",
    "data": {}
  }
}
```

### Command Queue: `agent-commands`

Lifecycle commands are sent to this queue:

```json
{
  "command": "start",
  "agent_id": "ceo",
  "params": {}
}
```

## Training LoRA Adapters

When a new agent is configured, its LoRA adapter can be trained:

1. **Prepare Training Data**: Upload training data to the path specified in `domain_knowledge.training_data_path`

2. **Trigger Training**: The agent will automatically use the adapter name from the `domain_knowledge.domain` field

3. **Inference**: The agent will use the trained adapter for all LLM operations

## Best Practices

### Configuration Management

- **Version Control**: Keep agent configurations in version control
- **Backup**: Regularly backup the agent registry
- **Validation**: Validate configurations before upload
- **Documentation**: Document the purpose and tools for each agent

### Security

- **Key Vault**: Store all secrets in Azure Key Vault
- **RBAC**: Use role-based access control for Function App
- **Monitoring**: Enable Application Insights for monitoring
- **Encryption**: Enable encryption at rest for Storage Account

### Performance

- **Batch Updates**: Group multiple agent changes together
- **Caching**: The registry is loaded once at startup
- **Scaling**: Configure auto-scaling for the Function App
- **Monitoring**: Monitor agent health and performance

## Troubleshooting

### Agent Not Starting

1. Check the agent registry is uploaded correctly
2. Verify `enabled: true` in configuration
3. Check Application Insights logs for errors
4. Verify Service Bus connection string

### MCP Tools Not Working

1. Verify MCP server is registered in MCPServers app
2. Check MCP server is running
3. Verify tool names match the registry
4. Check Service Bus topic for MCP requests

### LoRA Adapter Issues

1. Verify training data path is correct
2. Check adapter configuration is valid
3. Ensure Azure ML workspace is configured
4. Check adapter training logs

## Examples

See `example_agent_registry.json` for a complete example with multiple agents (CEO, CFO, CMO, COO).

## Support

For issues and questions, please refer to the main AOS documentation or create an issue in the repository.
