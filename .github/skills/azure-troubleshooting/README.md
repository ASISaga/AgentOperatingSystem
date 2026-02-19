# Azure Troubleshooting Skill

## Quick Start

This skill provides expert knowledge for troubleshooting Azure infrastructure issues in the Agent Operating System.

## What This Skill Covers

### Deployment Failures
- Resource naming conflicts
- Quota exceeded errors
- Invalid Bicep templates
- Regional availability issues

### Performance Issues
- High response times
- Error rate spikes
- Cold start problems
- Resource under-provisioning

### Connectivity Problems
- Service Bus connection failures
- Storage Account access denied
- Network configuration issues
- Key Vault access problems

### Resource Errors
- Resources in failed state
- Configuration errors
- Permission issues

## How to Use

### 1. Use Automated Troubleshooting Workflow

```bash
gh workflow run infrastructure-troubleshooting.yml \
  -f environment=dev \
  -f issue_type=deployment_failure \
  -f description="Your issue description"
```

### 2. Manual Troubleshooting

Refer to SKILL.md for:
- Diagnostic commands
- Resolution procedures
- Common error codes
- Best practices

### 3. Integration with Other Tools

This skill works with:
- Infrastructure troubleshooting workflow
- Infrastructure monitoring workflow
- Deployment error fixer skill

## Common Scenarios

### Scenario 1: Deployment Failed

```bash
# Run automated diagnostics
gh workflow run infrastructure-troubleshooting.yml \
  -f environment=prod \
  -f issue_type=deployment_failure

# Review the generated report
# Follow resolution steps in SKILL.md
```

### Scenario 2: Performance Degradation

```bash
# Collect performance diagnostics
gh workflow run infrastructure-troubleshooting.yml \
  -f environment=staging \
  -f issue_type=performance_degradation

# Analyze metrics
# Apply recommended fixes
```

### Scenario 3: Connectivity Issue

```bash
# Test connectivity
gh workflow run infrastructure-troubleshooting.yml \
  -f environment=dev \
  -f issue_type=connectivity_issue \
  -f resource_name=aos-func-dev

# Review connection status
# Fix network/permission issues
```

## Quick Reference

### Diagnostic Commands

```bash
# Check resource health
az resource list -g rg-aos-dev -o table

# View recent errors
az monitor activity-log list -g rg-aos-dev --query "[?level=='Error']"

# Check deployment history
az deployment group list -g rg-aos-dev

# View resource metrics
az monitor metrics list --resource <resource-id> --metric <metric-name>
```

### Common Fixes

```bash
# Fix permission issue
az role assignment create --assignee <principal-id> --role <role> --scope <scope>

# Scale up Function App
az functionapp plan update -g rg-aos-dev -n aos-plan --sku P1V2

# Enable Always On
az functionapp config set -g rg-aos-dev -n aos-func --always-on true

# Add Key Vault access
az keyvault set-policy -n aos-kv --object-id <id> --secret-permissions get list
```

## Documentation

- **Full Skill**: See [SKILL.md](SKILL.md) for comprehensive troubleshooting guide
- **Workflows**: Check [infrastructure-troubleshooting.yml](../../workflows/infrastructure-troubleshooting.yml)
- **Monitoring**: See [infrastructure-monitoring.yml](../../workflows/infrastructure-monitoring.yml)

## Related Skills

- [deployment-error-fixer](../deployment-error-fixer/) - Autonomous code error fixing
- [aos-architecture](../aos-architecture/) - System architecture knowledge

## Tips

1. **Start with automated diagnostics** - Run the troubleshooting workflow first
2. **Collect data before changes** - Don't change things blindly
3. **Document your steps** - Record what you try
4. **Test in dev first** - Validate fixes before production
5. **Update monitoring** - Add alerts for recurring issues

## Support

For issues not covered by this skill:
- Check Azure Status Page: https://status.azure.com
- Review Azure documentation
- Contact Azure Support
- Create a GitHub issue in the repository

## Summary

This skill enables rapid diagnosis and resolution of Azure infrastructure issues through:
- ✅ Systematic troubleshooting procedures
- ✅ Common error patterns and fixes
- ✅ Diagnostic command reference
- ✅ Integration with automated workflows
- ✅ Best practices and prevention strategies
