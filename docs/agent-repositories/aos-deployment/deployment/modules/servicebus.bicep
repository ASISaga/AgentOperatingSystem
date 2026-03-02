// Service Bus module — namespace + orchestration queue

@description('Azure region')
param location string

@description('Deployment environment')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Base project name')
param projectName string

@description('Resource tags')
param tags object

// ====================================================================
// Variables
// ====================================================================

var namespaceName = 'sb-${projectName}-${environment}'
// Standard for prod (supports target-based scaling); Basic for non-prod to eliminate fixed base fee
var skuName = environment == 'prod' ? 'Standard' : 'Basic'
var skuTier = skuName

// ====================================================================
// Resources
// ====================================================================

resource sbNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: namespaceName
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuTier
  }
}

resource orchestrationQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: sbNamespace
  name: 'aos-orchestration-requests'
  properties: {
    maxDeliveryCount: 10
    lockDuration: 'PT1M'
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
  }
}

// ====================================================================
// Outputs
// ====================================================================

output namespaceName string = sbNamespace.name
output namespaceId string = sbNamespace.id
output queueName string = orchestrationQueue.name
