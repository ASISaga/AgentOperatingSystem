# Repository Split Plan — Agent Operating System

**Status**: Complete  
**Last Updated**: 2026-03-22

## Overview

This document describes the completed migration from a monolithic `agent-operating-system` repository to a multi-repository architecture coordinated via Git submodules.

The migration separated a single large repository into **15 focused repositories**, each independently versioned, tested, and deployed under the [ASISaga](https://github.com/ASISaga) GitHub organization.

---

## Motivation

The original `agent-operating-system` repository contained all source code in a single monolith:

- `src/AgentOperatingSystem/` — kernel, agents, messaging, orchestration, ML
- `deployment/` — Bicep infrastructure
- `config/` — configuration JSON files
- `data/` — knowledge/learning JSON files
- `docs/` — all documentation
- `tests/` — all test files

**Problems with the monolith**:
- CI took too long (all tests ran for every change)
- Version management was impossible (one version for everything)
- Teams couldn't work independently on different agents
- Deployment was all-or-nothing
- Dependencies were entangled

---

## Migration Architecture

### Before

```
agent-operating-system/
├── src/AgentOperatingSystem/
│   ├── agents/           (cmo_agent.py, leadership_agent.py, purpose_driven.py, ...)
│   ├── messaging/        (bus.py, router.py, saga.py, ...)
│   ├── orchestration/    (engine.py, multi_agent.py, workflow.py, ...)
│   ├── knowledge/
│   ├── learning/
│   └── ml/
├── deployment/           (Bicep templates)
├── config/               (consolidated_config.json, self_learning_config.json, ...)
├── data/                 (knowledge JSON files)
├── docs/                 (all documentation)
└── tests/                (all test files)
```

### After

```
agent-operating-system/         ← meta-repo (this repo)
├── function_app.py             ← thin Azure Functions wrapper
├── .gitmodules                 ← 15 submodule definitions
│
├── aos-kernel/                 ← https://github.com/ASISaga/aos-kernel
├── aos-intelligence/           ← https://github.com/ASISaga/aos-intelligence
├── aos-infrastructure/         ← https://github.com/ASISaga/aos-infrastructure
├── aos-dispatcher/             ← https://github.com/ASISaga/aos-dispatcher
├── aos-client-sdk/             ← https://github.com/ASISaga/aos-client-sdk
│
├── purpose-driven-agent/       ← https://github.com/ASISaga/purpose-driven-agent
├── leadership-agent/           ← https://github.com/ASISaga/leadership-agent
├── ceo-agent/                  ← https://github.com/ASISaga/ceo-agent
├── cfo-agent/                  ← https://github.com/ASISaga/cfo-agent
├── cto-agent/                  ← https://github.com/ASISaga/cto-agent
├── cso-agent/                  ← https://github.com/ASISaga/cso-agent
├── cmo-agent/                  ← https://github.com/ASISaga/cmo-agent
│
├── realm-of-agents/            ← https://github.com/ASISaga/realm-of-agents
├── mcp/                        ← https://github.com/ASISaga/mcp
└── business-infinity/          ← https://github.com/ASISaga/business-infinity
```

---

## Repository Assignments

### Source Code Distribution

| Original `src/` module | Target repository |
|------------------------|------------------|
| `agents/` (cmo, leadership, purpose_driven) | `purpose-driven-agent`, `leadership-agent`, `cmo-agent` |
| `apps/app_config_schema.py` | `aos-kernel` |
| `auth/` | `aos-kernel` |
| `config/` | `aos-kernel` |
| `environment/` | `aos-kernel` |
| `executor/` | `aos-kernel` |
| `extensibility/` | `aos-kernel` |
| `governance/` | `aos-kernel` |
| `mcp/` | `aos-kernel` |
| `messaging/` | `aos-kernel` |
| `monitoring/` | `aos-kernel` |
| `observability/` | `aos-kernel` |
| `orchestration/` | `aos-kernel` |
| `platform/` | `aos-kernel` |
| `reliability/` | `aos-kernel` |
| `services/` | `aos-kernel` |
| `storage/` | `aos-kernel` |
| `testing/` | `aos-kernel` |
| `knowledge/` | `aos-intelligence` |
| `learning/` | `aos-intelligence` |
| `ml/` | `aos-intelligence` |
| `__init__.py`, `agent_operating_system.py` | `aos-kernel` |

### Configuration Distribution

| File | Target |
|------|--------|
| `config/consolidated_config.json` | `aos-kernel/config/` |
| `config/self_learning_config.json` | `aos-intelligence/config/` |
| `config/example_app_registry.json` | `aos-client-sdk/config/` |

### Data Distribution

| Files | Target |
|-------|--------|
| `data/*.json` (7 knowledge/learning files) | `aos-intelligence/data/` |

### Infrastructure Distribution

| Original | Target |
|----------|--------|
| `deployment/` (Bicep templates) | `aos-infrastructure/deployment/` |

### Test Distribution

| Test file | Target |
|-----------|--------|
| `tests/test_azure_functions_infrastructure.py` | `aos-dispatcher/tests/` |
| `tests/test_foundry_agent_service.py` | `aos-intelligence/tests/` |
| `tests/test_lorax.py` | `aos-intelligence/tests/` |
| `tests/validate_foundry_integration.py` | `aos-intelligence/tests/` |
| All other test files | `aos-kernel/tests/` |

---

## Repository Structure (Standard per Repo)

Each of the 15 repositories follows this standard layout:

```
<repo-name>/
├── src/<package_name>/     ← Python source
├── tests/                  ← pytest tests
├── docs/                   ← Module-specific docs
├── README.md               ← Repository overview
├── LICENSE                 ← Apache-2.0
├── pyproject.toml          ← Package definition (hatchling build system)
├── azure.yaml              ← azd deployment config (deployed repos only)
├── .gitignore
└── .github/
    └── workflows/
        ├── ci.yml          ← Test and lint on push/PR
        └── deploy.yml      ← Deploy to Azure on push to main
```

---

## Key Design Decisions

### 1. Thin Meta-Repo Entry Point

The `function_app.py` in this meta-repo is the Azure Functions entry point for `aos-dispatcher`. It is intentionally minimal — a thin wrapper that binds HTTP routes and Service Bus triggers to the `aos_dispatcher` library. All business logic lives in the `aos-dispatcher` submodule.

### 2. Code-Only Libraries vs Deployed Apps

Two repositories are **code-only libraries** (not deployed as Azure Functions):
- `purpose-driven-agent` — base agent class
- `leadership-agent` — leadership + orchestration capabilities

They are imported as pip packages by the C-suite agent function apps.

### 3. Independent Versioning

Each repository has its own version in `pyproject.toml` following semantic versioning. Dependencies between repos use `>=` constraints to allow patch updates without requiring meta-repo changes.

### 4. Submodule-Only Architecture

The meta-repo contains no source code of its own (except the thin `function_app.py` wrapper). All implementation lives in the submodules. This ensures:
- Each team owns and controls their repo
- CI/CD is scoped to what changed
- Version history is clean and meaningful

---

## Completion Status

All 8 migration tasks completed:

| Task | Status |
|------|--------|
| Copy kernel source (src/ → aos-kernel) | ✅ Complete |
| Distribute config files | ✅ Complete |
| Copy data files (data/ → aos-intelligence) | ✅ Complete |
| Distribute docs | ✅ Complete |
| Distribute tests | ✅ Complete |
| Merge deployment files (deployment/ → aos-infrastructure) | ✅ Complete |
| Clean up parent directories | ✅ Complete |
| Validate | ✅ Complete |

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) — Current system architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) — Developer guide for the multi-repo setup
- `spec/design.md` — Detailed file mapping used during migration
- `spec/requirements.md` — EARS requirements for the migration
- `spec/tasks.md` — Task tracking (all tasks complete)
