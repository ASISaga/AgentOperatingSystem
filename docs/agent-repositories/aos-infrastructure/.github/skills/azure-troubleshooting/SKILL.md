---
name: azure-troubleshooting
description: Expert knowledge for troubleshooting Azure infrastructure issues in the Agent Operating System. Provides diagnostic procedures, common issue patterns, and resolution strategies for deployment failures, performance problems, and connectivity issues.
---

# Azure Troubleshooting Skill

## Description
Expert skill for diagnosing and resolving Azure infrastructure issues in the Agent Operating System (AOS). This skill provides systematic troubleshooting procedures, common error patterns, and resolution strategies for the most frequent issues encountered in Azure deployments.

## When to Use This Skill
- Deployment failures in Azure
- Performance degradation of deployed resources
- Connectivity issues between Azure services
- Resource provisioning errors
- Configuration problems
- After automated diagnostics detect issues

## Common Azure Issues and Resolutions

### 1. Deployment Failures

#### Issue: Resource Name Already Exists
**Symptoms:**
```
Error: A resource with the name 'aos-storage' already exists
Code: ResourceExists
```

**Resolution:**
```bash
# Check if resource exists
az resource list --name aos-storage

# Delete if not needed, or use different name in template
az resource delete --ids $(az resource list --name aos-storage --query "[0].id" -o tsv)
```

#### Issue: Quota Exceeded
**Symptoms:**
```
Error: Operation could not be completed as it results in exceeding approved quota
Code: QuotaExceeded
```

**Diagnosis:**
```bash
# Check current quota usage
az vm list-usage --location eastus --query "[?currentValue >= maximumValue]" -o table
```

**Resolution:**
1. Request quota increase through Azure portal
2. Use different region with available capacity
3. Delete unused resources to free up quota
4. Use smaller SKUs if applicable

#### Issue: Invalid Template (BCP Errors)
**Symptoms:**
```
Error BCP029: The resource type is not valid
Error BCP033: Expected value type mismatch
```

**Resolution:**
- Use deployment-error-fixer skill for automatic fixes
- Validate Bicep templates: `az bicep build --file template.bicep`
- Check API version compatibility
- Verify parameter types

### 2. Performance Issues

#### Issue: High Response Time in Function Apps
**Symptoms:**
- Slow API responses (>5 seconds)
- Timeout errors

**Diagnosis:**
```bash
# Check Function App metrics
RESOURCE_ID=$(az functionapp show -g rg-aos-dev -n aos-func --query id -o tsv)

az monitor metrics list \
  --resource $RESOURCE_ID \
  --metric "AverageResponseTime" \
  --aggregation Average
```

**Common Causes:**
1. Cold starts (function went idle)
2. Under-provisioned resources
3. Inefficient code
4. Slow external dependencies
5. Throttling

**Resolution:**
```bash
# Enable Always On (Premium/Dedicated plans)
az functionapp config set -g rg-aos-dev -n aos-func --always-on true

# Scale up (increase resources)
az functionapp plan update -g rg-aos-dev -n aos-plan --sku P1V2

# Scale out (more instances)
az functionapp plan update -g rg-aos-dev -n aos-plan --number-of-workers 3
```

### 3. Connectivity Issues

#### Issue: Service Bus Connection Failed
**Symptoms:**
```
Error: ServiceUnavailable
Error: Unauthorized
```

**Resolution:**
1. Verify Service Bus is running
2. Check connection string in Function App settings
3. Verify network rules
4. Check Managed Identity permissions

#### Issue: Storage Account Access Denied
**Symptoms:**
```
Error: AuthorizationPermissionMismatch
```

**Resolution:**
```bash
# Assign required role
PRINCIPAL_ID=$(az functionapp identity show -g rg-aos-dev -n aos-func --query principalId -o tsv)
STORAGE_ID=$(az storage account show -g rg-aos-dev -n aosstoragedev --query id -o tsv)

az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope $STORAGE_ID
```

### 4. Key Vault Access Issues

**Symptoms:**
```
Error: Forbidden - No secrets get permission
```

**Resolution:**
```bash
# Add access policy
PRINCIPAL_ID=$(az functionapp identity show -g rg-aos-dev -n aos-func --query principalId -o tsv)

az keyvault set-policy \
  -g rg-aos-dev \
  -n aos-keyvault \
  --object-id $PRINCIPAL_ID \
  --secret-permissions get list
```

## Troubleshooting Workflow

### Step 1: Identify the Problem
- What is failing?
- When did it start?
- What changed recently?
- Is it intermittent or consistent?

### Step 2: Collect Diagnostics
```bash
# Use automated workflow
gh workflow run infrastructure-troubleshooting.yml \
  -f environment=dev \
  -f issue_type=deployment_failure

# Or manual collection
az monitor activity-log list \
  -g rg-aos-dev \
  --query "[?level=='Error']" \
  -o table
```

### Step 3: Analyze Root Cause
- Check error codes and messages
- Review recent changes
- Check for known issues
- Correlate with other events

### Step 4: Implement Fix
- Start with least disruptive fix
- Test in dev first
- Document the fix
- Monitor after applying

### Step 5: Verify Resolution
- Confirm issue resolved
- Check for side effects
- Update monitoring if needed

## Common Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| ResourceNotFound | Resource doesn't exist | Verify name, create resource |
| ResourceExists | Already exists | Use different name or delete |
| QuotaExceeded | Limit reached | Request increase or use different region |
| InvalidTemplate | Syntax error | Fix template, use linter |
| Unauthorized | Auth failed | Check credentials, add RBAC |
| Forbidden | Permission denied | Add required permissions |
| Conflict | Conflicting operation | Wait and retry |
| Throttled | Rate limited | Implement backoff |
| ServiceUnavailable | Transient failure | Retry, check Azure status |

## Diagnostic Commands

```bash
# Resource health
az resource list -g rg-aos-dev -o table

# Activity logs
az monitor activity-log list -g rg-aos-dev --max-events 50

# Deployment history
az deployment group list -g rg-aos-dev

# Network connectivity
curl -v https://<endpoint>
```

## Best Practices

**Prevention:**
1. Use Infrastructure as Code
2. Implement monitoring
3. Use health checks
4. Follow naming conventions
5. Test in dev first
6. Document changes
7. Use Managed Identities
8. Enable diagnostic logging

**During Incidents:**
1. Stay calm
2. Collect data first
3. Document steps
4. Communicate updates
5. Use systematic approach
6. Escalate when needed

**After Resolution:**
1. Document root cause
2. Implement preventive measures
3. Update monitoring
4. Share learnings
5. Update runbooks

## Integration with Workflows

Use the infrastructure-troubleshooting workflow for automated diagnostics and comprehensive reports.

## Related Documentation

- [Infrastructure Monitoring Workflow](../../workflows/infrastructure-monitoring.yml)
- [Infrastructure Troubleshooting Workflow](../../workflows/infrastructure-troubleshooting.yml)
- [Deployment Error Fixer Skill](../deployment-error-fixer/SKILL.md)

## Summary

This skill provides:
- ✅ Systematic troubleshooting procedures
- ✅ Common Azure error patterns
- ✅ Diagnostic command reference
- ✅ Best practices for prevention
- ✅ Integration with automated workflows
