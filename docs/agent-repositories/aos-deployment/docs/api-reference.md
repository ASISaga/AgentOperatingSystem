# API Reference — aos-deployment

## CLI Entry Point

### `deployment/deploy.py`

The main deployment CLI.

```bash
python deployment/deploy.py [OPTIONS]
```

#### Options

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--environment` | `str` | Yes | Target environment (`dev`, `staging`, `prod`) |
| `--resource-group` | `str` | Yes | Azure resource group name |
| `--location` | `str` | No | Azure region (auto-selected if omitted) |
| `--plan-only` | `flag` | No | Dry run — validate without deploying |
| `--skip-health-checks` | `flag` | No | Skip post-deployment health checks |
| `--skip-lint` | `flag` | No | Skip Bicep linting |
| `--verbose` | `flag` | No | Enable verbose output |

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Deployment failed (logic error) |
| 2 | Deployment failed (environmental error) |
| 3 | Health check failed |
| 4 | Validation/lint error |

## Bicep Templates

### `deployment/main-modular.bicep`

Primary template that composes all modules.

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `environment` | `string` | Target environment name |
| `location` | `string` | Azure region |
| `resourcePrefix` | `string` | Naming prefix for resources |

### `deployment/modules/`

Individual Bicep modules for each Azure resource type. Each module accepts environment-specific parameters and outputs resource IDs.

## Python Orchestrator

### `deployment/orchestrator/deployment_engine.py`

Core deployment state machine.

### `deployment/orchestrator/failure_classifier.py`

Classifies deployment errors:
- **Logic errors** — BCP codes, syntax errors, invalid parameters
- **Environmental errors** — Timeouts, throttling, transient failures

### `deployment/orchestrator/regional_validator.py`

Validates Azure region capabilities for required services.

### `deployment/orchestrator/health_checker.py`

Post-deployment verification of deployed resources.

### `deployment/orchestrator/audit_logger.py`

Records deployment operations for audit trail.

## Parameters

### `deployment/parameters/`

Environment-specific parameter files:
- `dev.parameters.json` — Development environment
- `staging.parameters.json` — Staging environment
- `prod.parameters.json` — Production environment
