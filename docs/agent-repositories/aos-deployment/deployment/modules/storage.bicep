// Storage module — Storage Account for AOS function app

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

// Storage account names: 3-24 lowercase alphanumeric only
var storageAccountName = 'st${projectName}${environment}${take(uniqueSuffix, 8)}'
// LRS for all environments — halves the base storage rate vs GRS; ZRS is available if zone resilience is needed
var skuName = environment == 'prod' ? 'Standard_ZRS' : 'Standard_LRS'

// ====================================================================
// Resources
// ====================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: skuName
  }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    // Explicit Hot tier minimises per-transaction costs for the active function apps
    accessTier: 'Hot'
  }
}

// ====================================================================
// Outputs
// ====================================================================

output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
