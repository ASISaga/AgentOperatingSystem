# Regional Validation Flow

## Deployment Decision Tree

```
┌─────────────────────────────────────────────┐
│  Start: Deploy AOS to Azure Region         │
│  User specifies: location, SKUs, services  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Step 1: Location Validation               │
│  Is location in allowed 33 regions?        │
└────────┬────────────────────┬───────────────┘
         │ NO                 │ YES
         ▼                    ▼
    ┌────────┐         ┌──────────────────┐
    │ ERROR  │         │  Continue        │
    └────────┘         └────────┬─────────┘
                                │
                                ▼
              ┌─────────────────────────────────────────┐
              │  Step 2: Check Azure ML Support        │
              │  Is location in azureMLSupportedRegions?│
              └────────┬────────────────┬───────────────┘
                       │ NO             │ YES
                       ▼                ▼
              ┌────────────────┐  ┌─────────────┐
              │ azureMLEnabled │  │azureMLEnabled│
              │    = false     │  │   = true     │
              │ ⚠️ WARNING     │  │  ✅ Deploy   │
              └────────┬───────┘  └──────┬──────┘
                       │                 │
                       └────────┬────────┘
                                │
                                ▼
              ┌─────────────────────────────────────────┐
              │  Step 3: Check Functions Premium        │
              │  Is location in functionsPremiumRegions?│
              └────────┬────────────────┬───────────────┘
                       │ NO             │ YES
                       ▼                ▼
              ┌────────────────┐  ┌─────────────────┐
              │effectiveFuncSku│  │effectiveFuncSku │
              │     = 'Y1'     │  │  = requested    │
              │ ⚠️ Downgrade   │  │  ✅ Use Premium │
              └────────┬───────┘  └──────┬──────────┘
                       │                 │
                       └────────┬────────┘
                                │
                                ▼
              ┌─────────────────────────────────────────┐
              │  Step 4: Check Service Bus Premium      │
              │  Is location in serviceBusPremiumRegions?│
              └────────┬────────────────┬───────────────┘
                       │ NO             │ YES
                       ▼                ▼
              ┌────────────────┐  ┌─────────────────┐
              │effectiveSBUSku │  │effectiveSBUSku  │
              │  = 'Standard'  │  │  = 'Premium'    │
              │ ⚠️ Downgrade   │  │  ✅ Use Premium │
              └────────┬───────┘  └──────┬──────────┘
                       │                 │
                       └────────┬────────┘
                                │
                                ▼
              ┌─────────────────────────────────────────┐
              │  Step 5: Deploy Resources               │
              │  - Storage (always)                     │
              │  - Key Vault (always)                   │
              │  - Service Bus (effective SKU)          │
              │  - Functions (effective SKU)            │
              │  - App Insights (if enabled)            │
              │  - Azure ML (if azureMLEnabled)         │
              └────────────────┬────────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────────────┐
              │  Step 6: Generate Warnings Output       │
              │  deploymentWarnings = {                 │
              │    azureMLDisabledDueToRegion: bool     │
              │    functionSkuDowngraded: bool          │
              │    serviceBusSkuDowngraded: bool        │
              │    effectiveFunctionSku: string         │
              │    effectiveServiceBusSku: string       │
              │    azureMLSupported: bool               │
              │    recommendedRegions: array            │
              │  }                                      │
              └────────────────┬────────────────────────┘
                               │
                               ▼
              ┌─────────────────────────────────────────┐
              │  ✅ Deployment Complete                 │
              │  Review warnings output for adjustments │
              └─────────────────────────────────────────┘
```

## Service Deployment Matrix

| Service | Availability | Fallback Behavior |
|---------|--------------|-------------------|
| **Storage Account** | ✅ All regions | Always deployed |
| **Key Vault** | ✅ All regions | Always deployed |
| **App Service Plan** | ✅ All regions | SKU adjusted per region |
| **Function Apps** | ✅ All regions | Use effective SKU |
| **Service Bus** | ✅ All regions | SKU adjusted per region |
| **Application Insights** | ✅ Most regions | Deployed if enabled |
| **Azure ML Workspace** | ⚠️ 19 regions | Skip if not supported |
| **Container Registry** | ⚠️ Depends on ML | Skip if ML skipped |

## Regional Capability Indicators

### Legend
- ✅ **Available**: Service deployed as requested
- ⚠️ **Adjusted**: Service deployed with fallback SKU
- ❌ **Skipped**: Service not available, deployment skipped
- 📝 **Warning**: Check deploymentWarnings output

### Example Scenarios

#### Scenario 1: Deploy to East US (Tier 1)
```
Input:
  location: eastus
  functionAppSku: EP1
  serviceBusSku: Premium
  enableAzureML: true

Result:
  ✅ All services deployed as requested
  📝 No warnings
```

#### Scenario 2: Deploy to Brazil South (Limited)
```
Input:
  location: brazilsouth
  functionAppSku: EP1
  serviceBusSku: Premium
  enableAzureML: true

Result:
  ✅ Storage, Key Vault: Deployed
  ⚠️ Functions: Y1 (downgraded from EP1)
  ⚠️ Service Bus: Standard (downgraded from Premium)
  ❌ Azure ML: Not deployed
  📝 Warnings: All three limitations flagged
```

#### Scenario 3: Deploy to UK South (Good Coverage)
```
Input:
  location: uksouth
  functionAppSku: EP1
  serviceBusSku: Premium
  enableAzureML: true

Result:
  ✅ Storage, Key Vault: Deployed
  ✅ Functions: EP1 (as requested)
  ✅ Service Bus: Premium (as requested)
  ✅ Azure ML: Deployed
  📝 No warnings
```

## Quick Decision Guide

### "Which region should I use?"

```
Are you deploying for PRODUCTION?
│
├─YES──► Use Tier 1 region
│        (eastus, eastus2, westus2, westeurope, northeurope, southeastasia)
│        ✅ All services available
│        ✅ Full capability
│        ✅ No warnings
│
└─NO───► Development/Testing?
         │
         ├─Need Azure ML?─YES──► Use Tier 1 or Tier 2 region
         │                      (see REGIONAL_REQUIREMENTS.md)
         │
         └─No Azure ML──────► Any supported region OK
                             Template will auto-adjust
                             Review warnings after deployment
```

### "What if I must use a specific region?"

```
Compliance/Data Residency Requirement
│
├─1. Check REGIONAL_REQUIREMENTS.md
│    for your required region
│
├─2. Deploy with desired parameters
│    Template will auto-adjust
│
├─3. Review deploymentWarnings output
│    Understand what was adjusted
│
├─4. Accept limitations OR
│    Request exception for critical services
│
└─5. Update architecture to work
     within regional constraints
```

## Checking Deployment Results

### PowerShell
```powershell
# Get deployment warnings
$deployment = Get-AzResourceGroupDeployment -ResourceGroupName "rg-aos" -Name "deployment-name"
$deployment.Outputs.deploymentWarnings.Value

# Check specific warnings
$warnings = $deployment.Outputs.deploymentWarnings.Value
if ($warnings.azureMLDisabledDueToRegion) {
    Write-Host "⚠️ Azure ML was not deployed due to region limitation"
}
if ($warnings.functionSkuDowngradedDueToRegion) {
    Write-Host "⚠️ Functions downgraded to: $($warnings.effectiveFunctionSku)"
}
if ($warnings.serviceBusSkuDowngradedDueToRegion) {
    Write-Host "⚠️ Service Bus downgraded to: $($warnings.effectiveServiceBusSku)"
}
```

### Azure CLI
```bash
# Get deployment warnings
az deployment group show \
  --resource-group "rg-aos" \
  --name "deployment-name" \
  --query properties.outputs.deploymentWarnings.value

# Check specific warnings (jq required)
az deployment group show \
  --resource-group "rg-aos" \
  --name "deployment-name" \
  --query properties.outputs.deploymentWarnings.value | jq '{
    azureML: .azureMLDisabledDueToRegion,
    functionSku: .effectiveFunctionSku,
    serviceBusSku: .effectiveServiceBusSku
  }'
```

## Maintenance Workflow

### Adding New Azure Regions

```
1. Azure announces new region or service expansion
   │
   ▼
2. Check which services are available
   - Azure ML?
   - Functions Premium?
   - Service Bus Premium?
   │
   ▼
3. Update main.bicep arrays:
   - azureMLSupportedRegions
   - functionsPremiumSupportedRegions
   - serviceBusPremiumSupportedRegions
   │
   ▼
4. Add to location @allowed constraint
   │
   ▼
5. Test deployment in new region
   │
   ▼
6. Update REGIONAL_REQUIREMENTS.md
   - Add to appropriate tier
   - Update availability tables
   │
   ▼
7. Update recommended regions if Tier 1
```

---

## Summary

The regional validation flow ensures:

1. ✅ **Deployments always succeed** (within supported regions)
2. ⚠️ **Users are warned** about automatic adjustments
3. 📝 **Clear documentation** of what was deployed
4. 🔄 **Fallback logic** prevents deployment failures
5. 🎯 **Production guidance** ensures optimal configuration

**Remember**: Always check `deploymentWarnings` output after deployment to understand what adjustments were made for your selected region.

For detailed service availability, see [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)

For technical implementation details, see [REGIONAL_IMPLEMENTATION_SUMMARY.md](./REGIONAL_IMPLEMENTATION_SUMMARY.md)
