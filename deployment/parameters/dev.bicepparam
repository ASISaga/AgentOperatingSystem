using '../main-modular.bicep'

// ============================================================================
// Development Environment Parameters
// Agent Operating System (AOS)
// ============================================================================

param location = 'eastus'
param environment = 'dev'
param namePrefix = 'aos'

// Compute SKUs - Development (Cost-optimized)
param functionAppSku = 'Y1'  // Consumption plan
param serviceBusSku = 'Standard'
param storageSku = 'Standard_LRS'

// Optional Features
param enableAppInsights = true
param enableAzureML = true
param enableB2C = false

// B2C Configuration (not used in dev)
param b2cTenantName = ''
param b2cPolicyName = ''
param b2cClientId = ''
param b2cClientSecret = ''

// Admin Configuration
param adminEmail = ''

// Tags
param tags = {
  Environment: 'dev'
  Application: 'AgentOperatingSystem'
  ManagedBy: 'Bicep'
  CreatedDate: '2026-02-07'
  CostCenter: 'Engineering'
}
