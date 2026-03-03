// AI Services module — Azure Cognitive Services (AIServices kind) with system-assigned managed identity
// Provides the foundational AI/ML endpoint used by AI Foundry Hub connections and the API gateway.

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

// ====================================================================
// Variables
// ====================================================================

var accountName = 'ai-${projectName}-${environment}-${take(uniqueSuffix, 6)}'

// ====================================================================
// Resources
// ====================================================================

resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  tags: tags
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: accountName
    publicNetworkAccess: environment == 'prod' ? 'Disabled' : 'Enabled'
    disableLocalAuth: false
    networkAcls: {
      defaultAction: environment == 'prod' ? 'Deny' : 'Allow'
    }
  }
}

// ====================================================================
// Outputs
// ====================================================================

output accountName string = aiServicesAccount.name
output accountId string = aiServicesAccount.id
output endpoint string = aiServicesAccount.properties.endpoint
output principalId string = aiServicesAccount.identity.principalId
