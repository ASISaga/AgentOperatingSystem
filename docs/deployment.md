# Production Deployment Guide

## Overview

This guide covers deploying the Agent Operating System (AOS) to production on Microsoft Azure. AOS is designed for cloud-native deployment with enterprise-grade reliability, security, and scalability.

---

## Prerequisites

### Required Tools
- Azure CLI (`az`) version 2.40 or later
- Python 3.9 or later
- Git
- Terraform or ARM templates (for IaC)

### Azure Subscription Requirements
- Active Azure subscription
- Contributor or Owner role on target resource group
- Sufficient quota for:
  - Azure Functions (Premium or App Service Plan)
  - Azure Service Bus (Standard or Premium tier)
  - Azure Storage (Standard or Premium)
  - Azure Key Vault

---

## Azure Resources Required

### Core Infrastructure
1. **Azure Functions** - Serverless compute for agent hosting
   - Recommended: Premium plan (EP1 or higher) for production
   - Supports VNet integration and private endpoints
   
2. **Azure Service Bus** - Message bus for agent communication
   - Recommended: Standard tier minimum (Premium for high throughput)
   - Topics and subscriptions for event distribution
   
3. **Azure Storage Account** - Persistent storage layer
   - Blob storage: Training data, model artifacts, large payloads
   - Table storage: Conversations, messages, agent state
   - Queue storage: Task queues, async processing
   
4. **Azure Key Vault** - Secrets and configuration management
   - API keys, connection strings, certificates
   - Encryption keys for data at rest
   
5. **Azure Monitor** - Observability and diagnostics
   - Application Insights for distributed tracing
   - Log Analytics workspace for centralized logging

### Optional Resources
6. **Azure Machine Learning** - ML model training and deployment
   - For LoRA adapter training
   - Model registry and experiment tracking
   
7. **Azure Container Registry** - Custom container images
   - For Docker-based deployments
   
8. **Azure Virtual Network** - Network isolation
   - Private endpoints for enhanced security
   - Network security groups for traffic control

---

## Deployment Steps

### 1. Setup Azure CLI

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group
az group create \
  --name aos-rg \
  --location westus2
```

### 2. Deploy Infrastructure

#### Option A: Using Azure CLI

```bash
# Create Storage Account
az storage account create \
  --name aosstorageacct \
  --resource-group aos-rg \
  --location westus2 \
  --sku Standard_LRS

# Create Service Bus Namespace
az servicebus namespace create \
  --name aos-servicebus \
  --resource-group aos-rg \
  --location westus2 \
  --sku Standard

# Create Key Vault
az keyvault create \
  --name aos-keyvault \
  --resource-group aos-rg \
  --location westus2

# Create Application Insights
az monitor app-insights component create \
  --app aos-insights \
  --resource-group aos-rg \
  --location westus2

# Create Function App
az functionapp create \
  --name aos-functions \
  --resource-group aos-rg \
  --storage-account aosstorageacct \
  --consumption-plan-location westus2 \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4
```

#### Option B: Using ARM Template

```bash
# Deploy using ARM template
az deployment group create \
  --resource-group aos-rg \
  --template-file infrastructure/azuredeploy.json \
  --parameters @infrastructure/parameters.json
```

#### Option C: Using Terraform

```bash
# Initialize Terraform
cd infrastructure/terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply deployment
terraform apply tfplan
```

### 3. Configure Application Settings

```bash
# Get connection strings
STORAGE_CONN=$(az storage account show-connection-string \
  --name aosstorageacct \
  --resource-group aos-rg \
  --query connectionString -o tsv)

SERVICEBUS_CONN=$(az servicebus namespace authorization-rule keys list \
  --resource-group aos-rg \
  --namespace-name aos-servicebus \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString -o tsv)

# Set Function App settings
az functionapp config appsettings set \
  --name aos-functions \
  --resource-group aos-rg \
  --settings \
    AzureWebJobsStorage="$STORAGE_CONN" \
    AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN" \
    AZURE_SERVICEBUS_CONNECTION_STRING="$SERVICEBUS_CONN" \
    APPLICATIONINSIGHTS_CONNECTION_STRING="..." \
    PYTHON_VERSION="3.9"
```

### 4. Deploy Application Code

```bash
# Build and package application
cd /path/to/AgentOperatingSystem
pip install -r requirements.txt --target .python_packages/lib/site-packages

# Create deployment package
zip -r aos-deploy.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"

# Deploy to Azure Functions
az functionapp deployment source config-zip \
  --name aos-functions \
  --resource-group aos-rg \
  --src aos-deploy.zip
```

### 5. Initialize AOS

```python
# Run initialization script
from AgentOperatingSystem import initialize_aos

await initialize_aos(
    storage_connection_string=STORAGE_CONN,
    servicebus_connection_string=SERVICEBUS_CONN,
    keyvault_url="https://aos-keyvault.vault.azure.net/"
)
```

---

## Configuration

### Environment Variables

Create a `.env` file or configure Azure Function App settings:

```bash
# Required
AZURE_STORAGE_CONNECTION_STRING=<storage-connection-string>
AZURE_SERVICEBUS_CONNECTION_STRING=<servicebus-connection-string>
APPLICATIONINSIGHTS_CONNECTION_STRING=<app-insights-connection-string>

# Optional
AZURE_KEYVAULT_URL=https://aos-keyvault.vault.azure.net/
AZURE_ML_WORKSPACE=aos-ml-workspace
ENABLE_SELF_LEARNING=true
LOG_LEVEL=INFO
```

### Configuration File

Create `config/production_config.json`:

```json
{
  "orchestrator": {
    "type": "production",
    "version": "3.0.0"
  },
  "azure": {
    "storage_connection": "${AZURE_STORAGE_CONNECTION_STRING}",
    "servicebus_connection": "${AZURE_SERVICEBUS_CONNECTION_STRING}",
    "keyvault_url": "${AZURE_KEYVAULT_URL}"
  },
  "agents": {
    "max_concurrent": 100,
    "default_timeout": 300,
    "health_check_interval": 60
  },
  "reliability": {
    "retry_attempts": 3,
    "circuit_breaker_threshold": 5,
    "backoff_multiplier": 2
  },
  "observability": {
    "enable_tracing": true,
    "enable_metrics": true,
    "sampling_rate": 0.1
  }
}
```

---

## Security Hardening

### 1. Enable Managed Identity

```bash
# Enable system-assigned managed identity
az functionapp identity assign \
  --name aos-functions \
  --resource-group aos-rg

# Grant Key Vault access
PRINCIPAL_ID=$(az functionapp identity show \
  --name aos-functions \
  --resource-group aos-rg \
  --query principalId -o tsv)

az keyvault set-policy \
  --name aos-keyvault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

### 2. Configure Private Endpoints

```bash
# Create VNet and subnet
az network vnet create \
  --name aos-vnet \
  --resource-group aos-rg \
  --address-prefix 10.0.0.0/16 \
  --subnet-name aos-subnet \
  --subnet-prefix 10.0.1.0/24

# Create private endpoint for Storage
STORAGE_RESOURCE_ID=$(az storage account show \
  --name aosstorageacct \
  --resource-group aos-rg \
  --query id -o tsv)

az network private-endpoint create \
  --name aos-storage-pe \
  --resource-group aos-rg \
  --vnet-name aos-vnet \
  --subnet aos-subnet \
  --private-connection-resource-id "$STORAGE_RESOURCE_ID" \
  --group-id blob \
  --connection-name aos-storage-connection
```

### 3. Configure Network Security

```bash
# Enable firewall on Storage Account
az storage account update \
  --name aosstorageacct \
  --resource-group aos-rg \
  --default-action Deny

# Add allowed IP ranges
az storage account network-rule add \
  --account-name aosstorageacct \
  --resource-group aos-rg \
  --ip-address "YOUR_IP_RANGE"
```

---

## Scaling Configuration

### Horizontal Scaling

```bash
# Configure autoscale for Function App
PLAN_RESOURCE_ID=$(az functionapp plan show \
  --name aos-plan \
  --resource-group aos-rg \
  --query id -o tsv)

az monitor autoscale create \
  --resource-group aos-rg \
  --resource "$PLAN_RESOURCE_ID" \
  --resource-type Microsoft.Web/serverfarms \
  --name aos-autoscale \
  --min-count 1 \
  --max-count 10 \
  --count 2

# Add scale rule based on CPU
az monitor autoscale rule create \
  --resource-group aos-rg \
  --autoscale-name aos-autoscale \
  --condition "Percentage CPU > 75 avg 5m" \
  --scale out 1
```

### Service Bus Scaling

```bash
# Upgrade to Premium tier for better throughput
az servicebus namespace update \
  --name aos-servicebus \
  --resource-group aos-rg \
  --sku Premium \
  --capacity 1
```

---

## Monitoring and Alerts

### Configure Alerts

```bash
# Create alert for high error rate
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group aos-rg \
  --scopes "/subscriptions/.../aos-functions" \
  --condition "count exceptions > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action email ops@example.com
```

### Application Insights Queries

```kusto
// View agent execution traces
traces
| where customDimensions.category == "agent_execution"
| project timestamp, message, agent_id=customDimensions.agent_id

// Monitor agent performance
requests
| where name startswith "agent_"
| summarize avg(duration), percentile(duration, 95) by name
| order by avg_duration desc
```

---

## Backup and Disaster Recovery

### Storage Backup

```bash
# Enable soft delete for blobs
az storage account blob-service-properties update \
  --account-name aosstorageacct \
  --enable-delete-retention true \
  --delete-retention-days 30

# Configure geo-redundancy
az storage account update \
  --name aosstorageacct \
  --resource-group aos-rg \
  --sku Standard_GRS
```

### Export Configuration

```bash
# Export ARM template for disaster recovery
az group export \
  --name aos-rg \
  --output-format json > aos-backup-template.json
```

---

## Cost Optimization

### 1. Right-size Resources
- Use consumption plan for variable workloads
- Scale down non-production environments
- Use reserved instances for predictable workloads

### 2. Storage Tiering
```bash
# Configure lifecycle management
az storage account management-policy create \
  --account-name aosstorageacct \
  --resource-group aos-rg \
  --policy @lifecycle-policy.json
```

### 3. Enable Caching
- Configure Redis cache for frequently accessed data
- Enable Application Insights sampling to reduce costs

---

## Troubleshooting

### Common Issues

**Issue: Function timeouts**
```bash
# Increase function timeout (max 10 minutes on consumption plan)
az functionapp config appsettings set \
  --name aos-functions \
  --resource-group aos-rg \
  --settings "functionTimeout=00:10:00"
```

**Issue: Storage connection failures**
```bash
# Verify connection string
az functionapp config appsettings list \
  --name aos-functions \
  --resource-group aos-rg \
  --query "[?name=='AzureWebJobsStorage'].value"
```

**Issue: Service Bus quota exceeded**
```bash
# Check quota usage
az servicebus namespace show \
  --name aos-servicebus \
  --resource-group aos-rg \
  --query "sku"
```

---

## Production Checklist

- [ ] All Azure resources deployed and configured
- [ ] Managed identities enabled for secure access
- [ ] Private endpoints configured for sensitive resources
- [ ] Application settings and secrets in Key Vault
- [ ] Monitoring and alerts configured
- [ ] Backup and disaster recovery plan in place
- [ ] Autoscaling rules configured
- [ ] Security hardening applied
- [ ] Cost optimization measures implemented
- [ ] Documentation updated with deployment details

---

## Next Steps

- **[Performance Tuning](performance.md)** - Optimize for production workloads
- **[Monitoring Guide](monitoring.md)** - Set up comprehensive monitoring
- **[Security Best Practices](../ARCHITECTURE.md#security-architecture)** - Enhance security posture
- **[Scaling Guide](scaling.md)** - Handle enterprise-scale deployments

---

**Need Help?** Check our [troubleshooting guide](troubleshooting.md) or [open an issue](https://github.com/ASISaga/AgentOperatingSystem/issues).
