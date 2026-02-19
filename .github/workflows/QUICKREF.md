# Infrastructure Deployment Agent - Quick Reference

## 🚀 Quick Deploy Commands

### Development
```bash
# In PR comment:
/deploy dev
```

### Staging
```bash
# Add label to PR:
deploy:staging
```

### Production
```bash
# Add both labels to PR:
status:approved
action:deploy
```

### Plan Only (Dry-Run)
```bash
# In PR comment:
/plan
```

---

## 📋 Workflow Triggers

| Trigger | Action | Environment | Safety |
|---------|--------|-------------|--------|
| Manual (UI) | Custom deployment | Configurable | Medium |
| `/deploy dev` | Deploy to dev | dev | Low |
| `/deploy staging` | Deploy to staging | staging | Medium |
| `/deploy prod` | Deploy to prod | prod | High |
| `/plan` | What-if analysis | N/A | None |
| Label: `deploy:dev` | Auto-deploy to dev | dev | Low |
| Label: `deploy:staging` | Auto-deploy to staging | staging | Medium |
| Labels: `status:approved` + `action:deploy` | Auto-deploy to prod | prod | High |

---

## 🎯 Environment Configuration

### Dev
- **Resource Group**: `aos-dev-rg`
- **Parameters**: `deployment/parameters/dev.bicepparam`
- **Auto-deploy**: Yes (with label or command)
- **Health Checks**: Optional
- **Approval**: Not required

### Staging
- **Resource Group**: `aos-staging-rg`
- **Parameters**: `deployment/parameters/staging.bicepparam`
- **Auto-deploy**: Yes (with label or command)
- **Health Checks**: Required
- **Approval**: Not required

### Production
- **Resource Group**: `aos-prod-rg`
- **Parameters**: `deployment/parameters/prod.bicepparam`
- **Auto-deploy**: Yes (with BOTH labels)
- **Health Checks**: Required
- **Approval**: REQUIRED (dual-label)

---

## 🔄 Self-Healing Retry

### Retry Schedule
| Attempt | Wait Time | Total Elapsed |
|---------|-----------|---------------|
| Initial | 0s | 0s |
| Retry 1 | 60s | 60s |
| Retry 2 | 120s | 180s |
| Retry 3 | 240s | 420s |

### Retry Triggers (Environmental Failures Only)
- ✅ Timeout
- ✅ Throttling
- ✅ Rate limit exceeded
- ✅ Service unavailable
- ✅ Network errors
- ✅ Temporary failures
- ✅ Quota exceeded
- ✅ Capacity unavailable
- ✅ Conflict with another operation

### No Retry (Logic Failures)
- ❌ Syntax errors
- ❌ Validation failures
- ❌ Template errors
- ❌ Invalid parameters
- ❌ Bicep errors (BCP codes)
- ❌ Missing required parameters

---

## 📊 Status Indicators

### Success
```
✅ Infrastructure Deployment Successful

Environment: dev
Status: Successful

Deployed Resources: 12
Duration: 180 seconds
```

### Logic Failure (No Retry)
```
❌ Infrastructure Deployment Failed

Failure Type: Logic Error (Code/Template)
Action Required: Fix the Bicep template and try again.

⚠️ No retry attempted - code error requires manual intervention.
```

### Environmental Failure (Auto-Retry)
```
✅ Infrastructure Deployment Successful

Self-Healing: Initially failed with transient error,
succeeded after 2 retry attempt(s). 🔄✨

Deployed Resources: 8
Duration: 245 seconds
```

### Environmental Failure (Retries Exhausted)
```
❌ Infrastructure Deployment Failed

Failure Type: Environmental (Transient Azure Issue)
Retries Attempted: 3

⚠️ Issue persisted. Check Azure service health and try again later.
```

---

## 🛡️ Safety Features

### Production Safeguards
- ✅ Requires TWO labels: `status:approved` AND `action:deploy`
- ✅ What-if analysis with confirmation for destructive changes
- ✅ Post-deployment health checks (mandatory)
- ✅ Complete audit trail with 90-day retention
- ✅ Detailed logging of all actions

### Plan Mode (Dry-Run)
- ✅ Runs on all PRs touching Bicep files (automatic)
- ✅ Shows intended changes without deploying
- ✅ Highlights destructive changes
- ✅ Safe to run anytime

### Audit Trail
- ✅ Git SHA tracking
- ✅ All deployment events logged
- ✅ Deployed resource IDs captured
- ✅ Duration tracking
- ✅ Success/failure reasons
- ✅ 90-day artifact retention

---

## 🔍 Monitoring & Troubleshooting

### View Workflow Runs
```
Repository → Actions → Infrastructure Deployment Agent → Select run
```

### Check Deployment Status
- Status is posted as PR comment
- Real-time updates in workflow logs
- Summary in GitHub Actions UI

### Access Audit Logs
```
Workflow run → Artifacts → Download deployment-audit-{run-id}
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Workflow doesn't trigger | Wrong label/command format | Use exact format: `/deploy dev` or label `deploy:dev` |
| Auth failed | Missing secrets | Configure Azure secrets in repo settings |
| Logic error | Template issue | Fix Bicep template, then retry |
| Environmental error | Azure service issue | Workflow auto-retries. If exhausted, wait and retry |
| Takes too long | Large deployment | Normal for many resources. Use `--skip-health` for dev |

---

## 📝 Required Secrets

Configure in: **Repository Settings → Secrets and variables → Actions**

| Secret | Description | Example |
|--------|-------------|---------|
| `AZURE_CLIENT_ID` | Azure AD App Client ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_TENANT_ID` | Azure AD Tenant ID | `87654321-4321-4321-4321-210987654321` |
| `AZURE_SUBSCRIPTION_ID` | Azure Subscription ID | `abcdef12-3456-7890-abcd-ef1234567890` |

---

## 📚 Documentation

- **Workflow README**: `.github/workflows/README.md`
- **Agent Instructions**: `.github/agents/infrastructure-deploy.agent.md`
- **Usage Examples**: `.github/workflows/USAGE_EXAMPLES.md`
- **Orchestrator Guide**: `deployment/ORCHESTRATOR_USER_GUIDE.md`
- **Deployment Plan**: `docs/development/DEPLOYMENT_PLAN.md`

---

## 💡 Pro Tips

### Fast Dev Iteration
1. Use `/plan` first to preview changes
2. Deploy to dev: `/deploy dev`
3. Test in dev environment
4. When confident, label: `deploy:staging`

### Emergency Hotfix
1. Create hotfix PR
2. Get quick approval
3. Add both production labels
4. Monitor workflow closely
5. Verify health checks pass

### Testing Individual Modules
1. Go to Actions → Infrastructure Deployment Agent
2. Run workflow manually
3. Specify custom template path
4. Deploy to isolated resource group

### Monitoring Active Deployments
1. Actions tab → Filter by workflow
2. Watch live execution
3. Check each step's output
4. Download audit logs when complete

---

## ⚡ Workflow Execution Time

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Setup & Auth | 30-60s | 30-60s |
| Linting | 10-20s | 40-80s |
| What-if Analysis | 30-60s | 70-140s |
| Deployment | 60-300s | 130-440s |
| Health Checks | 30-60s | 160-500s |
| **Total (typical)** | **~3-8 minutes** | - |

*Add 60-420s for retries on environmental failures*

---

## 🎯 Success Criteria

### Development
- ✅ What-if shows expected changes
- ✅ No linting errors
- ✅ Deployment completes successfully
- ✅ Resources created in dev environment

### Staging
- ✅ All dev criteria met
- ✅ Health checks pass
- ✅ No destructive changes (unless intended)
- ✅ Team validation successful

### Production
- ✅ All staging criteria met
- ✅ PR approved by reviewer
- ✅ Both labels applied
- ✅ Audit log generated
- ✅ Post-deployment health checks pass
- ✅ No errors in workflow run

---

## 🚨 Emergency Procedures

### Rollback
```bash
# Option 1: Revert PR and redeploy
git revert <commit-sha>
# Then use /deploy prod in new PR

# Option 2: Manual via Azure CLI
az deployment group create \
  --resource-group aos-prod-rg \
  --template-file deployment/main-modular.bicep \
  --parameters @deployment/parameters/prod-rollback.bicepparam
```

### Bypass Workflow (Emergency Only)
```bash
# Only if workflow is broken and deployment is critical
cd deployment
python3 deploy.py \
  --resource-group aos-prod-rg \
  --location eastus \
  --template main-modular.bicep \
  --parameters parameters/prod.bicepparam
```

**⚠️ Warning**: Document all manual deployments in incident log!

---

## 📞 Getting Help

1. **Check workflow logs**: Detailed execution trace
2. **Review PR comments**: Agent posts status
3. **Download audit logs**: Complete deployment history
4. **Consult documentation**: Links above
5. **Open issue**: Include workflow run URL and error

---

## Summary

**Deploy to dev**: `/deploy dev` in PR comment
**Deploy to staging**: Add label `deploy:staging`
**Deploy to production**: Add labels `status:approved` + `action:deploy`
**See what would change**: `/plan` in PR comment

The agent handles everything else: authentication, validation, deployment, retries, health checks, and status reporting! 🎉
