// Function App module — FC1 Flex Consumption plan + Function App + managed identity + RBAC
// One-app-per-plan pattern required by Flex Consumption.
// Code is deployed from a per-app blob container using Managed Identity.

@description('Azure region')
param location string

@description('Deployment environment')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Application module name (used in resource naming)')
param appName string

@description('Unique suffix for globally unique names')
param uniqueSuffix string

@description('Resource tags')
param tags object

// Dependencies from other modules
@description('Storage account name for function app backing store and deployment packages')
param storageAccountName string

@description('Storage account resource ID')
param storageAccountId string

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

// One dedicated plan per app (required by Flex Consumption)
var planName = 'plan-${appName}-${environment}'
var functionAppName = 'func-${appName}-${environment}-${take(uniqueSuffix, 6)}'
// Blob container holding the deployment package for this app
var deploymentContainerName = 'deploy-${appName}'

// RBAC role definition IDs
var storageBlobDataOwnerRole = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
var keyVaultSecretsUserRole = '4633458b-17de-408a-b874-0445c86b69e6'
var serviceBusDataSenderRole = '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39'
var serviceBusDataReceiverRole = '4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0'

// ====================================================================
// Resources
// ====================================================================

// Dedicated Flex Consumption plan — one per app
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  tags: tags
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  properties: {
    reserved: true // Linux
  }
}

// Reference existing storage account and its blob service to create per-app deployment container
resource existingStorageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' existing = {
  parent: existingStorageAccount
  name: 'default'
}

// Per-app blob container for deployment packages (Managed Identity access)
resource deploymentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: deploymentContainerName
  properties: {
    publicAccess: 'None'
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
    // Flex Consumption configuration block replaces legacy siteConfig scaling
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: 'https://${storageAccountName}.blob.core.windows.net/${deploymentContainerName}'
          authentication: {
            type: 'SystemAssignedIdentity'
          }
        }
      }
      scaleAndConcurrency: {
        // Target-based scaling: scale out to match Service Bus queue depth
        maximumInstanceCount: 40
        instanceMemoryMB: 2048
        triggers: {
          http: {
            perInstanceConcurrency: 16
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.11'
      }
    }
    siteConfig: {
      // Identity-based connections only — no connection strings or secrets
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: storageAccountName }
        { name: 'AzureWebJobsStorage__blobServiceUri', value: 'https://${storageAccountName}.blob.core.windows.net' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'ServiceBusConnection__fullyQualifiedNamespace', value: '${serviceBusNamespace}.servicebus.windows.net' }
        { name: 'KEY_VAULT_URI', value: 'https://${keyVaultName}.vault.azure.net/' }
        { name: 'ENVIRONMENT', value: environment }
      ]
    }
  }
  dependsOn: [deploymentContainer]
}

// RBAC — Storage Blob Data Owner (required for Flex Consumption deployment container access)
resource storageBlobOwnerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccountId, functionApp.id, storageBlobDataOwnerRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRole)
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
resource serviceBusSenderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusId, functionApp.id, serviceBusDataSenderRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', serviceBusDataSenderRole)
    principalId: functionApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Service Bus Data Receiver (needed for trigger-based scaling)
resource serviceBusReceiverRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusId, functionApp.id, serviceBusDataReceiverRole)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', serviceBusDataReceiverRole)
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
