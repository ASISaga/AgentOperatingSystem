# Agent Operating System - Deployment Plan

**Version:** 2.0.0  
**Last Updated:** February 13, 2026  
**Target Platform:** Microsoft Azure

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Phase](#pre-deployment-phase)
3. [Infrastructure Deployment Phase](#infrastructure-deployment-phase)
4. [Application Deployment Phase](#application-deployment-phase)
5. [Post-Deployment Phase](#post-deployment-phase)
6. [Production Readiness Phase](#production-readiness-phase)
7. [Rollback Procedures](#rollback-procedures)
8. [Deployment Architecture](#deployment-architecture)
9. [Security Considerations](#security-considerations)
10. [Monitoring and Observability](#monitoring-and-observability)
11. [Disaster Recovery](#disaster-recovery)

---

## Overview

This document provides a comprehensive deployment plan for the Agent Operating System (AOS) to Microsoft Azure. The deployment follows a phased approach with quality gates and verification at each stage.

### Deployment Philosophy

- **Infrastructure as Code (IaC)**: All infrastructure defined in Bicep templates
- **Quality-First**: Mandatory linting, validation, and health checks
- **Safety-Driven**: What-if analysis and destructive change confirmation
- **Traceable**: Complete audit trail with Git SHA linkage
- **Resilient**: Smart retry logic and failure classification

### Deployment Methods

1. **Python Orchestrator (Recommended)**: Production-grade deployment with quality gates
   - Location: `deployment/deploy.py`
   - Features: Linting, what-if, health checks, audit trail, smart retries

2. **Direct Azure CLI**: Manual deployment without quality gates
   - Use only for testing or when orchestrator is unavailable

3. **Legacy Scripts (Deprecated)**: Bash/PowerShell scripts in `deployment/legacy/`
   - Maintained for backward compatibility only

### Supported Environments

- **Development (`dev`)**: Testing and development work
- **Staging (`staging`)**: Pre-production validation
- **Production (`prod`)**: Live production environment

---

## Pre-Deployment Phase

### 1. Prerequisites Validation

#### Required Tools

| Tool | Version | Installation | Verification |
|------|---------|--------------|--------------|
| Azure CLI | Latest | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` | `az --version` |
| Bicep CLI | Latest | `az bicep install` | `az bicep version` |
| Python | 3.10+ | OS package manager | `python3 --version` |
| Git | Latest | OS package manager | `git --version` |

#### Azure Subscription Setup

1. **Subscription Access**
   - Owner or Contributor role
   - User Access Administrator for RBAC assignments
   - Verify: `az role assignment list --assignee $(az account show --query user.name -o tsv)`

2. **Service Quotas**
   - Review required quotas in [REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md)
   - Request increases if needed via Azure Portal

3. **Region Selection**
   - **Tier 1 (Full Capability)**: eastus, eastus2, westus2, westeurope, northeurope, southeastasia
   - **Considerations**: Azure ML availability, Functions Premium, Service Bus Premium
   - **Reference**: [deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md)

### 2. Configuration Preparation

#### Parameter Files

Review and customize parameter files in `deployment/parameters/`:

```bicep
// deployment/parameters/dev.bicepparam
using '../main-modular.bicep'

param location = 'eastus'              // Choose supported region
param environment = 'dev'               // dev, staging, or prod
param functionAppSku = 'Y1'            // Consumption plan for dev
param serviceBusSku = 'Standard'       // Standard tier for dev
param storageSku = 'Standard_LRS'      // Local redundancy for dev
param enableB2C = false                // B2C auth (requires setup)
param enableAppInsights = true         // Monitoring (recommended)
param enableAzureML = true             // ML workspace (optional)
```

#### Environment-Specific Settings

| Environment | Function SKU | Service Bus | Storage | Azure ML | B2C Auth |
|-------------|--------------|-------------|---------|----------|----------|
| **Development** | Y1 (Consumption) | Standard | Standard_LRS | Optional | No |
| **Staging** | EP1 (Premium) | Standard | Standard_GRS | Yes | Optional |
| **Production** | EP1/EP2 (Premium) | Premium | Standard_GRS | Yes | Yes |

### 3. Authentication Setup

#### Azure Login

```bash
# Interactive login
az login

# Service principal (CI/CD)
az login --service-principal \
  --username $CLIENT_ID \
  --password $CLIENT_SECRET \
  --tenant $TENANT_ID

# Verify active subscription
az account show
az account set --subscription "<subscription-id>"
```

#### Azure AD B2C Setup (Production Only)

If `enableB2C = true`:

1. Create Azure AD B2C tenant
2. Register application
3. Configure user flows
4. Obtain client ID and secret
5. Store in Key Vault (post-deployment)

### 4. Source Code Preparation

```bash
# Clone repository
git clone https://github.com/ASISaga/AgentOperatingSystem.git
cd AgentOperatingSystem

# Verify clean state
git status

# Get current Git SHA for audit trail
GIT_SHA=$(git rev-parse HEAD)
echo "Deploying from Git SHA: $GIT_SHA"
```

### 5. Pre-Deployment Checklist

- [ ] Azure CLI installed and authenticated
- [ ] Bicep CLI installed and updated
- [ ] Python 3.10+ available
- [ ] Target region selected and validated
- [ ] Parameter files reviewed and customized
- [ ] Resource naming conventions defined
- [ ] Subscription quotas verified
- [ ] Team notified of deployment window
- [ ] Backup plan prepared (if updating existing deployment)
- [ ] Rollback procedure reviewed

---

## Infrastructure Deployment Phase

### 1. Pre-Deployment Validation

#### Template Linting

The Python orchestrator automatically runs linting, but you can manually verify:

```bash
cd deployment

# Lint template
az bicep build --file main-modular.bicep

# Expected output:
# ✅ No errors or warnings
# OR
# ⚠️ Warnings (review but can proceed with --allow-warnings)
# ❌ Errors (must fix before deployment)
```

#### What-If Analysis

Preview changes before deployment:

```bash
az deployment group what-if \
  --resource-group "rg-aos-dev" \
  --template-file "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam"
```

Review output for:
- ➕ **CREATE**: New resources (expected on first deployment)
- 🔄 **MODIFY**: Changes to existing resources (review carefully)
- ❌ **DELETE**: Destructive changes (requires confirmation)

### 2. Resource Group Creation

```bash
# Create resource group
az group create \
  --name "rg-aos-dev" \
  --location "eastus" \
  --tags "environment=dev" "project=aos" "owner=<your-email>"
```

### 3. Infrastructure Deployment with Orchestrator

#### Development Deployment

```bash
cd deployment

python3 deploy.py \
  --resource-group "rg-aos-dev" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam" \
  --git-sha "$GIT_SHA" \
  --allow-warnings
```

#### Production Deployment

```bash
cd deployment

python3 deploy.py \
  --resource-group "rg-aos-prod" \
  --location "eastus2" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod.bicepparam" \
  --git-sha "$GIT_SHA"
  # Note: No --allow-warnings for production
```

### 4. Deployment Phases

The orchestrator executes these phases automatically:

1. **VALIDATING_PARAMETERS** (1-2 min)
   - Verify template and parameters files exist
   - Validate parameter syntax

2. **LINTING** (1-2 min)
   - Run `az bicep build`
   - Check for syntax errors and warnings
   - **Gate**: Errors halt deployment

3. **PLANNING** (2-5 min)
   - Run `az deployment group what-if`
   - Analyze infrastructure changes
   - Detect destructive operations

4. **AWAITING_CONFIRMATION** (manual)
   - If destructive changes detected
   - Review and confirm or cancel
   - **Gate**: Requires explicit confirmation

5. **DEPLOYING** (10-20 min)
   - Execute `az deployment group create`
   - Monitor deployment progress
   - Apply smart retry for environmental failures
   - **Gate**: Logic errors halt, environmental errors retry

6. **VERIFYING_HEALTH** (2-5 min)
   - Check resource provisioning state
   - Verify resource health via Azure APIs
   - **Gate**: Unhealthy resources fail deployment

7. **COMPLETED** or **FAILED**
   - Generate audit record
   - Display deployment summary

### 5. Deployed Infrastructure Components

#### Core Services (Always Deployed)

1. **Azure Functions (3 Function Apps)**
   - `aos-{env}-func` - Main orchestration
   - `aos-{env}-mcp-func` - MCP servers
   - `aos-{env}-realm-func` - Realm of Agents

2. **App Service Plan**
   - Dev: Consumption (Y1)
   - Prod: Elastic Premium (EP1/EP2)

3. **Azure Service Bus**
   - Namespace: `sb-aos-{env}-{uniqueid}`
   - Queues: `aos-requests`, `businessinfinity-responses`
   - Topics: `agent-events`, `system-events`

4. **Azure Storage Account**
   - Account: `staosdatadev{uniqueid}`
   - Containers: `aos-data`, `aos-config`, `aos-logs`
   - Tables: For state management
   - Queues: For async processing

5. **Azure Key Vault**
   - Vault: `kv-aos-{env}-{uniqueid}`
   - Soft delete: 7 days
   - RBAC access model

6. **Monitoring**
   - Application Insights: `appi-aos-{env}`
   - Log Analytics: `law-aos-{env}`
   - Retention: 30 days

7. **Managed Identities**
   - System-assigned for each Function App
   - User-assigned for cross-resource access

8. **RBAC Assignments**
   - Key Vault Secrets User
   - Storage Blob Data Contributor
   - Service Bus Data Owner

#### Optional Services (Conditional Deployment)

9. **Azure ML Workspace** (if `enableAzureML = true` and region supports)
   - Workspace: `mlw-aos-{env}`
   - Container Registry: `craos{env}{uniqueid}`
   - Storage: Uses main storage account

10. **Container Registry** (if Azure ML enabled)
    - Registry: `craos{env}{uniqueid}`
    - SKU: Basic (dev) or Standard (prod)

### 6. Post-Infrastructure Verification

```bash
# List all deployed resources
az resource list \
  --resource-group "rg-aos-dev" \
  --output table

# Verify Function Apps
az functionapp list \
  --resource-group "rg-aos-dev" \
  --output table

# Check deployment outputs
az deployment group show \
  --resource-group "rg-aos-dev" \
  --name "<deployment-name>" \
  --query properties.outputs
```

### 7. Regional Capability Warnings

Check for regional capability warnings:

```bash
az deployment group show \
  --resource-group "rg-aos-dev" \
  --name "<deployment-name>" \
  --query properties.outputs.deploymentWarnings
```

**Possible Warnings:**
- `azureMLDisabledDueToRegion = true` → Azure ML not deployed
- `functionSkuDowngradedDueToRegion = true` → Functions downgraded to Consumption
- `serviceBusSkuDowngradedDueToRegion = true` → Service Bus downgraded to Standard

**Action**: Review and decide if acceptable, or redeploy to Tier 1 region.

---

## Application Deployment Phase

### 1. Code Preparation

#### Build Python Application

```bash
# Navigate to project root
cd /path/to/AgentOperatingSystem

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[full]"
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Build package
python -m build
```

#### Prepare Function App Code

The repository uses Azure Functions for deployment:

```bash
# Verify function app structure
ls -la function_app.py
ls -la host.json
ls -la azure_functions/

# Install function dependencies
pip install -r requirements.txt
```

### 2. Configuration Management

#### Application Settings

Create `local.settings.json` for local testing (not committed to git):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AOS_ENVIRONMENT": "dev",
    "AOS_LOG_LEVEL": "INFO"
  }
}
```

#### Key Vault Secrets

Store sensitive configuration in Key Vault:

```bash
# Store secrets in Key Vault
az keyvault secret set \
  --vault-name "kv-aos-dev-{uniqueid}" \
  --name "ServiceBusConnectionString" \
  --value "<connection-string>"

az keyvault secret set \
  --vault-name "kv-aos-dev-{uniqueid}" \
  --name "StorageConnectionString" \
  --value "<connection-string>"

# If using B2C
az keyvault secret set \
  --vault-name "kv-aos-dev-{uniqueid}" \
  --name "B2CClientSecret" \
  --value "<client-secret>"
```

#### Function App Settings

Configure Function Apps to reference Key Vault:

```bash
# Get Key Vault URI
KEYVAULT_URI=$(az keyvault show \
  --resource-group "rg-aos-dev" \
  --name "kv-aos-dev-{uniqueid}" \
  --query properties.vaultUri -o tsv)

# Set app settings with Key Vault references
az functionapp config appsettings set \
  --resource-group "rg-aos-dev" \
  --name "aos-dev-func" \
  --settings \
    "AZURE_SERVICEBUS_CONNECTION_STRING=@Microsoft.KeyVault(VaultName=kv-aos-dev-{uniqueid};SecretName=ServiceBusConnectionString)" \
    "AZURE_STORAGE_CONNECTION_STRING=@Microsoft.KeyVault(VaultName=kv-aos-dev-{uniqueid};SecretName=StorageConnectionString)"
```

### 3. Application Deployment

#### Deploy to Function Apps

##### Method 1: Azure Functions Core Tools (Local Development)

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Deploy main function app
cd /path/to/AgentOperatingSystem
func azure functionapp publish aos-dev-func --python

# Deploy MCP servers function app
func azure functionapp publish aos-dev-mcp-func --python

# Deploy Realm of Agents function app
func azure functionapp publish aos-dev-realm-func --python
```

##### Method 2: Azure CLI with ZIP Deployment

```bash
# Package function app
cd /path/to/AgentOperatingSystem
zip -r function-app.zip . -x "*.git*" "tests/*" "venv/*"

# Deploy via Azure CLI
az functionapp deployment source config-zip \
  --resource-group "rg-aos-dev" \
  --name "aos-dev-func" \
  --src function-app.zip

# Repeat for other function apps
```

##### Method 3: CI/CD Pipeline (Recommended for Production)

See [CI/CD Integration](#cicd-integration) section.

#### Verify Deployment

```bash
# Check function app status
az functionapp show \
  --resource-group "rg-aos-dev" \
  --name "aos-dev-func" \
  --query state

# List functions
az functionapp function list \
  --resource-group "rg-aos-dev" \
  --name "aos-dev-func" \
  --output table

# View logs
az functionapp log tail \
  --resource-group "rg-aos-dev" \
  --name "aos-dev-func"
```

### 4. Agent Configuration

#### RealmOfAgents Setup

Deploy agents via configuration (zero code):

```bash
# Create agent configuration
cat > agent-config.json <<EOF
{
  "agent_id": "ceo",
  "agent_type": "LeadershipAgent",
  "purpose": "Strategic oversight and company growth",
  "purpose_scope": "Strategic planning, major decisions",
  "adapter_name": "ceo",
  "mcp_tools": [],
  "enabled": true
}
EOF

# Upload to storage
az storage blob upload \
  --account-name "staosdatadev{uniqueid}" \
  --container-name "aos-config" \
  --name "agents/ceo.json" \
  --file agent-config.json
```

#### MCP Servers Setup

Deploy MCP servers via configuration:

```bash
# Create MCP server configuration
cat > mcp-server-config.json <<EOF
{
  "server_id": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "@Microsoft.KeyVault(...)"
  },
  "enabled": true
}
EOF

# Upload to storage
az storage blob upload \
  --account-name "staosdatadev{uniqueid}" \
  --container-name "aos-config" \
  --name "mcp-servers/github.json" \
  --file mcp-server-config.json
```

---

## Post-Deployment Phase

### 1. Health Verification

#### Automated Health Checks

The orchestrator runs health checks automatically. Manual verification:

```bash
# Check all resources
az resource list \
  --resource-group "rg-aos-dev" \
  --query "[?provisioningState!='Succeeded'].{name:name, state:provisioningState}" \
  --output table

# Should return empty if all resources are healthy
```

#### Function App Health Checks

```bash
# Health endpoint (if implemented)
curl https://aos-dev-func.azurewebsites.net/api/health

# Expected: {"status": "healthy", "timestamp": "..."}

# Status endpoint
curl https://aos-dev-func.azurewebsites.net/api/status

# Expected: {"version": "2.0.0", "environment": "dev"}
```

#### Service Bus Health

```bash
# Check Service Bus namespace
az servicebus namespace show \
  --resource-group "rg-aos-dev" \
  --name "sb-aos-dev-{uniqueid}" \
  --query provisioningState

# List queues
az servicebus queue list \
  --resource-group "rg-aos-dev" \
  --namespace-name "sb-aos-dev-{uniqueid}" \
  --output table
```

#### Storage Health

```bash
# Check storage account
az storage account show \
  --resource-group "rg-aos-dev" \
  --name "staosdatadev{uniqueid}" \
  --query provisioningState

# List containers
az storage container list \
  --account-name "staosdatadev{uniqueid}" \
  --output table
```

### 2. Functional Testing

#### End-to-End Test

```bash
# Run integration tests
cd /path/to/AgentOperatingSystem
pytest tests/test_integration.py -v

# Run Function App tests
pytest tests/test_azure_functions_infrastructure.py -v
```

#### Manual Agent Test

```python
# test_agent_deployment.py
import asyncio
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import LeadershipAgent

async def test_agent():
    # Create agent
    agent = LeadershipAgent(
        agent_id="test-agent",
        purpose="Test deployment",
        adapter_name="general"
    )
    
    # Initialize and verify
    await agent.initialize()
    status = await agent.get_status()
    print(f"Agent Status: {status}")
    
    # Cleanup
    await agent.stop()

asyncio.run(test_agent())
```

### 3. Performance Validation

#### Load Testing

```bash
# Install load testing tool
pip install locust

# Create load test (locustfile.py)
# Run load test
locust -f locustfile.py --host https://aos-dev-func.azurewebsites.net
```

#### Monitoring Metrics

```bash
# View Application Insights metrics
az monitor app-insights metrics show \
  --app "appi-aos-dev" \
  --resource-group "rg-aos-dev" \
  --metric "requests/count" \
  --start-time "2026-02-13T00:00:00Z"
```

### 4. Documentation Update

- [ ] Update deployment audit log
- [ ] Document deployed resource IDs
- [ ] Update runbook with environment-specific details
- [ ] Share deployment summary with team

---

## Production Readiness Phase

### 1. Security Hardening

#### Network Security

```bash
# Enable VNET integration (if needed)
az functionapp vnet-integration add \
  --resource-group "rg-aos-prod" \
  --name "aos-prod-func" \
  --vnet "vnet-aos-prod" \
  --subnet "subnet-functions"

# Configure IP restrictions (production only)
az functionapp config access-restriction add \
  --resource-group "rg-aos-prod" \
  --name "aos-prod-func" \
  --rule-name "AllowCorporateNetwork" \
  --action Allow \
  --ip-address "203.0.113.0/24" \
  --priority 100
```

#### Managed Identity Configuration

```bash
# Verify managed identities
az functionapp identity show \
  --resource-group "rg-aos-prod" \
  --name "aos-prod-func"

# Verify RBAC assignments
az role assignment list \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod" \
  --output table
```

#### Key Vault Access Policies

```bash
# Verify Key Vault RBAC
az role assignment list \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.KeyVault/vaults/kv-aos-prod-{uniqueid}" \
  --output table
```

### 2. Monitoring Configuration

#### Application Insights Setup

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app "appi-aos-prod" \
  --location "eastus" \
  --resource-group "rg-aos-prod" \
  --workspace "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.OperationalInsights/workspaces/law-aos-prod"
```

#### Alerts Configuration

```bash
# Create alert for high error rate
az monitor metrics alert create \
  --name "HighErrorRate" \
  --resource-group "rg-aos-prod" \
  --scopes "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.Insights/components/appi-aos-prod" \
  --condition "avg exceptions/count > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group "<action-group-id>"

# Create alert for resource health
az monitor metrics alert create \
  --name "UnhealthyResources" \
  --resource-group "rg-aos-prod" \
  --scopes "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod" \
  --condition "avg ResourceHealth > 0" \
  --window-size 5m
```

#### Log Analytics Queries

Configure useful queries in Log Analytics:

```kql
// Failed requests
requests
| where success == false
| summarize count() by bin(timestamp, 5m), resultCode
| render timechart

// Agent operations
traces
| where message contains "agent"
| summarize count() by bin(timestamp, 5m), severityLevel
| render timechart

// MCP tool calls
customEvents
| where name == "MCPToolCall"
| extend tool = tostring(customDimensions.tool)
| summarize count() by bin(timestamp, 5m), tool
| render timechart
```

### 3. Backup Configuration

#### Automated Backups

```bash
# Enable storage account backup (via policy)
az backup policy create \
  --resource-group "rg-aos-prod" \
  --vault-name "rsv-aos-prod" \
  --name "DailyBackup" \
  --backup-management-type "AzureStorage" \
  --policy policy.json

# Enable Key Vault backup
az backup protection enable-for-azurekeyvault \
  --resource-group "rg-aos-prod" \
  --vault-name "rsv-aos-prod" \
  --keyvault "kv-aos-prod-{uniqueid}" \
  --policy-name "DailyBackup"
```

#### Data Export

```bash
# Export critical configuration
az storage blob download-batch \
  --source "aos-config" \
  --destination "./backup/config" \
  --account-name "staosproddata{uniqueid}"

# Export audit logs
sqlite3 deployment/audit/audit.db .dump > backup/audit-$(date +%Y%m%d).sql
```

### 4. Disaster Recovery Testing

- [ ] Document DR procedures
- [ ] Test failover to secondary region
- [ ] Validate backup restoration
- [ ] Verify RTO/RPO targets

### 5. Runbook Creation

Create operational runbooks for:

- [ ] Deployment procedures
- [ ] Incident response
- [ ] Scaling procedures
- [ ] Troubleshooting guides
- [ ] Rollback procedures

---

## Rollback Procedures

### 1. Application Rollback

#### Rollback Function App Deployment

```bash
# List deployment history
az functionapp deployment list-publishing-credentials \
  --resource-group "rg-aos-prod" \
  --name "aos-prod-func"

# Rollback to previous deployment slot (if using slots)
az functionapp deployment slot swap \
  --resource-group "rg-aos-prod" \
  --name "aos-prod-func" \
  --slot "staging" \
  --target-slot "production" \
  --action "swap"
```

#### Quick Rollback via Git

```bash
# Identify last good deployment
git log --oneline -10

# Checkout previous version
git checkout <previous-commit-sha>

# Redeploy
func azure functionapp publish aos-prod-func --python
```

### 2. Infrastructure Rollback

#### Restore from Previous Deployment

```bash
# List previous deployments
az deployment group list \
  --resource-group "rg-aos-prod" \
  --output table

# Identify last successful deployment
LAST_DEPLOYMENT=$(az deployment group list \
  --resource-group "rg-aos-prod" \
  --query "[?properties.provisioningState=='Succeeded'] | [0].name" \
  -o tsv)

# Extract parameters from previous deployment
az deployment group show \
  --resource-group "rg-aos-prod" \
  --name "$LAST_DEPLOYMENT" \
  --query properties.parameters > rollback-params.json

# Redeploy with previous parameters
python3 deploy.py \
  --resource-group "rg-aos-prod" \
  --location "eastus2" \
  --template "main-modular.bicep" \
  --parameters "rollback-params.json"
```

#### Manual Resource Restoration

If specific resources fail:

```bash
# Delete failed resource
az resource delete \
  --ids "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.Web/sites/aos-prod-func"

# Redeploy infrastructure
python3 deploy.py \
  --resource-group "rg-aos-prod" \
  --location "eastus2" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod.bicepparam"
```

### 3. Data Restoration

#### Restore from Backup

```bash
# Restore storage account data
az storage blob copy start-batch \
  --source-container "aos-data" \
  --destination-container "aos-data" \
  --source-account-name "backup-account" \
  --destination-account-name "staosdatadev{uniqueid}"

# Restore Key Vault secrets (from backup)
while read line; do
  secret_name=$(echo $line | jq -r '.name')
  secret_value=$(echo $line | jq -r '.value')
  az keyvault secret set \
    --vault-name "kv-aos-prod-{uniqueid}" \
    --name "$secret_name" \
    --value "$secret_value"
done < secrets-backup.json
```

### 4. Communication Plan

During rollback:

1. **Notify stakeholders**: Inform team of rollback initiation
2. **Disable traffic**: Temporarily disable or redirect traffic
3. **Execute rollback**: Follow procedures above
4. **Verify restoration**: Run health checks and functional tests
5. **Resume traffic**: Re-enable when verified
6. **Post-mortem**: Document incident and improvements

---

## Deployment Architecture

### Infrastructure Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                      │
│              (External Users, Services, APIs)               │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTPS/WSS
┌─────────────────────────────────────────────────────────────┐
│                  AZURE FUNCTIONS (Compute)                  │
│  ┌────────────────┬────────────────┬────────────────────┐  │
│  │  Main Function │ MCP Servers    │ Realm of Agents    │  │
│  │  App           │ Function App   │ Function App       │  │
│  └────────────────┴────────────────┴────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                   MESSAGING & INTEGRATION                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Azure Service Bus (Queues, Topics, Subscriptions)    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATA & STATE LAYER                      │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Azure Storage│  Azure Tables│  Cosmos DB (Optional)    │ │
│  │ (Blob/Queue) │              │                          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                   PLATFORM SERVICES                         │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Key Vault    │  App Insights│  Azure ML (Optional)     │ │
│  │ (Secrets)    │  (Monitoring)│  (LoRA Training)         │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│                  IDENTITY & ACCESS (IAM)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Managed Identities + RBAC + Azure AD (B2C Optional)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Flow

```
┌─────────────────┐
│  Git Repository │
│  (Source Code)  │
└────────┬────────┘
         │ Clone
         ↓
┌─────────────────┐
│ Local Developer │
│  Workstation    │
└────────┬────────┘
         │ Run deploy.py
         ↓
┌─────────────────────────────────────────────────────────────┐
│         PYTHON ORCHESTRATOR (Quality Gates)                 │
├─────────────────────────────────────────────────────────────┤
│  1. LINT    → az bicep build (syntax validation)           │
│  2. WHAT-IF → az deployment group what-if (preview)        │
│  3. CONFIRM → Manual approval for destructive changes       │
│  4. DEPLOY  → az deployment group create (provision)       │
│  5. VERIFY  → Health checks (post-deployment)              │
│  6. AUDIT   → Log deployment record (SQLite/JSON)          │
└────────┬────────────────────────────────────────────────────┘
         │ Azure CLI Commands
         ↓
┌─────────────────────────────────────────────────────────────┐
│              AZURE RESOURCE MANAGER (ARM)                   │
│          (Orchestrates Resource Provisioning)               │
└────────┬────────────────────────────────────────────────────┘
         │ Provision Resources
         ↓
┌─────────────────────────────────────────────────────────────┐
│                  AZURE SUBSCRIPTION                         │
│         (Deployed Infrastructure Resources)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### 1. Secrets Management

- **Never commit secrets to Git**: Use `.gitignore` for `local.settings.json`
- **Use Key Vault**: Store all secrets in Azure Key Vault
- **Managed Identity**: Prefer managed identity over connection strings
- **Key Vault References**: Use `@Microsoft.KeyVault(...)` in app settings

### 2. Network Security

- **VNET Integration**: Recommended for production
- **Private Endpoints**: For Storage, Service Bus, Key Vault
- **NSG Rules**: Restrict traffic between tiers
- **IP Restrictions**: Limit Function App access

### 3. Authentication & Authorization

- **Azure AD Integration**: For user authentication
- **B2C (Optional)**: For external users
- **RBAC**: Role-based access control for resources
- **Managed Identities**: For service-to-service auth

### 4. Data Protection

- **Encryption at Rest**: Enabled by default on all services
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Soft Delete**: Enabled on Key Vault and Storage
- **Backup**: Regular backups with retention policy

### 5. Compliance

- **Audit Logging**: Complete deployment audit trail
- **Compliance Tags**: Tag resources with compliance requirements
- **Data Residency**: Choose regions based on data residency requirements
- **Access Reviews**: Regular reviews of RBAC assignments

---

## Monitoring and Observability

### 1. Application Insights

**Metrics to Monitor:**
- Request count and response time
- Failure rate
- Dependency calls (Service Bus, Storage)
- Custom events (agent operations, MCP tool calls)

**Dashboard Queries:**

```kql
// Request volume
requests
| summarize count() by bin(timestamp, 5m)
| render timechart

// Error rate
requests
| summarize total=count(), failures=countif(success==false) by bin(timestamp, 5m)
| extend errorRate = (failures * 100.0) / total
| render timechart

// Agent activity
customEvents
| where name == "AgentOperation"
| summarize count() by tostring(customDimensions.agentId), bin(timestamp, 1h)
| render columnchart
```

### 2. Alerting Strategy

**Critical Alerts** (Page immediately):
- Function App down
- High error rate (>5% for 5 minutes)
- Service Bus queue depth >1000
- Storage account inaccessible

**Warning Alerts** (Email):
- Increased response time
- Resource utilization >80%
- Deployment failures
- Health check failures

### 3. Log Aggregation

**Structured Logging:**

```python
import logging
import json

logger = logging.getLogger(__name__)

# Structured log entry
logger.info(json.dumps({
    "event": "AgentInitialized",
    "agent_id": "ceo",
    "purpose": "Strategic oversight",
    "timestamp": "2026-02-13T10:00:00Z"
}))
```

**Log Queries:**

```kql
// Find errors
traces
| where severityLevel >= 3
| project timestamp, message, severityLevel
| order by timestamp desc

// Agent lifecycle events
customEvents
| where name in ("AgentInitialized", "AgentStarted", "AgentStopped")
| summarize count() by name, bin(timestamp, 1h)
```

### 4. Distributed Tracing

Enable Application Insights correlation:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Azure Monitor
configure_azure_monitor(
    connection_string="<app-insights-connection-string>"
)

# Create tracer
tracer = trace.get_tracer(__name__)

# Trace operations
with tracer.start_as_current_span("agent_operation"):
    # Agent logic here
    pass
```

---

## Disaster Recovery

### 1. Recovery Objectives

| Metric | Development | Staging | Production |
|--------|-------------|---------|------------|
| **RTO** (Recovery Time Objective) | 24 hours | 4 hours | 1 hour |
| **RPO** (Recovery Point Objective) | 24 hours | 1 hour | 15 minutes |

### 2. Backup Strategy

**Infrastructure:**
- Bicep templates in Git (Infrastructure as Code)
- Parameter files versioned
- Deployment audit logs

**Data:**
- Storage: Geo-redundant (GRS) in production
- Key Vault: Soft delete + purge protection
- Service Bus: Message backup (via consumer)

**Configuration:**
- Function App settings exported
- Agent configurations in Git
- MCP server configurations in Git

### 3. Multi-Region Deployment

For critical production workloads:

```bash
# Primary region
python3 deploy.py \
  --resource-group "rg-aos-prod-eastus" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod.bicepparam"

# Secondary region (DR)
python3 deploy.py \
  --resource-group "rg-aos-prod-westus" \
  --location "westus2" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod-dr.bicepparam"
```

Configure Traffic Manager or Front Door for failover.

### 4. DR Testing

**Quarterly DR Drills:**

1. Simulate primary region failure
2. Failover to secondary region
3. Verify functionality
4. Measure RTO/RPO achievement
5. Document lessons learned
6. Update DR procedures

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy-aos.yml
name: Deploy AOS

on:
  push:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'dev' }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          az bicep install
      
      - name: Deploy Infrastructure
        run: |
          cd deployment
          python3 deploy.py \
            --resource-group "${{ vars.RESOURCE_GROUP }}" \
            --location "${{ vars.LOCATION }}" \
            --template "main-modular.bicep" \
            --parameters "parameters/${{ vars.ENVIRONMENT }}.bicepparam" \
            --git-sha "${{ github.sha }}" \
            --audit-dir "./logs"
      
      - name: Deploy Function Apps
        run: |
          pip install azure-functions
          func azure functionapp publish ${{ vars.FUNCTION_APP_NAME }} --python
      
      - name: Run Health Checks
        run: |
          python3 scripts/health_check.py --environment ${{ vars.ENVIRONMENT }}
      
      - name: Upload Audit Logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: deployment-logs
          path: deployment/logs/
```

### Azure DevOps Pipeline Example

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

variables:
  - group: aos-$(Environment)

stages:
  - stage: Deploy
    jobs:
      - job: Infrastructure
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.11'
          
          - task: AzureCLI@2
            displayName: 'Install Bicep'
            inputs:
              azureSubscription: 'AOS-Production'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: 'az bicep install'
          
          - task: AzureCLI@2
            displayName: 'Deploy Infrastructure'
            inputs:
              azureSubscription: 'AOS-Production'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                cd deployment
                python3 deploy.py \
                  -g "$(ResourceGroup)" \
                  -l "$(Location)" \
                  -t "main-modular.bicep" \
                  -p "parameters/$(Environment).bicepparam" \
                  --git-sha "$(Build.SourceVersion)" \
                  --audit-dir "$(Build.ArtifactStagingDirectory)/logs"
          
          - task: PublishBuildArtifacts@1
            condition: always()
            inputs:
              pathToPublish: '$(Build.ArtifactStagingDirectory)/logs'
              artifactName: 'deployment-logs'
```

---

## Appendix

### A. Deployment Checklist

See [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) for detailed task checklist.

### B. Troubleshooting Guide

See [deployment/README.md](../../deployment/README.md#troubleshooting) for common issues.

### C. Resource Naming Conventions

| Resource Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Resource Group | `rg-<app>-<env>` | `rg-aos-dev` |
| Function App | `<app>-<env>-func` | `aos-dev-func` |
| Storage Account | `st<app><type><env><unique>` | `staosdatadev123abc` |
| Service Bus | `sb-<app>-<env>-<unique>` | `sb-aos-dev-abc123` |
| Key Vault | `kv-<app>-<env>-<unique>` | `kv-aos-dev-abc123` |
| App Insights | `appi-<app>-<env>` | `appi-aos-dev` |

### D. Cost Optimization

**Development:**
- Use Consumption plan for Functions
- Standard tier for Service Bus
- LRS storage
- Disable Azure ML if not needed

**Production:**
- Use Elastic Premium with right-sizing
- Premium Service Bus for VNet support
- GRS storage for redundancy
- Enable Azure ML only if using LoRA adapters

**Cost Monitoring:**

```bash
# View cost analysis
az consumption usage list \
  --start-date 2026-02-01 \
  --end-date 2026-02-13 \
  --query "[?contains(instanceName, 'aos')]" \
  --output table
```

### E. Compliance and Governance

**Azure Policy:**

```bash
# Assign policy to resource group
az policy assignment create \
  --name "EnforceTagging" \
  --policy "/providers/Microsoft.Authorization/policyDefinitions/..." \
  --resource-group "rg-aos-prod" \
  --params '{"tagName":{"value":"environment"}}'
```

**Resource Tagging:**

```bicep
// Required tags for all resources
var commonTags = {
  environment: environment
  project: 'aos'
  managedBy: 'bicep'
  costCenter: '1234'
  owner: 'platform-team'
}
```

### F. Support and Escalation

**Level 1 - Self-Service:**
- Review documentation
- Check deployment logs
- Search GitHub issues

**Level 2 - Team Support:**
- Open GitHub issue
- Contact platform team
- Review runbooks

**Level 3 - Microsoft Support:**
- Azure support ticket
- Premier support channel

---

**Document Version:** 1.0  
**Last Updated:** February 13, 2026  
**Next Review:** May 13, 2026  
**Maintained By:** AOS Platform Team
