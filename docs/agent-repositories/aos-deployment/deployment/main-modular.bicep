// AOS Infrastructure — Modular Bicep Template
//
// Deploys the full Agent Operating System infrastructure:
//   - Log Analytics + Application Insights (monitoring)
//   - Storage Account (function app backing store)
//   - Service Bus namespace + queue (orchestration messaging)
//   - Key Vault (secrets management)
//   - App Service Plan + Function App with managed identity
//   - RBAC role assignments

targetScope = 'resourceGroup'

// ====================================================================
// Parameters
// ====================================================================

@description('Deployment environment')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Primary Azure region for resource deployment')
param location string = resourceGroup().location

@description('Azure region for ML workloads (may differ from primary)')
param locationML string = location

@description('Base project name used in resource naming')
param projectName string = 'aos'

@description('Resource tags applied to every resource')
param tags object = {
  project: 'AgentOperatingSystem'
  environment: environment
  managedBy: 'bicep'
}

// ====================================================================
// Variables
// ====================================================================

var suffix = '${projectName}-${environment}'
var uniqueSuffix = uniqueString(resourceGroup().id, projectName, environment)

// ====================================================================
// Modules
// ====================================================================

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring-${suffix}'
  params: {
    location: location
    environment: environment
    projectName: projectName
    tags: tags
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage-${suffix}'
  params: {
    location: location
    environment: environment
    projectName: projectName
    uniqueSuffix: uniqueSuffix
    tags: tags
  }
}

module serviceBus 'modules/servicebus.bicep' = {
  name: 'servicebus-${suffix}'
  params: {
    location: location
    environment: environment
    projectName: projectName
    tags: tags
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-${suffix}'
  params: {
    location: location
    environment: environment
    projectName: projectName
    uniqueSuffix: uniqueSuffix
    tags: tags
  }
}

module functionApp 'modules/functionapp.bicep' = {
  name: 'functionapp-${suffix}'
  params: {
    location: location
    environment: environment
    projectName: projectName
    uniqueSuffix: uniqueSuffix
    tags: tags
    storageAccountName: storage.outputs.storageAccountName
    storageAccountId: storage.outputs.storageAccountId
    appInsightsInstrumentationKey: monitoring.outputs.instrumentationKey
    appInsightsConnectionString: monitoring.outputs.connectionString
    serviceBusNamespace: serviceBus.outputs.namespaceName
    serviceBusId: serviceBus.outputs.namespaceId
    keyVaultName: keyVault.outputs.keyVaultName
    keyVaultId: keyVault.outputs.keyVaultId
  }
}

// ====================================================================
// Outputs
// ====================================================================

output resourceGroupName string = resourceGroup().name
output functionAppName string = functionApp.outputs.functionAppName
output functionAppHostName string = functionApp.outputs.defaultHostName
output storageAccountName string = storage.outputs.storageAccountName
output serviceBusNamespace string = serviceBus.outputs.namespaceName
output keyVaultName string = keyVault.outputs.keyVaultName
output appInsightsName string = monitoring.outputs.appInsightsName
output logAnalyticsWorkspaceId string = monitoring.outputs.workspaceId
