// Model Registry module — Azure AI Foundry Model Registry linked to the Hub
//
// Provides permanent storage for LoRA adapter assets (adapter_model.bin +
// adapter_config.json) registered as MLflow Model Assets.  The registry is
// attached to the Hub workspace so that all Foundry projects that descend from
// the hub can discover and pull adapters by name/version.

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

@description('Storage account resource ID for registry artefact backing store')
param storageAccountId string

// ====================================================================
// Variables
// ====================================================================

var registryName = 'mlreg-${projectName}-${environment}-${take(uniqueSuffix, 6)}'

// ====================================================================
// Model Registry (Azure ML Registry)
// ====================================================================

resource modelRegistry 'Microsoft.MachineLearningServices/registries@2024-10-01' = {
  name: registryName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'AOS LoRA Adapter Registry — stores fine-tuned adapter assets for ${projectName} (${environment})'
    publicNetworkAccess: environment == 'prod' ? 'Disabled' : 'Enabled'
    regionDetails: [
      {
        location: location
        storageConfig: {
          storageAccountHnsEnabled: false
        }
      }
    ]
  }
}

// ====================================================================
// Outputs
// ====================================================================

output registryName string = modelRegistry.name
output registryId string = modelRegistry.id
output registryPrincipalId string = modelRegistry.identity.principalId
