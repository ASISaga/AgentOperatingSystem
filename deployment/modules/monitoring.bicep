// ============================================================================
// Monitoring Module
// Agent Operating System (AOS)
// ============================================================================
// Deploys:
// - Log Analytics Workspace
// - Application Insights
// ============================================================================

@description('Log Analytics workspace name')
param logAnalyticsName string

@description('Application Insights name')
param appInsightsName string

@description('Location for resources')
param location string

@description('Tags to apply to resources')
param tags object = {}

@description('Enable Application Insights deployment')
param enableAppInsights bool = true

@description('Log Analytics data retention in days')
param retentionInDays int = 30

// ============================================================================
// LOG ANALYTICS WORKSPACE
// ============================================================================

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = if (enableAppInsights) {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
  }
}

// ============================================================================
// APPLICATION INSIGHTS
// ============================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (enableAppInsights) {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: enableAppInsights ? logAnalyticsWorkspace.id : ''
    IngestionMode: 'LogAnalytics'
  }
}

// ============================================================================
// OUTPUTS
// ============================================================================

@description('Log Analytics workspace resource ID')
output logAnalyticsWorkspaceId string = enableAppInsights ? logAnalyticsWorkspace.id : ''

@description('Log Analytics workspace name')
output logAnalyticsWorkspaceName string = enableAppInsights ? logAnalyticsWorkspace.name : ''

@description('Application Insights resource ID')
output appInsightsId string = enableAppInsights ? appInsights.id : ''

@description('Application Insights name')
output appInsightsName string = enableAppInsights ? appInsights.name : ''

@description('Application Insights instrumentation key')
output appInsightsInstrumentationKey string = enableAppInsights ? appInsights.properties.InstrumentationKey : ''

@description('Application Insights connection string')
output appInsightsConnectionString string = enableAppInsights ? appInsights.properties.ConnectionString : ''
