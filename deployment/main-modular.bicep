// ============================================================================
// Azure Infrastructure as Code (Bicep Template)
// Agent Operating System (AOS) - Modular Deployment Orchestrator
// ============================================================================
// This template orchestrates the deployment of all AOS platform resources using
// production-grade bicep modules for better maintainability and reusability.
//
// Modules:
// - storage.bicep - Storage Account with blob, table, queue services
// - monitoring.bicep - Log Analytics and Application Insights
// - servicebus.bicep - Service Bus with queues and topics
// - keyvault.bicep - Key Vault with RBAC
// - identity.bicep - User-assigned Managed Identity
// - compute.bicep - App Service Plan and Function Apps (3 apps)
// - machinelearning.bicep - Azure ML Workspace and Container Registry
// - rbac.bicep - Role assignments for secure access
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

@description('Location for Azure ML and Container Registry resources. Defaults to primary location. Override when Azure ML is unavailable in the primary region.')
param locationML string = location

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
var userAssignedIdentityName = '${baseName}-identity'

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
// MODULE DEPLOYMENTS
// ============================================================================

// Storage Module
module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  params: {
    storageAccountName: storageAccountName
    location: location
    storageSku: storageSku
    tags: tags
    blobContainerName: 'aos-data'
  }
}

// Monitoring Module
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring-deployment'
  params: {
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    location: location
    tags: tags
    enableAppInsights: enableAppInsights
    retentionInDays: 30
  }
}

// Service Bus Module
module serviceBus 'modules/servicebus.bicep' = {
  name: 'servicebus-deployment'
  params: {
    serviceBusNamespaceName: serviceBusNamespaceName
    location: location
    serviceBusSku: effectiveServiceBusSku
    tags: tags
    queueNames: serviceBusQueues
    topicNames: serviceBusTopics
  }
}

// Key Vault Module
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  params: {
    keyVaultName: keyVaultName
    location: location
    tags: tags
    softDeleteRetentionInDays: 7
  }
}

// Identity Module
module identity 'modules/identity.bicep' = {
  name: 'identity-deployment'
  params: {
    identityName: userAssignedIdentityName
    location: location
    tags: tags
  }
}

// Compute Module (Function Apps)
module compute 'modules/compute.bicep' = {
  name: 'compute-deployment'
  params: {
    appServicePlanName: appServicePlanName
    functionAppName: functionAppName
    mcpServerFunctionAppName: mcpServerFunctionAppName
    realmFunctionAppName: realmFunctionAppName
    location: location
    tags: tags
    functionAppSku: effectiveFunctionSku
    userAssignedIdentityId: identity.outputs.identityId
    storageAccountName: storage.outputs.storageAccountName
    storageConnectionString: storage.outputs.storageConnectionString
    serviceBusConnectionString: serviceBus.outputs.serviceBusConnectionString
    keyVaultUri: keyVault.outputs.keyVaultUri
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    environment: environment
    enableB2C: enableB2C
    b2cTenantName: b2cTenantName
    b2cPolicyName: b2cPolicyName
    b2cClientId: b2cClientId
    b2cClientSecret: b2cClientSecret
  }
}

// Machine Learning Module
module machineLearning 'modules/machinelearning.bicep' = if (azureMLEnabled) {
  name: 'ml-deployment'
  params: {
    azureMLWorkspaceName: azureMLWorkspaceName
    containerRegistryName: containerRegistryName
    location: locationML
    tags: tags
    enableAzureML: azureMLEnabled
    storageAccountId: storage.outputs.storageAccountId
    keyVaultId: keyVault.outputs.keyVaultId
    appInsightsId: monitoring.outputs.appInsightsId
  }
}

// RBAC Module (Role Assignments)
module rbac 'modules/rbac.bicep' = {
  name: 'rbac-deployment'
  params: {
    keyVaultName: keyVault.outputs.keyVaultName
    storageAccountName: storage.outputs.storageAccountName
    serviceBusNamespaceName: serviceBus.outputs.serviceBusNamespaceName
    functionAppPrincipalId: compute.outputs.functionAppPrincipalId
    mcpServerFunctionAppPrincipalId: compute.outputs.mcpServerFunctionAppPrincipalId
    realmFunctionAppPrincipalId: compute.outputs.realmFunctionAppPrincipalId
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

output resourceGroupName string = resourceGroup().name
output location string = location
output locationML string = locationML
output environment string = environment

// Storage
output storageAccountName string = storage.outputs.storageAccountName
output storageAccountId string = storage.outputs.storageAccountId
@secure()
output storageConnectionString string = storage.outputs.storageConnectionString

// Service Bus
output serviceBusNamespaceName string = serviceBus.outputs.serviceBusNamespaceName
output serviceBusNamespaceId string = serviceBus.outputs.serviceBusNamespaceId
@secure()
output serviceBusConnectionString string = serviceBus.outputs.serviceBusConnectionString

// Key Vault
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultId string = keyVault.outputs.keyVaultId
output keyVaultUri string = keyVault.outputs.keyVaultUri

// Application Insights
output appInsightsName string = monitoring.outputs.appInsightsName
output appInsightsId string = monitoring.outputs.appInsightsId
output appInsightsInstrumentationKey string = monitoring.outputs.appInsightsInstrumentationKey
output appInsightsConnectionString string = monitoring.outputs.appInsightsConnectionString

// Azure Functions
output functionAppName string = compute.outputs.functionAppName
output functionAppId string = compute.outputs.functionAppId
output functionAppUrl string = compute.outputs.functionAppUrl
output mcpServerFunctionAppName string = compute.outputs.mcpServerFunctionAppName
output mcpServerFunctionAppUrl string = compute.outputs.mcpServerFunctionAppUrl
output realmFunctionAppName string = compute.outputs.realmFunctionAppName
output realmFunctionAppUrl string = compute.outputs.realmFunctionAppUrl

// Azure ML
output azureMLWorkspaceName string = machineLearning.?outputs.azureMLWorkspaceName ?? ''
output azureMLWorkspaceId string = machineLearning.?outputs.azureMLWorkspaceId ?? ''

// Managed Identity
output userAssignedIdentityId string = identity.outputs.identityId
output userAssignedIdentityPrincipalId string = identity.outputs.identityPrincipalId
output userAssignedIdentityClientId string = identity.outputs.identityClientId

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
  multiRegionDeployment: location != locationML
  recommendedRegionsForFullCapability: [
    'eastus'
    'eastus2'
    'westus2'
    'westeurope'
    'northeurope'
    'southeastasia'
  ]
}
