// ============================================================================
// Identity Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - User-assigned Managed Identity for cross-resource access
// ============================================================================

@description('Managed identity name')
param identityName string

@description('Location for the managed identity')
param location string

@description('Tags to apply to resources')
param tags object = {}

// ============================================================================
// USER-ASSIGNED MANAGED IDENTITY
// ============================================================================

resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Managed identity resource ID')
output identityId string = userAssignedIdentity.id

@description('Managed identity name')
output identityName string = userAssignedIdentity.name

@description('Managed identity principal ID')
output identityPrincipalId string = userAssignedIdentity.properties.principalId

@description('Managed identity client ID')
output identityClientId string = userAssignedIdentity.properties.clientId
