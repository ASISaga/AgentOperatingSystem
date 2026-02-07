# Bicep Deployment Orchestrator

A Python-based orchestration layer that governs Azure Bicep deployments with strict quality and safety standards.

## Overview

The Bicep Deployment Orchestrator is a production-grade deployment automation system that treats Azure CLI as its execution engine while enforcing:

- **Static Integrity**: Mandatory linting with error gates
- **Verified Convergence**: Post-deployment health verification
- **Risk Assessment**: What-if planning with destructive change detection
- **Failure Intelligence**: Smart classification and retry strategies
- **Audit & Traceability**: Complete deployment records with Git SHA linkage

## Architecture

```
orchestrator/
├── core/                      # Core orchestration logic
│   ├── orchestrator.py        # Main orchestrator class
│   ├── state_machine.py       # Deployment state management
│   └── failure_classifier.py  # Intelligent failure classification
├── validators/                # Pre-deployment validation
│   ├── linter.py             # Bicep linting (az bicep build)
│   └── whatif_planner.py     # What-if analysis (az deployment group what-if)
├── health/                    # Post-deployment verification
│   └── health_checker.py     # Resource health checks
├── audit/                     # Audit and traceability
│   └── audit_logger.py       # Structured audit logging (JSON/SQLite)
└── cli/                       # Command-line interface
    └── deploy.py             # CLI entry point
```

## Key Features

### 1. Static Integrity (Linter Gate)

The orchestrator performs mandatory static analysis using the Bicep linter:

```bash
az bicep build --file <template.bicep>
```

**Guarantees**:
- ❌ **Error-level violations**: Deployment halts immediately
- ⚠️ **Warning-level issues**: Logged but can proceed with `--allow-warnings`

### 2. Verified Convergence

Post-deployment health verification ensures resources are not just provisioned but **healthy**:

- **TCP connectivity checks**: Verify network reachability
- **HTTP health checks**: Validate endpoints return expected status codes
- **Azure Resource Health API**: Check provisioning state via `az resource show`

**Guarantees**:
- ✅ Success only when all health checks pass
- 🔄 Automatic retries for transient failures
- 📊 Complete health status in audit logs

### 3. Risk & Drift Assessment

What-if planning analyzes the deployment delta:

```bash
az deployment group what-if --resource-group <rg> --template-file <template>
```

**Guarantees**:
- 🔍 Full visibility into resource changes (Create/Modify/Delete)
- ⚠️ Destructive changes (deletions) trigger **mandatory manual confirmation**
- 🛡️ Prevents accidental data loss and downtime

### 4. Failure Intelligence

The orchestrator classifies failures into two categories:

#### Logic Failures (Halt Immediately)
- Linter errors
- Invalid Bicep syntax
- Template validation errors
- Missing required parameters
- Circular dependencies

#### Environmental Failures (Retry with Exponential Backoff)
- Network timeouts
- API throttling/rate limits
- Service unavailable (503)
- Quota exceeded
- Regional capacity issues

**Guarantees**:
- 🛑 Logic failures halt the process
- 🔄 Environmental failures trigger smart retry (up to 5 attempts with exponential backoff)
- 📊 All failures logged with classification

### 5. Audit & Traceability

Every deployment produces a structured audit record:

**Record Contents**:
- **Intent**: Git SHA + template/parameters file paths
- **Execution Log**: All CLI outputs and state transitions
- **Result**: Success/failure with detailed messages
- **Resource IDs**: All deployed resources with health status

**Storage Options**:
- **JSON files**: One file per deployment
- **SQLite database**: Queryable deployment history

## Installation

### Prerequisites

1. **Azure CLI** (required):
   ```bash
   # Install Azure CLI
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   
   # Or on macOS
   brew install azure-cli
   
   # Login
   az login
   ```

2. **Bicep CLI** (installed via Azure CLI):
   ```bash
   az bicep install
   az bicep version
   ```

3. **Python 3.8+** (uses standard library only, no additional packages):
   ```bash
   python3 --version
   ```

### Setup

No installation required! The orchestrator uses Python's standard library only.

## Usage

### Basic Deployment

```bash
cd deployment
python3 deploy.py \
  --resource-group "rg-aos-dev" \
  --location "eastus" \
  --template "main-modular.bicep"
```

### With Parameters File

```bash
python3 deploy.py \
  --resource-group "rg-aos-prod" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod.bicepparam"
```

### Parameter Overrides

```bash
python3 deploy.py \
  --resource-group "rg-aos-dev" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --parameters "parameters/dev.bicepparam" \
  --param environment=staging \
  --param functionAppSku=EP1
```

### Advanced Options

```bash
python3 deploy.py \
  --resource-group "rg-aos-prod" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --parameters "parameters/prod.bicepparam" \
  --allow-warnings \              # Allow linter warnings
  --skip-health \                 # Skip health checks (not recommended)
  --audit-dir "./deployment-logs" # Custom audit directory
```

### Dangerous: Skip Delete Confirmation

```bash
# USE WITH EXTREME CAUTION!
python3 deploy.py \
  --resource-group "rg-aos-dev" \
  --location "eastus" \
  --template "main-modular.bicep" \
  --no-confirm-deletes  # Skip confirmation for destructive changes
```

## CLI Reference

```
usage: deploy.py [-h] -g RESOURCE_GROUP -l LOCATION -t TEMPLATE
                 [-p PARAMETERS] [--param KEY=VALUE] [--allow-warnings]
                 [--no-confirm-deletes] [--skip-health] [--audit-dir AUDIT_DIR]
                 [--git-sha GIT_SHA]

Required Arguments:
  -g, --resource-group    Azure resource group name
  -l, --location          Azure region (e.g., eastus, westeurope)
  -t, --template          Path to Bicep template file

Optional Arguments:
  -p, --parameters        Path to parameters file (.bicepparam or .json)
  --param KEY=VALUE       Override a parameter (can be used multiple times)
  --allow-warnings        Allow deployment despite linter warnings
  --no-confirm-deletes    Skip confirmation for destructive changes (DANGEROUS!)
  --skip-health           Skip post-deployment health checks
  --audit-dir DIR         Directory for audit logs (default: ./audit)
  --git-sha SHA           Git commit SHA for audit trail (auto-detected)
```

## Deployment Lifecycle

The orchestrator follows a strict state machine:

```
INITIALIZED
    ↓
VALIDATING_PARAMETERS
    ↓
LINTING (az bicep build)
    ↓
PLANNING (az deployment group what-if)
    ↓
[AWAITING_CONFIRMATION] (if destructive changes detected)
    ↓
DEPLOYING (az deployment group create)
    ↓
VERIFYING_HEALTH (resource health checks)
    ↓
COMPLETED
```

At any point, failures transition to:
```
FAILED → [ROLLED_BACK]
```

## Audit Logs

### SQLite Database (Default)

Audit records are stored in `./audit/audit.db` with three tables:

- **deployments**: Main deployment records
- **deployment_events**: Timestamped event log
- **deployment_resources**: Deployed resources with health status

### JSON Files (Alternative)

Set `use_sqlite=False` in `AuditLogger` to use JSON files instead:

```
./audit/
├── <deployment-id-1>.json
├── <deployment-id-2>.json
└── ...
```

### Audit Record Structure

```json
{
  "deployment_id": "uuid",
  "git_sha": "abc123...",
  "template_file": "main-modular.bicep",
  "parameters_file": "parameters/prod.bicepparam",
  "timestamp": "2026-02-07T04:00:00Z",
  "events": [
    {
      "timestamp": "2026-02-07T04:00:01Z",
      "event_type": "lint",
      "message": "Linting template",
      "details": {}
    },
    ...
  ],
  "result": {
    "success": true,
    "message": "Deployment completed successfully",
    "timestamp": "2026-02-07T04:15:00Z"
  },
  "resources": [
    {
      "resource_id": "/subscriptions/.../resourceGroups/rg-aos-prod/...",
      "resource_type": "storageAccountId",
      "health_status": "healthy"
    },
    ...
  ]
}
```

## Error Handling

### Logic Failures

Halts immediately, no retry:

```
❌ DEPLOYMENT FAILED
Linter Error: Invalid parameter type
Classification: LOGIC
Action: Fix template and retry
```

### Environmental Failures

Retries with exponential backoff:

```
🔄 DEPLOYMENT FAILED (Attempt 1/5)
Error: Service temporarily unavailable (503)
Classification: ENVIRONMENTAL
Action: Retrying in 5 seconds...
```

Retry delays: 5s, 10s, 20s, 40s, 80s (max 5 minutes)

## Integration with Existing Scripts

The orchestrator can replace existing deployment scripts:

### Before (deploy-aos.sh):
```bash
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE" \
  --parameters "@$PARAMETERS_FILE"
```

### After (Python Orchestrator):
```bash
python3 deploy.py \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --template "$TEMPLATE_FILE" \
  --parameters "$PARAMETERS_FILE"
```

**Benefits**:
- ✅ Automatic linting
- ✅ What-if analysis
- ✅ Health verification
- ✅ Audit trail
- ✅ Smart retries
- ✅ Destructive change protection

## Examples

### Example 1: Development Deployment

```bash
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam"
```

### Example 2: Production with Overrides

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus2" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam" \
  --param functionAppSku=EP2 \
  --param serviceBusSku=Premium \
  --param storageSku=Standard_GRS
```

### Example 3: CI/CD Pipeline

```bash
#!/bin/bash
set -e

# Get Git SHA
GIT_SHA=$(git rev-parse HEAD)

# Deploy with orchestrator
python3 deployment/deploy.py \
  --resource-group "${RESOURCE_GROUP}" \
  --location "${LOCATION}" \
  --template "deployment/main-modular.bicep" \
  --parameters "deployment/parameters/${ENVIRONMENT}.bicepparam" \
  --git-sha "${GIT_SHA}" \
  --audit-dir "./deployment-logs" \
  --allow-warnings

# On success, exit code is 0
echo "✅ Deployment completed successfully"
```

## Troubleshooting

### Issue: Azure CLI not found

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

### Issue: Bicep CLI not found

```bash
az bicep install
az bicep upgrade
```

### Issue: Linting fails with errors

```bash
# Run linter directly to see detailed errors
az bicep build --file main-modular.bicep

# Fix errors in the template
# Then retry deployment
```

### Issue: What-if times out

```bash
# Increase timeout in whatif_planner.py
# Or check Azure service health
az status
```

### Issue: Health checks fail

```bash
# Check resource provisioning state manually
az resource show --ids <resource-id>

# Skip health checks if needed (not recommended for production)
python3 deploy.py ... --skip-health
```

## Best Practices

1. **Always use parameters files** for different environments
2. **Never skip health checks** in production
3. **Always review what-if output** before confirming destructive changes
4. **Use Git SHA tracking** for full traceability
5. **Store audit logs** in a persistent location
6. **Monitor deployment failures** and tune retry strategies
7. **Use parameter overrides** for environment-specific values
8. **Test in dev/staging** before production deployments

## Security Considerations

- **No secrets in parameters**: Use Azure Key Vault references
- **Audit logs contain resource IDs**: Store securely
- **Destructive changes require confirmation**: Unless explicitly disabled
- **Git SHA tracking**: Links deployments to code changes

## Future Enhancements

Potential improvements:

- [ ] Integration with Azure DevOps/GitHub Actions
- [ ] Rollback automation on health check failures
- [ ] Parallel resource health checking
- [ ] Custom health check plugins
- [ ] Email/Slack notifications
- [ ] Deployment metrics and dashboards
- [ ] Advanced retry strategies (circuit breaker, jitter)
- [ ] Multi-subscription deployments
- [ ] Cost estimation integration

## Contributing

To extend the orchestrator:

1. Add new validators in `validators/`
2. Add new health checkers in `health/`
3. Extend failure classification patterns in `core/failure_classifier.py`
4. Add new state transitions in `core/state_machine.py`

## License

See repository LICENSE file.

## Support

For issues and questions, please open a GitHub issue in the AgentOperatingSystem repository.
