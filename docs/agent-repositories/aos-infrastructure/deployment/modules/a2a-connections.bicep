// A2A Connections module — Agent-to-Agent connections for C-suite boardroom
//
// Creates Microsoft.MachineLearningServices/workspaces/connections of type
// Agent2Agent for each specialist agent in the C-suite, enabling the CEO
// (chairperson) to dynamically discover, consult, and delegate to specialists
// through the Azure AI Foundry Agent Service.
//
// All A2A traffic routes through the Foundry Private Link substrate — no
// public endpoint communication is permitted (Zero-Trust).

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

@description('AI Foundry Project resource name — parent workspace for A2A connections')
param aiProjectName string

@description('AI Gateway URL — used as the A2A endpoint target')
param aiGatewayUrl string

// ====================================================================
// Variables
// ====================================================================

// C-suite specialist roles that the CEO can consult via A2A
var specialistRoles = [
  'cfo'
  'cto'
  'cso'
  'cmo'
]

// ====================================================================
// Resources
// ====================================================================

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-10-01' existing = {
  name: aiProjectName
}

// One A2A connection per specialist agent
resource a2aConnections 'Microsoft.MachineLearningServices/workspaces/connections@2024-10-01' = [for role in specialistRoles: {
  parent: aiProject
  name: 'a2a-connection-${role}'
  properties: {
    category: 'Agent2Agent'
    target: aiGatewayUrl
    authType: 'ManagedIdentity'
    metadata: {
      agentRole: role
      environment: environment
      projectName: projectName
    }
  }
}]

// ====================================================================
// Outputs
// ====================================================================

output connectionNames array = [for (role, i) in specialistRoles: a2aConnections[i].name]
output connectionCount int = length(specialistRoles)
