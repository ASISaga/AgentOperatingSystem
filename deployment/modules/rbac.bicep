// ============================================================================
// RBAC Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Role assignments for Function Apps to access Key Vault, Storage, Service Bus
// Note: This module must be deployed in the same scope as the parent main.bicep
//       to enable proper role assignment scoping
// ============================================================================

@description('Key Vault name')
param keyVaultName string

@description('Storage account name')
param storageAccountName string

@description('Service Bus namespace name')
param serviceBusNamespaceName string

@description('Main Function App principal ID (system-assigned identity)')
param functionAppPrincipalId string

@description('MCP Server Function App principal ID (system-assigned identity)')
param mcpServerFunctionAppPrincipalId string

@description('Realm Function App principal ID (system-assigned identity)')
param realmFunctionAppPrincipalId string

// ============================================================================
// ROLE DEFINITIONS
// ============================================================================

// Key Vault Secrets User role
var keyVaultSecretsUserRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')

// Storage Blob Data Contributor role
var storageBlobDataContributorRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')

// Service Bus Data Owner role
var serviceBusDataOwnerRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '090c5cfd-751d-490a-894a-3ce6f1109419')

// ============================================================================
// EXISTING RESOURCES (for scope reference)
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' existing = {
  name: keyVaultName
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
}

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' existing = {
  name: serviceBusNamespaceName
}

// ============================================================================
// KEY VAULT ACCESS
// ============================================================================

resource functionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, functionAppPrincipalId, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource mcpFunctionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, mcpServerFunctionAppPrincipalId, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: mcpServerFunctionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource realmFunctionAppKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, realmFunctionAppPrincipalId, keyVaultSecretsUserRole)
  properties: {
    roleDefinitionId: keyVaultSecretsUserRole
    principalId: realmFunctionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// STORAGE ACCESS
// ============================================================================

resource functionAppStorageAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(storageAccount.id, functionAppPrincipalId, storageBlobDataContributorRole)
  properties: {
    roleDefinitionId: storageBlobDataContributorRole
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// SERVICE BUS ACCESS
// ============================================================================

resource functionAppServiceBusAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: serviceBusNamespace
  name: guid(serviceBusNamespace.id, functionAppPrincipalId, serviceBusDataOwnerRole)
  properties: {
    roleDefinitionId: serviceBusDataOwnerRole
    principalId: functionAppPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Function App Key Vault access role assignment ID')
output functionAppKeyVaultAccessId string = functionAppKeyVaultAccess.id

@description('Function App Storage access role assignment ID')
output functionAppStorageAccessId string = functionAppStorageAccess.id

@description('Function App Service Bus access role assignment ID')
output functionAppServiceBusAccessId string = functionAppServiceBusAccess.id
