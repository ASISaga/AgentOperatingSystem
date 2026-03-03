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
// Outputs
// ====================================================================

output projectName string = aiProject.name
output projectId string = aiProject.id
output projectPrincipalId string = aiProject.identity.principalId
output projectDiscoveryUrl string = aiProject.properties.discoveryUrl
