# AOS Deployment Architecture

## Three-Tier Deployment Model

1. **Agent Layer** — GitHub Actions workflow interprets deployment intent and handles errors
2. **Python Layer** — Deployment orchestrator (deploy.py) manages the deployment lifecycle
3. **Bicep Layer** — Infrastructure-as-Code defines Azure resources

## Deployment Pipeline

```
Developer → GitHub PR → Agentic Workflow → Python Orchestrator → Bicep → Azure
                         ↑                  ↑                     ↑
                    Error fixing        Linting/Validation    Regional validation
```

## Key Components

- **Orchestrator** — Core deployment engine with state machine
- **Failure Classifier** — Categorizes errors as logic or environmental
- **Regional Validator** — Validates and selects optimal Azure regions
- **Health Checker** — Post-deployment verification
- **Audit Logger** — Deployment audit trail

## Modular Bicep Architecture

```
main-modular.bicep              # Entry point — composes all modules
├── modules/functionApp.bicep   # Azure Functions resources
├── modules/storage.bicep       # Storage accounts
├── modules/serviceBus.bicep    # Service Bus namespace and queues
├── modules/keyVault.bicep      # Key Vault and secrets
├── modules/monitoring.bicep    # Application Insights, Log Analytics
└── modules/networking.bicep    # VNets, NSGs, private endpoints
```

## Python Orchestrator Architecture

```
deploy.py                       # CLI entry point
orchestrator/
├── deployment_engine.py        # Core state machine
├── failure_classifier.py       # Error categorization
├── regional_validator.py       # Region capability validation
├── health_checker.py           # Post-deployment checks
├── audit_logger.py             # Deployment audit trail
└── bicep_linter.py             # Pre-deployment validation
```

## Environment Strategy

| Environment | Purpose              | Deployment Trigger      |
|------------|----------------------|-------------------------|
| dev        | Development/testing  | Push to `develop`       |
| staging    | Pre-production       | PR to `main`            |
| prod       | Production           | Merge to `main`         |

## Error Recovery Flow

```
Deployment Attempt
    ├── Success → Health Check → Done
    └── Failure → Classify Error
                    ├── Logic Error → Auto-fix (deployment-error-fixer) → Retry
                    └── Environmental Error → Backoff → Retry (max 3)
```
