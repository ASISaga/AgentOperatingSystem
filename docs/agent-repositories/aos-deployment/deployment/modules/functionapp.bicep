// Function App module — FC1 Flex Consumption plan + Function App + User-Assigned Managed Identity + GitHub OIDC + Scoped RBAC
// One-app-per-plan pattern required by Flex Consumption.
// Each app has its own User-Assigned Identity used both as the runtime identity and as the GitHub Actions
// deployment agent. Workload Identity Federation (OIDC) restricts each identity to exactly one
// GitHub repository + environment, creating a hard security boundary between the 10 AOS modules.

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

@description('Table service URI for the shared storage account (for AOSStateStore connection)')
param tableServiceUri string

@description('URL of the core AOS Function App (aos-function-app) injected into all modules for peer discovery.')
param coreAppUrl string

@description('GitHub organization or user name that owns the AOS repositories (e.g. ASISaga)')
param githubOrg string

@description('GitHub Actions environment name used as the OIDC subject bound to this app. Defaults to the deployment environment value.')
param githubEnvironment string = environment

// ====================================================================
// Variables
// ====================================================================

// One dedicated plan per app (required by Flex Consumption)
var planName = 'plan-${appName}-${environment}'
var functionAppName = 'func-${appName}-${environment}-${take(uniqueSuffix, 6)}'
var identityName = 'id-${appName}-${environment}'
// Blob container holding the deployment package for this app
var deploymentContainerName = 'deploy-${appName}'

// RBAC role definition IDs
var storageBlobDataOwnerRole = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
var storageBlobDataContributorRole = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
var storageTableDataContributorRole = '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'
var websiteContributorRole = 'de139f84-1756-47ae-9be6-808fbbe84772'
var keyVaultSecretsUserRole = '4633458b-17de-408a-b874-0445c86b69e6'
var serviceBusDataSenderRole = '69a216fc-b8fb-44d8-bc22-1f3c2cd27a39'
var serviceBusDataReceiverRole = '4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0'

// ====================================================================
// Resources
// ====================================================================

// User-Assigned Managed Identity — one per app, acts as both the runtime identity and the
// GitHub Actions deployment agent for the corresponding AOS repository.
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

// Workload Identity Federation — binds the identity strictly to one GitHub repository + environment.
// Only a GitHub Actions workflow running in that exact repo/environment can exchange an OIDC token
// for an Azure credential, preventing cross-module deployments.
// NOTE: The GitHub OIDC subject for environment-based deployments is always
//   repo:{org}/{repo}:environment:{env}
// The 'ref' sub-claim is not part of the subject when an environment is set; the environment
// constraint itself is the security boundary (GitHub docs: "Configuring OpenID Connect in Azure").
resource federatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: userAssignedIdentity
  name: 'github-${appName}-${environment}'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubOrg}/${appName}:environment:${githubEnvironment}'
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

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

// References to shared resources used for RBAC scoping
resource existingKeyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

// The Service Bus namespace name is <projectName>-sb-<environment>; derive it from the namespace FQDN
// parameter by using the namespace name directly.
resource existingServiceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' existing = {
  name: serviceBusNamespace
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
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
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
            type: 'UserAssignedIdentity'
            userAssignedIdentityResourceId: userAssignedIdentity.id
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
        { name: 'AzureWebJobsStorage__credential', value: 'managedidentity' }
        { name: 'AzureWebJobsStorage__clientId', value: userAssignedIdentity.properties.clientId }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'ServiceBusConnection__fullyQualifiedNamespace', value: '${serviceBusNamespace}.servicebus.windows.net' }
        { name: 'ServiceBusConnection__credential', value: 'managedidentity' }
        { name: 'ServiceBusConnection__clientId', value: userAssignedIdentity.properties.clientId }
        // AOSStateStore — identity-based Table Storage connection for cross-module shared state
        { name: 'AosStateStore__accountName', value: storageAccountName }
        { name: 'AosStateStore__tableServiceUri', value: tableServiceUri }
        { name: 'AosStateStore__credential', value: 'managedidentity' }
        { name: 'AosStateStore__clientId', value: userAssignedIdentity.properties.clientId }
        { name: 'KEY_VAULT_URI', value: 'https://${keyVaultName}.vault.azure.net/' }
        { name: 'ENVIRONMENT', value: environment }
        { name: 'AZURE_CLIENT_ID', value: userAssignedIdentity.properties.clientId }
        // Peer discovery — URL of the core AOS orchestration hub
        { name: 'AOS_FUNCTION_APP_URL', value: coreAppUrl }
      ]
    }
  }
  dependsOn: [deploymentContainer]
}

// RBAC — Storage Blob Data Owner on the storage account (runtime: AzureWebJobsStorage identity-based connection)
resource storageBlobOwnerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccountId, userAssignedIdentity.id, storageBlobDataOwnerRole)
  scope: existingStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Storage Table Data Contributor on the storage account (AOSStateStore cross-module shared state)
resource storageTableContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccountId, userAssignedIdentity.id, storageTableDataContributorRole)
  scope: existingStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageTableDataContributorRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Storage Blob Data Contributor on the per-app deployment container (deployment package upload/read)
// Scoped to the individual container — no cross-app storage access.
resource deploymentContainerContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(deploymentContainer.id, userAssignedIdentity.id, storageBlobDataContributorRole)
  scope: deploymentContainer
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Website Contributor on this Function App only (GitHub Actions deployment)
// Scoped to the specific Function App resource — a credential for one repo cannot touch another app.
resource websiteContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(functionApp.id, userAssignedIdentity.id, websiteContributorRole)
  scope: functionApp
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', websiteContributorRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Key Vault Secrets User (scoped to this Key Vault only)
resource keyVaultSecretsRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVaultId, userAssignedIdentity.id, keyVaultSecretsUserRole)
  scope: existingKeyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Service Bus Data Sender (scoped to this Service Bus namespace only)
resource serviceBusSenderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusId, userAssignedIdentity.id, serviceBusDataSenderRole)
  scope: existingServiceBusNamespace
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', serviceBusDataSenderRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// RBAC — Service Bus Data Receiver (scoped to this Service Bus namespace only; needed for trigger-based scaling)
resource serviceBusReceiverRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(serviceBusId, userAssignedIdentity.id, serviceBusDataReceiverRole)
  scope: existingServiceBusNamespace
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', serviceBusDataReceiverRole)
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ====================================================================
// Outputs
// ====================================================================

output functionAppName string = functionApp.name
output defaultHostName string = functionApp.properties.defaultHostName
output principalId string = userAssignedIdentity.properties.principalId
// clientId is used as the AZURE_CLIENT_ID GitHub Actions secret for this repository's deployment workflow
output clientId string = userAssignedIdentity.properties.clientId
