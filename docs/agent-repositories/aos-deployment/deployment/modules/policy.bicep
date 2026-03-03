// policy.bicep — Azure Policy assignments for AOS governance
// Assigns the standard AOS governance policy initiative to the deployment scope.

@description('Deployment environment (dev, staging, prod)')
param environment string

@description('Azure region for the deployment')
param location string

@description('List of allowed Azure locations for resources')
param allowedLocations array = [
  'eastus'
  'eastus2'
  'westus2'
  'westeurope'
  'northeurope'
]

@description('Required resource tags enforced by policy')
param requiredTags object = {
  environment: environment
  managedBy: 'aos-deployment'
}

// ── Built-in policy definition IDs ──────────────────────────────────────────
var policyAllowedLocations = 'e56962a6-4747-49cd-b67b-bf8b01975c4c'
var policyRequireHttpsStorage = '404c3081-a854-4457-ae30-26a93ef643f9'
var policyKeyVaultSoftDelete = '1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d'

// ── Allowed Locations policy assignment ─────────────────────────────────────
resource allowedLocationsAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'aos-allowed-locations-${environment}'
  properties: {
    displayName: '[AOS] Allowed locations — ${environment}'
    policyDefinitionId: tenantResourceId('Microsoft.Authorization/policyDefinitions', policyAllowedLocations)
    parameters: {
      listOfAllowedLocations: {
        value: allowedLocations
      }
    }
    enforcementMode: environment == 'prod' ? 'Default' : 'DoNotEnforce'
  }
}

// ── Require HTTPS on Storage policy assignment ───────────────────────────────
resource httpsStorageAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'aos-https-storage-${environment}'
  properties: {
    displayName: '[AOS] Require HTTPS on Storage — ${environment}'
    policyDefinitionId: tenantResourceId('Microsoft.Authorization/policyDefinitions', policyRequireHttpsStorage)
    enforcementMode: environment == 'prod' ? 'Default' : 'DoNotEnforce'
  }
}

// ── Key Vault soft-delete policy assignment ──────────────────────────────────
resource kvSoftDeleteAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'aos-kv-softdelete-${environment}'
  properties: {
    displayName: '[AOS] Key Vault soft-delete — ${environment}'
    policyDefinitionId: tenantResourceId('Microsoft.Authorization/policyDefinitions', policyKeyVaultSoftDelete)
    enforcementMode: 'Default'
  }
}

// ── Outputs ──────────────────────────────────────────────────────────────────
output allowedLocationsAssignmentId string = allowedLocationsAssignment.id
output httpsStorageAssignmentId string = httpsStorageAssignment.id
output kvSoftDeleteAssignmentId string = kvSoftDeleteAssignment.id
