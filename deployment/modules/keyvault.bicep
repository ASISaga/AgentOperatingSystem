// ============================================================================
// Key Vault Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Azure Key Vault with RBAC authorization
// ============================================================================

@description('Key Vault name (must be globally unique, 3-24 chars)')
param keyVaultName string

@description('Location for the Key Vault')
param location string

@description('Tags to apply to resources')
param tags object = {}

@description('Soft delete retention period in days')
@minValue(7)
@maxValue(90)
param softDeleteRetentionInDays int = 7

// ============================================================================
// KEY VAULT
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true // Use RBAC instead of access policies
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: softDeleteRetentionInDays
    networkAcls: {
      defaultAction: 'Allow' // Set to 'Deny' in production
      bypass: 'AzureServices'
    }
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Key Vault resource ID')
output keyVaultId string = keyVault.id

@description('Key Vault name')
output keyVaultName string = keyVault.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri
