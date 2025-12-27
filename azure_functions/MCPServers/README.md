# MCPServers - Plug-and-Play MCP Server Infrastructure

## Overview

**MCPServers** is an Azure Functions application that provides plug-and-play infrastructure for MCP (Model Context Protocol) server deployment. It provides common Azure and MCP related infrastructure, enabling configuration-driven deployment of MCP servers.

This app communicates with the AgentOperatingSystem kernel over Azure Service Bus, providing a unified interface for all MCP operations.

## Key Features

- **Configuration-Driven**: All MCP servers are defined as JSON configuration
- **Zero Code Deployment**: Add new MCP servers without writing code
- **Common Infrastructure**: Implements all Azure and MCP protocol infrastructure
- **Service Bus Integration**: Communicates with AOS kernel over Azure Service Bus
- **Secret Management**: Automatic secret resolution from Azure Key Vault
- **Tool Discovery**: Automatic tool and resource discovery
- **Health Monitoring**: Built-in health checks and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         MCPServers (Azure Functions)                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  MCP Server Registry (Blob Storage)           │ │
│  │  - mcp_server_registry.json                   │ │
│  │  - Contains all MCP server configurations     │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  Configuration Loader                         │ │
│  │  - Loads and validates configurations         │ │
│  │  - Resolves secrets from Key Vault            │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  MCP Server Instantiation Engine              │ │
│  │  - Creates MCP client instances               │ │
│  │  - Initializes server processes               │ │
│  │  - Manages server lifecycle                   │ │
│  └───────────────────────────────────────────────┘ │
│                         ↓                           │
│  ┌───────────────────────────────────────────────┐ │
│  │  Active MCP Server Instances                  │ │
│  │  - GitHub, ERPNext, LinkedIn, Reddit, etc.    │ │
│  │  - Running and ready to handle requests       │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │ Azure Service Bus
                   ↓
┌─────────────────────────────────────────────────────┐
│      AgentOperatingSystem Kernel                    │
│                                                     │
│      GenesisAgents (consumes MCP tools)             │
└─────────────────────────────────────────────────────┘
```

## Configuration Schema

### MCP Server Configuration

Each MCP server is defined by a JSON configuration:

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
  "tools": [
    {
      "name": "create_issue",
      "description": "Create a new GitHub issue",
      "input_schema": {
        "type": "object",
        "properties": {
          "owner": {"type": "string"},
          "repo": {"type": "string"},
          "title": {"type": "string"}
        }
      }
    }
  ],
  "enabled": true,
  "auto_start": true
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `server_id` | string | Yes | Unique identifier for the server |
| `server_name` | string | Yes | Human-readable name |
| `server_type` | enum | Yes | Type: `stdio`, `sse`, or `websocket` |
| `command` | string | Yes | Command to start the server |
| `args` | array | No | Arguments for the command |
| `env` | object | No | Environment variables (supports ${VAR} from Key Vault) |
| `tools` | array | No | Tool definitions |
| `resources` | array | No | Resource definitions |
| `enabled` | boolean | No | Whether server is enabled (default: true) |
| `auto_start` | boolean | No | Auto-start on app startup (default: true) |
| `timeout_seconds` | integer | No | Operation timeout (default: 30) |
| `max_retries` | integer | No | Max retries (default: 3) |

## Deployment

### Prerequisites

- Azure subscription
- Azure Functions Core Tools
- Python 3.8+
- Azure CLI
- Azure Key Vault (for secrets)

### Step 1: Create Azure Resources

```bash
# Create resource group
az group create --name aos-mcp --location eastus

# Create storage account
az storage account create \
  --name aosmcpstore \
  --resource-group aos-mcp \
  --location eastus \
  --sku Standard_LRS

# Create Service Bus namespace
az servicebus namespace create \
  --name aos-mcp-bus \
  --resource-group aos-mcp \
  --location eastus \
  --sku Standard

# Create topics and subscriptions
az servicebus topic create \
  --name mcp-requests \
  --namespace-name aos-mcp-bus \
  --resource-group aos-mcp

az servicebus topic subscription create \
  --name mcp-servers \
  --topic-name mcp-requests \
  --namespace-name aos-mcp-bus \
  --resource-group aos-mcp

az servicebus topic create \
  --name mcp-responses \
  --namespace-name aos-mcp-bus \
  --resource-group aos-mcp

# Create queue for commands
az servicebus queue create \
  --name mcp-server-commands \
  --namespace-name aos-mcp-bus \
  --resource-group aos-mcp

# Create Key Vault
az keyvault create \
  --name aos-mcp-vault \
  --resource-group aos-mcp \
  --location eastus
```

### Step 2: Store Secrets in Key Vault

```bash
# Store GitHub token
az keyvault secret set \
  --vault-name aos-mcp-vault \
  --name GITHUB-TOKEN \
  --value "your-github-token"

# Store ERPNext credentials
az keyvault secret set \
  --vault-name aos-mcp-vault \
  --name ERPNEXT-API-KEY \
  --value "your-erpnext-key"

# Add other secrets as needed
```

### Step 3: Upload MCP Server Registry

```bash
# Get storage connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name aosmcpstore \
  --resource-group aos-mcp \
  --query connectionString -o tsv)

# Create container
az storage container create \
  --name mcp-registry \
  --connection-string "$STORAGE_CONN"

# Upload registry
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file example_mcp_server_registry.json \
  --connection-string "$STORAGE_CONN"
```

### Step 4: Configure Application Settings

Update `local.settings.json`:

```json
{
  "Values": {
    "AZURE_SERVICE_BUS_CONNECTION_STRING": "<your-service-bus-connection>",
    "AZURE_STORAGE_CONNECTION_STRING": "<your-storage-connection>",
    "AZURE_KEY_VAULT_URL": "https://aos-mcp-vault.vault.azure.net/",
    "MCP_REGISTRY_BLOB_CONTAINER": "mcp-registry"
  }
}
```

### Step 5: Deploy Function App

```bash
# Create Function App
az functionapp create \
  --name aos-mcp-servers \
  --resource-group aos-mcp \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account aosmcpstore \
  --os-type Linux

# Enable managed identity
az functionapp identity assign \
  --name aos-mcp-servers \
  --resource-group aos-mcp

# Grant Key Vault access
PRINCIPAL_ID=$(az functionapp identity show \
  --name aos-mcp-servers \
  --resource-group aos-mcp \
  --query principalId -o tsv)

az keyvault set-policy \
  --name aos-mcp-vault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list

# Deploy
cd azure_functions/MCPServers
func azure functionapp publish aos-mcp-servers
```

## Usage

### Adding a New MCP Server

1. **Create Configuration**: Add a new server configuration to `mcp_server_registry.json`

```json
{
  "server_id": "slack",
  "server_name": "Slack MCP Server",
  "server_type": "stdio",
  "command": "python",
  "args": ["-m", "slack_mcp_server"],
  "env": {
    "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
  },
  "tools": [
    {
      "name": "send_message",
      "description": "Send a message to Slack",
      "input_schema": {
        "type": "object",
        "properties": {
          "channel": {"type": "string"},
          "text": {"type": "string"}
        }
      }
    }
  ],
  "enabled": true,
  "auto_start": true
}
```

2. **Store Secrets**: Add secrets to Key Vault

```bash
az keyvault secret set \
  --vault-name aos-mcp-vault \
  --name SLACK-BOT-TOKEN \
  --value "your-slack-token"
```

3. **Upload Registry**: Upload the updated registry

```bash
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file mcp_server_registry.json \
  --connection-string "$STORAGE_CONN" \
  --overwrite
```

That's it! The server will be automatically loaded on the next startup.

### MCP Server Lifecycle Commands

Send commands via Service Bus queue `mcp-server-commands`:

```json
{
  "command": "start",
  "server_id": "slack",
  "params": {}
}
```

Available commands:
- `start`: Start a server
- `stop`: Stop a server
- `restart`: Restart a server
- `reload_registry`: Reload the entire registry

### Making MCP Requests

Send requests via Service Bus topic `mcp-requests`:

```json
{
  "server_id": "github",
  "method": "call_tool",
  "params": {
    "tool_name": "create_issue",
    "tool_params": {
      "owner": "ASISaga",
      "repo": "AgentOperatingSystem",
      "title": "New feature request"
    }
  },
  "request_id": "req-123"
}
```

Available methods:
- `list_tools`: List all available tools
- `call_tool`: Execute a tool
- `list_resources`: List all available resources
- `read_resource`: Read a resource

Responses are sent to topic `mcp-responses`.

### Monitoring

#### Health Check

```bash
curl https://aos-mcp-servers.azurewebsites.net/api/health
```

Response:
```json
{
  "status": "healthy",
  "active_servers": 5,
  "server_ids": ["github", "erpnext", "linkedin", "reddit", "excel"]
}
```

#### Server Status

```bash
curl https://aos-mcp-servers.azurewebsites.net/api/servers/github/status
```

Response:
```json
{
  "server_id": "github",
  "status": "running",
  "server_name": "GitHub MCP Server"
}
```

#### List All Servers

```bash
curl https://aos-mcp-servers.azurewebsites.net/api/servers
```

Response:
```json
{
  "servers": [
    {
      "server_id": "github",
      "server_name": "GitHub MCP Server",
      "server_type": "stdio",
      "enabled": true,
      "status": "running"
    }
  ]
}
```

## Service Bus Communication

### Request Topic: `mcp-requests`

MCP requests from agents/kernel:

```json
{
  "server_id": "github",
  "method": "call_tool",
  "params": {
    "tool_name": "create_issue",
    "tool_params": {...}
  },
  "request_id": "req-123"
}
```

### Response Topic: `mcp-responses`

MCP responses back to agents/kernel:

```json
{
  "request_id": "req-123",
  "server_id": "github",
  "response": {
    "result": {...}
  }
}
```

### Command Queue: `mcp-server-commands`

Lifecycle commands:

```json
{
  "command": "start",
  "server_id": "github"
}
```

## Secret Management

The app supports automatic secret resolution from Azure Key Vault using the `${SECRET_NAME}` syntax in the `env` field:

```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}"
  }
}
```

The app will:
1. Try to get the secret from Key Vault (using managed identity)
2. Fall back to environment variable if Key Vault is unavailable

## Supported MCP Server Types

### STDIO (Currently Implemented)

Standard I/O based MCP servers:
- Command-line executables (Python, Node.js, etc.)
- Communication via stdin/stdout
- Most common MCP server type

### SSE (Planned)

Server-Sent Events based MCP servers:
- HTTP-based streaming
- Real-time updates
- Web-based servers

### WebSocket (Planned)

WebSocket-based MCP servers:
- Bidirectional communication
- Low latency
- Real-time applications

## Best Practices

### Configuration Management

- **Version Control**: Keep server configurations in version control
- **Documentation**: Document each server's purpose and tools
- **Testing**: Test server configurations before deployment
- **Monitoring**: Monitor server health and performance

### Security

- **Key Vault**: Always use Key Vault for secrets
- **Managed Identity**: Use managed identity for authentication
- **Least Privilege**: Grant minimum required permissions
- **Secret Rotation**: Regularly rotate secrets

### Performance

- **Auto-Start**: Only enable auto-start for frequently used servers
- **Timeouts**: Set appropriate timeouts for each server
- **Retries**: Configure retry logic for reliability
- **Monitoring**: Monitor response times and errors

## Troubleshooting

### Server Not Starting

1. Check the registry is uploaded correctly
2. Verify `enabled: true` and `auto_start: true`
3. Check Application Insights logs
4. Verify command and args are correct
5. Check environment variables and secrets

### Tool Execution Failing

1. Verify tool name matches the definition
2. Check input schema is correct
3. Verify server is running
4. Check server logs for errors
5. Verify API credentials are valid

### Secret Resolution Issues

1. Verify Key Vault URL is correct
2. Check managed identity has access
3. Verify secret exists in Key Vault
4. Check secret name matches (use hyphens, not underscores)

## Examples

See `example_mcp_server_registry.json` for complete examples of:
- GitHub MCP Server
- ERPNext MCP Server
- LinkedIn MCP Server
- Reddit MCP Server
- Excel MCP Server

## Integration with GenesisAgents

Agents in GenesisAgents can reference tools from MCP servers:

```json
{
  "agent_id": "cmo",
  "mcp_tools": [
    {
      "server_name": "linkedin",
      "tool_name": "post_content"
    }
  ]
}
```

The MCPServers app will handle the tool execution and return results to the agent.

## Support

For issues and questions, please refer to the main AOS documentation or create an issue in the repository.
