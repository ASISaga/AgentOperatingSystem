# AOS Deployment — Copilot Instructions

This repo contains infrastructure deployment for AOS: Bicep templates,
Python orchestrator, regional validation, and CI/CD workflows.

## Key Patterns
- Bicep templates in deployment/modules/
- Python orchestrator in deployment/orchestrator/
- Parameter files use .bicepparam format
- Always validate with `az bicep build` before deploying
- Use the Python orchestrator (deploy.py) — never raw Azure CLI
- Three-tier: Agent Layer (workflow) → Python Layer (orchestrator) → Bicep Layer
