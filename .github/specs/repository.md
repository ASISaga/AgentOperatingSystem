# GitHub Copilot Instructions — AgentOperatingSystem (Meta-Repository)

## Overview

This is the **AgentOperatingSystem meta-repository**. It coordinates **15 focused repositories** under the [ASISaga](https://github.com/ASISaga) GitHub organization via Git submodules. Each sub-repository is independently versioned, tested, and deployed.

The AgentOperatingSystem provides **agent orchestrations as an infrastructure service** to client applications. Client apps stay lean (business logic only), while AOS handles agent lifecycle, orchestration, messaging, storage, and monitoring via the **Azure AI Foundry Agent Service**.

---

## Repository Map

### Agent Repositories (RealmOfAgents)

| Submodule | GitHub URL | Description |
|-----------|-----------|-------------|
| `purpose-driven-agent/` | https://github.com/ASISaga/purpose-driven-agent | Foundational agent base class (`PurposeDrivenAgent`) — building block of all AOS agents |
| `leadership-agent/` | https://github.com/ASISaga/leadership-agent | Leadership, decision-making, and multi-agent orchestration (`LeadershipAgent`) |
| `ceo-agent/` | https://github.com/ASISaga/ceo-agent | CEO agent — executive + boardroom orchestration |
| `cfo-agent/` | https://github.com/ASISaga/cfo-agent | CFO agent — finance + boardroom orchestration |
| `cto-agent/` | https://github.com/ASISaga/cto-agent | CTO agent — technology + boardroom orchestration |
| `cso-agent/` | https://github.com/ASISaga/cso-agent | CSO agent — security + boardroom orchestration |
| `cmo-agent/` | https://github.com/ASISaga/cmo-agent | CMO agent — marketing + boardroom orchestration |

### Platform Repositories

| Submodule | GitHub URL | Description |
|-----------|-----------|-------------|
| `aos-kernel/` | https://github.com/ASISaga/aos-kernel | OS kernel — orchestration, messaging, storage, auth, MCP, monitoring |
| `aos-intelligence/` | https://github.com/ASISaga/aos-intelligence | ML/AI — LoRA, DPO, self-learning, knowledge, RAG, Foundry integration |
| `aos-infrastructure/` | https://github.com/ASISaga/aos-infrastructure | Infrastructure — Bicep (AI Hub, Project, Services, Gateway), deployment orchestrator |

### Service Repositories

| Submodule | GitHub URL | Description |
|-----------|-----------|-------------|
| `aos-dispatcher/` | https://github.com/ASISaga/aos-dispatcher | Orchestration API — submit, monitor, retrieve orchestrations (Azure Functions) |
| `realm-of-agents/` | https://github.com/ASISaga/realm-of-agents | Agent catalog — browse and select agents (Azure Functions) |
| `mcp/` | https://github.com/ASISaga/mcp | MCP server deployment (Azure Functions) |

### Client Repositories

| Submodule | GitHub URL | Description |
|-----------|-----------|-------------|
| `aos-client-sdk/` | https://github.com/ASISaga/aos-client-sdk | App framework & SDK — Azure Functions scaffolding, Service Bus, auth, deployment |
| `business-infinity/` | https://github.com/ASISaga/business-infinity | Example client app — C-suite orchestrations via AOS (Azure Functions) |

---

## Architecture

```
┌───────────────────────────────────────┐
│  Client Application                   │  ← Your app (e.g. business-infinity)
│  (business logic only)                │     pip install aos-client-sdk[azure]
│  @app.workflow decorators             │
│  function_app.py = 7 lines            │
└───────────────────────────────────────┘
                 │ HTTPS / Azure Service Bus
┌────────────────▼────────────────────────────────────────────┐
│  Agent Operating System                                      │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │ aos-dispatcher    │  │ Azure AI Foundry Agent Service   │  │
│  │ POST /api/        │  │ AIProjectClient · AzureAIAgent   │  │
│  │  orchestrations   │  │ Thread management                │  │
│  └────────┬─────────┘  └──────────────────────────────────┘  │
│           │                                                   │
│  ┌────────▼──────────────────────────────────────────────────┐│
│  │ aos-kernel                                                 ││
│  │ Orchestration · Messaging · Storage · Auth · MCP          ││
│  └────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
                 │
     ┌───────────▼───────────┐
     │  RealmOfAgents         │  ← purpose-driven-agent, leadership-agent,
     │  Agent Catalog         │    ceo/cfo/cto/cso/cmo-agent
     └───────────────────────┘
```

### Dependency Hierarchy

```
agent_framework (Microsoft)
       │
purpose-driven-agent  ──── as_tool(), register_with_foundry()
    ┌──┴──┐                (code-only library, not deployed)
leadership-agent           (code-only library, not deployed)
┌───┬───┬───┬──┐
CEO CFO CTO CSO CMO        (each deployed as Azure Functions)
                 │
       aos-kernel ◄──────── azure-ai-projects, azure-ai-agents
       ┌──┴──┐
aos-intelligence │          (LoRA, DPO, self-learning, RAG)
       │       │
aos-dispatcher  realm-of-agents  mcp
       ▲                (Foundry registration)
       │
 aos-client-sdk ◄──────── app framework + HTTP/Service Bus SDK
       ▲
business-infinity ◄──────── lean client app (business logic only)

aos-infrastructure ──────── standalone Bicep: AI Hub, Project, Gateway
```

---

## Working with Submodules

Each subdirectory at the root of this meta-repo is a Git submodule pointing to its own GitHub repository. To work on a sub-repository:

```bash
# Initialize and update all submodules
git submodule update --init --recursive

# Work on a specific submodule
cd aos-kernel
git checkout main
# ... make changes, commit, push within that repo

# Update the meta-repo to point to the new submodule commit
cd ..
git add aos-kernel
git commit -m "chore: update aos-kernel submodule reference"
```

---

## Coding Conventions

### Python Packages

- All Python packages use `pyproject.toml` with `[build-system]` set to `hatchling`
- Package names follow kebab-case (e.g., `aos-kernel`, `purpose-driven-agent`)
- Python module names follow snake_case (e.g., `aos_kernel`, `purpose_driven_agent`)
- All packages target **Python 3.11+**
- Main agent class is always named after the repo (e.g., `CEOAgent` in `ceo-agent`)

### Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent  (purpose-driven-agent)
            └── LeadershipAgent  (leadership-agent)
                    └── CEOAgent / CFOAgent / CTOAgent / CSOAgent / CMOAgent
```

### Azure AI Foundry Integration

- All agents register with Foundry via `register_with_foundry()` in `PurposeDrivenAgent`
- Agent-to-agent (A2A) communication uses `as_tool()` returning `A2AAgentTool` dataclass
- `aos-kernel` exposes `enroll_agent_tools()` and `get_a2a_tool_definitions()` for boardroom orchestration
- `FoundryAgentManager` is used in `aos-mcp-servers` and `aos-realm-of-agents` for Foundry registration

### Infrastructure

- All Bicep templates are in `aos-infrastructure/deployment/`
- 12 deployed app modules (CEO, CFO, CTO, CSO, CMO agents + dispatcher + realm-of-agents + mcp-servers + infrastructure services)
- Deployment uses `azd` CLI + `azure-ai-agents` extension
- Agent repos use `azd ai agent init`; function repos do not

### Testing

- Each repo has `tests/` with pytest
- C-suite agent tests use `--rootdir` flag to avoid namespace conflicts
- Full test suite: ~387 tests across all repos

---

## Cross-Repository Change Guidelines

When making changes that span multiple repositories:

1. **Start with the lowest-level dependency** (e.g., `purpose-driven-agent` before `leadership-agent` before `ceo-agent`)
2. **Update the interface contract** in the base package first, then update dependent packages
3. **Bump versions** in `pyproject.toml` following semver (patch for fixes, minor for features, major for breaking changes)
4. **Update dependency constraints** in downstream repos' `pyproject.toml` files
5. **Run CI** in each affected repo before updating submodule pointers in this meta-repo

---

## Key Files in This Meta-Repository

| File | Purpose |
|------|---------|
| `README.md` | Architecture overview, repository map, quick-start guides |
| `.gitmodules` | Submodule definitions — all 15 sub-repositories |
| `function_app.py` | Azure Functions entry point for aos-dispatcher (thin HTTP/Service Bus wrapper) |
| `docs/ARCHITECTURE.md` | System architecture, dependency graph, Azure infrastructure |
| `docs/API-REFERENCE.md` | Complete dispatcher API endpoint reference |
| `docs/DEPLOYMENT.md` | Azure deployment guide (infra provisioning, secrets, CI/CD) |
| `docs/DEVELOPMENT.md` | Developer guide (submodules, conventions, adding agents/endpoints) |
| `docs/CONFIGURATION.md` | Environment variables, host.json, APIM, Service Bus configuration |
| `docs/REPOSITORY_SPLIT_PLAN.md` | The completed multi-repo architecture plan |
| `docs/AOS_ENHANCEMENT_REQUESTS.md` | Enhancement requests from BusinessInfinity to aos-client-sdk |
| `docs/AOS_FURTHER_ENHANCEMENTS.md` | Further enhancement requests for the SDK and platform |
| `spec/design.md` | Design document for the monolith-to-submodule migration |
| `spec/requirements.md` | EARS requirements for the migration |
| `spec/tasks.md` | Task tracking for the migration (all tasks complete) |

---

## GitHub Organization

All repositories live under the **[ASISaga](https://github.com/ASISaga)** GitHub organization:

- https://github.com/ASISaga/agent-operating-system (this meta-repo)
- https://github.com/ASISaga/purpose-driven-agent
- https://github.com/ASISaga/leadership-agent
- https://github.com/ASISaga/ceo-agent
- https://github.com/ASISaga/cfo-agent
- https://github.com/ASISaga/cto-agent
- https://github.com/ASISaga/cso-agent
- https://github.com/ASISaga/cmo-agent
- https://github.com/ASISaga/aos-kernel
- https://github.com/ASISaga/aos-intelligence
- https://github.com/ASISaga/aos-infrastructure
- https://github.com/ASISaga/aos-dispatcher
- https://github.com/ASISaga/realm-of-agents
- https://github.com/ASISaga/mcp
- https://github.com/ASISaga/aos-client-sdk
- https://github.com/ASISaga/business-infinity
