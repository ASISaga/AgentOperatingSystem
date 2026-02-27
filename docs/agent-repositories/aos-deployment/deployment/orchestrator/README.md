# AOS Deployment Orchestrator

Python orchestration logic for Azure infrastructure management.

## Structure

- `core/config.py` — `DeploymentConfig` pydantic model
- `core/manager.py` — `InfrastructureManager` (deploy, plan, status, monitor, troubleshoot, delete)
- `cli/workflow_helper.py` — GitHub Actions workflow helper (check-trigger, select-regions, analyze-output, retry, extract-summary)
- `cli/regional_tool.py` — Regional validation CLI (validate, summary, auto-select)
- `validators/regional_validator.py` — `RegionalValidator` for Azure region/service availability
