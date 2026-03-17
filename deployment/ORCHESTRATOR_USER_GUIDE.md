# Bicep Deployment Orchestrator - User Guide

## Quick Start

### 1. Prerequisites Check

```bash
# Check Azure CLI
az --version

# Check Bicep
az bicep version

# If not installed:
az bicep install
```

### 2. Your First Deployment

```bash
cd deployment

# Development environment
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam"
```

### 3. Understanding the Output

The orchestrator will:

1. ✅ **Validate** parameters and files
2. 🔍 **Lint** the Bicep template
3. 📊 **Analyze** changes (what-if)
4. ⚠️ **Confirm** destructive changes (if any)
5. 🚀 **Deploy** to Azure
6. 🏥 **Verify** resource health

## Common Workflows

### Development Deployment

```bash
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam" \
  --allow-warnings
```

### Production Deployment

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus2" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam"
```

### Deployment with Overrides

```bash
python3 deploy.py \
  -g "rg-aos-staging" \
  -l "westus2" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam" \
  --param environment=staging \
  --param functionAppSku=EP1 \
  --param serviceBusSku=Standard
```

### Quick Testing (No Health Checks)

```bash
python3 deploy.py \
  -g "rg-aos-test" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam" \
  --skip-health
```

## Understanding Quality Gates

### Gate 1: Linting

**What it does**: Validates Bicep syntax and best practices

**Example output**:
```
❌ ERRORS:
  [BCP001] Expected '{' but got 'invalid'
  [BCP012] Parameter 'location' is missing

⚠️  WARNINGS:
  [BCP073] Unused parameter 'testParam'
```

**What to do**:
- Errors: Fix the template, deployment will NOT proceed
- Warnings: Review and fix, or use `--allow-warnings` to proceed

### Gate 2: What-If Analysis

**What it does**: Shows what will change in Azure

**Example output**:
```
WHAT-IF ANALYSIS RESULTS
============================================================
Total changes: 5

➕ CREATE (3):
   - Microsoft.Storage/storageAccounts/storageaos123
   - Microsoft.ServiceBus/namespaces/sb-aos-dev
   - Microsoft.Web/sites/func-aos-dev

🔄 MODIFY (1):
   - Microsoft.Insights/components/appi-aos-dev

❌ DELETE (1) - DESTRUCTIVE:
   - Microsoft.Storage/storageAccounts/old-storage

⚠️  WARNING: Destructive changes detected!
   These operations will DELETE resources and may cause data loss.
```

**What to do**:
- Review all changes carefully
- For deletions, confirm you really want to delete
- Type "yes" to proceed or "no" to cancel

### Gate 3: Deployment

**What it does**: Executes the actual deployment

**Retry behavior**:
- **Logic errors** (e.g., invalid parameters): Immediate failure, no retry
- **Environmental errors** (e.g., timeout): Automatic retry with backoff

**Example output**:
```
🚀 Deploying to rg-aos-dev...
✅ Deployment succeeded

OR

❌ Deployment failed (Attempt 1/3)
Error: Service temporarily unavailable (503)
Classification: ENVIRONMENTAL
🔄 Retrying in 5 seconds...
```

### Gate 4: Health Verification

**What it does**: Verifies deployed resources are healthy

**Example output**:
```
HEALTH CHECK RESULTS
============================================================
Overall: 3/3 checks passed

✅ AzureResource:/subscriptions/.../storageAccounts/storageaos123
   Status: healthy
   Message: Resource provisioned successfully

✅ AzureResource:/subscriptions/.../namespaces/sb-aos-dev
   Status: healthy
   Message: Resource provisioned successfully

✅ AzureResource:/subscriptions/.../sites/func-aos-dev
   Status: healthy
   Message: Resource provisioned successfully
```

## Handling Errors

### Linting Errors

**Error**: `BCP001: Syntax error`

**Solution**:
```bash
# Run linter directly to see details
az bicep build --file main-modular.bicep

# Fix the syntax error
# Then retry deployment
```

### Template Validation Errors

**Error**: `Template validation failed: missing required parameter`

**Solution**:
```bash
# Add the parameter to your parameters file
# OR use --param to override
python3 deploy.py ... --param missingParam=value
```

### Timeout Errors

**Error**: `Request timeout while connecting to Azure`

**What happens**: Automatic retry with exponential backoff

**If it keeps failing**:
```bash
# Check Azure service health
az status

# Try a different region
python3 deploy.py -l "westus2" ...
```

### Quota Errors

**Error**: `Quota exceeded in region eastus`

**Solution**:
```bash
# Request quota increase in Azure Portal
# OR use a different region
python3 deploy.py -l "eastus2" ...

# OR downgrade SKU
python3 deploy.py ... --param functionAppSku=Y1
```

### Resource Already Exists

**Error**: `Resource 'storageaos123' already exists`

**Solution**:
```bash
# Use a different name prefix
python3 deploy.py ... --param namePrefix=aos2

# OR delete existing resource group
az group delete -n rg-aos-dev --yes
```

## Advanced Usage

### Parameter Override Syntax

```bash
# Single value
--param environment=prod

# Boolean
--param enableAzureML=true

# Number
--param instanceCount=3

# Multiple overrides
--param env=prod --param sku=EP2 --param count=5
```

### Custom Audit Directory

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus" \
  -t "main-modular.bicep" \
  --audit-dir "/var/log/aos-deployments"
```

### Manual Git SHA

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus" \
  -t "main-modular.bicep" \
  --git-sha "abc123def456"
```

### Skip Confirmations (DANGEROUS!)

```bash
# Only use in automated CI/CD where you're CERTAIN about changes
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  --no-confirm-deletes
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy AOS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy with Orchestrator
        run: |
          cd deployment
          python3 deploy.py \
            -g "${{ vars.RESOURCE_GROUP }}" \
            -l "${{ vars.LOCATION }}" \
            -t "main-modular.bicep" \
            -p "parameters/${{ vars.ENVIRONMENT }}.bicepparam" \
            --git-sha "${{ github.sha }}" \
            --audit-dir "./logs"
      
      - name: Upload Audit Logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: deployment-logs
          path: deployment/logs/
```

### Azure DevOps Pipeline Example

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: AzureCLI@2
  displayName: 'Deploy AOS'
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

## Viewing Audit Logs

### SQLite Query Examples

```bash
# Install sqlite3
sudo apt-get install sqlite3

# View recent deployments
sqlite3 audit/audit.db "SELECT deployment_id, timestamp, success, result_message FROM deployments ORDER BY timestamp DESC LIMIT 10;"

# View deployment events
sqlite3 audit/audit.db "SELECT timestamp, event_type, message FROM deployment_events WHERE deployment_id='<id>' ORDER BY timestamp;"

# View deployed resources
sqlite3 audit/audit.db "SELECT resource_type, health_status FROM deployment_resources WHERE deployment_id='<id>';"

# Count successful deployments
sqlite3 audit/audit.db "SELECT COUNT(*) FROM deployments WHERE success=1;"

# Find failed deployments
sqlite3 audit/audit.db "SELECT deployment_id, timestamp, result_message FROM deployments WHERE success=0 ORDER BY timestamp DESC;"
```

### JSON Log Inspection

```bash
# View latest deployment
ls -t audit/*.json | head -1 | xargs cat | python3 -m json.tool

# Search for specific Git SHA
grep -l "abc123" audit/*.json

# Count total deployments
ls audit/*.json | wc -l
```

## Troubleshooting

### Debug Mode

```bash
# Add -v for verbose output (if implemented)
# Or inspect audit logs for detailed trace
cat audit/<deployment-id>.json | python3 -m json.tool
```

### Common Issues

**Issue**: "Azure CLI not found"
```bash
which az
# If not found, install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**Issue**: "Permission denied: deploy.py"
```bash
chmod +x deploy.py
```

**Issue**: "ModuleNotFoundError: orchestrator"
```bash
# Make sure you're in the deployment directory
cd /path/to/deployment
python3 deploy.py ...
```

**Issue**: "Template file not found"
```bash
# Use absolute or relative paths correctly
ls -la main-modular.bicep
python3 deploy.py -t "$(pwd)/main-modular.bicep" ...
```

## Best Practices

1. **Always test in dev first**: `dev.bicepparam` → `staging.bicepparam` → `prod.bicepparam`

2. **Review what-if output carefully**: Especially destructive changes

3. **Use descriptive parameter files**: Name them after environments

4. **Keep audit logs**: Store them in a persistent location

5. **Track Git SHA**: Always use `--git-sha` in CI/CD

6. **Don't skip health checks in production**: Only use `--skip-health` for testing

7. **Use parameter overrides for secrets**: Never commit secrets to parameters files

8. **Monitor deployment patterns**: Review audit logs regularly

9. **Test retry behavior**: Simulate failures in dev to understand retry logic

10. **Document custom parameters**: Keep README updated with parameter meanings

## Getting Help

- **Check audit logs**: Detailed execution trace in `audit/audit.db` or `audit/*.json`
- **Run linter separately**: `az bicep build --file <template>`
- **Check what-if manually**: `az deployment group what-if ...`
- **Review Azure service health**: `az status`
- **Open GitHub issue**: For bugs or feature requests

## Next Steps

- Read [orchestrator/README.md](orchestrator/README.md) for architecture details
- Review [test examples](tests/test_orchestrator.py) for usage patterns
- Customize failure classification patterns
- Add custom health checkers
- Integrate with your CI/CD pipeline
