#!/bin/bash
# Setup Azure Infrastructure for RealmOfAgents and MCPServers
# This script creates all required Azure resources for the plug-and-play agent infrastructure

set -e

# Configuration
RESOURCE_GROUP_PREFIX="aos"
LOCATION="eastus"
ENVIRONMENT="${1:-dev}"  # dev, staging, or production

GENESIS_RG="${RESOURCE_GROUP_PREFIX}-realm-${ENVIRONMENT}"
MCP_RG="${RESOURCE_GROUP_PREFIX}-mcp-${ENVIRONMENT}"

echo "======================================================"
echo "  Azure Functions Infrastructure Setup"
echo "  Environment: ${ENVIRONMENT}"
echo "======================================================"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

echo "✓ Azure CLI found"

# Login check
echo "Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✓ Using subscription: ${SUBSCRIPTION_ID}"
echo ""

# Create RealmOfAgents Resources
echo "======================================================"
echo "  Creating RealmOfAgents Resources"
echo "======================================================"
echo ""

# Create resource group
echo "Creating resource group: ${GENESIS_RG}"
az group create --name ${GENESIS_RG} --location ${LOCATION}

# Create storage account
GENESIS_STORAGE="${RESOURCE_GROUP_PREFIX}realm${ENVIRONMENT}store"
echo "Creating storage account: ${GENESIS_STORAGE}"
az storage account create \
  --name ${GENESIS_STORAGE} \
  --resource-group ${GENESIS_RG} \
  --location ${LOCATION} \
  --sku Standard_LRS

# Get storage connection string
GENESIS_STORAGE_CONN=$(az storage account show-connection-string \
  --name ${GENESIS_STORAGE} \
  --resource-group ${GENESIS_RG} \
  --query connectionString -o tsv)

# Create storage containers
echo "Creating storage containers..."
az storage container create \
  --name agent-configs \
  --connection-string "${GENESIS_STORAGE_CONN}"

# Create Service Bus namespace
GENESIS_BUS="${RESOURCE_GROUP_PREFIX}-realm-bus-${ENVIRONMENT}"
echo "Creating Service Bus: ${GENESIS_BUS}"
az servicebus namespace create \
  --name ${GENESIS_BUS} \
  --resource-group ${GENESIS_RG} \
  --location ${LOCATION} \
  --sku Standard

# Get Service Bus connection string
GENESIS_BUS_CONN=$(az servicebus namespace authorization-rule keys list \
  --namespace-name ${GENESIS_BUS} \
  --resource-group ${GENESIS_RG} \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

# Create topics and subscriptions
echo "Creating Service Bus topics..."
az servicebus topic create \
  --name agent-events \
  --namespace-name ${GENESIS_BUS} \
  --resource-group ${GENESIS_RG}

az servicebus topic subscription create \
  --name realm-agents \
  --topic-name agent-events \
  --namespace-name ${GENESIS_BUS} \
  --resource-group ${GENESIS_RG}

az servicebus queue create \
  --name agent-commands \
  --namespace-name ${GENESIS_BUS} \
  --resource-group ${GENESIS_RG}

# Create Function App
GENESIS_FUNC="${RESOURCE_GROUP_PREFIX}-realm-agents-${ENVIRONMENT}"
echo "Creating Function App: ${GENESIS_FUNC}"
az functionapp create \
  --name ${GENESIS_FUNC} \
  --resource-group ${GENESIS_RG} \
  --consumption-plan-location ${LOCATION} \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account ${GENESIS_STORAGE} \
  --os-type Linux \
  --functions-version 4

echo "✓ RealmOfAgents resources created"
echo ""

# Create MCPServers Resources
echo "======================================================"
echo "  Creating MCPServers Resources"
echo "======================================================"
echo ""

# Create resource group
echo "Creating resource group: ${MCP_RG}"
az group create --name ${MCP_RG} --location ${LOCATION}

# Create storage account
MCP_STORAGE="${RESOURCE_GROUP_PREFIX}mcp${ENVIRONMENT}store"
echo "Creating storage account: ${MCP_STORAGE}"
az storage account create \
  --name ${MCP_STORAGE} \
  --resource-group ${MCP_RG} \
  --location ${LOCATION} \
  --sku Standard_LRS

# Get storage connection string
MCP_STORAGE_CONN=$(az storage account show-connection-string \
  --name ${MCP_STORAGE} \
  --resource-group ${MCP_RG} \
  --query connectionString -o tsv)

# Create storage containers
echo "Creating storage containers..."
az storage container create \
  --name mcp-registry \
  --connection-string "${MCP_STORAGE_CONN}"

# Create Key Vault
MCP_VAULT="${RESOURCE_GROUP_PREFIX}-mcp-vault-${ENVIRONMENT}"
echo "Creating Key Vault: ${MCP_VAULT}"
az keyvault create \
  --name ${MCP_VAULT} \
  --resource-group ${MCP_RG} \
  --location ${LOCATION}

VAULT_URL=$(az keyvault show --name ${MCP_VAULT} --resource-group ${MCP_RG} --query properties.vaultUri -o tsv)

# Create Service Bus namespace
MCP_BUS="${RESOURCE_GROUP_PREFIX}-mcp-bus-${ENVIRONMENT}"
echo "Creating Service Bus: ${MCP_BUS}"
az servicebus namespace create \
  --name ${MCP_BUS} \
  --resource-group ${MCP_RG} \
  --location ${LOCATION} \
  --sku Standard

# Get Service Bus connection string
MCP_BUS_CONN=$(az servicebus namespace authorization-rule keys list \
  --namespace-name ${MCP_BUS} \
  --resource-group ${MCP_RG} \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

# Create topics and subscriptions
echo "Creating Service Bus topics..."
az servicebus topic create \
  --name mcp-requests \
  --namespace-name ${MCP_BUS} \
  --resource-group ${MCP_RG}

az servicebus topic subscription create \
  --name mcp-servers \
  --topic-name mcp-requests \
  --namespace-name ${MCP_BUS} \
  --resource-group ${MCP_RG}

az servicebus topic create \
  --name mcp-responses \
  --namespace-name ${MCP_BUS} \
  --resource-group ${MCP_RG}

az servicebus queue create \
  --name mcp-server-commands \
  --namespace-name ${MCP_BUS} \
  --resource-group ${MCP_RG}

# Create Function App
MCP_FUNC="${RESOURCE_GROUP_PREFIX}-mcp-servers-${ENVIRONMENT}"
echo "Creating Function App: ${MCP_FUNC}"
az functionapp create \
  --name ${MCP_FUNC} \
  --resource-group ${MCP_RG} \
  --consumption-plan-location ${LOCATION} \
  --runtime python \
  --runtime-version 3.9 \
  --storage-account ${MCP_STORAGE} \
  --os-type Linux \
  --functions-version 4

# Enable managed identity
echo "Enabling managed identity..."
az functionapp identity assign \
  --name ${MCP_FUNC} \
  --resource-group ${MCP_RG}

# Grant Key Vault access
PRINCIPAL_ID=$(az functionapp identity show \
  --name ${MCP_FUNC} \
  --resource-group ${MCP_RG} \
  --query principalId -o tsv)

az keyvault set-policy \
  --name ${MCP_VAULT} \
  --object-id ${PRINCIPAL_ID} \
  --secret-permissions get list

echo "✓ MCPServers resources created"
echo ""

# Upload example configurations
echo "======================================================"
echo "  Uploading Example Configurations"
echo "======================================================"
echo ""

echo "Uploading agent registry..."
az storage blob upload \
  --container-name agent-configs \
  --name agent_registry.json \
  --file azure_functions/RealmOfAgents/example_agent_registry.json \
  --connection-string "${GENESIS_STORAGE_CONN}"

echo "Uploading MCP server registry..."
az storage blob upload \
  --container-name mcp-registry \
  --name mcp_server_registry.json \
  --file azure_functions/MCPServers/example_mcp_server_registry.json \
  --connection-string "${MCP_STORAGE_CONN}"

echo "✓ Example configurations uploaded"
echo ""

# Summary
echo "======================================================"
echo "  Setup Complete! 🎉"
echo "======================================================"
echo ""
echo "RealmOfAgents Resources:"
echo "  Resource Group: ${GENESIS_RG}"
echo "  Storage Account: ${GENESIS_STORAGE}"
echo "  Service Bus: ${GENESIS_BUS}"
echo "  Function App: ${GENESIS_FUNC}"
echo ""
echo "MCPServers Resources:"
echo "  Resource Group: ${MCP_RG}"
echo "  Storage Account: ${MCP_STORAGE}"
echo "  Key Vault: ${MCP_VAULT}"
echo "  Service Bus: ${MCP_BUS}"
echo "  Function App: ${MCP_FUNC}"
echo ""
echo "Next Steps:"
echo "  1. Deploy RealmOfAgents:"
echo "     cd azure_functions/RealmOfAgents"
echo "     func azure functionapp publish ${GENESIS_FUNC}"
echo ""
echo "  2. Deploy MCPServers:"
echo "     cd azure_functions/MCPServers"
echo "     func azure functionapp publish ${MCP_FUNC}"
echo ""
echo "  3. Add secrets to Key Vault (for MCP servers):"
echo "     az keyvault secret set --vault-name ${MCP_VAULT} --name GITHUB-TOKEN --value '<your-token>'"
echo ""
echo "Connection Strings (save these):"
echo "  GENESIS_STORAGE_CONN='${GENESIS_STORAGE_CONN}'"
echo "  GENESIS_BUS_CONN='${GENESIS_BUS_CONN}'"
echo "  MCP_STORAGE_CONN='${MCP_STORAGE_CONN}'"
echo "  MCP_BUS_CONN='${MCP_BUS_CONN}'"
echo "  VAULT_URL='${VAULT_URL}'"
echo ""
