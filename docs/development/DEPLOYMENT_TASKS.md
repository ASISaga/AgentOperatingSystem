# Agent Operating System - Deployment Task List

**Version:** 2.0.0  
**Last Updated:** February 13, 2026  
**Related:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)

---

## Purpose

This document provides comprehensive, actionable checklists for deploying the Agent Operating System (AOS) to Microsoft Azure. Use this alongside the [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) for complete deployment guidance.

---

## Table of Contents

1. [Pre-Deployment Tasks](#pre-deployment-tasks)
2. [Infrastructure Deployment Tasks](#infrastructure-deployment-tasks)
3. [Application Deployment Tasks](#application-deployment-tasks)
4. [Post-Deployment Verification Tasks](#post-deployment-verification-tasks)
5. [Production Readiness Tasks](#production-readiness-tasks)
6. [Ongoing Operations Tasks](#ongoing-operations-tasks)
7. [Environment-Specific Checklists](#environment-specific-checklists)

---

## Pre-Deployment Tasks

### Tools and Environment Setup

**Workstation Prerequisites:**
- [ ] Azure CLI installed and updated to latest version
  ```bash
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  az --version
  ```
- [ ] Bicep CLI installed via Azure CLI
  ```bash
  az bicep install
  az bicep upgrade
  az bicep version
  ```
- [ ] Python 3.10+ installed
  ```bash
  python3 --version
  # Should show 3.10.x or higher
  ```
- [ ] Git installed and configured
  ```bash
  git --version
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```
- [ ] Azure Functions Core Tools installed (for application deployment)
  ```bash
  npm install -g azure-functions-core-tools@4
  func --version
  ```

**Azure Subscription Setup:**
- [ ] Azure subscription identified
  ```bash
  az account list --output table
  ```
- [ ] Subscription set as active
  ```bash
  az account set --subscription "<subscription-id>"
  ```
- [ ] Subscription permissions verified (Owner or Contributor + User Access Administrator)
  ```bash
  az role assignment list --assignee $(az account show --query user.name -o tsv) --output table
  ```
- [ ] Service quotas reviewed for target region
  - Review [deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md)
  - Check Azure ML quota (if enabling ML features)
  - Check Functions Premium quota (if using EP SKU)
  - Check Service Bus Premium quota (if using Premium tier)

**Authentication:**
- [ ] Azure CLI authentication completed
  ```bash
  az login
  az account show
  ```
- [ ] Service principal created (if deploying via CI/CD)
  ```bash
  az ad sp create-for-rbac --name "aos-deploy-sp" --role Contributor --scopes /subscriptions/<subscription-id>
  ```
- [ ] Service principal credentials securely stored (GitHub Secrets, Azure DevOps Variable Group)

### Region and Configuration

**Region Selection:**
- [ ] Target Azure region selected from Tier 1 regions (recommended):
  - [ ] Americas: eastus, eastus2, westus2
  - [ ] Europe: westeurope, northeurope
  - [ ] Asia Pacific: southeastasia, australiaeast, japaneast
- [ ] Regional capability validated:
  - [ ] Azure ML Workspace availability checked
  - [ ] Azure Functions Premium (EP) availability checked
  - [ ] Service Bus Premium availability checked
- [ ] Fallback strategy defined if using Tier 2 region

**Parameter Files:**
- [ ] Parameter file copied from template
  ```bash
  cp deployment/parameters/dev.bicepparam deployment/parameters/myenv.bicepparam
  ```
- [ ] Parameter file customized for target environment:
  - [ ] `location` parameter set to chosen region
  - [ ] `environment` parameter set (dev, staging, prod)
  - [ ] `namePrefix` parameter customized (if needed for uniqueness)
  - [ ] `functionAppSku` parameter set appropriately
    - Dev: `Y1` (Consumption)
    - Staging: `EP1` (Elastic Premium)
    - Prod: `EP1` or `EP2` (Elastic Premium)
  - [ ] `serviceBusSku` parameter set appropriately
    - Dev: `Standard`
    - Prod: `Premium` (if VNet integration needed)
  - [ ] `storageSku` parameter set appropriately
    - Dev: `Standard_LRS`
    - Prod: `Standard_GRS` (geo-redundant)
  - [ ] `enableB2C` parameter set correctly
    - Set to `true` only if B2C tenant configured
  - [ ] `enableAppInsights` parameter set to `true` (recommended)
  - [ ] `enableAzureML` parameter set based on requirements
    - Set to `true` only if using LoRA adapters

**Resource Naming:**
- [ ] Resource naming strategy defined
- [ ] Naming conventions documented (see DEPLOYMENT_PLAN.md Appendix C)
- [ ] Unique suffix strategy defined for globally unique resources
- [ ] Resource tags planned
  ```bicep
  var commonTags = {
    environment: 'dev'
    project: 'aos'
    owner: 'team-email@example.com'
    costCenter: 'CC-1234'
  }
  ```

### Source Code Preparation

**Repository Setup:**
- [ ] Repository cloned
  ```bash
  git clone https://github.com/ASISaga/AgentOperatingSystem.git
  cd AgentOperatingSystem
  ```
- [ ] Correct branch checked out
  ```bash
  git checkout main  # or develop, or specific release tag
  ```
- [ ] Repository clean (no uncommitted changes)
  ```bash
  git status
  # Should show "working tree clean"
  ```
- [ ] Git SHA captured for audit trail
  ```bash
  GIT_SHA=$(git rev-parse HEAD)
  echo "Deploying Git SHA: $GIT_SHA"
  ```

**Dependencies:**
- [ ] Python virtual environment created
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```
- [ ] Python dependencies installed
  ```bash
  pip install -e ".[full]"
  pip install -r requirements-dev.txt
  ```
- [ ] Tests run successfully
  ```bash
  pytest tests/ -v
  # All tests should pass
  ```

### Team Communication

**Pre-Deployment Communication:**
- [ ] Deployment plan shared with team
- [ ] Deployment window scheduled and communicated
- [ ] Stakeholders notified
- [ ] On-call engineer identified
- [ ] Rollback plan reviewed with team
- [ ] Emergency contact list verified

### Documentation Review

**Pre-Deployment Reading:**
- [ ] [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) read and understood
- [ ] [deployment/README.md](../../deployment/README.md) reviewed
- [ ] [deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md) reviewed
- [ ] [deployment/ORCHESTRATOR_USER_GUIDE.md](../../deployment/ORCHESTRATOR_USER_GUIDE.md) reviewed (if using orchestrator)
- [ ] [deployment/QUICKSTART.md](../../deployment/QUICKSTART.md) reviewed for quick reference

---

## Infrastructure Deployment Tasks

### Pre-Deployment Validation

**Template Validation:**
- [ ] Bicep template linted manually (optional, orchestrator does this automatically)
  ```bash
  cd deployment
  az bicep build --file main-modular.bicep
  ```
- [ ] No linting errors present
- [ ] Linting warnings reviewed and accepted (if any)
- [ ] Parameter file syntax validated
  ```bash
  # Parameter file should reference template correctly
  head -5 parameters/dev.bicepparam
  # Should show: using '../main-modular.bicep'
  ```

**What-If Analysis:**
- [ ] What-if analysis executed (optional, orchestrator does this automatically)
  ```bash
  az deployment group what-if \
    --resource-group "rg-aos-dev" \
    --template-file "main-modular.bicep" \
    --parameters "parameters/dev.bicepparam"
  ```
- [ ] What-if results reviewed:
  - [ ] CREATE operations expected and understood
  - [ ] MODIFY operations expected and understood
  - [ ] DELETE operations expected and confirmed as intentional
  - [ ] No unexpected changes identified

**Resource Group:**
- [ ] Resource group created
  ```bash
  az group create \
    --name "rg-aos-dev" \
    --location "eastus" \
    --tags "environment=dev" "project=aos"
  ```
- [ ] Resource group tags applied
- [ ] Resource group locks configured (if production)
  ```bash
  # Production only
  az group lock create \
    --name "CannotDelete" \
    --resource-group "rg-aos-prod" \
    --lock-type CanNotDelete
  ```

### Orchestrator Deployment (Recommended Method)

**Using Python Orchestrator:**
- [ ] Navigate to deployment directory
  ```bash
  cd deployment
  ```
- [ ] Execute deployment with orchestrator
  ```bash
  python3 deploy.py \
    --resource-group "rg-aos-dev" \
    --location "eastus" \
    --template "main-modular.bicep" \
    --parameters "parameters/dev.bicepparam" \
    --git-sha "$GIT_SHA" \
    --allow-warnings  # Only for dev; remove for prod
  ```
- [ ] Monitor orchestrator output:
  - [ ] VALIDATING_PARAMETERS phase completed
  - [ ] LINTING phase completed (no errors)
  - [ ] PLANNING (what-if) phase completed
  - [ ] AWAITING_CONFIRMATION handled (if destructive changes)
  - [ ] DEPLOYING phase in progress (monitor for 10-20 minutes)
  - [ ] VERIFYING_HEALTH phase completed
  - [ ] COMPLETED status achieved
- [ ] Deployment succeeded (exit code 0)
- [ ] Audit log created in `deployment/audit/`
  ```bash
  ls -la deployment/audit/
  # Should show new .json file or updated audit.db
  ```

**Alternative: Direct Azure CLI Deployment** (if orchestrator unavailable)
- [ ] Template deployed directly
  ```bash
  az deployment group create \
    --name "aos-deployment-$(date +%Y%m%d-%H%M%S)" \
    --resource-group "rg-aos-dev" \
    --template-file "main-modular.bicep" \
    --parameters "parameters/dev.bicepparam"
  ```
- [ ] Deployment monitored in Azure Portal
- [ ] Deployment succeeded

### Post-Deployment Resource Verification

**Resource Inventory:**
- [ ] All expected resources created
  ```bash
  az resource list \
    --resource-group "rg-aos-dev" \
    --output table
  ```
- [ ] Resource count matches expectations:
  - [ ] 3 Function Apps (main, mcp, realm)
  - [ ] 1 App Service Plan
  - [ ] 1 Service Bus Namespace
  - [ ] 1 Storage Account
  - [ ] 1 Key Vault
  - [ ] 1 Application Insights
  - [ ] 1 Log Analytics Workspace
  - [ ] 1-3 Managed Identities
  - [ ] 1 Azure ML Workspace (if enabled)
  - [ ] 1 Container Registry (if ML enabled)

**Function Apps:**
- [ ] Main Function App created
  ```bash
  az functionapp show \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func" \
    --query "{name:name, state:state, sku:sku}"
  ```
- [ ] MCP Servers Function App created
- [ ] Realm of Agents Function App created
- [ ] Function Apps in "Running" state
- [ ] Function Apps using correct SKU (Y1, EP1, etc.)

**Service Bus:**
- [ ] Service Bus namespace created and accessible
  ```bash
  az servicebus namespace show \
    --resource-group "rg-aos-dev" \
    --name "sb-aos-dev-<uniqueid>" \
    --query provisioningState
  ```
- [ ] Required queues created:
  - [ ] `aos-requests` queue exists
  - [ ] `businessinfinity-responses` queue exists
- [ ] Required topics created:
  - [ ] `agent-events` topic exists
  - [ ] `system-events` topic exists

**Storage:**
- [ ] Storage account created and accessible
  ```bash
  az storage account show \
    --resource-group "rg-aos-dev" \
    --name "staosdatadev<uniqueid>" \
    --query provisioningState
  ```
- [ ] Blob containers created:
  - [ ] `aos-data` container exists
  - [ ] `aos-config` container exists
  - [ ] `aos-logs` container exists
- [ ] Tables available (for state management)
- [ ] Queues available (for async processing)

**Key Vault:**
- [ ] Key Vault created and accessible
  ```bash
  az keyvault show \
    --resource-group "rg-aos-dev" \
    --name "kv-aos-dev-<uniqueid>" \
    --query properties.provisioningState
  ```
- [ ] Soft delete enabled (7-day retention)
- [ ] RBAC access model configured

**Monitoring:**
- [ ] Application Insights workspace created
  ```bash
  az monitor app-insights component show \
    --resource-group "rg-aos-dev" \
    --app "appi-aos-dev" \
    --query provisioningState
  ```
- [ ] Log Analytics workspace created
- [ ] Workspace linked to Application Insights

**RBAC Assignments:**
- [ ] Function Apps have managed identities
  ```bash
  az functionapp identity show \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func"
  ```
- [ ] RBAC assignments verified:
  - [ ] Function Apps → Key Vault (Secrets User)
  - [ ] Function Apps → Storage (Blob Data Contributor)
  - [ ] Function Apps → Service Bus (Data Owner)

**Regional Capability Warnings:**
- [ ] Deployment warnings reviewed
  ```bash
  az deployment group show \
    --resource-group "rg-aos-dev" \
    --name "<deployment-name>" \
    --query properties.outputs.deploymentWarnings
  ```
- [ ] Any SKU downgrades documented and accepted
- [ ] Azure ML disabled status documented (if applicable)

---

## Application Deployment Tasks

### Code Preparation

**Build and Test:**
- [ ] Application built successfully
  ```bash
  cd /path/to/AgentOperatingSystem
  python -m build
  ```
- [ ] All tests passing
  ```bash
  pytest tests/ -v
  # No failures
  ```
- [ ] Code linting clean
  ```bash
  pylint src/AgentOperatingSystem
  # Score above 5.0/10
  ```

**Function App Packaging:**
- [ ] Function app structure verified
  ```bash
  ls -la function_app.py host.json azure_functions/
  ```
- [ ] Requirements file up to date
  ```bash
  pip freeze > requirements.txt
  # Review and clean up if needed
  ```
- [ ] Local settings configured (for local testing)
  ```bash
  cp local.settings.json.template local.settings.json
  # Edit with dev settings (NOT committed to git)
  ```

### Secrets and Configuration

**Key Vault Secrets:**
- [ ] Service Bus connection string added to Key Vault
  ```bash
  # Get connection string
  SERVICE_BUS_CONN=$(az servicebus namespace authorization-rule keys list \
    --resource-group "rg-aos-dev" \
    --namespace-name "sb-aos-dev-<uniqueid>" \
    --name "RootManageSharedAccessKey" \
    --query primaryConnectionString -o tsv)
  
  # Store in Key Vault
  az keyvault secret set \
    --vault-name "kv-aos-dev-<uniqueid>" \
    --name "ServiceBusConnectionString" \
    --value "$SERVICE_BUS_CONN"
  ```
- [ ] Storage connection string added to Key Vault
  ```bash
  # Get connection string
  STORAGE_CONN=$(az storage account show-connection-string \
    --resource-group "rg-aos-dev" \
    --name "staosdatadev<uniqueid>" \
    --query connectionString -o tsv)
  
  # Store in Key Vault
  az keyvault secret set \
    --vault-name "kv-aos-dev-<uniqueid>" \
    --name "StorageConnectionString" \
    --value "$STORAGE_CONN"
  ```
- [ ] Application Insights connection string added (if needed)
- [ ] B2C client secret added (if B2C enabled)
- [ ] Any external API keys added (GitHub PAT for MCP, etc.)

**Function App Settings:**
- [ ] Function App configured with Key Vault references
  ```bash
  KEYVAULT_NAME="kv-aos-dev-<uniqueid>"
  
  az functionapp config appsettings set \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func" \
    --settings \
      "AZURE_SERVICEBUS_CONNECTION_STRING=@Microsoft.KeyVault(VaultName=${KEYVAULT_NAME};SecretName=ServiceBusConnectionString)" \
      "AZURE_STORAGE_CONNECTION_STRING=@Microsoft.KeyVault(VaultName=${KEYVAULT_NAME};SecretName=StorageConnectionString)" \
      "AOS_ENVIRONMENT=dev" \
      "AOS_LOG_LEVEL=INFO"
  ```
- [ ] MCP Servers Function App configured
- [ ] Realm of Agents Function App configured
- [ ] Environment-specific settings applied

### Function App Deployment

**Main Function App:**
- [ ] Main function app deployed
  ```bash
  cd /path/to/AgentOperatingSystem
  func azure functionapp publish aos-dev-func --python
  ```
- [ ] Deployment succeeded
- [ ] Functions listed
  ```bash
  az functionapp function list \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func" \
    --output table
  ```

**MCP Servers Function App:**
- [ ] MCP servers function app deployed
  ```bash
  func azure functionapp publish aos-dev-mcp-func --python
  ```
- [ ] Deployment succeeded

**Realm of Agents Function App:**
- [ ] Realm of Agents function app deployed
  ```bash
  func azure functionapp publish aos-dev-realm-func --python
  ```
- [ ] Deployment succeeded

**Alternative: ZIP Deployment** (if func tools unavailable)
- [ ] Function app packaged as ZIP
  ```bash
  zip -r function-app.zip . -x "*.git*" "tests/*" "venv/*" ".venv/*"
  ```
- [ ] ZIP deployed
  ```bash
  az functionapp deployment source config-zip \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func" \
    --src function-app.zip
  ```

### Agent Configuration

**RealmOfAgents Configuration:**
- [ ] Agent configuration files created
  ```bash
  # Example: CEO agent
  cat > ceo-agent-config.json <<EOF
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
  ```
- [ ] Agent configurations uploaded to storage
  ```bash
  az storage blob upload \
    --account-name "staosdatadev<uniqueid>" \
    --container-name "aos-config" \
    --name "agents/ceo.json" \
    --file ceo-agent-config.json
  ```
- [ ] Multiple agents configured (as needed)
  - [ ] CEO agent
  - [ ] CFO agent
  - [ ] CTO agent
  - [ ] CMO agent
  - [ ] (Add others as needed)

**MCP Servers Configuration:**
- [ ] MCP server configuration files created
  ```bash
  # Example: GitHub MCP server
  cat > github-mcp-config.json <<EOF
  {
    "server_id": "github",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "@Microsoft.KeyVault(VaultName=kv-aos-dev-<uniqueid>;SecretName=GitHubPAT)"
    },
    "enabled": true
  }
  EOF
  ```
- [ ] MCP server configurations uploaded to storage
  ```bash
  az storage blob upload \
    --account-name "staosdatadev<uniqueid>" \
    --container-name "aos-config" \
    --name "mcp-servers/github.json" \
    --file github-mcp-config.json
  ```
- [ ] Multiple MCP servers configured (as needed)
  - [ ] GitHub server
  - [ ] Filesystem server
  - [ ] Database server (if needed)
  - [ ] (Add others as needed)

---

## Post-Deployment Verification Tasks

### Automated Health Checks

**Orchestrator Health Checks** (if using orchestrator):
- [ ] Health check results reviewed in orchestrator output
- [ ] All resources marked as "healthy"
- [ ] Any warnings investigated and resolved

**Manual Health Verification:**
- [ ] All resources in "Succeeded" provisioning state
  ```bash
  az resource list \
    --resource-group "rg-aos-dev" \
    --query "[?provisioningState!='Succeeded'].{name:name, state:provisioningState}" \
    --output table
  # Should return empty
  ```

### Function App Testing

**Health Endpoint:**
- [ ] Main function app health endpoint accessible
  ```bash
  curl https://aos-dev-func.azurewebsites.net/api/health
  # Expected: {"status": "healthy", ...}
  ```
- [ ] MCP servers function app health endpoint accessible
- [ ] Realm of Agents function app health endpoint accessible

**Status Endpoint:**
- [ ] Status endpoint returns correct information
  ```bash
  curl https://aos-dev-func.azurewebsites.net/api/status
  # Expected: {"version": "2.0.0", "environment": "dev"}
  ```

**Function Listing:**
- [ ] All expected functions deployed
  ```bash
  az functionapp function list \
    --resource-group "rg-aos-dev" \
    --name "aos-dev-func" \
    --output table
  ```

### Functional Testing

**Integration Tests:**
- [ ] Integration test suite executed
  ```bash
  # Set environment variables for integration tests
  export AOS_RESOURCE_GROUP="rg-aos-dev"
  export AOS_FUNCTION_APP="aos-dev-func"
  
  # Run integration tests
  pytest tests/test_integration.py -v
  ```
- [ ] All integration tests passing

**Azure Functions Infrastructure Tests:**
- [ ] Azure Functions tests executed
  ```bash
  pytest tests/test_azure_functions_infrastructure.py -v
  ```
- [ ] All Azure Functions tests passing

**Agent Operation Test:**
- [ ] Manual agent test executed
  ```python
  # test_deployed_agent.py
  import asyncio
  from AgentOperatingSystem.agents import LeadershipAgent
  
  async def test():
      agent = LeadershipAgent(
          agent_id="test-agent",
          purpose="Deployment verification",
          adapter_name="general"
      )
      await agent.initialize()
      status = await agent.get_status()
      print(f"Agent Status: {status}")
      assert status["state"] == "initialized"
      await agent.stop()
      print("✅ Agent test passed")
  
  asyncio.run(test())
  ```
- [ ] Agent operations successful

**Message Bus Test:**
- [ ] Service Bus message send/receive tested
  ```python
  # test_servicebus.py
  from azure.servicebus import ServiceBusClient, ServiceBusMessage
  import os
  
  connection_string = os.getenv("SERVICE_BUS_CONNECTION_STRING")
  client = ServiceBusClient.from_connection_string(connection_string)
  
  # Send test message
  with client:
      sender = client.get_queue_sender("aos-requests")
      message = ServiceBusMessage("Test message")
      sender.send_messages(message)
      print("✅ Message sent successfully")
  ```
- [ ] Messages successfully sent and received

**Storage Test:**
- [ ] Storage blob operations tested
  ```bash
  # Upload test file
  echo "Test content" > test-file.txt
  az storage blob upload \
    --account-name "staosdatadev<uniqueid>" \
    --container-name "aos-data" \
    --name "test/test-file.txt" \
    --file test-file.txt
  
  # Download test file
  az storage blob download \
    --account-name "staosdatadev<uniqueid>" \
    --container-name "aos-data" \
    --name "test/test-file.txt" \
    --file downloaded-test-file.txt
  
  # Verify content
  cat downloaded-test-file.txt
  # Should show: Test content
  ```
- [ ] Blob upload/download successful

### Monitoring Verification

**Application Insights:**
- [ ] Application Insights receiving data
  ```bash
  az monitor app-insights metrics show \
    --app "appi-aos-dev" \
    --resource-group "rg-aos-dev" \
    --metric "requests/count" \
    --start-time "$(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ')"
  ```
- [ ] Telemetry visible in Azure Portal
  - [ ] Navigate to Application Insights → Live Metrics
  - [ ] Verify live telemetry streaming
  - [ ] Check Failures blade (should be minimal)
  - [ ] Check Performance blade (response times reasonable)

**Log Analytics:**
- [ ] Logs flowing to Log Analytics
  ```kql
  # Run in Log Analytics workspace
  traces
  | where timestamp > ago(1h)
  | summarize count() by severityLevel
  ```
- [ ] Log queries functional

**Distributed Tracing:**
- [ ] End-to-end traces visible
  - [ ] Navigate to Application Insights → Application Map
  - [ ] Verify all components visible
  - [ ] Check Transaction Search for sample requests

### Performance Testing

**Load Test** (optional for dev, recommended for staging/prod):
- [ ] Load testing tool installed
  ```bash
  pip install locust
  ```
- [ ] Load test scenario created (locustfile.py)
- [ ] Load test executed
  ```bash
  locust -f locustfile.py --host https://aos-dev-func.azurewebsites.net --users 10 --spawn-rate 1 --run-time 5m --headless
  ```
- [ ] Results analyzed:
  - [ ] Response times within acceptable range
  - [ ] No errors under normal load
  - [ ] Resource utilization reasonable

---

## Production Readiness Tasks

### Security Hardening

**Network Security:**
- [ ] VNET integration configured (production only)
  ```bash
  az functionapp vnet-integration add \
    --resource-group "rg-aos-prod" \
    --name "aos-prod-func" \
    --vnet "vnet-aos-prod" \
    --subnet "subnet-functions"
  ```
- [ ] Private endpoints configured for sensitive services
  - [ ] Storage account private endpoint
  - [ ] Service Bus private endpoint
  - [ ] Key Vault private endpoint
- [ ] IP restrictions applied (production only)
  ```bash
  az functionapp config access-restriction add \
    --resource-group "rg-aos-prod" \
    --name "aos-prod-func" \
    --rule-name "AllowCorporateNetwork" \
    --action Allow \
    --ip-address "203.0.113.0/24" \
    --priority 100
  ```
- [ ] Network Security Groups (NSG) configured

**Managed Identities:**
- [ ] Managed identities verified for all Function Apps
- [ ] RBAC assignments verified
  ```bash
  az role assignment list \
    --scope "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod" \
    --output table
  ```
- [ ] Service principal access reviewed and minimized

**Key Vault:**
- [ ] Soft delete verified (7-day retention)
- [ ] Purge protection enabled (production only)
  ```bash
  az keyvault update \
    --resource-group "rg-aos-prod" \
    --name "kv-aos-prod-<uniqueid>" \
    --enable-purge-protection true
  ```
- [ ] RBAC access reviewed
- [ ] Audit logging enabled

**Data Protection:**
- [ ] Encryption at rest verified (enabled by default)
- [ ] Encryption in transit verified (HTTPS/TLS)
- [ ] Storage account soft delete configured
  ```bash
  az storage blob service-properties delete-policy update \
    --account-name "staosproddata<uniqueid>" \
    --enable true \
    --days-retained 7
  ```

### Monitoring and Alerting

**Application Insights Configuration:**
- [ ] Application Insights workspace validated
- [ ] Instrumentation key verified in Function Apps
- [ ] Custom metrics configured (if needed)
- [ ] Sampling rate appropriate for environment
  - Dev: 100% sampling (or lower to save costs)
  - Prod: 20-50% sampling (balance cost/observability)

**Alert Rules:**
- [ ] Critical alerts configured:
  - [ ] Function App down alert
    ```bash
    az monitor metrics alert create \
      --name "FunctionAppDown" \
      --resource-group "rg-aos-prod" \
      --scopes "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.Web/sites/aos-prod-func" \
      --condition "avg availabilityResults/availabilityPercentage < 99" \
      --window-size 5m \
      --evaluation-frequency 1m \
      --severity 0 \
      --action <action-group-id>
    ```
  - [ ] High error rate alert (>5% for 5 minutes)
  - [ ] Service Bus queue depth alert (>1000 messages)
  - [ ] Storage account accessibility alert
- [ ] Warning alerts configured:
  - [ ] Increased response time (>2s average)
  - [ ] Resource utilization (>80% CPU/memory)
  - [ ] Deployment failure notifications
- [ ] Action groups configured:
  - [ ] Email notifications
  - [ ] SMS/phone notifications (critical alerts only)
  - [ ] PagerDuty/Opsgenie integration (if used)
  - [ ] Webhook to incident management system

**Dashboard Creation:**
- [ ] Azure Dashboard created for monitoring
  - [ ] Function App health status
  - [ ] Request rate and response time
  - [ ] Error rate
  - [ ] Service Bus queue depths
  - [ ] Storage account metrics
  - [ ] Agent activity metrics
- [ ] Dashboard shared with team
- [ ] Dashboard bookmarked for quick access

### Backup and Disaster Recovery

**Backup Configuration:**
- [ ] Storage account geo-redundancy enabled (production)
  ```bash
  az storage account show \
    --resource-group "rg-aos-prod" \
    --name "staosproddata<uniqueid>" \
    --query sku.name
  # Should be: Standard_GRS or Standard_RAGRS
  ```
- [ ] Key Vault backup configured
  ```bash
  # Backup all secrets
  for secret in $(az keyvault secret list --vault-name "kv-aos-prod-<uniqueid>" --query "[].name" -o tsv); do
    az keyvault secret backup \
      --vault-name "kv-aos-prod-<uniqueid>" \
      --name "$secret" \
      --file "backup-${secret}.blob"
  done
  ```
- [ ] Configuration files backed up to git
  - [ ] Agent configurations committed
  - [ ] MCP server configurations committed
  - [ ] Parameter files committed
- [ ] Audit logs backed up
  ```bash
  # Backup SQLite audit database
  cp deployment/audit/audit.db backup/audit-$(date +%Y%m%d).db
  
  # Backup JSON audit files
  tar -czf backup/audit-logs-$(date +%Y%m%d).tar.gz deployment/audit/*.json
  ```

**DR Testing:**
- [ ] DR runbook created and documented
- [ ] DR test scheduled (quarterly for production)
- [ ] DR test procedures documented:
  - [ ] Failover to secondary region
  - [ ] Restore from backup
  - [ ] Verify functionality
  - [ ] Measure RTO/RPO
- [ ] DR test results documented

**Multi-Region Deployment** (critical production only):
- [ ] Secondary region identified
- [ ] Secondary infrastructure deployed
  ```bash
  python3 deploy.py \
    --resource-group "rg-aos-prod-westus" \
    --location "westus2" \
    --template "main-modular.bicep" \
    --parameters "parameters/prod-dr.bicepparam"
  ```
- [ ] Traffic Manager or Front Door configured for failover
- [ ] Data replication configured
- [ ] Failover procedures documented and tested

### Documentation

**Deployment Documentation:**
- [ ] Deployment completed date/time recorded
- [ ] Deployed Git SHA documented
- [ ] Resource IDs documented
  ```bash
  az resource list \
    --resource-group "rg-aos-prod" \
    --query "[].{name:name, type:type, id:id}" \
    --output json > deployed-resources.json
  ```
- [ ] Regional capability warnings documented
- [ ] Any deviations from plan documented
- [ ] Deployment audit log reviewed and archived

**Operational Runbooks:**
- [ ] Deployment runbook updated with environment-specific details
- [ ] Troubleshooting runbook created
- [ ] Incident response runbook created
- [ ] Scaling runbook created
- [ ] Rollback runbook created and tested
- [ ] Runbooks shared with team

**Team Handoff:**
- [ ] Operations team trained on deployment
- [ ] Monitoring dashboard access granted
- [ ] Alert notifications configured for on-call team
- [ ] Escalation procedures documented
- [ ] Support contact list updated

### Compliance and Governance

**Tagging:**
- [ ] All resources tagged appropriately
  ```bash
  # Verify tags
  az resource list \
    --resource-group "rg-aos-prod" \
    --query "[].{name:name, tags:tags}" \
    --output table
  ```
- [ ] Required tags present:
  - [ ] `environment` tag
  - [ ] `project` tag
  - [ ] `owner` tag
  - [ ] `costCenter` tag
  - [ ] `managedBy` tag

**Azure Policy:**
- [ ] Relevant Azure Policies assigned to resource group
- [ ] Policy compliance verified
  ```bash
  az policy state list \
    --resource-group "rg-aos-prod" \
    --query "[?complianceState=='NonCompliant']" \
    --output table
  # Should be empty
  ```

**Cost Management:**
- [ ] Budget alert configured
  ```bash
  az consumption budget create \
    --resource-group "rg-aos-prod" \
    --budget-name "MonthlyBudget" \
    --amount 1000 \
    --time-grain Monthly \
    --start-date "$(date -u +%Y-%m-01)" \
    --threshold 80 \
    --notification-email "billing@example.com"
  ```
- [ ] Cost allocation tags applied
- [ ] Cost monitoring dashboard created

**Audit Logging:**
- [ ] Azure Activity Log configured
- [ ] Diagnostic settings enabled for all resources
  ```bash
  az monitor diagnostic-settings create \
    --resource "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.Web/sites/aos-prod-func" \
    --name "DiagToLogAnalytics" \
    --workspace "/subscriptions/<sub-id>/resourceGroups/rg-aos-prod/providers/Microsoft.OperationalInsights/workspaces/law-aos-prod" \
    --logs '[{"category": "FunctionAppLogs", "enabled": true}]' \
    --metrics '[{"category": "AllMetrics", "enabled": true}]'
  ```
- [ ] Log retention policies configured

---

## Ongoing Operations Tasks

### Daily Operations

**Health Monitoring:**
- [ ] Check Azure Dashboard for any alerts
- [ ] Review Application Insights overview
  - [ ] Request rate trends
  - [ ] Error rate (should be <1%)
  - [ ] Response time trends
- [ ] Check Function App status
  ```bash
  az functionapp list \
    --resource-group "rg-aos-prod" \
    --query "[].{name:name, state:state}" \
    --output table
  # All should be "Running"
  ```
- [ ] Review Service Bus queue depths
  ```bash
  az servicebus queue list \
    --resource-group "rg-aos-prod" \
    --namespace-name "sb-aos-prod-<uniqueid>" \
    --query "[].{name:name, messageCount:messageCount}" \
    --output table
  ```

**Log Review:**
- [ ] Review error logs in Application Insights
  ```kql
  exceptions
  | where timestamp > ago(24h)
  | summarize count() by type, outerMessage
  | order by count_ desc
  ```
- [ ] Review failed requests
  ```kql
  requests
  | where timestamp > ago(24h) and success == false
  | summarize count() by resultCode
  ```
- [ ] Investigate any anomalies

### Weekly Operations

**Performance Review:**
- [ ] Review weekly performance trends
  - [ ] Average response time
  - [ ] Request volume
  - [ ] Error patterns
- [ ] Identify performance bottlenecks
- [ ] Plan optimizations if needed

**Cost Review:**
- [ ] Review weekly cost trends
  ```bash
  az consumption usage list \
    --start-date "$(date -u -d '7 days ago' +%Y-%m-%d)" \
    --end-date "$(date -u +%Y-%m-%d)" \
    --query "[?contains(instanceName, 'aos')]" \
    --output table
  ```
- [ ] Identify cost anomalies
- [ ] Review resource utilization vs. cost

**Security Review:**
- [ ] Review access logs in Key Vault
- [ ] Review failed authentication attempts
- [ ] Check for security advisories

### Monthly Operations

**Backup Verification:**
- [ ] Verify backup completeness
- [ ] Test restore procedure (sample data)
- [ ] Verify backup retention policies

**DR Test:**
- [ ] Run mini DR drill (off-hours)
- [ ] Document results
- [ ] Update DR procedures if needed

**Capacity Planning:**
- [ ] Review resource utilization trends
  - [ ] Function App CPU/memory
  - [ ] Storage account capacity
  - [ ] Service Bus throughput
- [ ] Plan scaling if needed
- [ ] Review and adjust SKUs if appropriate

**Dependency Updates:**
- [ ] Review Python package updates
  ```bash
  pip list --outdated
  ```
- [ ] Review Azure SDK updates
- [ ] Test updates in dev environment
- [ ] Plan update deployment to production

### Quarterly Operations

**DR Full Test:**
- [ ] Schedule maintenance window
- [ ] Execute full DR test
- [ ] Measure RTO/RPO achievement
- [ ] Document lessons learned
- [ ] Update DR procedures

**Security Audit:**
- [ ] Review RBAC assignments
- [ ] Remove unused identities
- [ ] Rotate secrets and keys
- [ ] Review network security rules
- [ ] Compliance audit

**Documentation Review:**
- [ ] Review and update deployment documentation
- [ ] Update runbooks
- [ ] Review and update architecture diagrams
- [ ] Team training on any changes

---

## Environment-Specific Checklists

### Development Environment Checklist

**Purpose:** Testing and development work

**Key Characteristics:**
- [ ] Consumption plan (Y1) for cost savings
- [ ] Standard tier Service Bus
- [ ] Local redundancy (LRS) storage
- [ ] No B2C authentication
- [ ] Basic monitoring
- [ ] No network restrictions
- [ ] Frequent deployments expected

**Additional Dev Tasks:**
- [ ] Local.settings.json configured for local development
- [ ] Development storage emulator configured (optional)
- [ ] Debug logging enabled (AOS_LOG_LEVEL=DEBUG)
- [ ] Test data loaded
- [ ] Development team access granted

### Staging Environment Checklist

**Purpose:** Pre-production validation

**Key Characteristics:**
- [ ] Elastic Premium (EP1) plan
- [ ] Standard tier Service Bus
- [ ] Geo-redundant (GRS) storage
- [ ] Optional B2C authentication
- [ ] Full monitoring
- [ ] Moderate network restrictions
- [ ] Production-like configuration

**Additional Staging Tasks:**
- [ ] Load testing executed
- [ ] Performance benchmarks established
- [ ] Integration tests run against staging
- [ ] Production deployment rehearsal
- [ ] Stakeholder UAT (User Acceptance Testing)

### Production Environment Checklist

**Purpose:** Live production workloads

**Key Characteristics:**
- [ ] Elastic Premium (EP1/EP2) plan
- [ ] Premium tier Service Bus (for VNet)
- [ ] Geo-redundant (GRS/RAGRS) storage
- [ ] B2C authentication (if needed)
- [ ] Full monitoring and alerting
- [ ] Strict network restrictions
- [ ] High availability configuration
- [ ] Disaster recovery configured

**Additional Production Tasks:**
- [ ] Change management process followed
- [ ] Deployment window scheduled
- [ ] Stakeholders notified
- [ ] Rollback plan prepared and reviewed
- [ ] On-call engineer assigned
- [ ] Post-deployment monitoring (24-48 hours)
- [ ] Production deployment documented
- [ ] Lessons learned session scheduled

---

## Emergency Rollback Checklist

**When to Use:** Critical production issues requiring immediate rollback

### Immediate Actions

- [ ] Incident declared and stakeholders notified
- [ ] On-call engineer mobilized
- [ ] Issue severity assessed:
  - **P0 (Critical)**: Complete outage, proceed with rollback
  - **P1 (High)**: Major degradation, consider rollback
  - **P2 (Medium)**: Minor issues, investigate first
- [ ] Decision to rollback documented

### Application Rollback

**Function App Rollback:**
- [ ] Previous deployment identified
  ```bash
  # List deployment history
  az functionapp deployment list-publishing-profiles \
    --resource-group "rg-aos-prod" \
    --name "aos-prod-func"
  ```
- [ ] Rollback executed
  ```bash
  # Option 1: Redeploy previous Git SHA
  git checkout <previous-sha>
  func azure functionapp publish aos-prod-func --python
  
  # Option 2: Swap deployment slot (if using slots)
  az functionapp deployment slot swap \
    --resource-group "rg-aos-prod" \
    --name "aos-prod-func" \
    --slot "staging" \
    --action "swap"
  ```
- [ ] Rollback verified
- [ ] Health checks passed

### Infrastructure Rollback

**Resource Rollback:**
- [ ] Last successful deployment identified
  ```bash
  az deployment group list \
    --resource-group "rg-aos-prod" \
    --query "[?properties.provisioningState=='Succeeded']" \
    --output table
  ```
- [ ] Previous deployment parameters extracted
  ```bash
  LAST_DEPLOYMENT="<deployment-name>"
  az deployment group show \
    --resource-group "rg-aos-prod" \
    --name "$LAST_DEPLOYMENT" \
    --query properties.parameters > rollback-params.json
  ```
- [ ] Rollback deployment executed
  ```bash
  python3 deploy.py \
    --resource-group "rg-aos-prod" \
    --location "eastus2" \
    --template "main-modular.bicep" \
    --parameters "rollback-params.json" \
    --no-confirm-deletes  # CAUTION: Use only if confident
  ```
- [ ] Rollback verified
- [ ] All resources healthy

### Data Restoration (if needed)

**Storage Restoration:**
- [ ] Identify data loss scope
- [ ] Locate most recent backup
- [ ] Restore data from backup
  ```bash
  # Restore specific blobs
  az storage blob copy start-batch \
    --source-container "aos-data" \
    --destination-container "aos-data" \
    --source-account-name "backup-account" \
    --destination-account-name "staosproddata<uniqueid>"
  ```
- [ ] Verify data integrity

**Key Vault Restoration:**
- [ ] Restore deleted secrets (soft delete)
  ```bash
  az keyvault secret recover \
    --vault-name "kv-aos-prod-<uniqueid>" \
    --name "<secret-name>"
  ```
- [ ] Or restore from backup
  ```bash
  az keyvault secret restore \
    --vault-name "kv-aos-prod-<uniqueid>" \
    --file "backup-<secret-name>.blob"
  ```

### Post-Rollback Actions

- [ ] Service fully restored and verified
- [ ] Stakeholders notified of resolution
- [ ] Incident timeline documented
- [ ] Root cause analysis initiated
- [ ] Post-mortem scheduled
- [ ] Preventive measures identified
- [ ] Deployment process improvements planned

---

## Checklist Completion Summary

**Overall Deployment Progress:**

- **Pre-Deployment:** ___% complete
- **Infrastructure:** ___% complete
- **Application:** ___% complete
- **Verification:** ___% complete
- **Production Readiness:** ___% complete

**Deployment Metadata:**

- **Environment:** ________________
- **Deployment Date:** ________________
- **Deployed By:** ________________
- **Git SHA:** ________________
- **Deployment Duration:** ________________
- **Issues Encountered:** ________________
- **Resolution Notes:** ________________

**Sign-Off:**

- **Deployment Engineer:** ________________ Date: ________
- **Operations Lead:** ________________ Date: ________
- **Technical Lead:** ________________ Date: ________

---

**Document Version:** 1.0  
**Last Updated:** February 13, 2026  
**Next Review:** May 13, 2026  
**Maintained By:** AOS Platform Team

---

## Additional Resources

- **[DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)**: Comprehensive deployment strategy and procedures
- **[deployment/README.md](../../deployment/README.md)**: Deployment infrastructure documentation
- **[deployment/ORCHESTRATOR_USER_GUIDE.md](../../deployment/ORCHESTRATOR_USER_GUIDE.md)**: Orchestrator usage guide
- **[deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md)**: Regional capability requirements
- **[deployment/QUICKSTART.md](../../deployment/QUICKSTART.md)**: Quick deployment reference
- **[CONTRIBUTING.md](./CONTRIBUTING.md)**: General contribution guidelines
