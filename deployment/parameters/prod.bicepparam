using '../main-modular.bicep'

// ============================================================================
// Production Environment Parameters
// Agent Operating System (AOS)
// ============================================================================

param location = 'eastus'
param environment = 'prod'
param namePrefix = 'aos'

// Compute SKUs - Production (Performance-optimized)
param functionAppSku = 'EP1'  // Elastic Premium
param serviceBusSku = 'Premium'
param storageSku = 'Standard_GRS'  // Geo-redundant

// Optional Features
param enableAppInsights = true
param enableAzureML = true
param enableB2C = true

// B2C Configuration (replace with actual values)
param b2cTenantName = 'YOUR_B2C_TENANT_NAME'
param b2cPolicyName = 'YOUR_B2C_POLICY_NAME'
param b2cClientId = 'YOUR_B2C_CLIENT_ID'
param b2cClientSecret = 'YOUR_B2C_CLIENT_SECRET'

// Tags
param tags = {
  Environment: 'prod'
  Application: 'AgentOperatingSystem'
  ManagedBy: 'Bicep'
  CreatedDate: '2026-02-07'
  CostCenter: 'Engineering'
  Compliance: 'SOC2'
}
