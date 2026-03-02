// AOS Infrastructure — Modular Bicep Template
//
// Deploys the full Agent Operating System infrastructure:
//   - Log Analytics + Application Insights (monitoring)
//   - Storage Account (function app backing store + deployment packages)
//   - Service Bus namespace + queue (orchestration messaging)
//   - Key Vault (secrets management)
//   - One dedicated FC1 Flex Consumption Plan + Function App per AOS module (10 total)
//   - RBAC role assignments (identity-based connections, no secrets in env vars)

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

@description('GitHub organization or user name that owns the AOS repositories (e.g. ASISaga). Used to construct the OIDC subject for Workload Identity Federation.')
param githubOrg string = 'ASISaga'

@description('List of AOS application module names — one dedicated Flex Consumption plan and Function App is created per entry. These are the 10 canonical AOS repository modules; override only when adding or retiring a module.')
param appNames array = [
  'purpose-driven-agent'
  'leadership-agent'
  'cmo-agent'
  'aos-kernel'
  'aos-intelligence'
  'aos-realm-of-agents'
  'aos-mcp-servers'
  'aos-client-sdk'
  'business-infinity'
  'aos-function-app'
]

// ====================================================================
// Variables
// ====================================================================

var suffix = '${projectName}-${environment}'
var uniqueSuffix = uniqueString(resourceGroup().id, projectName, environment)

// Core AOS orchestration hub — its URL is injected into every module's env vars for peer discovery.
// The hostname follows the same naming formula used in functionapp.bicep:
//   func-{appName}-{environment}-{take(uniqueSuffix,6)}.azurewebsites.net
var coreAppName = 'aos-function-app'
var coreAppUrl = 'https://func-${coreAppName}-${environment}-${take(uniqueSuffix, 6)}.azurewebsites.net'

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

// One dedicated FC1 Flex Consumption plan + Function App per AOS module
module functionApps 'modules/functionapp.bicep' = [for appName in appNames: {
  name: 'functionapp-${appName}-${suffix}'
  params: {
    location: location
    environment: environment
    appName: appName
    uniqueSuffix: uniqueSuffix
    tags: tags
    storageAccountName: storage.outputs.storageAccountName
    storageAccountId: storage.outputs.storageAccountId
    appInsightsConnectionString: monitoring.outputs.connectionString
    serviceBusNamespace: serviceBus.outputs.namespaceName
    serviceBusId: serviceBus.outputs.namespaceId
    keyVaultName: keyVault.outputs.keyVaultName
    keyVaultId: keyVault.outputs.keyVaultId
    tableServiceUri: storage.outputs.tableServiceUri
    coreAppUrl: coreAppUrl
    githubOrg: githubOrg
    githubEnvironment: environment
  }
}]

// ====================================================================
// Outputs
// ====================================================================

output resourceGroupName string = resourceGroup().name
output functionAppNames array = [for (appName, i) in appNames: functionApps[i].outputs.functionAppName]
// clientId per app — use as the AZURE_CLIENT_ID GitHub Actions secret in each repository's deployment workflow
output functionAppClientIds array = [for (appName, i) in appNames: functionApps[i].outputs.clientId]
output storageAccountName string = storage.outputs.storageAccountName
output serviceBusNamespace string = serviceBus.outputs.namespaceName
output keyVaultName string = keyVault.outputs.keyVaultName
output appInsightsName string = monitoring.outputs.appInsightsName
output logAnalyticsWorkspaceId string = monitoring.outputs.workspaceId
