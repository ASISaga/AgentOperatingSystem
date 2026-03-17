# RealmOfAgents Instructions

## Overview

RealmOfAgents is a config-driven agent deployment Azure Function app. Agents are
defined in JSON registry files and automatically deployed and managed.

## Agent Configuration

- Define agents in `example_agent_registry.json`
- Each agent entry specifies: agent type, purpose, adapter, and runtime config
- The function app reads the registry on startup and creates agent instances

## Development

- Use Azure Functions Core Tools for local development
- Test agent configurations with the validation schema
- Run `func start` to test locally

## Deployment

- Deploy through the aos-deployment orchestrator
- Agent registry is read at function app startup
- Configuration changes require function app restart

## Migration to Foundry

- RealmOfAgents supports migration from custom deployment to Microsoft Foundry
- See `docs/MIGRATION_TO_FOUNDRY.md` for migration guide
- Use the `function_app_original.py` as reference for pre-Foundry patterns
