# Azure Deployment Quick Start Guide

## 🚀 Deploy in 3 Steps

### Step 1: Prerequisites

Install Azure CLI:
```bash
# Windows (PowerShell)
winget install Microsoft.AzureCLI

# macOS
brew update && brew install azure-cli

# Linux (Ubuntu/Debian)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Login to Azure:
```bash
az login
```

### Step 2: Choose Your Deployment Method

#### Option A: Bash Script (Linux/Mac/WSL)

```bash
cd deployment
./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev"
```

#### Option B: PowerShell Script (Windows/Cross-platform)

```powershell
cd deployment
.\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev"
```

#### Option C: Direct Azure CLI

```bash
cd deployment
az group create --name "rg-aos-dev" --location "eastus"
az deployment group create \
  --name "aos-deployment-$(date +%Y%m%d)" \
  --resource-group "rg-aos-dev" \
  --template-file "main.bicep" \
  --parameters "@parameters.dev.json"
```

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

- **Full Documentation**: [README.md](./README.md)
- **Refactoring Guide**: [REFACTORING_RECOMMENDATIONS.md](./REFACTORING_RECOMMENDATIONS.md)
- **GitHub Issues**: https://github.com/ASISaga/AgentOperatingSystem/issues

## 🎯 Next Steps After Deployment

1. **Test Function Apps**
   ```bash
   curl https://aos-dev-{uniqueid}-func.azurewebsites.net/api/health
   ```

2. **View Logs**
   - Go to Application Insights in Azure Portal
   - Check "Live Metrics" and "Logs"

3. **Configure Secrets**
   - Add application secrets to Key Vault
   - Update Function App to reference them

4. **Deploy Code** (if not done during deployment)
   ```bash
   ./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev" -c
   ```

---

**Ready to deploy?** Run the command for your platform above! 🚀
