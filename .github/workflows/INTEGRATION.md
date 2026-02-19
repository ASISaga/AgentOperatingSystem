# Integration Architecture: Agentic Workflow + Python Orchestrator + Bicep

This document explains how the GitHub Agentic Deployment Workflow integrates with the existing AOS deployment infrastructure.

## System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflow                     │
│               (.github/workflows/infrastructure-deploy.yml)     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AGENT LAYER (Intent & Intelligence)                      │  │
│  │                                                           │  │
│  │  • Parse deployment intent (PR labels/comments/manual)   │  │
│  │  • Environment detection (dev/staging/prod)              │  │
│  │  • Azure OIDC authentication                             │  │
│  │  • Output analysis & failure classification              │  │
│  │  • Self-healing retry logic                              │  │
│  │  • Status communication (PR comments)                    │  │
│  │  • Safety constraints enforcement                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    Executes: python3 deploy.py
                              ↓
┌────────────────────────────────────────────────────────────────┐
│              Python Deployment Orchestrator                     │
│                   (deployment/deploy.py)                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ LOGIC LAYER (Orchestration & Quality Gates)             │  │
│  │                                                           │  │
│  │  Phase 1: Parameter Validation                           │  │
│  │    • Verify template and parameters files exist          │  │
│  │    • Validate parameter overrides                        │  │
│  │                                                           │  │
│  │  Phase 2: Bicep Linting                                  │  │
│  │    • Run az bicep build                                  │  │
│  │    • Check for errors and warnings                       │  │
│  │    • Fail on errors, warn on warnings                    │  │
│  │                                                           │  │
│  │  Phase 3: What-If Planning                               │  │
│  │    • Run az deployment group what-if                     │  │
│  │    • Analyze proposed changes                            │  │
│  │    • Detect destructive operations                       │  │
│  │    • Require confirmation for deletes                    │  │
│  │                                                           │  │
│  │  Phase 4: Deployment Execution                           │  │
│  │    • Run az deployment group create                      │  │
│  │    • Track deployment progress                           │  │
│  │    • Capture resource IDs                                │  │
│  │    • Classify failures (logic vs environmental)          │  │
│  │    • Implement basic retry (3 attempts)                  │  │
│  │                                                           │  │
│  │  Phase 5: Health Verification                            │  │
│  │    • Check deployed resources                            │  │
│  │    • Verify service endpoints                            │  │
│  │    • Validate resource states                            │  │
│  │                                                           │  │
│  │  Phase 6: Audit Logging                                  │  │
│  │    • Create audit record with Git SHA                    │  │
│  │    • Log all events and decisions                        │  │
│  │    • Capture deployed resource IDs                       │  │
│  │    • Save to deployment/audit/                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    Calls: az deployment group create
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                    Bicep Templates                              │
│              (deployment/main-modular.bicep)                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ RESOURCE LAYER (Infrastructure as Code)                  │  │
│  │                                                           │  │
│  │  Modules:                                                 │  │
│  │    • storage.bicep       - Azure Storage                 │  │
│  │    • monitoring.bicep    - App Insights, Log Analytics   │  │
│  │    • servicebus.bicep    - Service Bus                   │  │
│  │    • keyvault.bicep      - Key Vault                     │  │
│  │    • identity.bicep      - Managed Identities            │  │
│  │    • compute.bicep       - Function Apps, App Plans      │  │
│  │    • machinelearning.bicep - Azure ML (optional)         │  │
│  │    • rbac.bicep          - Role Assignments              │  │
│  │                                                           │  │
│  │  Parameters (environment-specific):                      │  │
│  │    • deployment/parameters/dev.bicepparam                │  │
│  │    • deployment/parameters/staging.bicepparam            │  │
│  │    • deployment/parameters/prod.bicepparam               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                              ↓
                    Provisions Azure Resources
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                    Azure Infrastructure                         │
│                                                                 │
│  • Storage Accounts                                             │
│  • Service Bus Namespaces                                       │
│  • Function Apps                                                │
│  • Key Vaults                                                   │
│  • Application Insights                                         │
│  • Managed Identities                                           │
│  • Azure ML Workspaces (optional)                               │
└────────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Workflow → Python Orchestrator

**Command Execution**:
```bash
python3 deployment/deploy.py \
  --resource-group aos-dev-rg \
  --location eastus \
  --template deployment/main-modular.bicep \
  --parameters deployment/parameters/dev.bicepparam \
  --allow-warnings \
  --git-sha ${{ github.sha }}
```

**Data Flow**:
- Workflow → Orchestrator: CLI arguments
- Orchestrator → Workflow: Exit code + stdout/stderr
- Orchestrator → Filesystem: Audit logs (deployment/audit/)

### 2. Output Parsing & Intelligence

**Workflow Analyzes**:
```bash
# Capture orchestrator output
python3 deploy.py ... 2>&1 | tee orchestrator-output.log

# Parse for success/failure
if grep -q "DEPLOYMENT SUCCESSFUL" orchestrator-output.log; then
  # Success path
fi

# Classify failures
if grep -qiE "lint.*error|bicep.*error|..." orchestrator-output.log; then
  FAILURE_TYPE="logic"
  SHOULD_RETRY="false"
elif grep -qiE "timeout|throttl.*|..." orchestrator-output.log; then
  FAILURE_TYPE="environmental"
  SHOULD_RETRY="true"
fi
```

**Enhanced Retry Logic**:
- Python orchestrator: Basic retry (3 attempts, immediate)
- GitHub workflow: Enhanced retry (exponential backoff: 60s, 120s, 240s)
- Workflow only retries if orchestrator indicates environmental failure

### 3. Audit Trail Integration

**Orchestrator Creates**:
```json
{
  "git_sha": "abc123...",
  "template_file": "deployment/main-modular.bicep",
  "start_time": "2024-02-19T10:00:00Z",
  "events": [...],
  "deployed_resources": [...]
}
```

**Workflow Uploads**:
- Artifact: `deployment-audit-{run-id}`
- Contents: All audit JSON files + orchestrator logs
- Retention: 90 days

### 4. Failure Classification Convergence

**Python Orchestrator** (`deployment/orchestrator/core/failure_classifier.py`):
- Defines failure patterns (logic vs environmental)
- Implements basic classification
- Used for orchestrator-level retry decisions

**GitHub Workflow** (`.github/workflows/infrastructure-deploy.yml`):
- Replicates failure patterns (kept in sync)
- Adds enhanced retry logic (exponential backoff)
- Provides human-readable explanations
- Posts status to PR/issues

**Synchronization**:
- Test suite validates both implementations match
- `.github/workflows/test-failure-classification.py` runs against workflow patterns
- Patterns should be kept aligned manually

## Enhanced Capabilities

### What the Workflow Adds

1. **Intent Parsing**:
   - Python orchestrator: Expects explicit CLI arguments
   - Workflow: Parses natural language commands, PR labels, manual inputs

2. **Authentication**:
   - Python orchestrator: Assumes Azure CLI is authenticated
   - Workflow: Handles OIDC authentication automatically

3. **Communication**:
   - Python orchestrator: Prints to stdout/stderr
   - Workflow: Posts structured comments to PR/issues

4. **Safety Constraints**:
   - Python orchestrator: Prompts for confirmation (if flag set)
   - Workflow: Enforces dual-label requirement for production

5. **Retry Logic**:
   - Python orchestrator: Basic retry (immediate, 3 attempts)
   - Workflow: Enhanced retry (exponential backoff, failure classification)

6. **Observability**:
   - Python orchestrator: Audit logs on filesystem
   - Workflow: Audit logs + workflow artifacts + PR comments + GitHub Actions UI

## Deployment Flow Example

### Scenario: Deploy to Dev via PR Comment

```
1. Developer comments on PR: "/deploy dev"
   └─ Workflow triggered (issue_comment event)

2. Workflow: Setup phase
   ├─ Parse comment: Detected "/deploy dev"
   ├─ Set environment = dev
   ├─ Set resource_group = aos-dev-rg
   ├─ Set parameters_file = deployment/parameters/dev.bicepparam
   └─ Post PR comment: "🚀 Starting deployment to dev..."

3. Workflow: Authentication
   ├─ Azure Login via OIDC
   └─ Verify credentials

4. Workflow: Execute Python Orchestrator
   └─ Run: python3 deploy.py -g aos-dev-rg -l eastus -t main-modular.bicep -p dev.bicepparam

5. Python Orchestrator: Phase 1 - Validate
   ├─ Check template file exists ✓
   ├─ Check parameters file exists ✓
   └─ Validation passed

6. Python Orchestrator: Phase 2 - Lint
   ├─ Run: az bicep build --file main-modular.bicep
   ├─ Check for errors: None found
   └─ Linting passed

7. Python Orchestrator: Phase 3 - Plan
   ├─ Run: az deployment group what-if
   ├─ Analyze changes:
   │   • +5 new resources
   │   • ~2 modified resources
   │   • No destructive changes
   └─ Planning passed

8. Python Orchestrator: Phase 4 - Deploy
   ├─ Run: az deployment group create
   ├─ Deploy resources...
   ├─ Capture resource IDs
   └─ Deployment succeeded

9. Python Orchestrator: Phase 5 - Health Check
   ├─ Verify storage account accessible
   ├─ Verify function app running
   ├─ Verify service bus operational
   └─ Health checks passed

10. Python Orchestrator: Phase 6 - Audit
    ├─ Create audit record
    ├─ Add all events
    ├─ Add deployed resources
    └─ Save to deployment/audit/deployment-20240219-100530.json

11. Workflow: Analyze Output
    ├─ Parse orchestrator output
    ├─ Detected: "DEPLOYMENT SUCCESSFUL"
    ├─ Status = success
    └─ Extract: 7 resources deployed in 180s

12. Workflow: Upload Artifacts
    ├─ Upload audit logs
    └─ Upload orchestrator output

13. Workflow: Post Result
    └─ PR Comment: "✅ Deployment successful! 7 resources in 180s"

14. Complete ✅
```

### Scenario: Deployment Fails with Transient Error

```
1. Developer: "/deploy staging"
2. Workflow: Setup + Auth ✓
3. Workflow: Execute orchestrator
4. Orchestrator: Validate ✓ → Lint ✓ → Plan ✓
5. Orchestrator: Deploy → ❌ "ServiceUnavailable: Azure throttled request"
6. Orchestrator: Internal retry 1 → ❌ Still throttled
7. Orchestrator: Internal retry 2 → ❌ Still throttled
8. Orchestrator: Internal retry 3 → ❌ Still throttled
9. Orchestrator: Exit with failure ❌

10. Workflow: Analyze output
    ├─ Detected: "ServiceUnavailable"
    ├─ Classify: Environmental failure
    └─ Decision: Should retry = true

11. Workflow: Self-Healing Retry 1
    ├─ Wait: 60 seconds
    ├─ Re-execute: python3 deploy.py ...
    └─ Result: ❌ Still throttled

12. Workflow: Self-Healing Retry 2
    ├─ Wait: 120 seconds
    ├─ Re-execute: python3 deploy.py ...
    └─ Result: ✅ Success!

13. Workflow: Post result
    └─ PR Comment: "✅ Succeeded after 2 retries! (Self-healing)"

14. Complete ✅ (with self-healing)
```

## Benefits of Integration

### Synergy Between Layers

**Agent Layer** provides:
- Natural language interface
- Intelligent failure handling
- Enhanced retry logic
- Human communication
- Safety enforcement

**Logic Layer** provides:
- Quality gates (lint, what-if, health)
- Deployment orchestration
- Audit logging
- Resource tracking
- Baseline retry

**Resource Layer** provides:
- Infrastructure as code
- Modular architecture
- Environment parameterization
- Azure resource provisioning

### Separation of Concerns

Each layer has clear responsibilities:
- **Agent**: "What should we do?" (intent)
- **Python**: "How do we do it?" (logic)
- **Bicep**: "What should exist?" (resources)

This separation allows:
- Testing each layer independently
- Evolving layers at different rates
- Using Python orchestrator standalone (local dev)
- Using workflow for automation (CI/CD)

## Standalone Usage

### Python Orchestrator (Local Development)

```bash
# Works without workflow
cd deployment
python3 deploy.py \
  -g my-dev-rg \
  -l eastus \
  -t main-modular.bicep \
  -p parameters/dev.bicepparam
```

**When to use**:
- Local development
- Quick testing
- Debugging template changes
- Manual deployments

### GitHub Workflow (Automated Operations)

```bash
# Comment on PR
/deploy dev
```

**When to use**:
- PR-driven deployments
- Automated CI/CD
- Team collaboration
- Production deployments
- Audited deployments

## Future Enhancements

### Potential Improvements

1. **Workflow → Orchestrator Communication**:
   - Pass workflow context to orchestrator
   - Enable orchestrator to post GitHub comments directly
   - Structured JSON output from orchestrator

2. **Failure Classification**:
   - Centralize patterns in shared file
   - Auto-sync between Python and workflow
   - ML-based classification

3. **Retry Strategy**:
   - Configurable retry schedules
   - Different strategies per failure type
   - Circuit breaker pattern

4. **Observability**:
   - Real-time deployment dashboard
   - Metrics collection (duration, success rate)
   - Alerting on repeated failures

5. **Advanced Intent**:
   - "Deploy latest to all non-prod" command
   - "Rollback production to previous" command
   - "Promote staging to production" command

## Summary

The GitHub Agentic Deployment Workflow integrates seamlessly with the existing Python orchestrator and Bicep templates, adding:
- ✅ Natural language interface
- ✅ Intelligent failure handling
- ✅ Enhanced retry logic
- ✅ Safety constraints
- ✅ Team collaboration
- ✅ Complete audit trail

While maintaining:
- ✅ Existing orchestrator quality gates
- ✅ Bicep infrastructure as code
- ✅ Standalone orchestrator usage
- ✅ Clear separation of concerns

The result is a powerful, intelligent deployment system that combines the best of automation, reliability, and human oversight.
