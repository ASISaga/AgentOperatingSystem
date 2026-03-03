// AI Gateway module — API Management service for AI traffic governance
// Provides rate limiting, JWT validation, and centralized routing to AI Services endpoints.
// Uses Consumption tier for dev/staging to minimize cost, Developer tier for prod.

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
@description('AI Services endpoint URL for the backend')
param aiServicesEndpoint string

@description('Application Insights instrumentation key for APIM diagnostics')
param appInsightsInstrumentationKey string

// ====================================================================
// Variables
// ====================================================================

var gatewayName = 'ai-gw-${projectName}-${environment}-${take(uniqueSuffix, 6)}'
var skuName = environment == 'prod' ? 'Developer' : 'Consumption'
// Developer SKU requires capacity >= 1; Consumption is always 0
var skuCapacity = environment == 'prod' ? 1 : 0
var publisherName = projectName
var publisherEmail = 'noreply@${projectName}.io'

// Rate-limit policy — tokens-per-minute throttling to protect backend AI Services
var rateLimitPolicy = '''<policies>
  <inbound>
    <base />
    <rate-limit-by-key calls="60" renewal-period="60"
      counter-key="@(context.Subscription?.Key ?? context.Request.IpAddress)"
      remaining-calls-header-name="x-ratelimit-remaining"
      total-calls-header-name="x-ratelimit-limit" />
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401" require-scheme="Bearer">
      <!-- Configure issuer and audience per tenant; stub shown for illustrative purposes -->
      <openid-config url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration" />
    </validate-jwt>
    <set-header name="api-key" exists-action="delete" />
    <set-backend-service base-url="{0}" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''

// ====================================================================
// Resources
// ====================================================================

resource apimService 'Microsoft.ApiManagement/service@2023-09-01-preview' = {
  name: gatewayName
  location: location
  tags: tags
  sku: {
    name: skuName
    capacity: skuCapacity
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherName: publisherName
    publisherEmail: publisherEmail
  }
}

// Application Insights logger for APIM diagnostics
resource apimLogger 'Microsoft.ApiManagement/service/loggers@2023-09-01-preview' = {
  parent: apimService
  name: 'appinsights-logger'
  properties: {
    loggerType: 'applicationInsights'
    credentials: {
      instrumentationKey: appInsightsInstrumentationKey
    }
    isBuffered: true
  }
}

// Backend pointing to the AI Services endpoint
resource aiBackend 'Microsoft.ApiManagement/service/backends@2023-09-01-preview' = {
  parent: apimService
  name: 'ai-services-backend'
  properties: {
    protocol: 'http'
    url: aiServicesEndpoint
    description: 'Azure AI Services endpoint'
    tls: {
      validateCertificateChain: true
      validateCertificateName: true
    }
  }
}

// API definition for AI Services traffic
resource aiApi 'Microsoft.ApiManagement/service/apis@2023-09-01-preview' = {
  parent: apimService
  name: 'ai-services-api'
  properties: {
    displayName: 'AI Services API'
    path: 'ai'
    protocols: [
      'https'
    ]
    subscriptionRequired: true
    serviceUrl: aiServicesEndpoint
    apiType: 'http'
  }
}

// Policy with rate limiting and JWT validation applied to the AI Services API
resource aiApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-09-01-preview' = {
  parent: aiApi
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: format(rateLimitPolicy, aiServicesEndpoint)
  }
}

// ====================================================================
// Outputs
// ====================================================================

output gatewayName string = apimService.name
output gatewayUrl string = apimService.properties.gatewayUrl
output gatewayPrincipalId string = apimService.identity.principalId
