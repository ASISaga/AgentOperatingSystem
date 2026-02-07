// ============================================================================
// Azure Infrastructure as Code (Bicep Template)
// Agent Operating System (AOS) - Complete Azure Deployment
// ============================================================================
// ⚠️ LEGACY MONOLITHIC TEMPLATE - For new deployments, use main-modular.bicep
//
// This is a legacy monolithic template kept for backward compatibility.
// For new deployments, use main-modular.bicep which provides:
//   - Better maintainability with modular architecture
//   - Production-grade separation of concerns
//   - Easier updates and customization
//
// See MIGRATION_GUIDE.md for migration instructions.
// ============================================================================
// This template deploys all required Azure resources for the AOS platform:
// - Azure Functions (App Service Plan + Function Apps)
// - Azure Service Bus (Namespace, Queues, Topics)
// - Azure Storage (Blob, Table, Queue)
// - Azure Key Vault (Secrets Management)
// - Azure Application Insights (Monitoring)
// - Azure Machine Learning Workspace (ML/LoRA Training)
// - Azure AI Services (Foundry Agent Service)
// - Managed Identities (Secure authentication)
// ============================================================================

// ============================================================================
// PARAMETERS
// ============================================================================

@description('Primary location for all resources. Must be a supported Azure region.')
@allowed([
  'eastus'
  'eastus2'
  'westus'
  'westus2'
  'westus3'
  'centralus'
  'northcentralus'
  'southcentralus'
  'westcentralus'
  'northeurope'
  'westeurope'
  'uksouth'
  'ukwest'
  'francecentral'
  'germanywestcentral'
  'switzerlandnorth'
  'norwayeast'
  'swedencentral'
  'southeastasia'
  'eastasia'
  'japaneast'
  'japanwest'
  'koreacentral'
  'australiaeast'
  'australiasoutheast'
  'canadacentral'
  'canadaeast'
  'brazilsouth'
  'southafricanorth'
  'uaenorth'
  'centralindia'
  'southindia'
])
param location string

@description('Environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('Unique suffix for resource names (auto-generated if empty)')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Name prefix for all resources')
param namePrefix string = 'aos'

@description('Azure Functions SKU')
@allowed([
  'Y1'  // Consumption plan
  'EP1' // Elastic Premium
  'EP2'
  'EP3'
])
param functionAppSku string = 'Y1'

@description('Service Bus SKU')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param serviceBusSku string = 'Standard'

@description('Storage account SKU')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
  'Premium_LRS'
])
param storageSku string = 'Standard_LRS'

@description('Enable Azure B2C Authentication')
param enableB2C bool = false

@description('Azure B2C Tenant Name')
param b2cTenantName string = ''

@description('Azure B2C Policy Name')
param b2cPolicyName string = ''

@description('Azure B2C Client ID')
@secure()
param b2cClientId string = ''

@description('Azure B2C Client Secret')
@secure()
param b2cClientSecret string = ''

@description('Enable Application Insights')
param enableAppInsights bool = true

@description('Enable Azure ML Workspace')
param enableAzureML bool = true

@description('Admin email for alerts')
param adminEmail string = ''

@description('Tags to apply to all resources')
param tags object = {
  Environment: environment
  Application: 'AgentOperatingSystem'
  ManagedBy: 'Bicep'
}

// ============================================================================
// VARIABLES
// ============================================================================

var baseName = '${namePrefix}-${environment}-${uniqueSuffix}'
var storageAccountName = replace('${namePrefix}${environment}${uniqueSuffix}', '-', '')
var functionAppName = '${baseName}-func'
var mcpServerFunctionAppName = '${baseName}-mcp-func'
var realmFunctionAppName = '${baseName}-realm-func'
var appServicePlanName = '${baseName}-plan'
var serviceBusNamespaceName = '${baseName}-sb'
var keyVaultName = take('${namePrefix}-${environment}-kv-${uniqueSuffix}', 24)
var appInsightsName = '${baseName}-ai'
var logAnalyticsName = '${baseName}-la'
var azureMLWorkspaceName = '${baseName}-ml'
var containerRegistryName = replace('${namePrefix}${environment}acr${uniqueSuffix}', '-', '')

// Service Bus Queues and Topics
var serviceBusQueues = [
  'aos-requests'
  'businessinfinity-responses'
]

var serviceBusTopics = [
  'agent-events'
  'system-events'
]

// ============================================================================
// REGIONAL CAPABILITY VALIDATION
// ============================================================================
// Define regions with full Azure ML and AI Services support
var azureMLSupportedRegions = [
  'eastus'
  'eastus2'
  'westus2'
  'westus3'
  'northcentralus'
  'southcentralus'
  'westeurope'
  'northeurope'
  'uksouth'
  'francecentral'
  'germanywestcentral'
  'switzerlandnorth'
  'swedencentral'
  'southeastasia'
  'japaneast'
  'australiaeast'
  'canadacentral'
  'koreacentral'
  'centralindia'
]

// Define regions with Azure Functions Premium (EP) support
var functionsPremiumSupportedRegions = [
  'eastus'
  'eastus2'
  'westus'
  'westus2'
  'westus3'
  'centralus'
  'northcentralus'
  'southcentralus'
  'westcentralus'
  'canadacentral'
  'canadaeast'
  'brazilsouth'
  'northeurope'
  'westeurope'
  'uksouth'
  'ukwest'
  'francecentral'
  'germanywestcentral'
  'switzerlandnorth'
  'norwayeast'
  'swedencentral'
  'southeastasia'
  'eastasia'
  'australiaeast'
  'australiasoutheast'
  'japaneast'
  'japanwest'
  'koreacentral'
  'centralindia'
  'southindia'
  'southafricanorth'
  'uaenorth'
]

// Define regions with Service Bus Premium support
var serviceBusPremiumSupportedRegions = [
  'eastus'
  'eastus2'
  'westus'
  'westus2'
  'westus3'
  'centralus'
  'northcentralus'
  'southcentralus'
  'westcentralus'
  'canadacentral'
  'canadaeast'
  'brazilsouth'
  'northeurope'
  'westeurope'
  'uksouth'
  'ukwest'
  'francecentral'
  'germanywestcentral'
  'switzerlandnorth'
  'norwayeast'
  'swedencentral'
  'southeastasia'
  'eastasia'
  'australiaeast'
  'australiasoutheast'
  'japaneast'
  'japanwest'
  'koreacentral'
  'centralindia'
  'southindia'
  'southafricanorth'
  'uaenorth'
]

// Check if selected location supports required services
var isAzureMLSupported = contains(azureMLSupportedRegions, location)
var isFunctionsPremiumSupported = contains(functionsPremiumSupportedRegions, location)
var isServiceBusPremiumSupported = contains(serviceBusPremiumSupportedRegions, location)

// Validate regional capabilities
var azureMLEnabled = enableAzureML && isAzureMLSupported
var effectiveFunctionSku = (functionAppSku != 'Y1' && !isFunctionsPremiumSupported) ? 'Y1' : functionAppSku
var effectiveServiceBusSku = (serviceBusSku == 'Premium' && !isServiceBusPremiumSupported) ? 'Standard' : serviceBusSku

// ============================================================================
// STORAGE ACCOUNT
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow' // Set to 'Deny' in production with specific rules
      bypass: 'AzureServices'
    }
  }
}

// Blob Services
resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

// Blob Container for AOS data
resource aosDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'aos-data'
  properties: {
    publicAccess: 'None'
  }
}

// Table Services
resource tableServices 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// Queue Services
resource queueServices 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// ============================================================================
// LOG ANALYTICS WORKSPACE (for Application Insights)
// ============================================================================

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (enableAppInsights) {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// APPLICATION INSIGHTS
// ============================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (enableAppInsights) {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: enableAppInsights ? logAnalyticsWorkspace.id : ''
    IngestionMode: 'LogAnalytics'
  }
}

// ============================================================================
// SERVICE BUS NAMESPACE
// ============================================================================

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusNamespaceName
  location: location
  tags: tags
  sku: {
    name: effectiveServiceBusSku
    tier: effectiveServiceBusSku
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

// Service Bus Queues
resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = [for queue in serviceBusQueues: {
  parent: serviceBusNamespace
  name: queue
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
    enableBatchedOperations: true
    maxDeliveryCount: 10
  }
}]

// Service Bus Topics
resource serviceBusTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = [for topic in serviceBusTopics: {
  parent: serviceBusNamespace
  name: topic
  properties: {
    maxSizeInMegabytes: 1024
    defaultMessageTimeToLive: 'P14D'
    enableBatchedOperations: true
  }
}]

// Default subscriptions for topics
resource serviceBusSubscription 'Microsoft.ServiceBus/namespaces/topics/subscriptions@2022-10-01-preview' = [for topic in serviceBusTopics: {
  parent: serviceBusTopic[indexOf(serviceBusTopics, topic)]
  name: 'default-subscription'
  properties: {
    lockDuration: 'PT5M'
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount: 10
  }
}]

// ============================================================================
// KEY VAULT
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true // Use RBAC instead of access policies
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    networkAcls: {
      defaultAction: 'Allow' // Set to 'Deny' in production
      bypass: 'AzureServices'
    }
  }
}

// ============================================================================
// AZURE MACHINE LEARNING WORKSPACE
// ============================================================================

// Container Registry for ML
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = if (azureMLEnabled) {
  name: containerRegistryName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Azure ML Workspace
resource azureMLWorkspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = if (azureMLEnabled) {
  name: azureMLWorkspaceName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AOS ML Workspace'
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    applicationInsights: enableAppInsights ? appInsights.id : null
    containerRegistry: azureMLEnabled ? containerRegistry.id : null
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// MANAGED IDENTITIES
// ============================================================================

// System-assigned identities are created for Function Apps
// User-assigned identity for shared access across resources
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${baseName}-identity'
  location: location
  tags: tags
}

// ============================================================================
// APP SERVICE PLAN
// ============================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: effectiveFunctionSku
    tier: effectiveFunctionSku == 'Y1' ? 'Dynamic' : 'ElasticPremium'
  }
  properties: {
    reserved: true // Linux
  }
  kind: 'linux'
}

// ============================================================================
// AZURE FUNCTIONS - MAIN FUNCTION APP
// ============================================================================

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_SERVICEBUS_CONNECTION_STRING'
          value: listKeys('${serviceBusNamespace.id}/AuthorizationRules/RootManageSharedAccessKey', serviceBusNamespace.apiVersion).primaryConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT'
          value: storageAccount.name
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: enableAppInsights ? appInsights.properties.ConnectionString : ''
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
        {
          name: 'B2C_TENANT'
          value: enableB2C ? b2cTenantName : ''
        }
        {
          name: 'B2C_POLICY'
          value: enableB2C ? b2cPolicyName : ''
        }
        {
          name: 'B2C_CLIENT_ID'
          value: enableB2C ? b2cClientId : ''
        }
        {
          name: 'B2C_CLIENT_SECRET'
          value: enableB2C ? b2cClientSecret : ''
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      pythonVersion: '3.11'
    }
    httpsOnly: true
  }
}

// ============================================================================
// AZURE FUNCTIONS - MCP SERVERS FUNCTION APP
// ============================================================================

resource mcpServerFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: mcpServerFunctionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(mcpServerFunctionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVault.properties.vaultUri
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: enableAppInsights ? appInsights.properties.ConnectionString : ''
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

// ============================================================================
// AZURE FUNCTIONS - REALM OF AGENTS FUNCTION APP
// ============================================================================

resource realmFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: realmFunctionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(realmFunctionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_SERVICEBUS_CONNECTION_STRING'
          value: listKeys('${serviceBusNamespace.id}/AuthorizationRules/RootManageSharedAccessKey', serviceBusNamespace.apiVersion).primaryConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: enableAppInsights ? appInsights.properties.ConnectionString : ''
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

// ============================================================================
// RBAC ROLE ASSIGNMENTS
// ============================================================================

// Function Apps need access to Key Vault
var keyVaultSecretsUserRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')

resource functionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, functionApp.id, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource mcpFunctionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, mcpServerFunctionApp.id, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: mcpServerFunctionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource realmFunctionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, realmFunctionApp.id, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: realmFunctionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Storage Blob Data Contributor role for Function Apps
var storageBlobDataContributorRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')

resource functionAppStorageAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, functionApp.id, storageBlobDataContributorRole)
  properties: {
    roleDefinitionId: storageBlobDataContributorRole
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Service Bus Data Owner role for Function Apps
var serviceBusDataOwnerRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '090c5cfd-751d-490a-894a-3ce6f1109419')

resource functionAppServiceBusAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: serviceBusNamespace
  name: guid(serviceBusNamespace.id, functionApp.id, serviceBusDataOwnerRole)
  properties: {
    roleDefinitionId: serviceBusDataOwnerRole
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

output resourceGroupName string = resourceGroup().name
output location string = location
output environment string = environment

// Storage
output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${az.environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'

// Service Bus
output serviceBusNamespaceName string = serviceBusNamespace.name
output serviceBusNamespaceId string = serviceBusNamespace.id
output serviceBusConnectionString string = listKeys('${serviceBusNamespace.id}/AuthorizationRules/RootManageSharedAccessKey', serviceBusNamespace.apiVersion).primaryConnectionString

// Key Vault
output keyVaultName string = keyVault.name
output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri

// Application Insights
output appInsightsName string = enableAppInsights ? appInsights.name : ''
output appInsightsId string = enableAppInsights ? appInsights.id : ''
output appInsightsInstrumentationKey string = enableAppInsights ? appInsights.properties.InstrumentationKey : ''
output appInsightsConnectionString string = enableAppInsights ? appInsights.properties.ConnectionString : ''

// Azure Functions
output functionAppName string = functionApp.name
output functionAppId string = functionApp.id
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
output mcpServerFunctionAppName string = mcpServerFunctionApp.name
output mcpServerFunctionAppUrl string = 'https://${mcpServerFunctionApp.properties.defaultHostName}'
output realmFunctionAppName string = realmFunctionApp.name
output realmFunctionAppUrl string = 'https://${realmFunctionApp.properties.defaultHostName}'

// Azure ML
output azureMLWorkspaceName string = azureMLEnabled ? azureMLWorkspace.name : ''
output azureMLWorkspaceId string = azureMLEnabled ? azureMLWorkspace.id : ''

// Managed Identity
output userAssignedIdentityId string = userAssignedIdentity.id
output userAssignedIdentityPrincipalId string = userAssignedIdentity.properties.principalId
output userAssignedIdentityClientId string = userAssignedIdentity.properties.clientId

// ============================================================================
// DEPLOYMENT WARNINGS AND REGIONAL INFORMATION
// ============================================================================

output deploymentWarnings object = {
  azureMLDisabledDueToRegion: enableAzureML && !isAzureMLSupported
  functionSkuDowngradedDueToRegion: functionAppSku != effectiveFunctionSku
  serviceBusSkuDowngradedDueToRegion: serviceBusSku != effectiveServiceBusSku
  effectiveFunctionSku: effectiveFunctionSku
  effectiveServiceBusSku: effectiveServiceBusSku
  azureMLSupported: isAzureMLSupported
  functionsPremiumSupported: isFunctionsPremiumSupported
  serviceBusPremiumSupported: isServiceBusPremiumSupported
  recommendedRegionsForFullCapability: [
    'eastus'
    'eastus2'
    'westus2'
    'westeurope'
    'northeurope'
    'southeastasia'
  ]
}
