# Infrastructure Deployment Agent - Usage Examples

This document provides practical examples of using the GitHub Agentic Infrastructure Deployment workflow.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Development Workflow](#development-workflow)
3. [Staging Deployment](#staging-deployment)
4. [Production Deployment](#production-deployment)
5. [What-If Analysis](#what-if-analysis)
6. [Handling Failures](#handling-failures)
7. [Advanced Scenarios](#advanced-scenarios)

---

## Quick Start

### Deploy to Dev via PR Comment

**Scenario**: You've made infrastructure changes and want to deploy them to dev.

**Steps**:
1. Create a PR with your infrastructure changes
2. Wait for CI checks to pass
3. Add a comment to the PR:
   ```
   /deploy dev
   ```
4. The workflow will:
   - Authenticate to Azure
   - Run linting and what-if analysis
   - Deploy to dev environment
   - Post results back to the PR

**Expected Output**:
```
🚀 Infrastructure Deployment Started

Environment: dev
Resource Group: aos-dev-rg
Location: eastus
Template: deployment/main-modular.bicep

The agent is now analyzing the deployment...
```

Then after completion:
```
✅ Infrastructure Deployment Successful

Environment: dev
Resource Group: aos-dev-rg
Status: Successful

Deployed Resources: 12
Duration: 180 seconds

View workflow run
```

---

## Development Workflow

### Typical Dev-to-Prod Flow

```
┌─────────────────────────────────────────────┐
│ 1. Developer makes infrastructure changes   │
│    - Edit Bicep files                       │
│    - Update parameters                      │
│    - Create PR                              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 2. Automatic what-if analysis               │
│    - Workflow detects Bicep changes         │
│    - Runs in plan mode                      │
│    - Posts analysis to PR                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 3. Deploy to dev                            │
│    - Developer comments: /deploy dev        │
│    - Workflow deploys to dev                │
│    - Developer tests changes                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 4. Deploy to staging                        │
│    - Developer adds label: deploy:staging   │
│    - Workflow auto-deploys                  │
│    - Team validates in staging              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 5. Production approval                      │
│    - Reviewer approves PR                   │
│    - Add label: status:approved             │
│    - Add label: action:deploy               │
│    - Workflow deploys to production         │
└─────────────────────────────────────────────┘
```

**Example PR Timeline**:

```
Day 1, 10:00 AM - Developer creates PR
  📝 PR #123: Add Azure AI Search module

Day 1, 10:05 AM - Automatic plan runs
  🤖 Bot comments: "Plan shows: +3 new resources, ~2 modified"

Day 1, 11:30 AM - Deploy to dev
  💬 Developer: "/deploy dev"
  🚀 Workflow: "Starting deployment to dev..."
  ✅ Workflow: "Deployment successful! 5 resources deployed in 120s"

Day 1, 2:00 PM - Deploy to staging
  🏷️ Developer adds label: deploy:staging
  🚀 Workflow auto-triggers
  ✅ "Deployment to staging successful!"

Day 2, 9:00 AM - Production deployment
  👍 Reviewer approves PR
  🏷️ Reviewer adds: status:approved, action:deploy
  🚀 Workflow deploys to production
  ✅ "Production deployment successful!"
  🎉 PR merged
```

---

## Staging Deployment

### Deploy to Staging via Label

**Scenario**: Your dev deployment succeeded, now deploy to staging.

**Steps**:
1. Go to your PR
2. Click "Labels" on the right sidebar
3. Add the `deploy:staging` label
4. Workflow auto-triggers

**Configuration**:
- Environment: `staging`
- Resource Group: `aos-staging-rg`
- Parameters: `deployment/parameters/staging.bicepparam`

**Safety**: Staging deployments are automatic when labeled. No additional approval needed.

---

## Production Deployment

### Deploy to Production (Dual-Label Safety)

**Scenario**: All testing complete, ready for production.

**Steps**:
1. Ensure PR is approved by reviewer
2. Add TWO labels (both required):
   - `status:approved` - Indicates code review approval
   - `action:deploy` - Explicit deployment authorization
3. Workflow auto-triggers and deploys to production

**Why Two Labels?**
This dual-label requirement prevents accidental production deployments:
- `status:approved` alone = PR approved but not deployed
- `action:deploy` alone = Cannot deploy without approval
- Both together = Approved AND authorized to deploy

**Example**:
```
Reviewer flow:
1. Review code changes
2. Approve PR (GitHub approval)
3. Add label: status:approved
4. Verify deployment intent
5. Add label: action:deploy
6. Monitor deployment
```

**Production Safety Checks**:
- ✅ Both labels present
- ✅ What-if analysis with destructive change confirmation
- ✅ Post-deployment health checks
- ✅ Complete audit trail
- ✅ 90-day log retention

---

## What-If Analysis

### Plan Without Deploying

**Scenario**: You want to see what changes would be made without actually deploying.

**Method 1: Automatic (PR created)**
- Create PR touching Bicep files
- Workflow automatically runs what-if analysis
- Results posted to PR

**Method 2: Manual (/plan command)**
```
1. Create PR
2. Comment: /plan
3. Workflow runs analysis
4. Results posted back
```

**Example Output**:
```
📊 Infrastructure Plan/Analysis Successful

Environment: dev
Resource Group: aos-dev-rg
Status: Successful

This was a plan/dry-run - no actual infrastructure changes were made.

Planned Changes:
  + storage account: aosdevstorage123
  + key vault: aos-dev-kv-456
  ~ function app: aos-dev-func (update)
  - cosmos db: aos-dev-cosmos (delete) ⚠️

View workflow run
```

---

## Handling Failures

### Scenario 1: Bicep Syntax Error (Logic Failure)

**What Happens**:
```
PR Comment: /deploy dev

Workflow runs:
  🔍 Linting template...
  ❌ Error BCP123: Property 'invalidProperty' is not allowed

Agent analyzes:
  🔴 Logic failure detected - code/template error
  ⚠️ No retry attempted
```

**Posted Comment**:
```
❌ Infrastructure Deployment Failed

Environment: dev
Status: Failed

Failure Type: Logic Error (Code/Template)
Action Required: Please fix the Bicep template and try again.

⚠️ No retry attempted - this is a code error that requires manual intervention.

Error: Property 'invalidProperty' is not allowed on resource type 'Microsoft.Storage/storageAccounts'
```

**Developer Action**:
1. Review error in workflow logs
2. Fix Bicep template
3. Commit fix to PR
4. Re-trigger deployment: `/deploy dev`

---

### Scenario 2: Azure Throttling (Environmental Failure)

**What Happens**:
```
PR Comment: /deploy dev

Workflow runs:
  🔍 Linting... ✅
  📊 What-if... ✅
  🚀 Deploying...
  ❌ TooManyRequests: Rate limit exceeded

Agent analyzes:
  🟡 Environmental failure detected - transient Azure issue
  🔄 Self-healing retry enabled

Retry 1 (wait 60s):
  🕐 Waiting...
  🔄 Retrying deployment...
  ❌ Still throttled

Retry 2 (wait 120s):
  🕐 Waiting...
  🔄 Retrying deployment...
  ✅ Success!
```

**Posted Comment**:
```
✅ Infrastructure Deployment Successful

Environment: dev
Status: Successful

Self-Healing: The deployment initially failed with a transient error,
but succeeded after 2 retry attempt(s). 🔄✨

Deployed Resources: 8
Duration: 245 seconds (including retry delays)
```

**Developer Action**: None! The agent self-healed.

---

### Scenario 3: Persistent Environmental Failure

**What Happens**:
```
Initial deployment: ❌ ServiceUnavailable
Retry 1: ❌ ServiceUnavailable
Retry 2: ❌ ServiceUnavailable  
Retry 3: ❌ ServiceUnavailable

All retries exhausted.
```

**Posted Comment**:
```
❌ Infrastructure Deployment Failed

Environment: dev
Status: Failed

Failure Type: Environmental (Transient Azure Issue)
Retries Attempted: 3

⚠️ The issue persisted after retry attempts. This may require:
- Checking Azure service health
- Trying again later
- Adjusting resource configurations
```

**Developer Action**:
1. Check Azure service health dashboard
2. Wait for Azure service to recover
3. Manually re-trigger: `/deploy dev`

---

## Advanced Scenarios

### Custom Parameters via Manual Trigger

**Scenario**: Deploy with custom resource group or region.

**Steps**:
1. Go to **Actions** → **Infrastructure Deployment Agent**
2. Click **Run workflow**
3. Fill in parameters:
   - **Environment**: `dev`
   - **Resource Group**: `my-custom-rg`
   - **Location**: `westeurope`
   - **Template**: `deployment/main-modular.bicep`
   - **Skip health checks**: `false`
4. Click **Run workflow**

**Use Cases**:
- Testing in isolated resource groups
- Deploying to different regions
- Quick experimentation
- Disaster recovery to alternate region

---

### Skipping Health Checks (Dev Only)

**Scenario**: Fast iteration in dev, skip post-deployment health checks.

**Method**: Manual workflow trigger with skip option

**Steps**:
1. Actions → Infrastructure Deployment Agent
2. Run workflow
3. Check "Skip health checks"
4. Deploy

**Warning**: Only use in dev! Production should always have health checks.

---

### Deploying Specific Template

**Scenario**: Deploy a specific Bicep template, not the main one.

**Method**: Manual workflow trigger

**Example**:
```
Template: deployment/modules/storage.bicep
Parameters: deployment/parameters/storage-dev.bicepparam
```

**Use Case**: Testing individual modules before integrating.

---

### Monitoring Active Deployments

**Steps**:
1. Go to **Actions** tab
2. Filter by "Infrastructure Deployment Agent"
3. View active/recent runs
4. Click run for detailed logs

**Real-time Monitoring**:
- See live workflow execution
- View each step's output
- Monitor retry attempts
- Check audit log uploads

---

### Accessing Audit Logs

**Steps**:
1. Go to completed workflow run
2. Scroll to **Artifacts** section
3. Download `deployment-audit-{run-id}`
4. Extract ZIP file
5. Open JSON audit file

**Audit Log Contents**:
```json
{
  "git_sha": "abc123...",
  "template_file": "deployment/main-modular.bicep",
  "parameters_file": "deployment/parameters/dev.bicepparam",
  "start_time": "2024-02-19T10:00:00Z",
  "end_time": "2024-02-19T10:05:30Z",
  "duration_seconds": 330,
  "success": true,
  "events": [
    {
      "timestamp": "2024-02-19T10:00:00Z",
      "phase": "validate",
      "message": "Validating parameters",
      "details": {}
    },
    ...
  ],
  "deployed_resources": [
    "/subscriptions/.../resourceGroups/aos-dev-rg/providers/Microsoft.Storage/storageAccounts/aosdevstorage",
    ...
  ]
}
```

**Use Cases**:
- Compliance auditing
- Troubleshooting historical deployments
- Resource tracking
- Duration analysis

---

## Troubleshooting Guide

### "Workflow didn't trigger"

**Check**:
- [ ] Label is exact (case-sensitive)
- [ ] Comment format is exact: `/deploy dev` (no extra spaces)
- [ ] Workflow file has no syntax errors
- [ ] You have write permissions on the repo

### "Authentication failed"

**Check**:
- [ ] Secrets are configured in repo settings
- [ ] OIDC federation is set up in Azure AD
- [ ] Service principal has contributor role
- [ ] Subscription ID is correct

### "Deployment takes too long"

**Causes**:
- Large number of resources
- Cross-region replication
- Custom script extensions

**Solutions**:
- Use `--skip-health` for dev (manual trigger)
- Deploy incrementally (one module at a time)
- Check for timeout issues in logs

### "Getting logic errors but template is valid"

**Check**:
- [ ] Bicep CLI version matches workflow
- [ ] Parameters file format is correct (.bicepparam)
- [ ] All required parameters are provided
- [ ] Resource names meet Azure naming rules

---

## Best Practices

### ✅ Do

- Use `/plan` before deploying major changes
- Test in dev before staging
- Test in staging before production
- Review what-if output carefully
- Monitor workflow execution
- Check audit logs for compliance
- Use custom resource groups for experiments

### ❌ Don't

- Deploy to production without approval labels
- Skip health checks in production
- Ignore what-if warnings
- Deploy without testing in lower environments
- Bypass the workflow (use Azure CLI directly) unless emergency
- Delete workflow artifacts prematurely (90-day retention is intentional)

---

## Getting Help

1. **Check workflow logs**: Actions → Run → View logs
2. **Review audit logs**: Download from artifacts
3. **Check PR comments**: Agent posts detailed status
4. **Consult documentation**: 
   - `.github/workflows/README.md`
   - `.github/agents/infrastructure-deploy.agent.md`
   - `deployment/ORCHESTRATOR_USER_GUIDE.md`
4. **Open issue**: Include workflow run URL and error message

---

## Summary

The Infrastructure Deployment Agent provides:
- 🎯 **Intent-based deployment**: Natural language commands
- 🛡️ **Safety constraints**: Production requires dual approval
- 🔄 **Self-healing**: Auto-retry transient failures
- 📊 **Visibility**: Detailed status in PR comments
- 📝 **Audit trail**: Complete deployment history
- 🚀 **Automation**: From comment to deployed infrastructure

Start with `/plan` to see what would change, then `/deploy dev` when ready!
