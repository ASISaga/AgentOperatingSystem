# aos-deployment

Complete Azure infrastructure lifecycle manager for the Agent Operating System, providing a robust, scalable, and resilient foundation for AgentOperatingSystem and the applications utilizing it.

The repository is organised around **three pillars**:

| Pillar | Responsibility |
|---|---|
| **Governance** | Policy enforcement, cost management, RBAC access review, tag compliance |
| **Automation** | Lint → validate → what-if → deploy pipeline, smart retry, regional selection, audit trail |
| **Reliability** | Drift detection, SLA-aware health monitoring, DR readiness assessment |

## Overview

`aos-deployment` contains all deployment infrastructure for AOS:

- **Bicep Templates** — Modular Azure infrastructure definitions (13 modules, including `policy.bicep` and `budget.bicep`)
- **Python Orchestrator** — Smart deployment CLI with linting, validation, health checks, and lifecycle management
- **Governance Pillar** — Azure Policy assignments, cost/budget management, RBAC access review
- **Reliability Pillar** — Infrastructure drift detection, SLA compliance tracking, DR readiness
- **Regional Validation** — Automatic region selection and capability validation
- **CI/CD Workflows** — Deploy, monitoring, troubleshooting, governance, and drift-detection workflows

## Quick Start

```bash
# Deploy to dev environment
python deployment/deploy.py --environment dev --resource-group my-rg

# Plan deployment (dry run)
python deployment/deploy.py --environment dev --resource-group my-rg --plan-only

# Run governance checks (policy compliance, cost, RBAC)
python deployment/deploy.py govern --environment dev --resource-group my-rg

# Run reliability checks (health, SLA, drift, DR)
python deployment/deploy.py reliability --environment dev --resource-group my-rg

# Validate Bicep templates
az bicep build --file deployment/main-modular.bicep --stdout
```

## Repository Structure

```
deployment/                        # Bicep templates, orchestrator, validators
├── main-modular.bicep             # Primary Bicep template (13 modules)
├── modules/                       # Bicep modules
│   ├── policy.bicep               # Azure Policy assignments (Governance)
│   ├── budget.bicep               # Cost Management budget (Governance)
│   └── ...                        # monitoring, storage, servicebus, keyvault, ...
├── parameters/                    # Environment-specific parameters
├── orchestrator/                  # Python deployment orchestrator
│   ├── core/                      # Config + InfrastructureManager
│   ├── governance/                # PolicyManager, CostManager, RbacManager
│   ├── reliability/               # DriftDetector, HealthMonitor
│   ├── validators/                # RegionalValidator
│   └── cli/                       # regional_tool, workflow_helper
├── tests/                         # Deployment tests (64 tests)
└── deploy.py                      # Entry point
docs/                              # Deployment documentation
.github/                           # Workflows, skills, prompts
└── workflows/
    ├── infrastructure-deploy.yml          # Deployment pipeline
    ├── infrastructure-monitoring.yml      # Health monitoring
    ├── infrastructure-troubleshooting.yml # Troubleshooting
    ├── infrastructure-governance.yml      # Governance (daily)
    └── infrastructure-drift-detection.yml # Drift detection (every 6 h)
```

## Three-Pillar Lifecycle

### 🏛️ Governance

```python
from orchestrator.core.config import DeploymentConfig, GovernanceConfig
from orchestrator.core.manager import InfrastructureManager

cfg = DeploymentConfig(
    environment="prod",
    resource_group="rg-aos-prod",
    location="westeurope",
    governance=GovernanceConfig(
        enforce_policies=True,
        budget_amount=2000.0,
        required_tags={"environment": "prod", "team": "platform"},
        review_rbac=True,
    ),
)
mgr = InfrastructureManager(cfg)
mgr.govern()   # evaluate policy compliance, tags, budget, RBAC
```

Standalone governance components:

```python
from orchestrator.governance.policy_manager import PolicyManager
from orchestrator.governance.cost_manager   import CostManager
from orchestrator.governance.rbac_manager   import RbacManager

pm = PolicyManager("rg-aos-prod", subscription_id="...")
pm.evaluate_compliance()
pm.assign_aos_policies("prod")
pm.enforce_required_tags({"environment": "prod"})

cm = CostManager("rg-aos-prod")
cm.get_current_spend(period_days=30)
cm.check_budget_alerts()

rm = RbacManager("rg-aos-prod")
rm.review_privileged_access()
```

### ⚙️ Automation

The existing `InfrastructureManager.deploy()` and `plan()` pipelines are
supplemented by post-deploy governance and reliability lifecycle hooks that
activate automatically when the corresponding settings are enabled in
`DeploymentConfig`.

### 🔁 Reliability

```python
from orchestrator.core.config import DeploymentConfig, ReliabilityConfig
from orchestrator.core.manager import InfrastructureManager

cfg = DeploymentConfig(
    environment="prod",
    resource_group="rg-aos-prod",
    location="westeurope",
    template="deployment/main-modular.bicep",
    reliability=ReliabilityConfig(
        enable_drift_detection=True,
        check_dr_readiness=True,
    ),
)
mgr = InfrastructureManager(cfg)
mgr.reliability_check()  # health + SLA + drift + DR
```

Standalone reliability components:

```python
from orchestrator.reliability.drift_detector import DriftDetector
from orchestrator.reliability.health_monitor import HealthMonitor

dd = DriftDetector("rg-aos-prod")
dd.detect_drift("deployment/main-modular.bicep")          # template what-if
dd.detect_drift_from_manifest([{"name": "st1", ...}])     # manifest compare

hm = HealthMonitor("rg-aos-prod", "prod")
hm.check_all()
hm.check_sla_compliance()
hm.check_disaster_recovery_readiness()
```

## Key Features

- **Agentic Deployment** — GitHub Actions workflow with autonomous error fixing
- **Smart Retry** — Failure classification (logic vs environmental) with exponential backoff
- **Regional Validation** — Automatic region selection based on service availability
- **Deployment Audit** — Full audit trail of all deployment operations
- **Health Checks** — Post-deployment verification with SLA tracking
- **Governance Policies** — Azure Policy assignments for location, HTTPS, KV soft-delete
- **Cost Management** — Monthly budget with percentage-threshold alerts
- **RBAC Review** — Privileged-access review and least-privilege enforcement
- **Drift Detection** — Detect infrastructure drift via Bicep what-if or manifest comparison
- **DR Readiness** — Key Vault soft-delete, geo-replication, and purge-protection checks

## No Runtime Dependency

This repository has **zero Python runtime dependency** on `aos-kernel` or any AOS package. The deployment orchestrator is a standalone CLI tool.

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-dispatcher](https://github.com/ASISaga/aos-dispatcher) — Main Azure Functions app
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents function app
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app

## License

Apache License 2.0 — see [LICENSE](LICENSE)
