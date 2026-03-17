# Azure Regional Availability Updates - Quick Start

## 🎯 What Changed

The bicep deployment template has been enhanced with **automatic regional validation and fallback** to handle Azure service availability limitations across different regions.

## 📖 Documentation Guide

This directory now contains comprehensive regional documentation:

### For Users (Start Here)
1. **[REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)** (13KB)
   - **What:** Complete guide to Azure service availability by region
   - **Why:** Helps you choose the right region for your deployment
   - **When:** Read BEFORE deploying, especially for production

### For Developers/Operators
2. **[REGIONAL_VALIDATION_FLOW.md](./REGIONAL_VALIDATION_FLOW.md)** (10KB)
   - **What:** Visual diagrams and decision trees
   - **Why:** Understand how automatic fallback works
   - **When:** When troubleshooting or understanding deployment behavior

3. **[REGIONAL_IMPLEMENTATION_SUMMARY.md](./REGIONAL_IMPLEMENTATION_SUMMARY.md)** (11KB)
   - **What:** Technical implementation details
   - **Why:** Understand the code changes and maintenance procedures
   - **When:** When modifying the template or updating regional lists

### For Reference
4. **[README.md](./README.md)** (Enhanced)
   - Now includes regional warnings and verification steps

## ⚡ Quick Start

### I just want to deploy AOS...

**For Production:**
```bash
# Use a Tier 1 region (all services available)
az deployment group create \
  --resource-group "rg-aos-prod" \
  --template-file "main.bicep" \
  --parameters location=eastus environment=prod \
               functionAppSku=EP1 serviceBusSku=Premium enableAzureML=true
```

**For Development:**
```bash
# Any supported region works, template auto-adjusts
az deployment group create \
  --resource-group "rg-aos-dev" \
  --template-file "main.bicep" \
  --parameters location=eastus environment=dev \
               functionAppSku=Y1 serviceBusSku=Standard enableAzureML=true
```

**After Deployment:**
```bash
# Check if any services were adjusted
az deployment group show \
  --resource-group "rg-aos-prod" \
  --name "deployment-name" \
  --query properties.outputs.deploymentWarnings
```

### I need to choose a region...

**Simple Answer:**
- **Production:** Use `eastus`, `eastus2`, `westus2`, `westeurope`, `northeurope`, or `southeastasia`
- **Development:** Any of the 33 supported regions (see [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md))

**Detailed Guidance:** See [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) → "Region Selection Guide"

### I deployed and got warnings...

**Check the warnings:**
```bash
az deployment group show \
  --resource-group "your-rg" \
  --name "deployment-name" \
  --query properties.outputs.deploymentWarnings.value
```

**Common warnings and what they mean:**

| Warning | Meaning | What to do |
|---------|---------|------------|
| `azureMLDisabledDueToRegion: true` | Azure ML not available in your region | Redeploy to a supported region OR disable Azure ML in parameters |
| `functionSkuDowngradedDueToRegion: true` | Functions downgraded to Consumption (Y1) | Redeploy to a region with Premium support OR accept Consumption plan |
| `serviceBusSkuDowngradedDueToRegion: true` | Service Bus downgraded to Standard | Redeploy to a region with Premium support OR accept Standard tier |

**Full troubleshooting:** See [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) → "Troubleshooting"

## 🌍 Supported Regions

### 33 Total Regions

**Tier 1 (Full Capability - Recommended for Production):**
- Americas: `eastus`, `eastus2`, `westus2`
- Europe: `westeurope`, `northeurope`
- Asia Pacific: `southeastasia`, `australiaeast`, `japaneast`

**Tier 2 (Good Coverage):**
- `westus3`, `canadacentral`, `uksouth`, `francecentral`, `swedencentral`, `koreacentral`, `centralindia`

**Tier 3 (Basic Coverage):**
- All other supported regions (see [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md))

## 🔍 What Services Are Affected

| Service | Availability | Auto-Fallback |
|---------|--------------|---------------|
| Storage, Key Vault, App Insights | ✅ All regions | N/A |
| Azure Functions (Consumption) | ✅ All regions | N/A |
| Azure Functions (Premium) | ⚠️ 27 regions | → Y1 Consumption |
| Service Bus (Standard) | ✅ All regions | N/A |
| Service Bus (Premium) | ⚠️ 27 regions | → Standard |
| Azure ML Workspace | ⚠️ 19 regions | → Disabled |

## 🛠️ Maintenance

**Updating regional lists:**
1. Monitor Azure announcements for new regions/services
2. Update arrays in `main.bicep` (lines 160-250)
3. Test deployment in new region
4. Update [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)

**For details:** See [REGIONAL_IMPLEMENTATION_SUMMARY.md](./REGIONAL_IMPLEMENTATION_SUMMARY.md) → "Maintenance Notes"

## ❓ FAQ

**Q: Do I need to change my existing deployments?**
A: No, if you're already deploying to a good region (like eastus), nothing changes.

**Q: What happens if I deploy to a region that doesn't support Azure ML?**
A: The template automatically skips Azure ML deployment and sets a warning flag. Everything else deploys normally.

**Q: Can I force deployment to fail instead of auto-adjusting?**
A: Currently no - the template prioritizes successful deployments. Check `deploymentWarnings` output to see what was adjusted.

**Q: Which region should I use for production?**
A: Use a Tier 1 region: eastus, eastus2, westus2, westeurope, northeurope, or southeastasia

**Q: How do I know if my deployment was adjusted?**
A: Check the `deploymentWarnings` output after deployment (see commands above)

**Q: Is this a breaking change?**
A: No - fully backward compatible. Existing deployments work without modification.

## 📞 Support

**For deployment issues:**
1. Check [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) troubleshooting section
2. Review deployment warnings output
3. Verify region selection
4. Open an issue: https://github.com/ASISaga/AgentOperatingSystem/issues

## 🎓 Learning Path

**New to AOS deployment:**
1. Read this README
2. Skim [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) → "Recommended Regions"
3. Deploy to a Tier 1 region
4. Check warnings output

**Planning production deployment:**
1. Read [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) → "Region Selection Guide"
2. Review [REGIONAL_VALIDATION_FLOW.md](./REGIONAL_VALIDATION_FLOW.md) → "Example Scenarios"
3. Choose appropriate region(s)
4. Test in dev/staging first

**Troubleshooting deployment:**
1. Check deployment warnings output
2. Review [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) → "Troubleshooting"
3. Compare with [REGIONAL_VALIDATION_FLOW.md](./REGIONAL_VALIDATION_FLOW.md) → "Example Scenarios"

**Contributing/Modifying:**
1. Understand [REGIONAL_IMPLEMENTATION_SUMMARY.md](./REGIONAL_IMPLEMENTATION_SUMMARY.md)
2. Review [REGIONAL_VALIDATION_FLOW.md](./REGIONAL_VALIDATION_FLOW.md) → "Maintenance Workflow"
3. Test changes in multiple regions
4. Update all documentation

---

## 🎉 Summary

The Azure regional validation feature ensures your AOS deployment succeeds regardless of region limitations, while providing clear transparency about any automatic adjustments made.

**Key Benefits:**
- ✅ Deployments always succeed (no regional failures)
- ✅ Clear warnings about adjustments
- ✅ Comprehensive documentation
- ✅ Production guidance for optimal configuration
- ✅ Flexible development options

**Remember:** Always check `deploymentWarnings` output after deployment!

For complete details, see [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)

---

**Version:** 2.0  
**Last Updated:** February 7, 2026
