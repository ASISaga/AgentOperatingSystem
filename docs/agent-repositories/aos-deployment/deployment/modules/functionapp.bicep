// Function App module — App Service Plan + Function App + managed identity + RBAC

@description('Azure region')
param location string

@description('Deployment environment')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Base project name')
param projectName string

@description('Unique suffix for globally unique names')
param uniqueSuffix string

@description('Resource tags')
param tags object

// Dependencies from other modules
@description('Storage account name for function app')
param storageAccountName string

@description('Storage account resource ID')
param storageAccountId string

@description('Application Insights instrumentation key')
param appInsightsInstrumentationKey string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Service Bus namespace name')
param serviceBusNamespace string

@description('Service Bus namespace resource ID')
param serviceBusId string

@description('Key Vault name')
param keyVaultName string

@description('Key Vault resource ID')
param keyVaultId string

// ====================================================================
// Variables
// ====================================================================

var planName = 'plan-${projectName}-${environment}'
var functionAppName = 'func-${projectName}-${environment}-${take(uniqueSuffix, 6)}'
var isConsumption = environment == 'dev'
var planSku = isConsumption ? 'Y1' : 'EP1'
var planTier = isConsumption ? 'Dynamic' : 'ElasticPremium'

// RBAC role definition IDs
var storageBlobDataContributorRole = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var keyVaultSecretsUserRole = '4633458b-17de-408a-b874-0445c86b69e6'
var serviceBusDataSenderRole = '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39'

// ====================================================================
// Resources
// ====================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  tags: tags
  sku: {
    name: planSku
    tier: planTier
  }
  properties: {
    reserved: true // Linux
  }
}

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: storageAccountName }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'APPINSIGHTS_INSTRUMENTATIONKEY', value: appInsightsInstrumentationKey }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'ServiceBusConnection__fullyQualifiedNamespace', value: '${serviceBusNamespace}.servicebus.windows.net' }
        { name: 'KEY_VAULT_NAME', value: keyVaultName }
        { name: 'ENVIRONMENT', value: environment }
      ]
    }
  }
}

// RBAC — Storage Blob Data Contributor
resource storageBlobRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccountId, functionApp.id, storageBlobDataContributorRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRole)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Key Vault Secrets User
resource keyVaultSecretsRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVaultId, functionApp.id, keyVaultSecretsUserRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRole)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Service Bus Data Sender
resource serviceBusRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusId, functionApp.id, serviceBusDataSenderRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', serviceBusDataSenderRole)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ====================================================================
// Outputs
// ====================================================================

output functionAppName string = functionApp.name
output defaultHostName string = functionApp.properties.defaultHostName
output principalId string = functionApp.identity.principalId
