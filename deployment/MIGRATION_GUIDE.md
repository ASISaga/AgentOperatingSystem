# Migration Guide: Monolithic to Modular Bicep

This guide helps you transition from the original monolithic `main.bicep` to the new modular architecture.

## Overview

The AOS deployment has been refactored from a single 858-line bicep file into a modular architecture with 8 focused modules and modern bicepparam parameter files.

## ✅ What's Changed

### File Structure

**Before:**
```
deployment/
├── main.bicep              # 858 lines, all resources
├── parameters.dev.json     # JSON parameters
└── parameters.prod.json    # JSON parameters
```

**After:**
```
deployment/
├── main.bicep              # Original (kept for reference)
├── main-modular.bicep      # New orchestrator (467 lines)
├── modules/                # 8 focused modules
│   ├── storage.bicep
│   ├── monitoring.bicep
│   ├── servicebus.bicep
│   ├── keyvault.bicep
│   ├── identity.bicep
│   ├── compute.bicep
│   ├── machinelearning.bicep
│   └── rbac.bicep
└── parameters/             # Modern bicepparam files
    ├── dev.bicepparam
    └── prod.bicepparam
```

### Deployment Commands

**Before:**
```bash
# JSON parameters
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "main.bicep" \
  --parameters "@parameters.dev.json"
```

**After (Recommended):**
```bash
# Bicepparam files
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam"
```

## 🔄 Migration Options

### Option 1: Gradual Migration (Recommended)

Keep both versions side-by-side during transition:

1. **Test new modular deployment** in dev/test environment:
   ```bash
   az deployment group create \
     --resource-group "rg-aos-test" \
     --template-file "main-modular.bicep" \
     --parameters "parameters/dev.bicepparam"
   ```

2. **Verify outputs match** original deployment
3. **Update CI/CD pipelines** to use new template
4. **Deploy to production** when confident

### Option 2: Direct Switch

Switch immediately if you're comfortable:

1. Update deployment scripts/pipelines to use `main-modular.bicep`
2. Convert existing parameters to bicepparam format
3. Deploy

### Option 3: Continue Using Original

The original `main.bicep` is still available and will continue to work. However, it won't receive new features.

## 📋 Parameter Migration

### JSON to Bicepparam Conversion

**Old (JSON):**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {
      "value": "eastus"
    },
    "environment": {
      "value": "dev"
    },
    "functionAppSku": {
      "value": "Y1"
    }
  }
}
```

**New (Bicepparam):**
```bicep
using './main-modular.bicep'

param location = 'eastus'
param environment = 'dev'
param functionAppSku = 'Y1'
```

### Parameter Compatibility

✅ **No parameter changes required!** The modular template accepts the same parameters as the original:

- `location`
- `environment`
- `namePrefix`
- `uniqueSuffix`
- `functionAppSku`
- `serviceBusSku`
- `storageSku`
- `enableB2C`, `b2cTenantName`, `b2cPolicyName`, `b2cClientId`, `b2cClientSecret`
- `enableAppInsights`
- `enableAzureML`
- `adminEmail`
- `tags`

### Converting Your Parameters

**Automated Conversion (if needed):**
```bash
# Simple conversion script
cat parameters.dev.json | jq -r '
  "using \"./main-modular.bicep\"\n\n" +
  (.parameters | to_entries | map(
    "param \(.key) = " + (
      if .value.value | type == "string" then "'\(.value.value)'"
      elif .value.value | type == "boolean" then "\(.value.value)"
      elif .value.value | type == "number" then "\(.value.value)"
      elif .value.value | type == "object" then "\(.value.value | tojson)"
      elif .value.value | type == "array" then "\(.value.value | tojson)"
      else .value.value | tostring
      end
    )
  ) | join("\n"))
' > parameters/dev.bicepparam
```

## 🎯 Output Compatibility

✅ **All outputs preserved!** The modular template produces the same outputs as the original:

| Category | Outputs |
|----------|---------|
| **General** | resourceGroupName, location, environment |
| **Storage** | storageAccountName, storageAccountId, storageConnectionString |
| **Service Bus** | serviceBusNamespaceName, serviceBusNamespaceId, serviceBusConnectionString |
| **Key Vault** | keyVaultName, keyVaultId, keyVaultUri |
| **Monitoring** | appInsightsName, appInsightsId, appInsightsInstrumentationKey, appInsightsConnectionString |
| **Functions** | functionAppName, functionAppId, functionAppUrl, mcpServerFunctionAppName/Url, realmFunctionAppName/Url |
| **Azure ML** | azureMLWorkspaceName, azureMLWorkspaceId |
| **Identity** | userAssignedIdentityId, userAssignedIdentityPrincipalId, userAssignedIdentityClientId |
| **Warnings** | deploymentWarnings (regional capability info) |

**Scripts using outputs will continue to work without changes!**

## 🔍 What's Different Under the Hood

### Resource Organization

Resources are now organized into logical modules:

| Original Section | New Module |
|------------------|------------|
| Storage Account + Services | storage.bicep |
| Log Analytics + App Insights | monitoring.bicep |
| Service Bus + Queues + Topics | servicebus.bicep |
| Key Vault | keyvault.bicep |
| Managed Identity | identity.bicep |
| App Service Plan + Function Apps | compute.bicep |
| Azure ML + Container Registry | machinelearning.bicep |
| Role Assignments | rbac.bicep |

### Deployment Order

The orchestrator (`main-modular.bicep`) deploys modules in the correct order:

1. **Foundation**: Storage, Monitoring, Service Bus, Key Vault, Identity (parallel)
2. **Compute**: Function Apps (depends on foundation)
3. **ML**: Azure ML Workspace (conditional, depends on foundation)
4. **Security**: RBAC role assignments (depends on all above)

## 🚀 CI/CD Pipeline Updates

### Azure DevOps

**Before:**
```yaml
- task: AzureResourceManagerTemplateDeployment@3
  inputs:
    deploymentScope: 'Resource Group'
    azureResourceManagerConnection: '$(ServiceConnection)'
    resourceGroupName: '$(ResourceGroupName)'
    location: '$(Location)'
    templateLocation: 'Linked artifact'
    csmFile: 'deployment/main.bicep'
    csmParametersFile: 'deployment/parameters.dev.json'
```

**After:**
```yaml
- task: AzureResourceManagerTemplateDeployment@3
  inputs:
    deploymentScope: 'Resource Group'
    azureResourceManagerConnection: '$(ServiceConnection)'
    resourceGroupName: '$(ResourceGroupName)'
    location: '$(Location)'
    templateLocation: 'Linked artifact'
    csmFile: 'deployment/main-modular.bicep'
    csmParametersFile: 'deployment/parameters/dev.bicepparam'
```

### GitHub Actions

**Before:**
```yaml
- name: Deploy AOS Infrastructure
  uses: azure/arm-deploy@v1
  with:
    subscriptionId: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    resourceGroupName: rg-aos-dev
    template: deployment/main.bicep
    parameters: deployment/parameters.dev.json
```

**After:**
```yaml
- name: Deploy AOS Infrastructure
  uses: azure/arm-deploy@v1
  with:
    subscriptionId: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    resourceGroupName: rg-aos-dev
    template: deployment/main-modular.bicep
    parameters: deployment/parameters/dev.bicepparam
```

### PowerShell Scripts

Update `Deploy-AOS.ps1`:

```powershell
# Change template file reference
$TemplateFile = Join-Path $PSScriptRoot "main-modular.bicep"

# Change parameters file reference (if using file-based params)
$ParametersFile = Join-Path $PSScriptRoot "parameters" "$Environment.bicepparam"
```

### Bash Scripts

Update `deploy-aos.sh`:

```bash
# Change template file
TEMPLATE_FILE="${SCRIPT_DIR}/main-modular.bicep"

# Change parameters file
PARAMETERS_FILE="${SCRIPT_DIR}/parameters/${ENVIRONMENT}.bicepparam"
```

## ⚠️ Important Notes

### No Resource Deletion

The modular template deploys the **same resources** as the original. Azure will update resources in-place when you switch templates. **No resources will be deleted.**

### State Preservation

Azure tracks deployment state by:
- Resource group
- Resource names
- Resource types

Since the modular template uses the same names and types, Azure recognizes them as updates to existing resources.

### First Deployment After Migration

The first deployment using the modular template may show many resources as "modified" even though configuration hasn't changed. This is normal - Azure is updating metadata.

### Regional Validation

Both templates include the same regional validation logic:
- Automatic SKU downgrades in unsupported regions
- Azure ML conditional deployment
- `deploymentWarnings` output

## 🧪 Testing Your Migration

### 1. Validate Template

```bash
cd deployment
az bicep build --file main-modular.bicep
```

### 2. What-If Analysis

```bash
az deployment group what-if \
  --resource-group "rg-aos-dev" \
  --template-file "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam"
```

Review the what-if output to verify expected changes.

### 3. Test Deployment

Deploy to a test environment first:

```bash
az deployment group create \
  --resource-group "rg-aos-test" \
  --template-file "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam"
```

### 4. Verify Outputs

```bash
# Get deployment outputs
az deployment group show \
  --resource-group "rg-aos-test" \
  --name "<deployment-name>" \
  --query properties.outputs

# Compare with original deployment outputs
```

### 5. Validate Resources

```bash
# Check all resources deployed
az resource list \
  --resource-group "rg-aos-test" \
  --output table

# Verify specific resources
az storage account show -n <storage-name> -g rg-aos-test
az functionapp show -n <function-name> -g rg-aos-test
```

## 🆘 Troubleshooting

### Issue: "Module not found"

**Cause**: Bicepparam file references wrong path

**Fix**: Update the `using` statement in bicepparam file:
```bicep
using '../main-modular.bicep'  // From parameters/ directory
```

### Issue: "Deployment fails with missing parameters"

**Cause**: Bicepparam file missing required parameters

**Fix**: Ensure all required parameters from original JSON are in bicepparam file

### Issue: "Unexpected resource changes in what-if"

**Cause**: Normal for first deployment with new template

**Fix**: Review changes carefully - if they're just metadata/formatting, it's safe to proceed

### Issue: "Can't find module X"

**Cause**: Deploying from wrong directory

**Fix**: Deploy from deployment/ directory or use absolute paths

## 📞 Support

If you encounter issues during migration:

1. Check this migration guide
2. Review [modules/README.md](modules/README.md)
3. Compare parameters with original template
4. Test with what-if deployment
5. Open an issue on GitHub with deployment logs

## ✅ Migration Checklist

- [ ] Review new modular architecture
- [ ] Test modular template in dev/test environment
- [ ] Create bicepparam files for your environments
- [ ] Update CI/CD pipelines
- [ ] Update deployment scripts
- [ ] Perform what-if analysis
- [ ] Deploy to test environment
- [ ] Verify outputs match original
- [ ] Deploy to production
- [ ] Update documentation
- [ ] Train team on new structure

## 🎉 Benefits of Migration

After migrating to the modular architecture:

✅ **Better Organization**: Focused modules instead of one large file  
✅ **Easier Maintenance**: Update specific modules without touching others  
✅ **Reusability**: Use modules in other projects  
✅ **Modern Tooling**: Bicepparam format with better IDE support  
✅ **Testability**: Test individual modules independently  
✅ **Scalability**: Add new modules without modifying existing ones  

---

**Last Updated**: February 7, 2026  
**Questions?** Open an issue or check the main [README](README.md)
