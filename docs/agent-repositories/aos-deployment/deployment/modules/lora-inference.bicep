// LoRA Inference module — Llama-3.3-70B-Instruct Managed Online Endpoint with Multi-LoRA support
//
// Deploys the base model as a Managed Online Endpoint on Azure AI Services.
// Multi-LoRA is enabled via deployment metadata so that LoRA adapters stored in
// the Model Registry can be injected at inference time without reloading weights.

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

@description('AI Hub workspace resource ID (parent for the endpoint)')
param hubId string

@description('AI Services account resource ID (compute backbone)')
param aiServicesAccountId string

// ====================================================================
// Variables
// ====================================================================

var endpointName = 'ep-llama-${projectName}-${environment}-${take(uniqueSuffix, 6)}'
var deploymentName = 'llama-33-70b-instruct'
var baseModelId = 'azureml://registries/azureml-meta/models/Meta-Llama-3.3-70B-Instruct/versions/1'

// ====================================================================
// Managed Online Endpoint
// ====================================================================

resource llamaEndpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2024-10-01' = {
  name: '${split(hubId, '/')[8]}/${endpointName}'
  location: location
  tags: tags
  kind: 'Managed'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'Llama-3.3-70B-Instruct Multi-LoRA inference endpoint (${environment})'
    authMode: 'Key'
    publicNetworkAccess: environment == 'prod' ? 'Disabled' : 'Enabled'
  }
}

// ====================================================================
// Base Model Deployment — Provisioned Throughput, Multi-LoRA enabled
// ====================================================================

resource llamaDeployment 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments@2024-10-01' = {
  name: '${split(hubId, '/')[8]}/${endpointName}/${deploymentName}'
  location: location
  tags: tags
  sku: {
    // Provisioned Throughput keeps base weights resident in VRAM
    name: 'Provisioned'
    capacity: 1
  }
  properties: {
    endpointComputeType: 'Managed'
    model: baseModelId
    description: 'meta-llama/Llama-3.3-70B-Instruct — Multi-LoRA base deployment'
    scaleSettings: {
      scaleType: 'Default'
    }
    requestSettings: {
      maxConcurrentRequestsPerInstance: 8
    }
    // Multi-LoRA support metadata — enables adapter injection at inference time
    // without evicting base weights from VRAM
    properties: {
      multiLora: 'enabled'
      baseModelId: baseModelId
      aiServicesAccountId: aiServicesAccountId
    }
  }
  dependsOn: [
    llamaEndpoint
  ]
}

// ====================================================================
// Outputs
// ====================================================================

output endpointName string = endpointName
output deploymentName string = deploymentName
output scoringUri string = llamaEndpoint.properties.scoringUri
