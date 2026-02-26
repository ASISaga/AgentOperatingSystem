# aos-deployment

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/aos-deployment/actions/workflows/infrastructure-deploy.yml/badge.svg)](https://github.com/ASISaga/aos-deployment/actions)

**Infrastructure deployment for the Agent Operating System.**

Bicep templates, Python orchestrator, regional validation, and CI/CD workflows
for deploying AOS to Azure.

## Quick Start

```bash
# Deploy to dev environment
python deployment/deploy.py --environment dev --auto-region

# Plan only (what-if)
python deployment/deploy.py --environment dev --plan-only
```

## Structure

```
aos-deployment
├── deployment/
│   ├── main-modular.bicep       # Primary Bicep template
│   ├── modules/                 # Bicep modules
│   ├── parameters/              # Environment parameter files
│   ├── orchestrator/            # Python deployment orchestrator
│   └── tests/                   # Deployment tests
├── .github/
│   ├── workflows/               # CI/CD workflows
│   ├── skills/                  # Deployment-specific Copilot skills
│   └── agents/                  # Agentic deployment agent
└── docs/                        # Deployment documentation
```

## Related Packages

| Package | Description |
|---|---|
| [`aos-kernel`](https://github.com/ASISaga/aos-kernel) | AOS kernel runtime |
| [`aos-function-app`](https://github.com/ASISaga/aos-function-app) | Main Azure Functions host |

## License

[MIT License](LICENSE)
