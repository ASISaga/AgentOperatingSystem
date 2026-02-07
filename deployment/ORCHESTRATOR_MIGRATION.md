# Migration Guide: Transitioning to Python Orchestrator

This guide helps you migrate from legacy deployment scripts to the new Python orchestration layer.

## Why Migrate?

The Python orchestrator provides:

✅ **Static Integrity**: Mandatory Bicep linting before deployment  
✅ **Risk Assessment**: What-if analysis with destructive change warnings  
✅ **Health Verification**: Post-deployment resource health checks  
✅ **Failure Intelligence**: Smart retry for environmental issues  
✅ **Audit Trail**: Complete deployment history with Git SHA tracking  
✅ **Parameter Override**: Dynamic parameter modification  

## Migration Comparison

### Before: PowerShell Script

```powershell
.\Deploy-AOS.ps1 `
  -ResourceGroupName "rg-aos-prod" `
  -Location "eastus" `
  -Environment "prod" `
  -DeployCode
```

**Limitations:**
- No linting before deployment
- No what-if analysis
- No health verification
- Limited error handling
- No audit trail

### After: Python Orchestrator

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam"
```

**Benefits:**
- ✅ Automatic linting with error gates
- ✅ What-if analysis before deployment
- ✅ Health verification after deployment
- ✅ Smart retry on failures
- ✅ Complete audit trail in SQLite/JSON

## Step-by-Step Migration

### 1. Verify Prerequisites

```bash
# Check Python version (3.8+)
python3 --version

# Check Azure CLI
az --version

# Check Bicep CLI
az bicep version
```

### 2. Convert Parameters (If Needed)

If you're using legacy JSON parameters, convert to `.bicepparam` format:

**Old (parameters.dev.json):**
```json
{
  "$schema": "...",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {"value": "eastus"},
    "environment": {"value": "dev"}
  }
}
```

**New (parameters/dev.bicepparam):**
```bicep
using '../main-modular.bicep'

param location = 'eastus'
param environment = 'dev'
param functionAppSku = 'Y1'
param serviceBusSku = 'Standard'
```

### 3. Test in Development First

```bash
cd deployment

# Run a dev deployment
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam" \
  --allow-warnings
```

### 4. Review Quality Gates

The orchestrator will:

1. **Validate** parameters and files
2. **Lint** the Bicep template
3. **Analyze** changes (what-if)
4. **Prompt** for confirmation on deletions
5. **Deploy** to Azure
6. **Verify** resource health

### 5. Migrate Production

```bash
python3 deploy.py \
  -g "rg-aos-prod" \
  -l "eastus2" \
  -t "main-modular.bicep" \
  -p "parameters/prod.bicepparam" \
  --git-sha "$(git rev-parse HEAD)"
```

## Command Mapping

### PowerShell → Python Orchestrator

| PowerShell | Python Orchestrator |
|------------|---------------------|
| `-ResourceGroupName "rg-aos-dev"` | `-g "rg-aos-dev"` or `--resource-group "rg-aos-dev"` |
| `-Location "eastus"` | `-l "eastus"` or `--location "eastus"` |
| `-Environment "dev"` | `-p "parameters/dev.bicepparam"` |
| `-ParametersFile "custom.json"` | `-p "custom.bicepparam"` or `-p "custom.json"` |
| `-SkipPreCheck` | Not applicable (always validates) |
| `-SkipPostCheck` | `--skip-health` |
| N/A | `--param key=value` (parameter overrides) |
| N/A | `--allow-warnings` (allow linter warnings) |
| N/A | `--audit-dir "./logs"` (custom audit location) |

### Bash → Python Orchestrator

| Bash | Python Orchestrator |
|------|---------------------|
| `./deploy-aos.sh -g "rg" -l "loc" -e "env"` | `python3 deploy.py -g "rg" -l "loc" -t "template" -p "params"` |
| `-c, --deploy-code` | Not applicable (infrastructure only) |
| `--skip-pre-check` | Not applicable (always validates) |
| `--skip-post-check` | `--skip-health` |

## Parameter Override Examples

### Before: PowerShell

```powershell
# No built-in override - had to edit parameters file
```

### After: Python Orchestrator

```bash
# Dynamic parameter overrides
python3 deploy.py \
  -g "rg-aos-staging" \
  -l "westus2" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam" \
  --param environment=staging \
  --param functionAppSku=EP1 \
  --param serviceBusSku=Premium
```

## CI/CD Migration

### Before: GitHub Actions with PowerShell

```yaml
- name: Deploy Infrastructure
  run: |
    cd deployment
    pwsh Deploy-AOS.ps1 `
      -ResourceGroupName "${{ vars.RESOURCE_GROUP }}" `
      -Location "${{ vars.LOCATION }}" `
      -Environment "${{ vars.ENVIRONMENT }}"
```

### After: GitHub Actions with Orchestrator

```yaml
- name: Deploy Infrastructure
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

## Handling Common Scenarios

### Scenario 1: Allowing Warnings

**Before**: No option (warnings ignored)

**After**:
```bash
python3 deploy.py ... --allow-warnings
```

### Scenario 2: Skipping Health Checks

**Before**: `--skip-post-check`

**After**:
```bash
python3 deploy.py ... --skip-health
```

### Scenario 3: Custom Parameters File

**Before**: `-ParametersFile "custom.json"`

**After**:
```bash
python3 deploy.py ... -p "custom.bicepparam"
# OR
python3 deploy.py ... -p "custom.json"  # Legacy JSON still supported
```

### Scenario 4: Automated Deployments (No Prompts)

**Before**: No confirmations

**After**: Use `--no-confirm-deletes` (DANGEROUS!)
```bash
python3 deploy.py ... --no-confirm-deletes
```

**⚠️ Warning**: Only use in CI/CD where you're CERTAIN about changes!

## Rollback Strategy

If you need to rollback to legacy scripts:

1. Keep legacy scripts for backup:
   - `Deploy-AOS.ps1`
   - `deploy-aos.sh`

2. Use legacy JSON parameters:
   - `parameters.dev.json`
   - `parameters.prod.json`

3. Deploy with legacy method:
   ```bash
   ./deploy-aos.sh -g "rg-aos-dev" -l "eastus" -e "dev"
   ```

## Troubleshooting Migration

### Issue: "Template file not found"

**Problem**: Incorrect path to template file

**Solution**:
```bash
# Use correct path
python3 deploy.py -t "main-modular.bicep" ...
# OR absolute path
python3 deploy.py -t "$(pwd)/main-modular.bicep" ...
```

### Issue: "Parameters file not found"

**Problem**: Incorrect path to parameters file

**Solution**:
```bash
# Use correct path
python3 deploy.py -p "parameters/dev.bicepparam" ...
```

### Issue: Linting fails with errors

**Problem**: Template has syntax errors

**Solution**:
```bash
# Run linter directly to see detailed errors
az bicep build --file main-modular.bicep

# Fix errors in template
# Then retry deployment
```

### Issue: What-if shows unexpected changes

**Problem**: Template or parameters changed

**Solution**:
1. Review what-if output carefully
2. Confirm changes are expected
3. Type "yes" to proceed or "no" to cancel
4. Fix template/parameters if needed

### Issue: Health checks fail

**Problem**: Resources not fully provisioned

**Solution**:
1. Check Azure portal for resource status
2. Review audit logs for details
3. Retry deployment if transient failure
4. Or skip health checks: `--skip-health` (not recommended for production)

## Best Practices

1. **Always test in dev first**: Validate the orchestrator works with your templates

2. **Review what-if output**: Understand changes before confirming

3. **Use Git SHA tracking**: Enable full traceability
   ```bash
   --git-sha "$(git rev-parse HEAD)"
   ```

4. **Store audit logs**: Keep deployment history
   ```bash
   --audit-dir "/var/log/deployments"
   ```

5. **Parameter overrides for environments**: Use same parameters file, override as needed
   ```bash
   python3 deploy.py \
     -p "parameters/dev.bicepparam" \
     --param environment=staging \
     --param functionAppSku=EP1
   ```

6. **CI/CD automation**: Upload audit logs as artifacts

7. **Keep legacy scripts**: As backup during transition period

## Support

For issues during migration:
- Review [ORCHESTRATOR_USER_GUIDE.md](./ORCHESTRATOR_USER_GUIDE.md)
- Check [orchestrator/README.md](./orchestrator/README.md)
- Open GitHub issue for bugs or questions

## Complete Migration Checklist

- [ ] Verify Python 3.8+ installed
- [ ] Verify Azure CLI and Bicep CLI installed
- [ ] Convert parameters to `.bicepparam` format (or use legacy JSON)
- [ ] Test orchestrator in dev environment
- [ ] Review and understand quality gates
- [ ] Update CI/CD pipelines
- [ ] Migrate staging deployments
- [ ] Migrate production deployments
- [ ] Document any custom configurations
- [ ] Train team on new orchestrator
- [ ] Archive legacy scripts (don't delete yet)

## Timeline Recommendation

- **Week 1**: Test orchestrator in dev, familiarize with features
- **Week 2**: Update CI/CD pipelines, test in staging
- **Week 3**: Migrate production, monitor closely
- **Week 4**: Review audit logs, tune configurations
- **Month 2**: Fully operational, can retire legacy scripts

## Questions?

See the [User Guide](./ORCHESTRATOR_USER_GUIDE.md) for detailed usage information.
