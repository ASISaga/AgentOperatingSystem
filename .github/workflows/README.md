# GitHub Workflows Documentation

This directory contains GitHub Actions workflows for the Agent Operating System (AOS) repository.

## Available Workflows

### 1. Infrastructure Deployment Agent (`infrastructure-deploy.yml`)

**Purpose**: Agentic deployment operator that manages infrastructure deployments using a three-tier architecture.

**Architecture**:
```
Agent Layer (Workflow) → Python Layer (deploy.py) → Bicep Layer (Infrastructure)
```

**Key Features**:
- **Intent-based deployment**: Deploy via PR labels, comments, or manual trigger
- **Intelligent error handling**: Classifies failures as logic vs environmental
- **Self-healing**: Auto-retry transient Azure API errors with exponential backoff
- **Safety constraints**: Requires approval labels for production deployments
- **Audit trail**: Complete deployment history with 90-day artifact retention

**Triggers**:
- **Manual**: Via workflow_dispatch in GitHub UI
- **PR Labels**: `deploy:dev`, `deploy:staging`, or `status:approved` + `action:deploy`
- **Comments**: `/deploy dev`, `/deploy staging`, `/deploy prod`, or `/plan`

**Usage Examples**:

```bash
# Deploy to dev environment via PR comment
/deploy dev

# Run what-if analysis without deploying
/plan

# Deploy to production (requires approval labels)
# 1. Add labels: status:approved AND action:deploy
# 2. Workflow auto-triggers
```

**Required Secrets**:
- `AZURE_CLIENT_ID`: Azure AD application client ID
- `AZURE_TENANT_ID`: Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID

**Documentation**: See `.github/agents/infrastructure-deploy.agent.md` for detailed agent instructions.

---

### 2. Pylint Code Quality (`pylint.yml`)

**Purpose**: Automated code quality checks using Pylint.

**Triggers**:
- Push to `main` or `develop` branches (Python files only)
- Pull requests to `main` or `develop` branches (Python files only)

**Features**:
- Tests against Python 3.10, 3.11, and 3.12
- Generates detailed reports for source, tests, and function_app.py
- Uploads results as artifacts
- Enforces minimum quality score of 5.0/10

**Usage**: Automatically runs on Python file changes. No manual intervention required.

---

## Workflow Best Practices

### When to Use Infrastructure Deployment Agent

**✅ Use for**:
- Deploying infrastructure changes from PRs
- Running what-if analysis before merging
- Automated deployments to dev/staging
- Controlled production deployments with approval

**❌ Do not use for**:
- Quick local testing (use `deployment/deploy.py` locally instead)
- Emergency hotfixes (use Azure Portal or Azure CLI directly)
- Non-infrastructure changes

### Safety Guidelines

#### Production Deployments
Production deployments require **both** of these labels on the PR:
1. `status:approved` - Indicates code review approval
2. `action:deploy` - Explicit deployment authorization

This two-label requirement prevents accidental production deployments.

#### Development/Staging Deployments
Single label required:
- `deploy:dev` - Deploy to dev environment
- `deploy:staging` - Deploy to staging environment

#### Plan/Dry-Run Mode
Any PR touching infrastructure files without deployment labels will run in plan mode:
- Executes what-if analysis
- Shows intended changes
- Does not modify infrastructure

### Monitoring Deployments

#### View Active Runs
1. Go to repository **Actions** tab
2. Select **Infrastructure Deployment Agent** workflow
3. Click on specific run to view details

#### Check Deployment Status
- Status is posted as PR comment automatically
- Includes: environment, resource group, success/failure, retry information

#### Access Audit Logs
1. Go to workflow run page
2. Scroll to **Artifacts** section
3. Download `deployment-audit-{run-id}`
4. Extract and review JSON audit files

### Troubleshooting

#### Deployment Fails with "Logic Error"
**Cause**: Syntax error, validation failure, or template issue
**Action**: 
1. Review error details in PR comment
2. Fix Bicep template or parameters
3. Push changes to trigger re-run

#### Deployment Fails with "Environmental Error"
**Cause**: Azure API throttling, timeout, or service unavailable
**Action**:
1. Check if workflow auto-retried (shown in PR comment)
2. If retries exhausted, wait and manually re-trigger
3. Check Azure service health status

#### Workflow Doesn't Trigger
**Possible causes**:
- PR doesn't have correct label
- Comment format incorrect (must be exact: `/deploy dev`)
- Workflow file has syntax error

**Action**:
1. Verify label is applied correctly
2. Check comment is exact command format
3. Validate workflow YAML syntax

#### Authentication Fails
**Cause**: Missing or incorrect Azure secrets
**Action**:
1. Verify secrets are configured in repository settings
2. Check OIDC federation is set up in Azure AD
3. Verify service principal has necessary permissions

## Workflow Maintenance

### Adding New Workflow

1. Create `.github/workflows/my-workflow.yml`
2. Add workflow documentation to this README
3. Test in PR before merging to main
4. Update any related documentation

### Modifying Existing Workflow

1. Create feature branch
2. Modify workflow file
3. Test thoroughly in PR
4. Update documentation if behavior changes
5. Get review before merging

### Secrets Management

**Never commit secrets to workflow files!**

Required secrets are configured in:
- Repository Settings → Secrets and variables → Actions
- Environment-specific secrets in repository environments

To add/update secrets:
1. Go to repository Settings
2. Navigate to Secrets and variables → Actions
3. Click "New repository secret" or update existing
4. Enter name and value
5. Click "Add secret"

## Integration with Development Workflow

### Development Flow
```
1. Developer creates PR with infrastructure changes
2. Workflow runs what-if analysis automatically
3. Developer reviews changes in PR comment
4. Developer adds deploy:dev label
5. Workflow deploys to dev environment
6. Developer tests changes in dev
7. Developer adds deploy:staging label  
8. Workflow deploys to staging
9. Team validates in staging
10. Reviewer approves PR and adds status:approved
11. Approver adds action:deploy label
12. Workflow deploys to production
13. PR is merged
```

### Local Development
For local testing before creating PR:
```bash
cd deployment
python3 deploy.py \
  --resource-group my-dev-rg \
  --location eastus \
  --template main-modular.bicep \
  --parameters parameters/dev.bicepparam
```

See `deployment/ORCHESTRATOR_USER_GUIDE.md` for more details.

## Advanced Usage

### Custom Parameters
Override parameters via manual workflow trigger:
1. Go to Actions → Infrastructure Deployment Agent
2. Click "Run workflow"
3. Fill in custom values
4. Click "Run workflow" button

### Skipping Health Checks
For faster deployments in dev:
1. Use manual trigger
2. Check "Skip health checks" option
3. Run workflow

**Warning**: Only skip health checks in dev environment!

### Audit Trail Analysis
Audit logs contain:
- Git SHA of deployed code
- Template and parameters used
- All deployment events with timestamps
- Deployed resource IDs
- Success/failure status
- Duration

Example audit log query:
```bash
# Download audit artifact
unzip deployment-audit-12345.zip

# View latest audit
cat audit/deployment-*.json | jq .

# Extract deployed resources
cat audit/deployment-*.json | jq '.deployed_resources'
```

## Related Documentation

- **Agent Documentation**: `.github/agents/infrastructure-deploy.agent.md`
- **Deployment Guide**: `deployment/ORCHESTRATOR_USER_GUIDE.md`
- **Deployment Plan**: `docs/development/DEPLOYMENT_PLAN.md`
- **Bicep Templates**: `deployment/README.md`
- **Regional Requirements**: `deployment/REGIONAL_REQUIREMENTS.md`

## Support

For issues or questions:
1. Check this documentation first
2. Review workflow run logs
3. Check audit logs for deployment details
4. Open issue in repository with:
   - Workflow run URL
   - Error message
   - Expected vs actual behavior
