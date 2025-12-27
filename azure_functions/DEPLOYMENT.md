# Deployment Guide - GenesisAgents & MCPServers

This guide walks you through deploying the plug-and-play Azure Functions infrastructure for AgentOperatingSystem.

## Overview

The deployment consists of two Azure Functions applications:
- **GenesisAgents**: Configuration-driven agent deployment
- **MCPServers**: Configuration-driven MCP server deployment

## Prerequisites

Before you begin, ensure you have:

- ✅ Azure subscription with appropriate permissions
- ✅ Azure CLI installed and configured
- ✅ Azure Functions Core Tools v4.x
- ✅ Python 3.9+ installed
- ✅ Git repository cloned

### Install Prerequisites

```bash
# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Verify installations
az --version
func --version
python --version
```

## Quick Start (Automated)

The easiest way to deploy is using the automated setup script:

```bash
# Navigate to azure_functions directory
cd azure_functions

# Run the setup script (creates all Azure resources)
./setup_infrastructure.sh dev

# The script creates:
# - Resource groups
# - Storage accounts with containers
# - Service Bus namespaces with topics/queues
# - Key Vault (for MCPServers)
# - Function Apps
# - Uploads example configurations
```

The script accepts an environment parameter: `dev`, `staging`, or `production`.

### What the Script Creates

**For GenesisAgents:**
- Resource Group: `aos-realm-{env}`
- Storage Account: `aosgenesis{env}store`
- Service Bus: `aos-realm-bus-{env}`
  - Topic: `agent-events` (subscription: `realm-agents`)
  - Queue: `agent-commands`
- Function App: `aos-realm-agents-{env}`

**For MCPServers:**
- Resource Group: `aos-mcp-{env}`
- Storage Account: `aosmcp{env}store`
- Service Bus: `aos-mcp-bus-{env}`
  - Topic: `mcp-requests` (subscription: `mcp-servers`)
  - Topic: `mcp-responses`
  - Queue: `mcp-server-commands`
- Key Vault: `aos-mcp-vault-{env}`
- Function App: `aos-mcp-servers-{env}`

## Manual Deployment (Step-by-Step)

If you prefer manual control, follow these detailed steps:

### Step 1: Login to Azure

```bash
az login
az account set --subscription "<your-subscription-id>"
```

### Step 2: Create GenesisAgents Infrastructure

```bash
# Variables
RESOURCE_GROUP="aos-realm-dev"
LOCATION="eastus"
STORAGE_ACCOUNT="aosgenesisdevstore"
SERVICE_BUS="aos-realm-bus-dev"
FUNCTION_APP="aos-realm-agents-dev"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Get storage connection string
STORAGE_CONN=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query connectionString -o tsv)

# Create container for agent configurations
az storage container create \
  --name agent-configs \
  --connection-string "$STORAGE_CONN"

# Create Service Bus namespace
az servicebus namespace create \
  --name $SERVICE_BUS \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard

# Create Service Bus topic and subscription
az servicebus topic create \
  --name agent-events \
  --namespace-name $SERVICE_BUS \
  --resource-group $RESOURCE_GROUP

az servicebus topic subscription create \
  --name realm-agents \
  --topic-name agent-events \
  --namespace-name $SERVICE_BUS \
  --resource-group $RESOURCE_GROUP

# Create Service Bus queue
az servicebus queue create \
  --name agent-commands \
  --namespace-name $SERVICE_BUS \
  --resource-group $RESOURCE_GROUP

# Get Service Bus connection string
BUS_CONN=$(az servicebus namespace authorization-rule keys list \
  --namespace-name $SERVICE_BUS \
  --resource-group $RESOURCE_GROUP \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

# Create Function App
az functionapp create \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux \
  --functions-version 4

# Upload agent registry
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file GenesisAgents/example_agent_registry.json \
  --connection-string "$STORAGE_CONN"
```

### Step 3: Create MCPServers Infrastructure

```bash
# Variables
MCP_RESOURCE_GROUP="aos-mcp-dev"
MCP_STORAGE="aosmcpdevstore"
MCP_SERVICE_BUS="aos-mcp-bus-dev"
MCP_VAULT="aos-mcp-vault-dev"
MCP_FUNCTION_APP="aos-mcp-servers-dev"

# Create resource group
az group create --name $MCP_RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $MCP_STORAGE \
  --resource-group $MCP_RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Get storage connection string
MCP_STORAGE_CONN=$(az storage account show-connection-string \
  --name $MCP_STORAGE \
  --resource-group $MCP_RESOURCE_GROUP \
  --query connectionString -o tsv)

# Create container
az storage container create \
  --name mcp-registry \
  --connection-string "$MCP_STORAGE_CONN"

# Create Key Vault
az keyvault create \
  --name $MCP_VAULT \
  --resource-group $MCP_RESOURCE_GROUP \
  --location $LOCATION

VAULT_URL=$(az keyvault show --name $MCP_VAULT --resource-group $MCP_RESOURCE_GROUP --query properties.vaultUri -o tsv)

# Create Service Bus namespace
az servicebus namespace create \
  --name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard

# Create topics and queues
az servicebus topic create \
  --name mcp-requests \
  --namespace-name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP

az servicebus topic subscription create \
  --name mcp-servers \
  --topic-name mcp-requests \
  --namespace-name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP

az servicebus topic create \
  --name mcp-responses \
  --namespace-name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP

az servicebus queue create \
  --name mcp-server-commands \
  --namespace-name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP

# Get Service Bus connection string
MCP_BUS_CONN=$(az servicebus namespace authorization-rule keys list \
  --namespace-name $MCP_SERVICE_BUS \
  --resource-group $MCP_RESOURCE_GROUP \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

# Create Function App
az functionapp create \
  --name $MCP_FUNCTION_APP \
  --resource-group $MCP_RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account $MCP_STORAGE \
  --os-type Linux \
  --functions-version 4

# Enable managed identity
az functionapp identity assign \
  --name $MCP_FUNCTION_APP \
  --resource-group $MCP_RESOURCE_GROUP

# Grant Key Vault access
PRINCIPAL_ID=$(az functionapp identity show \
  --name $MCP_FUNCTION_APP \
  --resource-group $MCP_RESOURCE_GROUP \
  --query principalId -o tsv)

az keyvault set-policy \
  --name $MCP_VAULT \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list

# Upload MCP server registry
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file MCPServers/example_mcp_server_registry.json \
  --connection-string "$MCP_STORAGE_CONN"
```

### Step 4: Configure Application Settings

```bash
# GenesisAgents settings
az functionapp config appsettings set \
  --name $FUNCTION_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_SERVICE_BUS_CONNECTION_STRING="$BUS_CONN" \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN" \
    AGENT_CONFIG_BLOB_CONTAINER="agent-configs"

# MCPServers settings
az functionapp config appsettings set \
  --name $MCP_FUNCTION_APP \
  --resource-group $MCP_RESOURCE_GROUP \
  --settings \
    AZURE_SERVICE_BUS_CONNECTION_STRING="$MCP_BUS_CONN" \
    AZURE_STORAGE_CONNECTION_STRING="$MCP_STORAGE_CONN" \
    AZURE_KEY_VAULT_URL="$VAULT_URL" \
    MCP_REGISTRY_BLOB_CONTAINER="mcp-registry"
```

### Step 5: Add Secrets to Key Vault

Add API keys and tokens for MCP servers:

```bash
# GitHub token
az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name GITHUB-TOKEN \
  --value "<your-github-personal-access-token>"

# ERPNext credentials
az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name ERPNEXT-API-KEY \
  --value "<your-erpnext-api-key>"

az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name ERPNEXT-API-SECRET \
  --value "<your-erpnext-api-secret>"

az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name ERPNEXT-BASE-URL \
  --value "<your-erpnext-base-url>"

# LinkedIn token
az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name LINKEDIN-ACCESS-TOKEN \
  --value "<your-linkedin-access-token>"

# Reddit credentials
az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name REDDIT-CLIENT-ID \
  --value "<your-reddit-client-id>"

az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name REDDIT-CLIENT-SECRET \
  --value "<your-reddit-client-secret>"

az keyvault secret set \
  --vault-name $MCP_VAULT \
  --name REDDIT-USER-AGENT \
  --value "AgentOS/1.0"
```

### Step 6: Deploy Function Apps

```bash
# Deploy GenesisAgents
cd GenesisAgents
func azure functionapp publish $FUNCTION_APP

# Deploy MCPServers
cd ../MCPServers
func azure functionapp publish $MCP_FUNCTION_APP
```

## Verification

### Test GenesisAgents

```bash
# Health check
GENESIS_URL="https://${FUNCTION_APP}.azurewebsites.net"
curl "${GENESIS_URL}/api/health"

# Expected response:
# {"status": "healthy", "active_agents": 4, "agent_ids": ["ceo", "cfo", "cmo", "coo"]}
```

### Test MCPServers

```bash
# Health check
MCP_URL="https://${MCP_FUNCTION_APP}.azurewebsites.net"
curl "${MCP_URL}/api/health"

# Expected response:
# {"status": "healthy", "active_servers": 5, "server_ids": ["github", "erpnext", "linkedin", "reddit", "excel"]}

# List servers
curl "${MCP_URL}/api/servers"
```

## Monitoring

### View Logs

```bash
# GenesisAgents logs
az functionapp log tail --name $FUNCTION_APP --resource-group $RESOURCE_GROUP

# MCPServers logs
az functionapp log tail --name $MCP_FUNCTION_APP --resource-group $MCP_RESOURCE_GROUP
```

### Application Insights

Both function apps automatically create Application Insights instances. View metrics in the Azure Portal:

1. Navigate to your Function App
2. Click on "Application Insights"
3. View requests, failures, performance metrics

## Updating Configurations

### Update Agent Registry

```bash
# Edit agent configuration
vi agent_registry.json

# Upload to Blob Storage
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file agent_registry.json \
  --connection-string "$STORAGE_CONN" \
  --overwrite

# Trigger reload (via Service Bus or restart function app)
az functionapp restart --name $FUNCTION_APP --resource-group $RESOURCE_GROUP
```

### Update MCP Server Registry

```bash
# Edit MCP server configuration
vi mcp_server_registry.json

# Upload to Blob Storage
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file mcp_server_registry.json \
  --connection-string "$MCP_STORAGE_CONN" \
  --overwrite

# Trigger reload
az functionapp restart --name $MCP_FUNCTION_APP --resource-group $MCP_RESOURCE_GROUP
```

## Troubleshooting

### Function App Not Starting

1. Check Application Insights for errors
2. Verify connection strings in app settings
3. Check Python version (must be 3.9+)
4. Verify dependencies in requirements.txt

### Agents Not Loading

1. Verify agent_registry.json is in Blob Storage
2. Check the registry JSON is valid (use tests)
3. Review function logs for errors
4. Verify Service Bus connection

### MCP Servers Not Working

1. Verify secrets exist in Key Vault
2. Check managed identity has Key Vault permissions
3. Verify MCP server commands are correct
4. Check server logs for startup errors

## Cost Optimization

- Use **Consumption Plan** for development/testing
- Consider **Premium Plan** for production (better performance, VNet integration)
- Enable **Application Insights sampling** to reduce costs
- Use **Azure Monitor** alerts to track spending

## Security Best Practices

1. **Secrets**: Never commit secrets - use Key Vault
2. **RBAC**: Use role-based access control
3. **Managed Identity**: Use for Azure resource access
4. **VNet**: Consider VNet integration for production
5. **Application Insights**: Review security logs regularly

## Next Steps

1. **Customize Agents**: Edit agent_registry.json for your use case
2. **Add MCP Servers**: Add new servers to mcp_server_registry.json
3. **Training Data**: Upload LoRA training data to Blob Storage
4. **Monitoring**: Set up alerts and dashboards
5. **CI/CD**: Integrate with GitHub Actions or Azure DevOps

## Support

For issues:
- Check [GenesisAgents README](GenesisAgents/README.md)
- Check [MCPServers README](MCPServers/README.md)
- Review Application Insights logs
- Create an issue in the repository
