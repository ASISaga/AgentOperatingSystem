// Monitoring module — Log Analytics workspace + Application Insights

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

var workspaceName = 'log-${projectName}-${environment}'
var appInsightsName = 'appi-${projectName}-${environment}'
var retentionDays = environment == 'prod' ? 90 : (environment == 'staging' ? 60 : 30)

// ====================================================================
// Resources
// ====================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionDays
    // Daily ingestion cap prevents heartbeat logs from bloating the bill during idle periods
    workspaceCapping: {
      dailyQuotaGb: environment == 'prod' ? 5 : 1
    }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// ====================================================================
// Outputs
// ====================================================================

output workspaceId string = logAnalytics.id
output workspaceName string = logAnalytics.name
output appInsightsName string = appInsights.name
output appInsightsId string = appInsights.id
output instrumentationKey string = appInsights.properties.InstrumentationKey
output connectionString string = appInsights.properties.ConnectionString
