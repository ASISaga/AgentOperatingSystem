# Azure Deployment Guide for Agent Operating System

This directory contains all necessary scripts, templates, and documentation for deploying the Agent Operating System (AOS) to Microsoft Azure.

⚠️ **IMPORTANT**: Before deploying, review [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) to ensure your chosen Azure region supports all required services.

## 📁 Directory Contents

```
deployment/
├── main.bicep                          # Main Bicep infrastructure template (v2.0 with regional validation)
├── parameters.dev.json                 # Development environment parameters
├── parameters.prod.json                # Production environment parameters
├── Deploy-AOS.ps1                      # PowerShell deployment script (Windows)
├── deploy-aos.sh                       # Bash deployment script (Linux/Mac)
├── REGIONAL_REQUIREMENTS.md            # ⭐ Azure regional availability guide (NEW)
├── REFACTORING_RECOMMENDATIONS.md      # Infrastructure refactoring guide
└── README.md                           # This file
```

## 🌍 Regional Considerations

**Before you deploy**, please read [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) for critical information about:
- Azure service availability by region
- Recommended regions for full AOS capability
- Automatic fallback behavior for unsupported services
- How to interpret deployment warnings

**Recommended regions for production:** `eastus`, `eastus2`, `westus2`, `westeurope`, `northeurope`, `southeastasia`

## 🚀 Quick Start

### Prerequisites

Before deploying, ensure you have:

1. **Azure CLI** installed and configured
   - Download: https://docs.microsoft.com/cli/azure/install-azure-cli
   - Login: `az login`

2. **Bicep CLI** installed
   - Install: `az bicep install`
   - Verify: `az bicep version`

3. **Azure Subscription** with appropriate permissions
   - Owner or Contributor role on subscription
   - Ability to create resource groups and resources

4. **Region Selection** (Important!)
   - Review [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md)
   - Choose a supported region from the allowed list

5. **(Optional) For code deployment**: 
   - PowerShell 7+ (for Deploy-AOS.ps1)
   - Bash shell (for deploy-aos.sh)

### Deployment Options

#### Option 1: PowerShell Script (Recommended for Windows)

```powershell
# Basic deployment (infrastructure only)
# Use a recommended region: eastus, eastus2, westus2, westeurope, northeurope, or southeastasia
.\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev"

# Full deployment (infrastructure + code)
.\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev" -DeployCode

# Using Azure CLI instead of PowerShell modules
.\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev" -UseAzCli
```

#### Option 2: Bash Script (Recommended for Linux/Mac)

```bash
# Make script executable (first time only)
chmod +x deploy-aos.sh

# Basic deployment
./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev"

# Full deployment with code
./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev" -c

# Skip validation checks (use with caution)
./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev" --skip-pre-check
```

#### Option 3: Direct Azure CLI

```bash
# Create resource group
az group create --name "rg-aos-dev" --location "eastus"

# Deploy infrastructure
az deployment group create \
  --name "aos-deployment-$(date +%Y%m%d)" \
  --resource-group "rg-aos-dev" \
  --template-file "main.bicep" \
  --parameters "@parameters.dev.json"
```

## 📋 Deployment Script Features

### PowerShell Script (Deploy-AOS.ps1)

**Parameters:**
- `-ResourceGroupName` (required): Azure Resource Group name
- `-Location` (required): Azure region (e.g., eastus, westus2)
- `-Environment` (required): Environment (dev, staging, prod)
- `-ParametersFile` (optional): Custom parameters file path
- `-SkipPreCheck`: Skip pre-deployment validation
- `-SkipPostCheck`: Skip post-deployment verification
- `-DeployCode`: Deploy Function App code after infrastructure
- `-UseAzCli`: Use Azure CLI instead of PowerShell modules

**Features:**
- ✅ Pre-deployment prerequisite checks
- ✅ Azure authentication verification
- ✅ Bicep template validation
- ✅ Infrastructure deployment
- ✅ **Bi-directional status checking from Azure**
- ✅ Post-deployment resource verification
- ✅ Optional Function App code deployment
- ✅ Comprehensive logging
- ✅ Detailed deployment summary

### Bash Script (deploy-aos.sh)

**Options:**
- `-g, --resource-group`: Azure Resource Group name (required)
- `-l, --location`: Azure region (required)
- `-e, --environment`: Environment (dev/staging/prod) (required)
- `-p, --parameters`: Custom parameters file path (optional)
- `-c, --deploy-code`: Deploy Function App code
- `--skip-pre-check`: Skip validation
- `--skip-post-check`: Skip verification
- `-h, --help`: Show help message

**Features:**
- Same comprehensive features as PowerShell script
- Cross-platform compatibility (Linux, Mac, WSL)
- Colored console output for better readability
- JSON processing with jq

## 🏗️ Infrastructure Components

The deployment creates the following Azure resources:

### Core Services
- **Azure Functions** (3 Function Apps)
  - Main Function App (aos-{env}-func)
  - MCP Servers Function App (aos-{env}-mcp-func)
  - Realm of Agents Function App (aos-{env}-realm-func)
- **App Service Plan** (Consumption or Elastic Premium)

### Messaging
- **Azure Service Bus** Namespace
  - Queues: `aos-requests`, `businessinfinity-responses`
  - Topics: `agent-events`, `system-events`

### Storage
- **Azure Storage Account**
  - Blob Storage (container: `aos-data`)
  - Table Storage
  - Queue Storage

### Security
- **Azure Key Vault**
  - Secrets management
  - RBAC-based access
  - 7-day soft delete retention

### Monitoring
- **Application Insights**
  - Distributed tracing
  - Performance monitoring
  - Log aggregation
- **Log Analytics Workspace**
  - 30-day retention
  - Custom queries

### Machine Learning
- **Azure ML Workspace** (optional)
  - LoRA model training
  - Inference endpoints
- **Container Registry** (for ML)

### Identity
- **Managed Identities**
  - System-assigned for each Function App
  - User-assigned for cross-resource access

### RBAC Assignments
- Key Vault Secrets User (Function Apps → Key Vault)
- Storage Blob Data Contributor (Function Apps → Storage)
- Service Bus Data Owner (Function Apps → Service Bus)

## ⚙️ Configuration

### Parameters Files

Edit the parameters files to customize your deployment:

**parameters.dev.json** - Development environment
```json
{
  "location": { "value": "eastus" },
  "environment": { "value": "dev" },
  "functionAppSku": { "value": "Y1" },        // Consumption plan
  "serviceBusSku": { "value": "Standard" },
  "storageSku": { "value": "Standard_LRS" },
  "enableB2C": { "value": false },
  "enableAppInsights": { "value": true },
  "enableAzureML": { "value": true }
}
```

**parameters.prod.json** - Production environment
```json
{
  "location": { "value": "eastus" },
  "environment": { "value": "prod" },
  "functionAppSku": { "value": "EP1" },       // Elastic Premium
  "serviceBusSku": { "value": "Premium" },
  "storageSku": { "value": "Standard_GRS" },  // Geo-redundant
  "enableB2C": { "value": true },
  "enableAppInsights": { "value": true },
  "enableAzureML": { "value": true }
}
```

### Environment Variables

After deployment, configure these environment variables in Function Apps:

**Required:**
- `AZURE_SERVICEBUS_CONNECTION_STRING` - Automatically configured
- `AZURE_STORAGE_CONNECTION_STRING` - Automatically configured
- `APPLICATIONINSIGHTS_CONNECTION_STRING` - Automatically configured

**Optional (if using Azure B2C):**
- `B2C_TENANT` - Your B2C tenant name
- `B2C_POLICY` - B2C policy name
- `B2C_CLIENT_ID` - B2C application client ID
- `B2C_CLIENT_SECRET` - B2C application client secret

## 🔍 Deployment Verification

### Automated Checks

Both deployment scripts perform these verification steps:

1. **Pre-deployment:**
   - Azure CLI/PowerShell availability
   - Bicep CLI installation
   - Template file existence
   - Parameters file validation
   - Azure authentication status

2. **During deployment:**
   - Template validation
   - Resource creation monitoring
   - Error detection and logging

3. **Post-deployment:**
   - Storage Account accessibility
   - Service Bus Namespace connectivity
   - Key Vault access verification
   - Function Apps status check
   - Application Insights validation
   - **Regional capability warnings** (check deployment output)

### Checking Deployment Warnings (Important!)

After deployment, check for regional capability warnings:

```bash
# View deployment output including warnings
az deployment group show \
  --resource-group "rg-aos-dev" \
  --name "<deployment-name>" \
  --query properties.outputs.deploymentWarnings

# Example: Check if any services were downgraded due to region
az deployment group show \
  --resource-group "rg-aos-dev" \
  --name "<deployment-name>" \
  --query "properties.outputs.deploymentWarnings.value.{azureMLDisabled:azureMLDisabledDueToRegion,functionSkuDowngraded:functionSkuDowngradedDueToRegion,serviceBusDowngraded:serviceBusSkuDowngradedDueToRegion}"
```

**Understanding warnings:**
- `azureMLDisabledDueToRegion = true` → Azure ML was not deployed (region doesn't support it)
- `functionSkuDowngradedDueToRegion = true` → Elastic Premium downgraded to Consumption
- `serviceBusSkuDowngradedDueToRegion = true` → Premium Service Bus downgraded to Standard

See [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) for details on how to resolve these warnings.

### Manual Verification

After deployment, verify resources in Azure Portal:

1. Navigate to your Resource Group
2. Verify all expected resources are present
3. Check Function Apps are running
4. Test Function App endpoints
5. Review Application Insights data

### Test Endpoints

```bash
# Health check endpoint
curl https://aos-dev-{uniqueid}-func.azurewebsites.net/api/health

# Status endpoint
curl https://aos-dev-{uniqueid}-func.azurewebsites.net/api/status
```

## 📊 Monitoring Deployment

### View Deployment Status

**Azure Portal:**
1. Go to Resource Group → Deployments
2. Find your deployment by name
3. View deployment details and logs

**Azure CLI:**
```bash
# List deployments
az deployment group list --resource-group "rg-aos-dev" --output table

# Show deployment details
az deployment group show \
  --name "aos-deployment-20260207" \
  --resource-group "rg-aos-dev"

# Check deployment operations
az deployment operation group list \
  --name "aos-deployment-20260207" \
  --resource-group "rg-aos-dev"
```

### Deployment Logs

Logs are automatically created by deployment scripts:
- **PowerShell**: `deployment-{env}-{timestamp}.log`
- **Bash**: `deployment-{timestamp}.log`

## 🔧 Troubleshooting

### Common Issues

**Issue: Template validation fails**
```
Solution: Check parameters file matches template requirements
- Verify all required parameters are provided
- Check parameter types match (string, bool, int)
- Ensure SKU values are valid
```

**Issue: Resource names already exist**
```
Solution: Resource names must be globally unique
- Change the namePrefix parameter
- Or delete existing resources
- Or use a different resource group
```

**Issue: Insufficient permissions**
```
Solution: Ensure you have appropriate Azure RBAC roles
- Owner or Contributor on subscription
- User Access Administrator for role assignments
- Run: az role assignment list --assignee $(az account show --query user.name -o tsv)
```

**Issue: Bicep CLI not found**
```
Solution: Install Bicep CLI
- Azure CLI: az bicep install
- Standalone: https://docs.microsoft.com/azure/azure-resource-manager/bicep/install
```

**Issue: Deployment timeout**
```
Solution: Some resources take time to provision
- Wait for deployment to complete (can take 10-15 minutes)
- Check deployment status in Azure Portal
- Review deployment logs for specific errors
```

### Debug Mode

Enable verbose output:

**PowerShell:**
```powershell
.\Deploy-AOS.ps1 -ResourceGroupName "rg-aos-dev" -Location "eastus" -Environment "dev" -Verbose
```

**Bash:**
```bash
# Enable debug mode
set -x
./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev"
```

## 🔐 Security Best Practices

1. **Never commit secrets to git**
   - Use Key Vault for all secrets
   - Use Managed Identity instead of connection strings

2. **Review parameters before deployment**
   - Ensure production uses appropriate SKUs
   - Enable B2C only when configured
   - Use geo-redundant storage for production

3. **Network security (recommended)**
   - Implement Virtual Network integration
   - Use Private Endpoints for storage and Service Bus
   - Configure Network Security Groups

4. **Access control**
   - Use RBAC instead of Key Vault access policies
   - Follow principle of least privilege
   - Regular access reviews

See [REFACTORING_RECOMMENDATIONS.md](./REFACTORING_RECOMMENDATIONS.md) for comprehensive security improvements.

## 📈 Scaling Recommendations

### Development Environment
- Consumption plan for Functions (Y1)
- Basic/Standard Service Bus
- Standard_LRS storage
- Minimal monitoring

### Production Environment
- Elastic Premium for Functions (EP1/EP2)
- Premium Service Bus (for VNet support)
- Standard_GRS storage (geo-redundant)
- Full monitoring and alerting

### Multi-Region Deployment

For high availability, deploy to multiple regions:

```bash
# Deploy to primary region
./deploy-aos.sh -g "rg-aos-prod-eastus" -l "eastus" -e "prod"

# Deploy to secondary region
./deploy-aos.sh -g "rg-aos-prod-westus" -l "westus2" -e "prod"

# Configure Traffic Manager for failover (manual step)
```

## 💰 Cost Estimation

### Development (~$50-100/month)
- Function Apps (Consumption): ~$0-20
- Service Bus (Standard): ~$10
- Storage (Standard_LRS): ~$5
- Application Insights: ~$5-10
- Azure ML: ~$0-50 (usage-based)

### Production (~$500-1500/month)
- Function Apps (EP1): ~$150-300
- Service Bus (Premium): ~$100
- Storage (Standard_GRS): ~$20-50
- Application Insights: ~$20-50
- Azure ML: ~$100-500 (usage-based)
- Data transfer: ~$50-100

Use Azure Pricing Calculator for detailed estimates: https://azure.microsoft.com/pricing/calculator/

## 📚 Additional Resources

- **⭐ Regional Requirements**: [REGIONAL_REQUIREMENTS.md](./REGIONAL_REQUIREMENTS.md) - Azure service availability by region
- **Architecture Documentation**: [../docs/architecture/ARCHITECTURE.md](../docs/architecture/ARCHITECTURE.md)
- **Refactoring Guide**: [REFACTORING_RECOMMENDATIONS.md](./REFACTORING_RECOMMENDATIONS.md)
- **Azure Functions Documentation**: https://docs.microsoft.com/azure/azure-functions/
- **Bicep Documentation**: https://docs.microsoft.com/azure/azure-resource-manager/bicep/
- **Azure Well-Architected Framework**: https://docs.microsoft.com/azure/architecture/framework/
- **Azure Products by Region**: https://azure.microsoft.com/global-infrastructure/services/

## 🤝 Contributing

To improve deployment scripts:

1. Test changes in development environment
2. Update both PowerShell and Bash scripts
3. Update parameters files if needed
4. Update this README and REGIONAL_REQUIREMENTS.md if adding new services
5. Submit pull request

## 📝 Version History

- **2.0.0** (2026-02-07): Regional validation and automatic fallback
  - Added regional capability validation
  - Automatic SKU downgrade for unsupported regions
  - Comprehensive regional requirements documentation
  - Deployment warnings output
  
- **1.0.0** (2026-02-07): Initial deployment scripts and documentation
  - Bicep template for all infrastructure
  - PowerShell deployment script
  - Bash deployment script
  - Comprehensive refactoring recommendations

## 📞 Support

For issues with deployment:
1. Check troubleshooting section above
2. Review deployment logs
3. Check Azure Portal deployment status
4. Open an issue on GitHub: https://github.com/ASISaga/AgentOperatingSystem/issues

---

**Last Updated**: February 7, 2026  
**Maintained By**: Agent Operating System Team
