# Repository Split Plan: AgentOperatingSystem → Multi-Repository Architecture

**Version:** 1.2  
**Date:** February 2026  
**Status:** Proposed  
**Author:** Architecture Analysis  
**Last Updated:** February 26, 2026 (agent repositories extracted; aos-core renamed to aos-kernel)

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Current State Analysis](#current-state-analysis)
- [Proposed Repository Structure](#proposed-repository-structure)
- [Repository Details](#repository-details)
  - [1. purpose-driven-agent](#1-purpose-driven-agent)
  - [2. leadership-agent](#2-leadership-agent)
  - [3. cmo-agent](#3-cmo-agent)
  - [4. aos-kernel](#4-aos-kernel)
  - [5. aos-deployment](#5-aos-deployment)
  - [6. aos-intelligence](#6-aos-intelligence)
  - [7. aos-docs](#7-aos-docs)
  - [8. aos-azure-functions](#8-aos-azure-functions)
  - [9. aos-copilot-extensions](#9-aos-copilot-extensions)
- [Dependency Graph](#dependency-graph)
- [Shared Contracts & Interfaces](#shared-contracts--interfaces)
- [Migration Strategy](#migration-strategy)
- [Cross-Repository CI/CD](#cross-repository-cicd)
- [Risks & Mitigations](#risks--mitigations)
- [Decision Log](#decision-log)

---

## Executive Summary

The AgentOperatingSystem repository currently contains **198 Python files** (~45,000 LOC), **117 Markdown documents** (~38,000 lines), **9 Bicep infrastructure templates**, **5 CI/CD workflows**, and **8 GitHub Copilot skills** — all in a single repository. These components span six distinct domains with different release cadences, team ownership profiles, and dependency chains:

1. **Core OS runtime** (agents, orchestration, messaging, storage, auth, config)
2. **Infrastructure deployment** (Bicep templates, Python orchestrator, regional validation)
3. **Agent intelligence** (ML pipelines, LoRA/LoRAx, DPO training, self-learning, knowledge/RAG)
4. **Documentation** (architecture, specifications, guides, release notes)
5. **Azure Functions hosting** (function apps, MCP servers, RealmOfAgents)
6. **GitHub Copilot extensions** (skills, prompts, instructions, agent configs, workflows)

This plan proposes splitting into **9 focused repositories** under the `ASISaga` GitHub organization, connected via Python package dependencies and shared interface contracts.

---

## Current State Analysis

### Repository Size

| Area | Python Files | Python LOC | Markdown Files | Markdown Lines | Other |
|------|-------------|------------|----------------|----------------|-------|
| `src/AgentOperatingSystem/` | 124 | 33,692 | 0 | 0 | — |
| `tests/` | 20 | 3,423 | 0 | 0 | — |
| `deployment/` | 27 | 4,574 | 15 | 5,209 | 9 Bicep, 3 bicepparam |
| `azure_functions/` | 8 | 1,556 | 6 | — | — |
| `examples/` | 7 | 1,933 | 1 | — | — |
| `docs/` | 0 | 0 | 54 | 21,595 | — |
| `.github/` | 3 | — | 38 | 10,972 | 5 YAML workflows |
| Root | 1 | 332 | 3 | — | pyproject.toml, host.json |
| `data/` + `knowledge/` + `config/` | 0 | 0 | 0 | 0 | 19 JSON |

**Total: ~198 Python files, ~45,510 Python LOC, ~117 Markdown files, ~37,776 Markdown lines**

### Source Module Sizes (LOC)

| Module | LOC | Domain |
|--------|-----|--------|
| `orchestration/` | 6,129 | Core |
| `messaging/` | 4,245 | Core |
| `ml/` | 3,159 | Intelligence |
| `reliability/` | 2,442 | Core |
| `learning/` | 2,411 | Intelligence |
| `observability/` | 2,108 | Core |
| `testing/` | 1,862 | Core |
| `extensibility/` | 1,619 | Core |
| `monitoring/` | 1,399 | Core |
| `agents/` | 1,315 | Core |
| `governance/` | 1,314 | Core |
| `mcp/` | 1,049 | Core |
| `platform/` | 746 | Core |
| `knowledge/` | 691 | Intelligence |
| `storage/` | 784 | Core |
| `config/` | 391 | Core |
| `auth/` | 381 | Core |
| `environment/` | 413 | Core |
| `services/` | 312 | Core |
| `shared/` | 80 | Core |
| `apps/` | 178 | Core |
| `executor/` | 28 | Core |

### Cross-Module Dependency Map

```
agents       → mcp, ml
orchestration → agents, config, messaging, ml, monitoring, storage
messaging    → config
ml           → config
learning     → agents, storage
auth         → config
storage      → config
monitoring   → config
testing      → governance, platform
```

Key observation: The `orchestration` module is the most coupled, depending on 6 other modules. The `ml` module is imported by `agents` and `orchestration`, creating a tight coupling between core OS and intelligence concerns.

### Problems with Current Structure

1. **Mixed release cadences**: Deployment infrastructure changes independently of core agent runtime; ML models evolve differently than messaging protocols.
2. **Bloated CI/CD**: Every PR triggers checks across all domains. A docs-only change runs Python tests; a Bicep change runs agent tests.
3. **Unclear ownership**: No clear team boundaries between infrastructure operators, core runtime developers, ML engineers, and documentation writers.
4. **Dependency bloat**: Installing the core OS pulls in ML, Azure Functions, and deployment dependencies via transitive imports.
5. **Documentation sprawl**: 117 markdown files scattered across `docs/`, `.github/`, `deployment/`, root, and `azure_functions/` with significant duplication and cross-referencing challenges.
6. **Copilot extension lock-in**: Skills, prompts, and instructions are repository-specific but contain general-purpose patterns.

---

## Proposed Repository Structure

```
ASISaga/
├── purpose-driven-agent  # PurposeDrivenAgent - the fundamental building block (inherits agent_framework.Agent)
├── leadership-agent      # LeadershipAgent - inherits PurposeDrivenAgent
├── cmo-agent             # CMOAgent - inherits LeadershipAgent
├── aos-kernel            # OS kernel: orchestration, messaging, storage, auth (renamed from aos-core)
├── aos-deployment        # Infrastructure: Bicep, orchestrator, regional validation, CI/CD
├── aos-intelligence      # ML/AI: LoRA, DPO, self-learning, knowledge, RAG
├── aos-docs              # All documentation: architecture, specs, guides, API ref
├── aos-azure-functions   # Azure Functions: function_app.py, RealmOfAgents, MCPServers
└── aos-copilot-extensions # GitHub Copilot: skills, prompts, instructions, agent configs
```

### Why 9 Repositories (Not Fewer, Not More)

- **Three agent repos** reflect the agent inheritance hierarchy: each agent is independently deployable, versioned, and documented. Teams building new agents can take `purpose-driven-agent` as their base without pulling in the full AOS kernel.
- **`aos-kernel`** (renamed from `aos-core`) better reflects its role as the OS kernel — orchestration engine, messaging, storage, auth — not a "core" library. The `aos-` prefix distinguishes it from the agent repos which are standalone.
- **6 remaining repos** retain the natural domain boundaries: deployment infrastructure, ML intelligence, documentation, Azure Functions hosting, and Copilot developer tooling.
- **Each repo has a distinct release cadence**: agent repos (semver, API-stability focused), kernel (breaking-change gated), deployment (infra change driven), intelligence (model/training driven), docs (continuous), azure-functions (deployment driven), copilot-extensions (feature driven).
- **Each repo has a distinct primary audience**: agent repos (agent SDK consumers, other agent authors), kernel (SDK consumers, platform engineers), deployment (infra operators), intelligence (ML engineers), docs (all stakeholders), azure-functions (platform engineers), copilot-extensions (developer experience).

---

## Repository Details

### 1. purpose-driven-agent

**Purpose:** The fundamental building block of the Agent Operating System. `PurposeDrivenAgent` is the abstract base class from which all AOS agents inherit. It inherits from `agent_framework.Agent` (Microsoft Agent Framework), establishing a clean hierarchy: `Agent → PurposeDrivenAgent → {LeadershipAgent, CMOAgent, ...}`.

**Cut-paste-ready directory structure:** `docs/agent-repositories/purpose-driven-agent/` in this monorepo.

**What moves here:**

```
src/
└── purpose_driven_agent/
    ├── __init__.py                 # Exports: PurposeDrivenAgent, GenericPurposeDrivenAgent
    ├── agent.py                    # PurposeDrivenAgent + GenericPurposeDrivenAgent
    ├── ml_interface.py             # IMLService abstract interface (decoupled from aos-intelligence)
    └── context_server.py           # Lightweight ContextMCPServer (standalone, no Azure deps)
tests/
├── conftest.py
└── test_purpose_driven_agent.py
examples/
└── basic_usage.py
docs/
├── architecture.md
├── api-reference.md
└── contributing.md
.github/
├── skills/purpose-driven-agent/SKILL.md    # GitHub Copilot skill
├── prompts/purpose-driven-expert.md        # Copilot prompt
├── instructions/purpose-driven-agent.instructions.md
└── workflows/ci.yml
pyproject.toml
README.md
LICENSE
```

**Package name:** `purpose-driven-agent`  
**Install:** `pip install purpose-driven-agent`

**Estimated size:** ~900 Python LOC + ~200 test LOC

**Key design decisions:**
- Inherits from `agent_framework.Agent` (Microsoft Agent Framework `>=1.0.0rc1`) with a graceful fallback stub when the package is not installed, mirroring the pattern used elsewhere in AOS.
- No dependency on `aos-kernel`. All ML operations are delegated through the `IMLService` abstract interface defined in `ml_interface.py`; the concrete implementation is registered at runtime by `aos-intelligence`.
- Lightweight in-process `ContextMCPServer` stub ships with this package; the full Azure-backed implementation is provided by `aos-kernel[azure]` when installed.
- The `GenericPurposeDrivenAgent` concrete class is included as a minimal concrete implementation for teams that need an off-the-shelf agent without subclassing.

**pyproject.toml dependencies:**
```toml
dependencies = [
    "agent-framework>=1.0.0rc1",
    "pydantic>=2.12.0",
]

[project.optional-dependencies]
azure = [
    "azure-identity>=1.25.0",
    "azure-ai-agents>=1.1.0",
    "azure-ai-projects>=1.0.0",
    "agent-framework-azure-ai>=1.0.0rc1",
]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pylint>=3.0.0",
]
```

---

### 2. leadership-agent

**Purpose:** Leadership and decision-making agent. `LeadershipAgent` extends `PurposeDrivenAgent` with decision provenance, stakeholder coordination, consensus building, and delegation patterns. The Leadership purpose is mapped to the "leadership" LoRA adapter.

**Cut-paste-ready directory structure:** `docs/agent-repositories/leadership-agent/` in this monorepo.

**What moves here:**

```
src/
└── leadership_agent/
    ├── __init__.py                 # Exports: LeadershipAgent
    └── agent.py                    # LeadershipAgent class
tests/
├── conftest.py
└── test_leadership_agent.py
examples/
└── basic_usage.py
docs/
├── architecture.md
├── api-reference.md
└── contributing.md
.github/
├── skills/leadership-agent/SKILL.md
├── prompts/leadership-expert.md
├── instructions/leadership-agent.instructions.md
└── workflows/ci.yml
pyproject.toml
README.md
LICENSE
```

**Package name:** `leadership-agent`  
**Install:** `pip install leadership-agent`

**Estimated size:** ~200 Python LOC + ~150 test LOC

**pyproject.toml dependencies:**
```toml
dependencies = [
    "purpose-driven-agent>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pylint>=3.0.0",
]
```

---

### 3. cmo-agent

**Purpose:** Chief Marketing Officer agent. `CMOAgent` extends `LeadershipAgent` with marketing-specific capabilities. Maps two purposes to two LoRA adapters: Marketing → "marketing" adapter, Leadership → "leadership" adapter (inherited).

**Cut-paste-ready directory structure:** `docs/agent-repositories/cmo-agent/` in this monorepo.

**What moves here:**

```
src/
└── cmo_agent/
    ├── __init__.py                 # Exports: CMOAgent
    └── agent.py                    # CMOAgent class
tests/
├── conftest.py
└── test_cmo_agent.py
examples/
└── basic_usage.py
docs/
├── architecture.md
├── api-reference.md
└── contributing.md
.github/
├── skills/cmo-agent/SKILL.md
├── prompts/cmo-expert.md
├── instructions/cmo-agent.instructions.md
└── workflows/ci.yml
pyproject.toml
README.md
LICENSE
```

**Package name:** `cmo-agent`  
**Install:** `pip install cmo-agent`

**Estimated size:** ~250 Python LOC + ~180 test LOC

**pyproject.toml dependencies:**
```toml
dependencies = [
    "leadership-agent>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pylint>=3.0.0",
]
```

---

### 4. aos-kernel

**Purpose:** The Agent Operating System kernel — orchestration engine, messaging, storage, authentication, and all supporting system services. Renamed from `aos-core` to more accurately reflect its role as an operating system kernel rather than a generic library.

**What moves here:**

```
src/AgentOperatingSystem/
├── __init__.py
├── agent_operating_system.py
├── agents/                   # Thin compatibility shim — re-exports from published packages
│   ├── __init__.py           # from purpose_driven_agent import PurposeDrivenAgent, etc.
│   └── (no source files — agents live in their own repos)
├── orchestration/            # Full orchestration engine (6,129 LOC)
├── messaging/                # Message bus, routing, contracts, Service Bus (4,245 LOC)
├── storage/                  # Storage backends (784 LOC)
├── auth/                     # Authentication (381 LOC)
├── config/                   # Configuration classes (391 LOC)
├── environment/              # Environment manager (413 LOC)
├── mcp/                      # MCP client, protocol (1,049 LOC)
├── reliability/              # Circuit breaker, retry, patterns (2,442 LOC)
├── observability/            # Logging, metrics, tracing (2,108 LOC)
├── governance/               # Audit, compliance, risk (1,314 LOC)
├── monitoring/               # System monitor, audit trail (1,399 LOC)
├── extensibility/            # Plugin framework, registries (1,619 LOC)
├── platform/                 # Platform contracts, events (746 LOC)
├── services/                 # Service interfaces (312 LOC)
├── shared/                   # Shared models (80 LOC)
├── testing/                  # Test framework (1,862 LOC)
├── apps/                     # App config (178 LOC)
└── executor/                 # Base executor (28 LOC)
tests/
├── conftest.py
├── simple_test.py
├── test_advanced_features.py
├── test_agent_framework_components.py
├── test_extensibility.py
├── test_integration.py
├── test_new_features.py
├── test_persona_registry.py
├── test_purpose_driven_integration.py
├── test_testing_framework.py
├── test_testing_standalone.py
└── validate_implementation.py
examples/
├── perpetual_agents_demo.py
├── perpetual_agents_example.py
└── platform_integration_example.py
pyproject.toml              # Kernel dependencies only (no ML, no Azure Functions)
README.md
LICENSE
```

**Package name:** `aos-kernel`  
**Install:** `pip install aos-kernel` (or `pip install aos-kernel[azure]` for Azure service backends)

**Estimated size:** ~21,000 Python LOC + ~3,000 test LOC (agents module is now a shim)

**Key change — Agents module becomes a compatibility shim:**
With agents in their own repos, `aos-kernel`'s `agents/` module becomes a thin re-export shim so that existing code using `from AgentOperatingSystem.agents import PurposeDrivenAgent` continues to work:
```python
# aos-kernel/src/AgentOperatingSystem/agents/__init__.py
from purpose_driven_agent import PurposeDrivenAgent, GenericPurposeDrivenAgent
from leadership_agent import LeadershipAgent
from cmo_agent import CMOAgent
```

**Key change — Remove ML dependency from orchestration:**
Currently `orchestration.py` imports `from ..ml.pipeline import MLPipelineManager`. This coupling must be broken by:
- Defining abstract interfaces for ML operations in `services/service_interfaces.py`
- Having `orchestration.py` depend only on the interface
- The `aos-intelligence` package provides the concrete implementation and registers it at runtime

**pyproject.toml dependencies (kernel only):**
```toml
dependencies = [
    "purpose-driven-agent>=1.0.0",
    "python-dotenv>=1.1.0",
    "pydantic>=2.12.0",
    "fastapi>=0.128.0",
    "uvicorn>=0.40.0",
    "psutil>=7.0.0",
    "PyJWT>=2.10.0",
    "cryptography>=45.0.0",
    "httpx>=0.28.0",
    "jsonschema>=4.23.0",
    "opentelemetry-api>=1.30.0",
    "opentelemetry-sdk>=1.30.0",
    "opentelemetry-exporter-otlp-proto-grpc>=1.30.0",
    "opentelemetry-instrumentation-fastapi>=0.51b0",
    "agent-framework>=1.0.0rc1",
    "agent-framework-orchestrations>=1.0.0b260219",
]

[project.optional-dependencies]
azure = [
    "azure-identity>=1.25.0",
    "azure-storage-blob>=12.25.0",
    "azure-storage-queue>=12.13.0",
    "azure-data-tables>=12.7.0",
    "azure-servicebus>=7.14.0",
    "azure-keyvault-secrets>=4.10.0",
    "azure-ai-agents>=1.1.0",
    "azure-ai-projects>=1.0.0",
    "agent-framework-azure-ai>=1.0.0rc1",
]
```

---

### 5. aos-deployment

**Purpose:** Infrastructure-as-Code, deployment orchestration, regional validation, and deployment-specific CI/CD workflows.

**What moves here:**

```
deployment/
├── main-modular.bicep          # Primary Bicep template
├── modules/                    # 8 Bicep modules (compute, identity, keyvault, etc.)
├── parameters/                 # .bicepparam files (dev, staging, prod)
├── orchestrator/               # Python deployment orchestrator (4,241 LOC)
│   ├── core/                   # Orchestrator engine, failure classifier, state machine
│   ├── cli/                    # CLI tools (deploy.py, regional_tool.py, workflow_helper.py)
│   ├── validators/             # Linter, whatif planner, regional validator
│   ├── audit/                  # Deployment audit logger
│   └── health/                 # Health checker
├── tests/                      # Deployment tests (test_orchestrator.py)
├── examples/                   # Orchestrator example
├── docs/                       # Deployment-specific docs (archive, regional validation)
├── deploy.py                   # Top-level deployment entry point
├── README.md
├── ORCHESTRATOR_USER_GUIDE.md
├── QUICKSTART.md
└── REGIONAL_REQUIREMENTS.md
.github/workflows/
├── infrastructure-deploy.yml       # Agentic deployment workflow
├── infrastructure-monitoring.yml   # Infrastructure monitoring
└── infrastructure-troubleshooting.yml  # Troubleshooting workflow
.github/agents/
└── infrastructure-deploy.agent.md
.github/skills/
├── deployment-error-fixer/         # Deployment error fixer skill (6 files)
└── azure-troubleshooting/          # Azure troubleshooting skill (2 files)
Root files:
├── DEPLOYMENT_DOCS_SUMMARY.md
└── REGIONAL_HANDLING_SUMMARY.md
docs/development/
├── DEPLOYMENT_PLAN.md
└── DEPLOYMENT_TASKS.md
docs/getting-started/
├── deployment.md
└── azure-functions.md
```

**Estimated size:** ~4,574 Python LOC + 9 Bicep + ~5,200 doc lines + 3 workflows

**Key design decisions:**
- This repo has **zero Python runtime dependency on aos-kernel**. The deployment orchestrator is a standalone CLI tool.
- Deployment workflows reference this repo's own Bicep templates and orchestrator.
- The `deployment-error-fixer` and `azure-troubleshooting` skills move here since they are deployment-specific.
- Deployment docs (`DEPLOYMENT_PLAN.md`, `DEPLOYMENT_TASKS.md`, `deployment.md`) consolidate here.

---

### 6. aos-intelligence

**Purpose:** Machine learning pipelines, LoRA/LoRAx adapter management, DPO training, self-learning systems, knowledge management, and RAG engine.

**What moves here:**

```
src/AgentOperatingSystem/
├── ml/                         # ML pipeline, DPO trainer, LoRAx, Foundry (3,159 LOC)
│   ├── pipeline.py
│   ├── pipeline_ops.py
│   ├── dpo_trainer.py
│   ├── lorax_server.py
│   ├── foundry_agent_service.py
│   └── self_learning_system.py
├── learning/                   # Self-learning agents, knowledge, RAG (2,411 LOC)
│   ├── self_learning_agents.py
│   ├── self_learning_mixin.py
│   ├── knowledge_manager.py
│   ├── rag_engine.py
│   ├── interaction_learner.py
│   ├── domain_expert.py
│   └── learning_pipeline.py
├── knowledge/                  # Knowledge indexing, evidence, precedent (691 LOC)
│   ├── indexing.py
│   ├── evidence.py
│   └── precedent.py
├── platform/foundry/           # Foundry agent service integration (746 LOC combined)
│   └── purpose_driven_foundry.py
tests/
├── test_lorax.py
├── test_foundry_agent_service.py
└── validate_foundry_integration.py
examples/
├── dpo_training_example.py
├── foundry_agent_service_example.py
└── lorax_multi_agent_example.py
data/                           # Training data, learning metrics
├── knowledge_*.json
└── learning_*.json
knowledge/                      # Domain knowledge bases
├── agent_directives.json
├── domain_contexts.json
└── domain_knowledge.json
config/
└── self_learning_config.json
```

**Package name:** `aos-intelligence`  
**Install:** `pip install aos-intelligence` (requires `aos-kernel` as dependency)

**Estimated size:** ~6,261 Python LOC + 19 JSON data files

**pyproject.toml dependencies:**
```toml
dependencies = [
    "aos-kernel>=3.0.0",      # AOS kernel runtime
]

[project.optional-dependencies]
ml = [
    "transformers>=4.50.0",
    "torch>=2.6.0",
    "scikit-learn>=1.6.0",
    "numpy>=2.0.0",
    "pandas>=2.2.0",
    "trl>=0.16.0",
    "peft>=0.15.0",
    "accelerate>=1.5.0",
    "datasets>=3.5.0",
    "mlflow>=3.5.0",
]
foundry = [
    "azure-ai-agents>=1.1.0",
    "azure-ai-projects>=1.0.0",
]
```

**Key design decision — Interface boundary with aos-kernel:**
- `purpose-driven-agent` defines `IMLService` interface in `ml_interface.py`
- `aos-kernel` re-exports this interface in `services/service_interfaces.py`
- `aos-intelligence` implements this interface and registers via plugin/extensibility framework
- `agents/purpose_driven.py` calls ML operations through the interface, not direct imports
- If `aos-intelligence` is not installed, ML operations gracefully degrade (already partially implemented with try/except patterns)

---

### 7. aos-docs

**Purpose:** All project documentation — architecture, specifications, guides, API reference, release notes, and contributor guides.

**What moves here:**

```
docs/
├── README.md                       # Documentation index
├── architecture/
│   └── ARCHITECTURE.md             # System architecture (803 lines)
├── overview/
│   ├── vision.md
│   ├── principles.md
│   ├── perpetual-agents.md
│   └── services.md
├── getting-started/
│   ├── quickstart.md
│   ├── quickstart-old.md
│   ├── installation.md
│   └── azure-functions.md          # (keep reference, detail in aos-azure-functions)
├── specifications/
│   ├── README.md
│   ├── auth.md
│   ├── extensibility.md
│   ├── governance.md
│   ├── learning.md
│   ├── mcp.md
│   ├── messaging.md
│   ├── ml.md
│   ├── observability.md
│   ├── orchestration.md
│   ├── refactoring.md
│   ├── reliability.md
│   └── storage.md
├── features/
│   ├── features-overview.md
│   └── advanced-features.md
├── development/
│   ├── CONTRIBUTING.md
│   ├── MIGRATION.md
│   ├── REFACTORING.md
│   └── README.md
├── reference/
│   └── system-apis.md
├── releases/
│   ├── CHANGELOG.md
│   ├── RELEASE_NOTES.md
│   └── BREAKING_CHANGES.md
├── # Standalone docs from root
├── APP_CONFIGURATION.md
├── CODE_ORGANIZATION.md
├── DPO_README.md
├── ENHANCED_ORCHESTRATION_INTEGRATION.md
├── FOUNDRY_AGENT_SERVICE.md
├── INTEGRATION_COMPLETE.md
├── Implementation.md
├── LORAX.md
├── RealmOfAgents.md
├── a2a_communication.md
├── configuration.md
├── development.md
├── extensibility.md
├── llm_architecture.md
├── rest_api.md
├── self_learning.md
├── testing.md
└── testing_infrastructure.md
```

**Estimated size:** ~21,595 Markdown lines (docs/) + select root .md files

**Key design decisions:**
- Uses **GitHub Pages** or a docs site generator (MkDocs/Docusaurus) for a unified documentation site.
- Each sub-repo keeps only a minimal README.md pointing to aos-docs for detailed documentation.
- API reference auto-generated from `purpose-driven-agent`, agent repos, `aos-kernel`, and `aos-intelligence` source code.
- Versioned documentation matching `aos-kernel` release versions.

---

### 8. aos-azure-functions

**Purpose:** Azure Functions host applications that expose AOS as cloud services — the function app, RealmOfAgents (config-driven agent deployment), and MCPServers (config-driven MCP server deployment).

**What moves here:**

```
function_app.py                 # Main Azure Functions entry point (332 LOC)
host.json                       # Azure Functions host configuration
local.settings.json             # Local dev settings (template)
azure_functions/
├── RealmOfAgents/              # Config-driven agent deployment
│   ├── function_app.py         # RealmOfAgents function app
│   ├── function_app_original.py
│   ├── agent_config_schema.py
│   ├── example_agent_registry.json
│   ├── host.json
│   ├── requirements.txt
│   ├── README.md
│   └── MIGRATION_TO_FOUNDRY.md
├── MCPServers/                 # Config-driven MCP server deployment
│   ├── function_app.py         # MCPServers function app
│   ├── mcp_server_schema.py
│   ├── example_mcp_server_registry.json
│   ├── host.json
│   ├── requirements.txt
│   └── README.md
├── README.md
├── DEPLOYMENT.md
├── IMPLEMENTATION_SUMMARY.md
└── setup_infrastructure.sh
.github/workflows/
└── cicd-pipeline.yml           # CI/CD pipeline (references function apps)
```

**Estimated size:** ~1,888 Python LOC + configuration files

**pyproject.toml / requirements.txt dependencies:**
```
aos-kernel[azure]>=3.0.0
aos-intelligence[foundry]>=1.0.0    # Optional, for ML-backed agents
azure-functions>=1.21.0
agent-framework>=1.0.0rc1
agent-framework-orchestrations>=1.0.0b260219
agent-framework-azurefunctions>=1.0.0b260219
```

**Key design decisions:**
- This is a **deployment target**, not a library. It depends on `aos-kernel` and optionally `aos-intelligence`.
- The `cicd-pipeline.yml` workflow moves here since it's specific to building and deploying the function apps.
- `host.json` and Azure Functions configuration stay here.

---

### 9. aos-copilot-extensions

**Purpose:** GitHub Copilot skills, custom prompts, instructions, and agent configuration files that enhance developer experience across all AOS repositories.

**What moves here:**

```
.github/
├── skills/
│   ├── Readme.md
│   ├── aos-architecture/SKILL.md
│   ├── async-python-testing/SKILL.md
│   ├── azure-functions/SKILL.md
│   ├── code-quality-pylint/SKILL.md
│   ├── code-refactoring/SKILL.md
│   └── perpetual-agents/SKILL.md
├── prompts/
│   ├── README.md
│   ├── azure-expert.md
│   ├── code-quality-expert.md
│   ├── python-expert.md
│   └── testing-expert.md
├── instructions/
│   ├── Readme.md
│   ├── agents.instructions.md
│   ├── architecture.instructions.md
│   ├── code-quality.instructions.md
│   ├── development.instructions.md
│   ├── documents.instructions.md
│   └── python.instructions.md
├── spec/
│   └── skills.md
├── README.md
├── ONBOARDING_VALIDATION.md
├── PYLINT_IMPLEMENTATION_SUMMARY.md
└── PYLINT_QUICKREF.md
.github/workflows/
└── pylint.yml                  # Code quality workflow (applicable across repos)
```

**Estimated size:** ~10,972 Markdown lines + 1 YAML workflow

**Key design decisions:**
- Skills that are repo-specific (`deployment-error-fixer`, `azure-troubleshooting`) move to their respective repos (aos-deployment).
- General-purpose skills (architecture, testing, code quality, agents) live here.
- Prompts and instructions are reusable across all AOS repos.
- Each AOS repo includes this as a Git submodule or copies relevant skills via CI.
- The `deployment-expert.md` prompt moves to aos-deployment.

---

## Dependency Graph

```
                    ┌──────────────────┐
                    │    aos-docs      │  (no code dependencies)
                    └──────────────────┘

┌──────────────────────┐
│ aos-copilot-extensions│  (no code dependencies, used as submodule)
└──────────────────────┘

          ┌────────────────────────────────┐
          │      agent_framework           │  ← External (Microsoft Agent Framework)
          └────────────────┬───────────────┘
                           │
          ┌────────────────▼───────────────┐
          │      purpose-driven-agent      │  ← Foundational agent base class
          └────────┬───────────────────────┘
                   │
         ┌─────────▼─────────┐
         │  leadership-agent  │  ← Inherits PurposeDrivenAgent
         └─────────┬──────────┘
                   │
         ┌─────────▼─────────┐
         │     cmo-agent      │  ← Inherits LeadershipAgent
         └───────────────────┘

          ┌────────────────────────────────┐
          │         aos-kernel             │  ← OS kernel (depends on purpose-driven-agent)
          └─────────────┬──────────────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
    ┌─────────────────┐  ┌──────────────────────┐
    │ aos-intelligence│  │  aos-azure-functions  │
    │  depends on:    │  │     depends on:       │
    │  aos-kernel     │  │     aos-kernel        │
    └─────────────────┘  │     aos-intelligence  │ (optional)
                         └───────────────────────┘

          ┌──────────────────┐
          │  aos-deployment  │  (standalone, no Python AOS deps)
          └──────────────────┘
```

**Dependency rules:**
1. `purpose-driven-agent` depends on `agent-framework>=1.0.0rc1` and nothing else in AOS.
2. `leadership-agent` depends on `purpose-driven-agent>=1.0.0`.
3. `cmo-agent` depends on `leadership-agent>=1.0.0`.
4. `aos-kernel` depends on `purpose-driven-agent>=1.0.0` and no other AOS packages.
5. `aos-intelligence` depends on `aos-kernel>=3.0.0` for interfaces and base classes.
6. `aos-azure-functions` depends on `aos-kernel` (required) and `aos-intelligence` (optional).
7. `aos-deployment` is **standalone** — it deploys Azure infrastructure and has no Python dependency on AOS runtime.
8. `aos-docs` is **standalone** — pure documentation, no code.
9. `aos-copilot-extensions` is **standalone** — developer tooling, used as a submodule or reference.

---

## Shared Contracts & Interfaces

### Interface Package in purpose-driven-agent

The `ml_interface.py` module in `purpose-driven-agent` defines the canonical ML service boundary that decouples agents from the intelligence layer:

```python
# purpose-driven-agent: src/purpose_driven_agent/ml_interface.py

class IMLService(ABC):
    """Interface for ML pipeline operations — implemented by aos-intelligence."""
    
    @abstractmethod
    async def trigger_lora_training(self, agent_role: str, params: Dict) -> str: ...
    
    @abstractmethod
    async def run_ml_pipeline(self, pipeline_config: Dict) -> Dict: ...
    
    @abstractmethod
    async def infer(self, model_id: str, prompt: str) -> Dict: ...

class IKnowledgeService(ABC):
    """Interface for knowledge management — implemented by aos-intelligence."""
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[Dict]: ...
    
    @abstractmethod
    async def index_document(self, document: Dict) -> str: ...

class ILearningService(ABC):
    """Interface for self-learning — implemented by aos-intelligence."""
    
    @abstractmethod
    async def learn_from_interaction(self, interaction: Dict) -> None: ...
    
    @abstractmethod
    async def get_learning_metrics(self) -> Dict: ...
```

### Registration Pattern

```python
# aos-intelligence registers implementations at import time
from aos_core.services import IMLService, register_service
from aos_intelligence.ml.pipeline import MLPipelineManager

register_service(IMLService, MLPipelineManager)
```

### Messaging Contracts

The `messaging/contracts.py` module stays in `aos-kernel` as the canonical message format definition. All repos that send/receive messages import from `aos-kernel`.

---

## Migration Strategy

### Phase 1: Prepare Boundaries (In Current Monorepo)

**Duration:** 1-2 weeks  
**Risk:** Low (no repo split yet)

1. **Extract ML interfaces**: `IMLService`, `IKnowledgeService`, `ILearningService` are now defined in `purpose-driven-agent`'s `ml_interface.py` (already done for the standalone repo). Mirror them in `aos-kernel`'s `services/service_interfaces.py` for kernel-level usage.
2. **Decouple agents from ML** *(partially done)*: `purpose_driven.py` now declares `PurposeDrivenAgent(_AgentFrameworkBase, ABC)` — inheriting from `agent_framework.Agent`. Replace remaining direct `from ..ml.pipeline_ops import ...` with interface-based calls.
3. **Decouple orchestration from ML**: Replace `from ..ml.pipeline import MLPipelineManager` in `orchestration.py` with interface injection.
4. **Add service registration**: Create `services/registry.py` for runtime service registration.
5. **Verify tests pass** with the decoupled architecture.

### Phase 2: Create Target Repositories

**Duration:** 1 week  
**Risk:** Low

1. Create empty repos: `purpose-driven-agent`, `leadership-agent`, `cmo-agent`, `aos-kernel`, `aos-deployment`, `aos-intelligence`, `aos-docs`, `aos-azure-functions`, `aos-copilot-extensions`.
2. Copy the cut-paste-ready structures from `docs/agent-repositories/` into the three agent repos.
3. Set up CI/CD templates in each.
4. Set up package publishing (PyPI or private registry) for agent repos and `aos-kernel`.

### Phase 3: Split Code (Parallel Work Streams)

**Duration:** 2-3 weeks  
**Risk:** Medium

Use `git filter-branch` or `git subtree split` to preserve commit history:

| Stream | Source Paths | Target Repo |
|--------|-------------|-------------|
| A0 | `docs/agent-repositories/purpose-driven-agent/` | purpose-driven-agent |
| A1 | `docs/agent-repositories/leadership-agent/` | leadership-agent |
| A2 | `docs/agent-repositories/cmo-agent/` | cmo-agent |
| B | `src/AgentOperatingSystem/` (minus agents/, ml/, learning/, knowledge/), `tests/` (minus agent/ML tests) | aos-kernel |
| C | `deployment/`, select workflows, select docs | aos-deployment |
| D | `src/AgentOperatingSystem/{ml,learning,knowledge}/`, `data/`, `knowledge/`, ML tests | aos-intelligence |
| E | `docs/`, select root .md files | aos-docs |
| F | `function_app.py`, `azure_functions/`, `host.json` | aos-azure-functions |
| G | `.github/{skills,prompts,instructions,spec}/`, select .github/*.md | aos-copilot-extensions |

### Phase 4: Wire Dependencies

**Duration:** 1 week  
**Risk:** Medium

1. Publish `purpose-driven-agent` as a Python package.
2. Publish `leadership-agent` and `cmo-agent` depending on it.
3. Publish `aos-kernel` depending on `purpose-driven-agent`.
4. Update `aos-intelligence` to depend on `aos-kernel`.
5. Update `aos-azure-functions` to depend on `aos-kernel` and `aos-intelligence`.
6. Set up cross-repo CI triggers (e.g., `purpose-driven-agent` release triggers downstream CI).

### Phase 5: Archive and Redirect

**Duration:** 1 week  
**Risk:** Low

1. Archive the original `AgentOperatingSystem` repo (or mark as deprecated).
2. Update all links, references, and installation instructions.
3. Add redirect notices to the original repo's README.

---

## Cross-Repository CI/CD

### Per-Repository Workflows

| Repository | Workflows |
|-----------|-----------|
| purpose-driven-agent | `ci.yml` (lint, test, build), `release.yml` (publish to PyPI) |
| leadership-agent | `ci.yml` (lint, test against purpose-driven-agent), `release.yml` |
| cmo-agent | `ci.yml` (lint, test against leadership-agent), `release.yml` |
| aos-kernel | `ci.yml` (lint, test, build), `release.yml` (publish to PyPI) |
| aos-deployment | `infrastructure-deploy.yml`, `infrastructure-monitoring.yml`, `infrastructure-troubleshooting.yml` |
| aos-intelligence | `ci.yml` (lint, test against aos-kernel), `release.yml` |
| aos-docs | `docs-build.yml` (build docs site), `docs-deploy.yml` (publish) |
| aos-azure-functions | `cicd-pipeline.yml` (build, test, deploy function apps) |
| aos-copilot-extensions | `validate.yml` (validate skill format per spec) |

### Cross-Repository Triggers

```yaml
# In leadership-agent CI:
on:
  workflow_dispatch:
  push:
  repository_dispatch:
    types: [purpose-driven-agent-released]  # Triggered when purpose-driven-agent publishes

# In aos-intelligence CI:
on:
  workflow_dispatch:
  push:
  repository_dispatch:
    types: [aos-kernel-released]  # Triggered when aos-kernel publishes new version
```

### Dependency Version Matrix

| Package | Consumed By |
|---------|------------|
| `purpose-driven-agent>=1.0.0` | leadership-agent, cmo-agent, aos-kernel |
| `leadership-agent>=1.0.0` | cmo-agent |
| `aos-kernel>=3.0.0` | aos-intelligence, aos-azure-functions |
| `aos-intelligence>=1.0.0` | aos-azure-functions (optional) |
| `agent-framework>=1.0.0rc1` | purpose-driven-agent, aos-kernel, aos-azure-functions |
| `agent-framework-orchestrations>=1.0.0b260219` | aos-kernel, aos-azure-functions |

---

## Risks & Mitigations

### Risk 1: Breaking Cross-Module Imports

**Impact:** High  
**Likelihood:** High  
**Mitigation:**
- Phase 1 (prepare boundaries) must be completed and all tests passing before any split.
- The `agents → ml` and `orchestration → ml` couplings are the primary risk. Define interfaces first.
- Use a compatibility shim package initially if needed.

### Risk 2: Increased Development Friction

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:**
- Use a monorepo development workflow (e.g., `pip install -e ../purpose-driven-agent`) for local development across repos.
- Provide a `docker-compose.yml` or `Makefile` in a meta-repo for full-stack local setup.
- Keep dependency version ranges wide enough that not every kernel change requires intelligence/functions updates.

### Risk 3: Documentation Staleness

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:**
- Auto-generate API reference from source code in `purpose-driven-agent`, agent repos, `aos-kernel`, and `aos-intelligence`.
- Use a docs CI pipeline that builds and validates cross-references.
- Each sub-repo's README links to the canonical docs in aos-docs.

### Risk 4: History Fragmentation

**Impact:** Low  
**Likelihood:** High  
**Mitigation:**
- Use `git filter-branch` to preserve relevant commit history in each target repo.
- Keep the original repo archived as a historical reference.
- Document the split in CHANGELOG entries in all repos.

### Risk 5: CI/CD Complexity

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:**
- Use GitHub Actions `repository_dispatch` for cross-repo CI triggers.
- Pin dependency versions in CI matrices.
- Create a weekly integration test that installs all packages together and runs end-to-end tests.

---

## Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Split into 6 repos, not 3 or 4 | Natural domain boundaries; different release cadences and audiences | Feb 2026 |
| 2 | `aos-deployment` has no Python dependency on `aos-kernel` | Deployment orchestrator is standalone CLI; no runtime coupling needed | Feb 2026 |
| 3 | ML/Intelligence in separate repo from kernel | Heavy dependencies (PyTorch, transformers), different release cadence, different team expertise | Feb 2026 |
| 4 | Copilot extensions in separate repo | Reusable across all AOS repos; distinct lifecycle from code | Feb 2026 |
| 5 | Interface-based decoupling over direct imports | Enables optional installation of intelligence; follows dependency inversion principle | Feb 2026 |
| 6 | Phase 1 (prepare boundaries) before any split | Reduces risk of broken imports; validates architecture in safe monorepo environment | Feb 2026 |
| 7 | Preserve git history via filter-branch | Maintains traceability; important for audit and compliance | Feb 2026 |
| 8 | Docs in separate repo with docs site | Enables unified documentation experience; scales independently | Feb 2026 |
| 9 | Each agent in its own dedicated repository | Agents have distinct purposes, audiences, and versioning; each can be consumed independently; clean inheritance hierarchy expressed as package dependencies | Feb 2026 |
| 10 | Rename `aos-core` to `aos-kernel` | "Kernel" better describes the role: the orchestration engine, messaging bus, and system services that form the OS foundation; distinguishes clearly from `purpose-driven-agent` which is the agent foundation | Feb 2026 |
| 11 | `PurposeDrivenAgent` inherits from `agent_framework.Agent` | Establishes the canonical class hierarchy on top of the Microsoft Agent Framework runtime; graceful fallback stub preserves behaviour when package is not installed | Feb 2026 |
| 12 | Agent repo cut-paste structures in `docs/agent-repositories/` | Provides immediately usable scaffolding for the split without requiring a separate meta-repository; each folder is a complete, self-sufficient repository ready to cut-paste | Feb 2026 |

---

## Appendix: File Count Summary by Target Repository

| Target Repository | Python Files | Markdown Files | Other Files | Estimated Total |
|------------------|-------------|----------------|-------------|-----------------|
| purpose-driven-agent | ~4 | ~5 | pyproject.toml, LICENSE | ~10 |
| leadership-agent | ~2 | ~5 | pyproject.toml, LICENSE | ~8 |
| cmo-agent | ~2 | ~5 | pyproject.toml, LICENSE | ~8 |
| aos-kernel | ~111 | ~5 | pyproject.toml | ~116 |
| aos-deployment | ~27 | ~20 | 12 Bicep/param, 3 YAML | ~62 |
| aos-intelligence | ~20 | ~5 | 19 JSON | ~44 |
| aos-docs | 0 | ~60 | 0 | ~60 |
| aos-azure-functions | ~10 | ~8 | 3 JSON, host.json | ~21 |
| aos-copilot-extensions | ~2 | ~25 | 1 YAML | ~28 |
| **Total** | **~178** | **~138** | **~38** | **~357** |

> Note: Some files appear in multiple counts due to shared ownership (e.g., docs that reference deployment).
> The current monorepo has ~198 Python + ~117 MD + ~40 other = ~355 files.

---

## Next Steps

1. **Review this plan** with all stakeholders (core team, ML team, infra team, docs team, agent authors).
2. **Approve the interface boundaries** defined in [Shared Contracts & Interfaces](#shared-contracts--interfaces).
3. **Begin Phase 1** (prepare boundaries in current monorepo) — this is the lowest-risk step and provides immediate value even without the split. `PurposeDrivenAgent` already inherits from `agent_framework.Agent` (done).
4. **Publish agent repos** using cut-paste structures from `docs/agent-repositories/` — start with `purpose-driven-agent` as it has zero AOS dependencies.
5. **Set a target date** for Phase 3 (the actual split) — recommend 4-6 weeks from approval.
