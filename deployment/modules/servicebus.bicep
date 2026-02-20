// ============================================================================
// Service Bus Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Service Bus Namespace
// - Queues
// - Topics and Subscriptions
// ============================================================================

@description('Service Bus namespace name')
param serviceBusNamespaceName string

@description('Location for the Service Bus')
param location string

@description('Service Bus SKU')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param serviceBusSku string = 'Standard'

@description('Tags to apply to resources')
param tags object = {}

@description('Array of queue names to create')
param queueNames array = []

@description('Array of topic names to create')
param topicNames array = []

// ============================================================================
// SERVICE BUS NAMESPACE
// ============================================================================

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: serviceBusNamespaceName
  location: location
  tags: tags
  sku: {
    name: serviceBusSku
    tier: serviceBusSku
  }
  properties: {
    minimumTlsVersion: '1.2'
  }
}

// ============================================================================
// SERVICE BUS QUEUES
// ============================================================================

resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = [for queue in queueNames: {
  parent: serviceBusNamespace
  name: queue
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
    enableBatchedOperations: true
    maxDeliveryCount: 10
  }
}]

// ============================================================================
// SERVICE BUS TOPICS
// ============================================================================

resource serviceBusTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = [for topic in topicNames: {
  parent: serviceBusNamespace
  name: topic
  properties: {
    maxSizeInMegabytes: 1024
    defaultMessageTimeToLive: 'P14D'
    enableBatchedOperations: true
  }
}]

// ============================================================================
// TOPIC SUBSCRIPTIONS (Default)
// ============================================================================

resource serviceBusSubscription 'Microsoft.ServiceBus/namespaces/topics/subscriptions@2022-10-01-preview' = [for (topic, i) in topicNames: {
  parent: serviceBusTopic[i]
  name: 'default-subscription'
  properties: {
    lockDuration: 'PT5M'
    requiresSession: false
    defaultMessageTimeToLive: 'P14D'
    deadLetteringOnMessageExpiration: true
    maxDeliveryCount: 10
  }
}]

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Service Bus namespace resource ID')
output serviceBusNamespaceId string = serviceBusNamespace.id

@description('Service Bus namespace name')
output serviceBusNamespaceName string = serviceBusNamespace.name

#disable-next-line outputs-should-not-contain-secrets
@description('Service Bus connection string (contains secrets)')
@secure()
output serviceBusConnectionString string = listKeys('${serviceBusNamespace.id}/AuthorizationRules/RootManageSharedAccessKey', serviceBusNamespace.apiVersion).primaryConnectionString

@description('Service Bus endpoint')
output serviceBusEndpoint string = serviceBusNamespace.properties.serviceBusEndpoint
