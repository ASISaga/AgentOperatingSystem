# Production Deployment Guide

## Azure Resources Required

AOS runs on Microsoft Azure and automatically provisions:

- **Compute:** Azure Functions / Container Instances
- **Storage:** Blob Storage, Table Storage, Queue Storage
- **Database:** Cosmos DB
- **Messaging:** Service Bus (Topics, Queues, Subscriptions)
- **ML:** Azure Machine Learning Workspace
- **Security:** Key Vault, Azure AD B2C
- **Monitoring:** Application Insights, Log Analytics

## Deployment via Infrastructure as Code

```bash
# Login to Azure
az login

# Deploy AOS infrastructure
cd /path/to/AgentOperatingSystem
az deployment group create \
  --resource-group aos-production \
  --template-file azure/main.bicep \
  --parameters azure/parameters.json

# Configure environment
export AOS_SUBSCRIPTION_ID="your-sub-id"
export AOS_RESOURCE_GROUP="aos-production"

# Initialize AOS
python -m AgentOperatingSystem.cli init --environment production
```

## Environment Configuration

Set the following environment variables or configure in Azure Key Vault:

```bash
# Azure Subscription
export AOS_SUBSCRIPTION_ID="your-subscription-id"
export AOS_RESOURCE_GROUP="aos-resources"

# Storage
export AOS_STORAGE_ACCOUNT="your-storage-account"
export AOS_STORAGE_KEY="your-storage-key"

# Service Bus
export AOS_SERVICE_BUS_CONNECTION="your-service-bus-connection-string"

# Azure ML
export AOS_ML_WORKSPACE="your-ml-workspace"

# Authentication
export AOS_AZURE_B2C_TENANT="your-b2c-tenant"
export AOS_AZURE_B2C_CLIENT_ID="your-client-id"
```

## Deployment Checklist

- [ ] Azure subscription and resource group created
- [ ] Infrastructure deployed via Bicep/ARM templates
- [ ] Environment variables configured
- [ ] Key Vault secrets set up
- [ ] Storage accounts provisioned
- [ ] Service Bus configured
- [ ] Azure ML workspace created
- [ ] Application Insights enabled
- [ ] Agents registered and configured
- [ ] Monitoring and alerts configured

## Production Best Practices

### Security
- Use Azure Key Vault for all secrets
- Enable managed identities
- Configure network security groups
- Enable Azure AD B2C for authentication
- Use RBAC for access control

### Monitoring
- Enable Application Insights
- Configure Log Analytics workspace
- Set up alerts for critical metrics
- Monitor agent health and performance

### Reliability
- Configure auto-scaling
- Set up redundancy and failover
- Enable circuit breakers
- Implement retry logic
- Test disaster recovery procedures

### Performance
- Monitor and optimize costs
- Use appropriate service tiers
- Implement caching strategies
- Optimize ML inference

## See Also

- [Installation Guide](installation.md) - Installation instructions
- [Configuration Guide](../configuration.md) - Configuration options
- [Azure Functions](azure-functions.md) - Azure Functions infrastructure
- [Quick Start](quickstart.md) - Quick start guide
