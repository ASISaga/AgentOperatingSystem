# Bicep Modules

This directory contains production-grade, reusable Bicep modules for deploying Agent Operating System (AOS) infrastructure components.

## 📁 Module Inventory

### Core Infrastructure Modules

| Module | Description | Resources | Dependencies |
|--------|-------------|-----------|--------------|
| **storage.bicep** | Storage account with blob, table, and queue services | Storage Account, Blob Services, Table Services, Queue Services, Container | None |
| **monitoring.bicep** | Observability infrastructure | Log Analytics Workspace, Application Insights | None |
| **servicebus.bicep** | Messaging infrastructure | Service Bus Namespace, Queues, Topics, Subscriptions | None |
| **keyvault.bicep** | Secrets management | Key Vault | None |
| **identity.bicep** | Managed identity for secure authentication | User-assigned Managed Identity | None |

### Application Modules

| Module | Description | Resources | Dependencies |
|--------|-------------|-----------|--------------|
| **compute.bicep** | Function Apps platform | App Service Plan, 3× Function Apps (main, MCP, realm) | Storage, Service Bus, Key Vault, Monitoring, Identity |
| **machinelearning.bicep** | ML training infrastructure | Azure ML Workspace, Container Registry | Storage, Key Vault, Monitoring (optional) |

### Security Modules

| Module | Description | Resources | Dependencies |
|--------|-------------|-----------|--------------|
| **rbac.bicep** | Role assignments for secure access | 6× Role Assignments (Key Vault, Storage, Service Bus access) | Key Vault, Storage, Service Bus, Compute |

## 🎯 Usage

### Individual Module Deployment

Each module can be deployed independently for testing or custom scenarios:

```bash
# Deploy storage module
az deployment group create \
  --resource-group "rg-test" \
  --template-file "modules/storage.bicep" \
  --parameters \
    storageAccountName="teststorage123" \
    location="eastus" \
    storageSku="Standard_LRS" \
    tags='{"Environment":"test"}'

# Deploy monitoring module
az deployment group create \
  --resource-group "rg-test" \
  --template-file "modules/monitoring.bicep" \
  --parameters \
    logAnalyticsName="test-la" \
    appInsightsName="test-ai" \
    location="eastus" \
    enableAppInsights=true
```

### Orchestrated Deployment

Use the main-modular.bicep to deploy all modules together:

```bash
# Using bicepparam file (recommended)
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "../main-modular.bicep" \
  --parameters "../parameters/dev.bicepparam"

# Using inline parameters
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "../main-modular.bicep" \
  --parameters location=eastus environment=dev
```

## 📖 Module Documentation

### storage.bicep

**Purpose:** Deploys Azure Storage Account with blob, table, and queue services.

**Parameters:**
- `storageAccountName` (string, required): Globally unique storage account name (3-24 chars, lowercase alphanumeric)
- `location` (string, required): Azure region
- `storageSku` (string): SKU - Standard_LRS | Standard_GRS | Standard_RAGRS | Premium_LRS (default: Standard_LRS)
- `tags` (object): Resource tags
- `blobContainerName` (string): Name of blob container (default: "aos-data")

**Outputs:**
- `storageAccountId`: Resource ID
- `storageAccountName`: Account name
- `storageAccountEndpoints`: Primary endpoints object
- `storageConnectionString`: Connection string (contains secrets)
- `blobContainerName`: Container name

**Features:**
- Hot access tier
- HTTPS-only traffic
- TLS 1.2 minimum
- Blob and container soft delete (7 days)
- Private blob access

### monitoring.bicep

**Purpose:** Deploys observability infrastructure with Log Analytics and Application Insights.

**Parameters:**
- `logAnalyticsName` (string, required): Log Analytics workspace name
- `appInsightsName` (string, required): Application Insights name
- `location` (string, required): Azure region
- `tags` (object): Resource tags
- `enableAppInsights` (bool): Enable deployment (default: true)
- `retentionInDays` (int): Data retention period (default: 30)

**Outputs:**
- `logAnalyticsWorkspaceId`: Workspace resource ID
- `logAnalyticsWorkspaceName`: Workspace name
- `appInsightsId`: App Insights resource ID
- `appInsightsName`: App Insights name
- `appInsightsInstrumentationKey`: Instrumentation key
- `appInsightsConnectionString`: Connection string

**Features:**
- PerGB2018 pricing tier
- Integrated Log Analytics workspace
- Web application type

### servicebus.bicep

**Purpose:** Deploys Azure Service Bus with queues and topics.

**Parameters:**
- `serviceBusNamespaceName` (string, required): Namespace name
- `location` (string, required): Azure region
- `serviceBusSku` (string): SKU - Basic | Standard | Premium (default: Standard)
- `tags` (object): Resource tags
- `queueNames` (array): Queue names to create
- `topicNames` (array): Topic names to create

**Outputs:**
- `serviceBusNamespaceId`: Namespace resource ID
- `serviceBusNamespaceName`: Namespace name
- `serviceBusConnectionString`: Connection string (contains secrets)
- `serviceBusEndpoint`: Service Bus endpoint

**Features:**
- TLS 1.2 minimum
- 5-minute lock duration
- 14-day message TTL
- Dead-letter queues enabled
- Default subscriptions for topics

### keyvault.bicep

**Purpose:** Deploys Azure Key Vault with RBAC authorization.

**Parameters:**
- `keyVaultName` (string, required): Key Vault name (3-24 chars, globally unique)
- `location` (string, required): Azure region
- `tags` (object): Resource tags
- `softDeleteRetentionInDays` (int): Soft delete retention (7-90 days, default: 7)

**Outputs:**
- `keyVaultId`: Resource ID
- `keyVaultName`: Vault name
- `keyVaultUri`: Vault URI

**Features:**
- RBAC authorization (not access policies)
- Soft delete enabled
- Template deployment enabled
- Standard SKU

### identity.bicep

**Purpose:** Deploys user-assigned managed identity for cross-resource access.

**Parameters:**
- `identityName` (string, required): Identity name
- `location` (string, required): Azure region
- `tags` (object): Resource tags

**Outputs:**
- `identityId`: Resource ID
- `identityName`: Identity name
- `identityPrincipalId`: Principal ID (for RBAC)
- `identityClientId`: Client ID

### compute.bicep

**Purpose:** Deploys App Service Plan and three Function Apps (main, MCP server, realm).

**Parameters:**
- `appServicePlanName` (string, required): App Service Plan name
- `functionAppName` (string, required): Main Function App name
- `mcpServerFunctionAppName` (string, required): MCP Server Function App name
- `realmFunctionAppName` (string, required): Realm Function App name
- `location` (string, required): Azure region
- `tags` (object): Resource tags
- `functionAppSku` (string, required): SKU - Y1 | EP1 | EP2 | EP3
- `userAssignedIdentityId` (string, required): Managed identity resource ID
- `storageAccountName` (string, required): Storage account name
- `storageConnectionString` (string, secure, required): Storage connection string
- `serviceBusConnectionString` (string, secure, required): Service Bus connection string
- `keyVaultUri` (string, required): Key Vault URI
- `appInsightsConnectionString` (string, secure): App Insights connection string
- `environment` (string, required): Environment name
- `enableB2C` (bool): Enable B2C auth
- `b2cTenantName`, `b2cPolicyName`, `b2cClientId`, `b2cClientSecret`: B2C configuration

**Outputs:**
- `appServicePlanId`: App Service Plan ID
- `functionAppId`, `functionAppName`, `functionAppUrl`, `functionAppPrincipalId`: Main Function App details
- `mcpServerFunctionAppId`, `mcpServerFunctionAppName`, `mcpServerFunctionAppUrl`, `mcpServerFunctionAppPrincipalId`: MCP Server details
- `realmFunctionAppId`, `realmFunctionAppName`, `realmFunctionAppUrl`, `realmFunctionAppPrincipalId`: Realm Function App details

**Features:**
- Python 3.11 runtime
- Linux-based
- System-assigned + user-assigned identity
- HTTPS only
- FTPS disabled
- TLS 1.2 minimum

### machinelearning.bicep

**Purpose:** Deploys Azure ML Workspace and Container Registry for ML model training.

**Parameters:**
- `azureMLWorkspaceName` (string, required): ML Workspace name
- `containerRegistryName` (string, required): Container Registry name (alphanumeric)
- `location` (string, required): Azure region
- `tags` (object): Resource tags
- `enableAzureML` (bool): Enable deployment (default: true)
- `storageAccountId` (string, required): Storage account resource ID
- `keyVaultId` (string, required): Key Vault resource ID
- `appInsightsId` (string): App Insights resource ID (optional)

**Outputs:**
- `containerRegistryId`: Container Registry resource ID
- `containerRegistryName`: Registry name
- `azureMLWorkspaceId`: ML Workspace resource ID
- `azureMLWorkspaceName`: Workspace name

**Features:**
- Standard tier Container Registry
- Admin user enabled
- System-assigned identity for ML Workspace
- Public network access enabled

### rbac.bicep

**Purpose:** Deploys role assignments for Function Apps to securely access Key Vault, Storage, and Service Bus.

**Parameters:**
- `keyVaultName` (string, required): Key Vault name
- `storageAccountName` (string, required): Storage account name
- `serviceBusNamespaceName` (string, required): Service Bus namespace name
- `functionAppPrincipalId` (string, required): Main Function App principal ID
- `mcpServerFunctionAppPrincipalId` (string, required): MCP Server principal ID
- `realmFunctionAppPrincipalId` (string, required): Realm Function App principal ID

**Outputs:**
- `functionAppKeyVaultAccessId`: Key Vault role assignment ID
- `functionAppStorageAccessId`: Storage role assignment ID
- `functionAppServiceBusAccessId`: Service Bus role assignment ID

**Features:**
- Key Vault Secrets User role
- Storage Blob Data Contributor role
- Service Bus Data Owner role
- Scoped to specific resources

## 🔒 Security Best Practices

### Secrets Handling

Modules follow secure secret management:
- Parameters marked with `@secure()` decorator for sensitive values
- Outputs containing secrets include warning comments
- Managed identities preferred over connection strings where possible

### RBAC Over Access Policies

- Key Vault uses RBAC authorization (not legacy access policies)
- Least privilege principle applied
- Role assignments scoped to specific resources

### Network Security

Current modules allow public access with these recommendations for production:
- Implement Virtual Network integration
- Use Private Endpoints for Storage, Key Vault, Service Bus
- Configure Network Security Groups
- Set storage `networkAcls.defaultAction` to 'Deny'

## 🏗️ Module Design Principles

1. **Single Responsibility**: Each module owns related resources
2. **Reusability**: Modules can be used across projects
3. **Parameterization**: Configurable through parameters
4. **Documentation**: Inline comments and descriptions
5. **Outputs**: Expose necessary information for consumers
6. **Dependencies**: Explicit via module dependencies
7. **Idempotency**: Safe to run multiple times

## 📊 Regional Considerations

Some modules are subject to regional availability:

- **machinelearning.bicep**: Azure ML available in 19 regions
- **compute.bicep**: Functions Premium (EP) available in 27 regions
- **servicebus.bicep**: Service Bus Premium available in 27 regions

The main orchestrator (main-modular.bicep) handles regional validation automatically.

## 🧪 Testing Modules

### Validation

```bash
# Validate individual module
az bicep build --file modules/storage.bicep

# Validate all modules
for module in modules/*.bicep; do
  echo "Validating $module"
  az bicep build --file "$module"
done
```

### What-If Deployment

```bash
# Preview changes without deploying
az deployment group what-if \
  --resource-group "rg-test" \
  --template-file "modules/storage.bicep" \
  --parameters storageAccountName="test123" location="eastus"
```

## 🔄 Updating Modules

When updating modules:

1. **Update the module** with your changes
2. **Validate** with `az bicep build`
3. **Test** with what-if deployment
4. **Update version comments** in module header
5. **Test orchestrator** (main-modular.bicep) still works
6. **Update this README** if parameters/outputs changed

## 📝 Version History

- **v1.0.0** (2026-02-07): Initial modular architecture
  - 8 production-grade modules
  - Regional validation support
  - Bicepparam parameter files
  - Comprehensive documentation

## 🤝 Contributing

When adding new modules:

1. Follow existing module structure
2. Include parameter descriptions with `@description()`
3. Use appropriate decorators (`@secure()`, `@allowed()`, `@minValue()`, etc.)
4. Document all outputs
5. Include inline comments for complex logic
6. Add module to this README
7. Test compilation and deployment

## 📚 Additional Resources

- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Module Best Practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices)
- [Main Deployment README](../README.md)
- [Regional Requirements](../REGIONAL_REQUIREMENTS.md)

---

**Last Updated**: February 7, 2026  
**Maintained By**: Agent Operating System Team
