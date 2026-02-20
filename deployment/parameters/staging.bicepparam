using '../main-modular.bicep'

// ============================================================================
// Staging Environment Parameters
// Agent Operating System (AOS)
// ============================================================================

param location = 'eastus'
param environment = 'staging'
param namePrefix = 'aos'

// Compute SKUs - Staging (Production-like for pre-production validation)
param functionAppSku = 'EP1'  // Elastic Premium (matches prod)
param serviceBusSku = 'Standard'
param storageSku = 'Standard_LRS'

// Optional Features
param enableAppInsights = true
param enableAzureML = true
param enableB2C = false

// B2C Configuration (not used in staging)
param b2cTenantName = ''
param b2cPolicyName = ''
param b2cClientId = ''
param b2cClientSecret = ''

// Admin Configuration
param adminEmail = ''

// Tags
param tags = {
  Environment: 'staging'
  Application: 'AgentOperatingSystem'
  ManagedBy: 'Bicep'
  CreatedDate: '2026-02-20'
  CostCenter: 'Engineering'
}
