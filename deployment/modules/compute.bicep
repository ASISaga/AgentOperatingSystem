// ============================================================================
// Compute Module (Function Apps)
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - App Service Plan
// - Main Function App
// - MCP Server Function App
// - Realm Function App
// ============================================================================

@description('App Service Plan name')
param appServicePlanName string

@description('Main Function App name')
param functionAppName string

@description('MCP Server Function App name')
param mcpServerFunctionAppName string

@description('Realm Function App name')
param realmFunctionAppName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object = {}

@description('Function App SKU (Y1, EP1, EP2, EP3)')
param functionAppSku string

@description('User-assigned managed identity resource ID')
param userAssignedIdentityId string

@description('Storage account name for Function Apps')
param storageAccountName string

@description('Storage connection string')
@secure()
param storageConnectionString string

@description('Service Bus connection string')
@secure()
param serviceBusConnectionString string

@description('Key Vault URI')
param keyVaultUri string

@description('Application Insights connection string')
@secure()
param appInsightsConnectionString string = ''

@description('Environment name (dev, staging, prod)')
param environment string

@description('Enable Azure B2C Authentication')
param enableB2C bool = false

@description('Azure B2C Tenant Name')
param b2cTenantName string = ''

@description('Azure B2C Policy Name')
param b2cPolicyName string = ''

@description('Azure B2C Client ID')
@secure()
param b2cClientId string = ''

@description('Azure B2C Client Secret')
@secure()
param b2cClientSecret string = ''

// ============================================================================
// APP SERVICE PLAN
// ============================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: functionAppSku
    tier: functionAppSku == 'Y1' ? 'Dynamic' : 'ElasticPremium'
  }
  properties: {
    reserved: true // Linux
  }
  kind: 'linux'
}

// ============================================================================
// MAIN FUNCTION APP
// ============================================================================

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_SERVICEBUS_CONNECTION_STRING'
          value: serviceBusConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: storageConnectionString
        }
        {
          name: 'AZURE_STORAGE_ACCOUNT'
          value: storageAccountName
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVaultUri
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
        {
          name: 'B2C_TENANT'
          value: enableB2C ? b2cTenantName : ''
        }
        {
          name: 'B2C_POLICY'
          value: enableB2C ? b2cPolicyName : ''
        }
        {
          name: 'B2C_CLIENT_ID'
          value: enableB2C ? b2cClientId : ''
        }
        {
          name: 'B2C_CLIENT_SECRET'
          value: enableB2C ? b2cClientSecret : ''
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      pythonVersion: '3.11'
    }
    httpsOnly: true
  }
}

// ============================================================================
// MCP SERVER FUNCTION APP
// ============================================================================

resource mcpServerFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: mcpServerFunctionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(mcpServerFunctionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: storageConnectionString
        }
        {
          name: 'KEY_VAULT_URL'
          value: keyVaultUri
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

// ============================================================================
// REALM FUNCTION APP
// ============================================================================

resource realmFunctionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: realmFunctionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    reserved: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: storageConnectionString
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(realmFunctionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'AZURE_SERVICEBUS_CONNECTION_STRING'
          value: serviceBusConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: storageConnectionString
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'APP_ENVIRONMENT'
          value: environment
        }
      ]
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
    }
    httpsOnly: true
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('App Service Plan resource ID')
output appServicePlanId string = appServicePlan.id

@description('Main Function App resource ID')
output functionAppId string = functionApp.id

@description('Main Function App name')
output functionAppName string = functionApp.name

@description('Main Function App default hostname')
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'

@description('Main Function App principal ID (system-assigned identity)')
output functionAppPrincipalId string = functionApp.identity.principalId

@description('MCP Server Function App resource ID')
output mcpServerFunctionAppId string = mcpServerFunctionApp.id

@description('MCP Server Function App name')
output mcpServerFunctionAppName string = mcpServerFunctionApp.name

@description('MCP Server Function App default hostname')
output mcpServerFunctionAppUrl string = 'https://${mcpServerFunctionApp.properties.defaultHostName}'

@description('MCP Server Function App principal ID (system-assigned identity)')
output mcpServerFunctionAppPrincipalId string = mcpServerFunctionApp.identity.principalId

@description('Realm Function App resource ID')
output realmFunctionAppId string = realmFunctionApp.id

@description('Realm Function App name')
output realmFunctionAppName string = realmFunctionApp.name

@description('Realm Function App default hostname')
output realmFunctionAppUrl string = 'https://${realmFunctionApp.properties.defaultHostName}'

@description('Realm Function App principal ID (system-assigned identity)')
output realmFunctionAppPrincipalId string = realmFunctionApp.identity.principalId
