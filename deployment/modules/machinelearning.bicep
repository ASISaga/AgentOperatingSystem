// ============================================================================
// Machine Learning Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Container Registry (for ML)
// - Azure ML Workspace
// ============================================================================

@description('Azure ML Workspace name')
param azureMLWorkspaceName string

@description('Container Registry name (must be globally unique, alphanumeric)')
param containerRegistryName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object = {}

@description('Enable Azure ML deployment')
param enableAzureML bool = true

@description('Storage account resource ID for ML workspace')
param storageAccountId string

@description('Key Vault resource ID for ML workspace')
param keyVaultId string

@description('Application Insights resource ID for ML workspace')
param appInsightsId string = ''

// ============================================================================
// CONTAINER REGISTRY (for ML)
// ============================================================================

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = if (enableAzureML) {
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

// ============================================================================
// AZURE ML WORKSPACE
// ============================================================================

resource azureMLWorkspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = if (enableAzureML) {
  name: azureMLWorkspaceName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AOS ML Workspace'
    storageAccount: storageAccountId
    keyVault: keyVaultId
    applicationInsights: !empty(appInsightsId) ? appInsightsId : null
    containerRegistry: enableAzureML ? containerRegistry.id : null
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Container Registry resource ID')
output containerRegistryId string = enableAzureML ? containerRegistry.id : ''

@description('Container Registry name')
output containerRegistryName string = enableAzureML ? containerRegistry.name : ''

@description('Azure ML Workspace resource ID')
output azureMLWorkspaceId string = enableAzureML ? azureMLWorkspace.id : ''

@description('Azure ML Workspace name')
output azureMLWorkspaceName string = enableAzureML ? azureMLWorkspace.name : ''
