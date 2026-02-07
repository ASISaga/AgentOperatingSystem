# Azure Deployment Quick Start Guide

## 🚀 Deploy in 3 Steps

### Step 1: Prerequisites

Install Azure CLI and Python:
```bash
# Windows (PowerShell)
winget install Microsoft.AzureCLI
winget install Python.Python.3.11

# macOS
brew update && brew install azure-cli python@3.11

# Linux (Ubuntu/Debian)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
sudo apt install python3 python3-pip
```

Login to Azure:
```bash
az login
```

Install Bicep:
```bash
az bicep install
```

### Step 2: Deploy with Python Orchestrator (Recommended)

```bash
cd deployment

# Development deployment
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam"

# Production deployment
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus2" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam"
```

The orchestrator provides:
- ✅ Mandatory Bicep linting with error gates
- ✅ What-if analysis and destructive change detection
- ✅ Post-deployment health verification
- ✅ Smart retry strategies for environmental failures
- ✅ Complete audit trail with Git SHA linkage

#### Alternative: Direct Azure CLI (Not Recommended)

```bash
cd deployment
az group create --name "rg-aos-dev" --location "eastus"
az deployment group create \
  --name "aos-deployment-$(date +%Y%m%d)" \
  --resource-group "rg-aos-dev" \
  --template-file "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam"
```

> **Note**: Direct CLI deployment lacks quality gates, health checks, and audit features.

#### Legacy Scripts (Deprecated)

The bash and PowerShell scripts in `legacy/` are deprecated. Use the Python orchestrator instead.

### Step 3: Verify Deployment

Check Azure Portal:
1. Go to https://portal.azure.com
2. Navigate to your resource group
3. Verify all resources are created

Or use Azure CLI:
```bash
az resource list --resource-group "rg-aos-dev" --output table
```

## 📋 What Gets Deployed?

✅ 3 Azure Function Apps  
✅ Service Bus Namespace with Queues and Topics  
✅ Storage Account (Blob, Table, Queue)  
✅ Key Vault for secrets  
✅ Application Insights for monitoring  
✅ Azure ML Workspace (optional)  
✅ Managed Identities for security  

## ⏱️ Deployment Time

- **Development**: ~10-15 minutes
- **Production**: ~15-20 minutes (includes ML workspace)

## 💡 Common Commands

### List deployments
```bash
az deployment group list --resource-group "rg-aos-dev" --output table
```

### Show deployment status
```bash
az deployment group show \
  --name "your-deployment-name" \
  --resource-group "rg-aos-dev"
```

### Delete deployment (cleanup)
```bash
az group delete --name "rg-aos-dev" --yes --no-wait
```

## 🔍 Troubleshooting

### Issue: "Template validation failed"
**Solution**: Check your parameters file matches the environment

### Issue: "Resource name already exists"
**Solution**: Resource names must be globally unique. Edit `namePrefix` in parameters file

### Issue: "Insufficient permissions"
**Solution**: Ensure you have Owner/Contributor role on subscription

## 📚 Need More Help?

- **Orchestrator Guide**: [ORCHESTRATOR_USER_GUIDE.md](./ORCHESTRATOR_USER_GUIDE.md)
- **Full Documentation**: [README.md](./README.md)
- **Regional Requirements**: [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **Refactoring Guide**: [REFACTORING_RECOMMENDATIONS.md](./REFACTORING_RECOMMENDATIONS.md)
- **GitHub Issues**: https://github.com/ASISaga/AgentOperatingSystem/issues

## 🎯 Next Steps After Deployment

1. **Check Deployment Audit Log**
   ```bash
   # View deployment audit trail (created by orchestrator)
   cat deployment/audit/deployment-*.json
   ```

2. **Test Function Apps**
   ```bash
   curl https://aos-dev-{uniqueid}-func.azurewebsites.net/api/health
   ```

3. **View Logs**
   - Go to Application Insights in Azure Portal
   - Check "Live Metrics" and "Logs"

4. **Configure Secrets**
   - Add application secrets to Key Vault
   - Update Function App to reference them

---

**Ready to deploy?** Use the Python orchestrator command above! 🚀
