# aos-deployment

Infrastructure-as-Code, deployment orchestration, regional validation, and deployment-specific CI/CD for the Agent Operating System.

## Overview

`aos-deployment` contains all deployment infrastructure for AOS:

- **Bicep Templates** — Modular Azure infrastructure definitions
- **Python Orchestrator** — Smart deployment CLI with linting, validation, health checks
- **Regional Validation** — Automatic region selection and capability validation
- **CI/CD Workflows** — Agentic deployment, monitoring, and troubleshooting workflows

## Quick Start

```bash
# Deploy to dev environment
python deployment/deploy.py --environment dev --resource-group my-rg

# Plan deployment (dry run)
python deployment/deploy.py --environment dev --resource-group my-rg --plan-only

# Validate Bicep templates
az bicep build --file deployment/main-modular.bicep --stdout
```

## Repository Structure

```
deployment/                     # Bicep templates, orchestrator, validators
├── main-modular.bicep         # Primary Bicep template
├── modules/                   # Bicep modules
├── parameters/                # Environment-specific parameters
├── orchestrator/              # Python deployment orchestrator
├── tests/                     # Deployment tests
└── deploy.py                  # Entry point
docs/                          # Deployment documentation
.github/                       # Workflows, skills, prompts
```

## Key Features

- **Agentic Deployment** — GitHub Actions workflow with autonomous error fixing
- **Smart Retry** — Failure classification (logic vs environmental) with exponential backoff
- **Regional Validation** — Automatic region selection based on service availability
- **Deployment Audit** — Full audit trail of all deployment operations
- **Health Checks** — Post-deployment verification

## No Runtime Dependency

This repository has **zero Python runtime dependency** on `aos-kernel` or any AOS package. The deployment orchestrator is a standalone CLI tool.

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Main Azure Functions app
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents function app
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app

## License

Apache License 2.0 — see [LICENSE](LICENSE)
