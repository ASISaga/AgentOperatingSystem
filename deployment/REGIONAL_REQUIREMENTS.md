# Azure Regional Requirements for AOS Deployment

## Overview

The Agent Operating System (AOS) deployment uses several Azure services that have varying levels of regional availability. This document provides guidance on selecting appropriate Azure regions and understanding the regional constraints for each service.

**Last Updated:** February 7, 2026  
**Bicep Template Version:** 2.0

---

## Critical Information

⚠️ **IMPORTANT**: Not all Azure services used by AOS are available in all regions. The bicep template (`main.bicep`) now includes automatic validation and fallback mechanisms to ensure successful deployment even in regions with limited service availability.

### What the Template Does Automatically

1. **Validates Region Support**: Checks if the selected region supports all requested services
2. **Automatic Fallback**: Downgrades SKUs to available alternatives if premium services aren't supported
3. **Deployment Warnings**: Provides detailed output about any automatic adjustments made
4. **Regional Capability Reporting**: Reports which services are and aren't available in the selected region

---

## Regional Service Availability

### 1. Azure Machine Learning Workspace

**Availability:** Limited regions

**Supported Regions (as of Feb 2026):**
- **Americas:** East US, East US 2, West US 2, West US 3, North Central US, South Central US, Canada Central
- **Europe:** West Europe, North Europe, UK South, France Central, Germany West Central, Switzerland North, Sweden Central
- **Asia Pacific:** Southeast Asia, Japan East, Australia East, Korea Central, Central India

**Template Behavior:**
- If `enableAzureML = true` and region doesn't support Azure ML → Azure ML deployment is automatically **disabled**
- Container Registry (required for Azure ML) is also skipped if Azure ML is disabled
- Check `deploymentWarnings.azureMLDisabledDueToRegion` output to see if this occurred

**Workaround:**
- Use a supported region from the list above
- Or set `enableAzureML = false` in parameters if ML capabilities aren't required

### 2. Azure Functions Premium (Elastic Premium) Plans

**Availability:** Most regions

**SKU Options:**
- **Y1** (Consumption): Available in all Azure regions
- **EP1/EP2/EP3** (Elastic Premium): Available in most regions, but not all

**Supported Premium Regions:**
Most major regions support Elastic Premium, including:
- All US regions (East US, East US 2, West US, West US 2, West US 3, Central US, etc.)
- All major European regions (North Europe, West Europe, UK South, UK West, etc.)
- All major Asia Pacific regions (Southeast Asia, East Asia, Japan East, Australia East, etc.)

**Template Behavior:**
- If `functionAppSku = 'EP1/EP2/EP3'` and region doesn't support Premium → Automatically falls back to **Y1 (Consumption)**
- Check `deploymentWarnings.functionSkuDowngradedDueToRegion` output to see if this occurred
- `deploymentWarnings.effectiveFunctionSku` shows the actual SKU used

**Considerations:**
- Consumption plan (Y1) has cold start delays and execution time limits
- Elastic Premium provides better performance but at higher cost
- For production workloads, prefer regions that support Elastic Premium

### 3. Azure Service Bus Premium

**Availability:** Most regions

**SKU Options:**
- **Basic:** Limited features, available in most regions
- **Standard:** Full messaging features, available in most regions  
- **Premium:** VNet integration, dedicated capacity, available in most major regions

**Supported Premium Regions:**
Available in most major Azure regions including:
- All US regions
- All major European regions
- All major Asia Pacific regions

**Template Behavior:**
- If `serviceBusSku = 'Premium'` and region doesn't support Premium → Automatically falls back to **Standard**
- Check `deploymentWarnings.serviceBusSkuDowngradedDueToRegion` output to see if this occurred
- `deploymentWarnings.effectiveServiceBusSku` shows the actual SKU used

**Considerations:**
- Premium tier required for VNet integration and network isolation
- Standard tier sufficient for most messaging scenarios
- Basic tier not recommended for production (lacks topic support)

### 4. Container Registry (for Azure ML)

**Availability:** Most regions

**SKU Options:**
- **Standard:** Sufficient for most scenarios, widely available
- **Premium:** Advanced features (geo-replication, etc.), most major regions

**Template Behavior:**
- Uses **Standard** SKU by default
- Only deployed if Azure ML is enabled and supported in the region
- No automatic downgrade needed (Standard is widely available)

### 5. Other Services

The following services have excellent regional availability:

**Available in ALL Azure regions:**
- Azure Storage (Blob, Table, Queue)
- Azure Key Vault
- Azure Functions (Consumption plan - Y1)
- Azure Service Bus (Basic and Standard tiers)

**Available in MOST regions:**
- Application Insights
- Log Analytics Workspace
- Managed Identities

---

## Recommended Regions for AOS

### Tier 1: Full Capability Regions (All Services Available)

These regions support ALL AOS services including Azure ML and all premium SKUs:

**Americas:**
- `eastus` - East US (Recommended for US deployments)
- `eastus2` - East US 2
- `westus2` - West US 2 (Recommended for US West Coast)

**Europe:**
- `westeurope` - West Europe (Recommended for EU deployments)
- `northeurope` - North Europe

**Asia Pacific:**
- `southeastasia` - Southeast Asia (Recommended for APAC deployments)
- `australiaeast` - Australia East
- `japaneast` - Japan East

### Tier 2: Good Coverage (Most Services Available)

These regions support most services but may have limitations on certain advanced features:

**Americas:**
- `westus3` - West US 3
- `canadacentral` - Canada Central

**Europe:**
- `uksouth` - UK South
- `francecentral` - France Central
- `swedencentral` - Sweden Central

**Asia Pacific:**
- `koreacentral` - Korea Central
- `centralindia` - Central India

### Tier 3: Basic Coverage

These regions support core services but may lack Azure ML or premium SKUs:

- Other regions in the allowed list may have limited service availability
- Not recommended for production deployments requiring all features
- Suitable for development/testing with core services only

---

## Region Selection Guide

### For Production Deployments

**Recommended approach:**

1. **Choose a Tier 1 region** from the list above for full capability
2. **Enable all services:**
   ```json
   {
     "location": { "value": "eastus" },
     "functionAppSku": { "value": "EP1" },
     "serviceBusSku": { "value": "Premium" },
     "enableAzureML": { "value": true }
   }
   ```

3. **Consider regional pairs for DR:**
   - East US ↔ West US
   - North Europe ↔ West Europe
   - Southeast Asia ↔ East Asia

### For Development/Testing

**Cost-optimized approach:**

1. **Choose any supported region** from the allowed list
2. **Use consumption/standard SKUs:**
   ```json
   {
     "location": { "value": "eastus" },
     "functionAppSku": { "value": "Y1" },
     "serviceBusSku": { "value": "Standard" },
     "enableAzureML": { "value": true }
   }
   ```

3. Azure ML can be disabled if not needed for dev/test:
   ```json
   {
     "enableAzureML": { "value": false }
   }
   ```

### For Compliance/Data Residency

If you must use a specific region due to compliance or data residency requirements:

1. **Verify service availability** in that region using deployment warnings
2. **Accept automatic downgrades** if premium services aren't available
3. **Review deployment output** to understand what was actually deployed
4. **Consider exceptions** for non-sensitive data that could be stored in a different region

---

## Using the Template

### Deployment with Regional Validation

The template automatically validates and adjusts based on regional capabilities:

```bash
# Deploy to East US (full capability)
az deployment group create \
  --resource-group "rg-aos-prod" \
  --template-file "main.bicep" \
  --parameters location=eastus environment=prod functionAppSku=EP1 serviceBusSku=Premium enableAzureML=true

# Deploy to a limited region (automatic fallback)
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "main.bicep" \
  --parameters location=brazilsouth environment=dev functionAppSku=EP1 serviceBusSku=Premium enableAzureML=true
```

### Checking Deployment Warnings

After deployment, check the warnings output:

```bash
# Get deployment output
az deployment group show \
  --resource-group "rg-aos-prod" \
  --name "<deployment-name>" \
  --query properties.outputs.deploymentWarnings

# Example output:
{
  "azureMLDisabledDueToRegion": false,
  "functionSkuDowngradedDueToRegion": false,
  "serviceBusSkuDowngradedDueToRegion": false,
  "effectiveFunctionSku": "EP1",
  "effectiveServiceBusSku": "Premium",
  "azureMLSupported": true,
  "functionsPremiumSupported": true,
  "serviceBusPremiumSupported": true,
  "recommendedRegionsForFullCapability": [
    "eastus",
    "eastus2",
    "westus2",
    "westeurope",
    "northeurope",
    "southeastasia"
  ]
}
```

### Interpreting Warnings

**If `azureMLDisabledDueToRegion = true`:**
- Azure ML Workspace was NOT deployed
- Container Registry was NOT deployed
- LoRA training and ML features unavailable
- **Action:** Redeploy to a supported region or disable Azure ML in parameters

**If `functionSkuDowngradedDueToRegion = true`:**
- Elastic Premium SKU not available, using Consumption instead
- May experience cold starts and performance degradation
- **Action:** Use a region with Premium support or accept Consumption plan

**If `serviceBusSkuDowngradedDueToRegion = true`:**
- Premium Service Bus not available, using Standard instead
- VNet integration and dedicated capacity unavailable
- **Action:** Use a region with Premium support or accept Standard tier

---

## Updating Regional Lists

The regional capability lists are maintained in `main.bicep` as variables:

```bicep
// Define regions with full Azure ML and AI Services support
var azureMLSupportedRegions = [
  'eastus'
  'eastus2'
  // ... add new regions here
]

// Define regions with Azure Functions Premium (EP) support
var functionsPremiumSupportedRegions = [
  'eastus'
  'eastus2'
  // ... add new regions here
]

// Define regions with Service Bus Premium support
var serviceBusPremiumSupportedRegions = [
  'eastus'
  'eastus2'
  // ... add new regions here
]
```

**To update:**
1. Check Azure service availability documentation
2. Update the appropriate array in `main.bicep`
3. Test deployment in the new region
4. Update this documentation

---

## Troubleshooting

### Error: "Location not valid for this subscription"

**Cause:** The region you selected is not available in your Azure subscription

**Solution:**
- Check available regions: `az account list-locations -o table`
- Use a region from your subscription's available locations
- Contact Azure support to enable additional regions

### Error: "Resource type not available in region"

**Cause:** A required resource type is not available in the selected region, and automatic fallback didn't handle it

**Solution:**
- Check deployment warnings output
- Review this document for service availability
- Choose a recommended region from Tier 1 list
- If issue persists, disable the problematic service (e.g., set `enableAzureML=false`)

### Warning: "Azure ML disabled due to region"

**Cause:** Azure ML is not available in the selected region

**Solution:**
- This is expected behavior, not an error
- If Azure ML is required, redeploy to a supported region (Tier 1 regions)
- If Azure ML is not critical, continue with current deployment

### Performance Issues After Deployment

**Cause:** May be due to SKU downgrade (e.g., EP1 → Y1)

**Solution:**
- Check `deploymentWarnings.effectiveFunctionSku` output
- If downgraded, redeploy to a region with Premium support
- Or accept the Consumption plan performance characteristics

---

## Azure Service Documentation

For the latest regional availability information, refer to:

- **Azure Products by Region:** https://azure.microsoft.com/global-infrastructure/services/
- **Azure ML Regions:** https://azure.microsoft.com/global-infrastructure/services/?products=machine-learning-service
- **Azure Functions Regions:** https://azure.microsoft.com/global-infrastructure/services/?products=functions
- **Service Bus Regions:** https://azure.microsoft.com/global-infrastructure/services/?products=service-bus

---

## Quick Reference

| Service | All Regions | Most Regions | Limited Regions |
|---------|-------------|--------------|-----------------|
| Storage | ✅ | - | - |
| Key Vault | ✅ | - | - |
| Functions (Y1) | ✅ | - | - |
| Service Bus (Basic/Std) | ✅ | - | - |
| Functions (Premium) | - | ✅ | - |
| Service Bus (Premium) | - | ✅ | - |
| App Insights | - | ✅ | - |
| Azure ML | - | - | ✅ Limited |

**Legend:**
- ✅ = Available in all or most regions
- Limited = Available in specific regions only (see above)

---

## Support

For questions or issues related to regional deployment:

1. Check this documentation first
2. Review deployment warnings output
3. Consult Azure regional availability documentation
4. Open an issue: https://github.com/ASISaga/AgentOperatingSystem/issues

---

**Document Version:** 1.0  
**Template Version:** 2.0  
**Last Verified:** February 7, 2026
