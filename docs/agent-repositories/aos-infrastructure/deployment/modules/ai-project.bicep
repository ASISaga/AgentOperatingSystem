// AI Project module — Azure AI Foundry Project (ML Workspace, Project kind)
// A child workspace of the AI Foundry Hub that inherits its connections and governance
// settings, providing an isolated project workspace for model experimentation and deployment.

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

// Dependencies from other modules
@description('AI Foundry Hub resource ID (parent workspace)')
param hubId string

@description('AI Services account resource ID — used to assign Cognitive Services User role')
param aiServicesAccountId string

// ====================================================================
// Variables
// ====================================================================

var aiProjectName = 'ai-project-${projectName}-${environment}-${take(uniqueSuffix, 6)}'

// ====================================================================
// Resources
// ====================================================================

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' = {
  name: aiProjectName
  location: location
  kind: 'Project'
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: 'AI Foundry Project (${environment})'
    description: 'Azure AI Foundry Project for ${projectName} — ${environment}'
    hubResourceId: hubId
    publicNetworkAccess: environment == 'prod' ? 'Disabled' : 'Enabled'
  }
}

// ====================================================================
// RBAC — Cognitive Services User role for the Project Managed Identity
// ====================================================================

// Allows the Project's managed identity to call the AI Services inference API
// and to fetch LoRA adapters from the Model Registry and inject them at runtime.
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

resource cogServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiProject.id, aiProject.identity.principalId, cognitiveServicesUserRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalId: aiProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ====================================================================
// Outputs
// ====================================================================

output projectName string = aiProject.name
output projectId string = aiProject.id
output projectPrincipalId string = aiProject.identity.principalId
output projectDiscoveryUrl string = aiProject.properties.discoveryUrl
