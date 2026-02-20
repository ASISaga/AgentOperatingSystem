// ============================================================================
// Storage Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Storage Account
// - Blob Services and Containers
// - Table Services
// - Queue Services
// ============================================================================

@description('Storage account name (must be globally unique, 3-24 chars, lowercase alphanumeric)')
param storageAccountName string

@description('Location for the storage account')
param location string

@description('Storage account SKU')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
  'Standard_RAGRS'
  'Premium_LRS'
])
param storageSku string = 'Standard_LRS'

@description('Tags to apply to resources')
param tags object = {}

@description('Name of the blob container for AOS data')
param blobContainerName string = 'aos-data'

// ============================================================================
// STORAGE ACCOUNT
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow' // Set to 'Deny' in production with specific rules
      bypass: 'AzureServices'
    }
  }
}

// ============================================================================
// BLOB SERVICES
// ============================================================================

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

// Blob Container for AOS data
resource aosDataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: blobContainerName
  properties: {
    publicAccess: 'None'
  }
}

// ============================================================================
// TABLE SERVICES
// ============================================================================

resource tableServices 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// ============================================================================
// QUEUE SERVICES
// ============================================================================

resource queueServices 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Storage account resource ID')
output storageAccountId string = storageAccount.id

@description('Storage account name')
output storageAccountName string = storageAccount.name

@description('Storage account primary endpoints')
output storageAccountEndpoints object = storageAccount.properties.primaryEndpoints

@description('Storage connection string (contains secrets)')
@secure()
output storageConnectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'

@description('Blob container name')
output blobContainerName string = aosDataContainer.name
