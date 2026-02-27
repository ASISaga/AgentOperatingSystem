# Agent Operating System

**Agent Orchestrations as an Infrastructure Service**

The Agent Operating System (AOS) provides **agent orchestrations as an infrastructure service** to client applications. Client apps stay lean, containing only business logic, while AOS handles agent lifecycle, orchestration, messaging, storage, and monitoring.

## How It Works

```
┌───────────────────────────────┐
│  Client Application           │  ← Your app (e.g. BusinessInfinity)
│  (business logic only)        │     pip install aos-client-sdk
│  aos-client-sdk ──────────────┼──┐
└───────────────────────────────┘  │
                                   │ HTTPS / Service Bus
┌──────────────────────────────────┼────────────────────────────────┐
│  Agent Operating System          ▼                                │
│  ┌──────────────────┐  ┌────────────────────┐  ┌──────────────┐  │
│  │ aos-function-app  │  │ aos-realm-of-      │  │ aos-mcp-     │  │
│  │ POST /api/        │  │ agents             │  │ servers      │  │
│  │  orchestrations   │  │ GET /api/realm/    │  │ MCP protocol │  │
│  │ Orchestration API │  │  agents            │  │              │  │
│  │                   │  │ Agent catalog:     │  │              │  │
│  │                   │  │  CEO · CFO · CMO   │  │              │  │
│  │                   │  │  COO · CTO · ...   │  │              │  │
│  └────────┬─────────┘  └────────────────────┘  └──────────────┘  │
│           │                                                       │
│  ┌────────▼─────────────────────────────────────────────────────┐ │
│  │ aos-kernel                                                    │ │
│  │ Orchestration · Messaging · Storage · Auth · MCP · Monitoring │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Example: BusinessInfinity

[BusinessInfinity](https://github.com/ASISaga/business-infinity) is a lean Azure Functions app that selects C-suite agents from the RealmOfAgents catalog and runs orchestrations via AOS — with **zero agent code and zero infrastructure code**:

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    # Browse the agent catalog
    agents = await client.list_agents()

    # Select C-suite agents and run a strategic review
    c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent")]
    result = await client.run_orchestration(
        agent_ids=c_suite,
        task={"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
    )
    print(result.summary)
```

## Repository Structure

This meta-repository coordinates **11 focused repositories** under the [ASISaga](https://github.com/ASISaga) organization. Each is independently versioned, tested, and deployed. After testing/review, these would be moved to their dedicated repositories.

### Agent Repositories (RealmOfAgents)

| Repository | Description | Package |
|-----------|-------------|---------|
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | Foundational agent base class — the building block of AOS | `pip install purpose-driven-agent` |
| [leadership-agent](https://github.com/ASISaga/leadership-agent) | Leadership and decision-making agent | `pip install leadership-agent` |
| [cmo-agent](https://github.com/ASISaga/cmo-agent) | Chief Marketing Officer agent | `pip install cmo-agent` |

### Platform Repositories

| Repository | Description | Package |
|-----------|-------------|---------|
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | OS kernel — orchestration, messaging, storage, auth | `pip install aos-kernel` |
| [aos-intelligence](https://github.com/ASISaga/aos-intelligence) | ML/AI — LoRA, DPO, self-learning, knowledge, RAG | `pip install aos-intelligence` |
| [aos-deployment](https://github.com/ASISaga/aos-deployment) | Infrastructure — Bicep, orchestrator, regional validation | Standalone CLI |

### Service Repositories (AOS Infrastructure)

| Repository | Description | Deployment |
|-----------|-------------|------------|
| [aos-function-app](https://github.com/ASISaga/aos-function-app) | Orchestration API — submit, monitor, retrieve orchestrations | Azure Functions |
| [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) | Agent catalog — browse and select agents | Azure Functions |
| [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) | MCP server deployment | Azure Functions |

### Client Repositories

| Repository | Description | Package |
|-----------|-------------|---------|
| [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) | Lightweight SDK for client apps to interact with AOS | `pip install aos-client-sdk` |
| [business-infinity](https://github.com/ASISaga/business-infinity) | Example client app — C-suite orchestrations via AOS | Azure Functions |

## Dependency Graph

```
                agent_framework (Microsoft)
                       │
                purpose-driven-agent
                    ┌──┴──┐
            leadership-agent  │
                    │         │
                cmo-agent     │
                              │
                    aos-kernel ◄──────── depends on purpose-driven-agent
                    ┌──┴──┐
          aos-intelligence  │
                    │       │
          aos-function-app  aos-realm-of-agents  aos-mcp-servers
                    ▲
                    │
              aos-client-sdk ◄──────── lightweight HTTP SDK
                    ▲
                    │
            business-infinity ◄──────── lean client app (business logic only)

          aos-deployment (standalone — no AOS runtime deps)
```

## Quick Start

### For Client Application Developers

```bash
# Install the client SDK — no agent or infrastructure dependencies
pip install aos-client-sdk
```

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    agents = await client.list_agents()
    result = await client.run_orchestration(
        agent_ids=["ceo", "cfo", "cmo"],
        task={"type": "quarterly_review", "data": {"quarter": "Q1-2026"}},
    )
```

### For AOS Platform Developers

```bash
# Install the kernel with Azure backends
pip install aos-kernel[azure]

# Install with ML intelligence
pip install aos-kernel[full]

# Or install individual agents
pip install purpose-driven-agent
pip install leadership-agent
pip install cmo-agent
```

## Cut-Paste Ready Repositories

The `docs/agent-repositories/` directory contains **cut-paste ready** scaffolding for each of the 11 repositories. Each subdirectory is a complete, self-sufficient repository structure:

```
docs/agent-repositories/
├── purpose-driven-agent/   # Agent base class
├── leadership-agent/       # Leadership agent
├── cmo-agent/              # CMO agent
├── aos-kernel/             # OS kernel
├── aos-deployment/         # Infrastructure deployment
├── aos-intelligence/       # ML/AI intelligence
├── aos-function-app/       # Orchestration API
├── aos-realm-of-agents/    # Agent catalog
├── aos-mcp-servers/        # MCP servers
├── aos-client-sdk/         # Client SDK
└── business-infinity/      # Example client app
```

## Architecture

For detailed architecture documentation, see:
- [Repository Split Plan](docs/development/REPOSITORY_SPLIT_PLAN.md) — Complete multi-repo architecture plan
- Each repository's own `docs/` for module-specific architecture

## Git Submodules

Once the repositories are created on GitHub, this meta-repo references them as submodules:

```bash
git submodule add https://github.com/ASISaga/purpose-driven-agent.git
git submodule add https://github.com/ASISaga/leadership-agent.git
git submodule add https://github.com/ASISaga/cmo-agent.git
git submodule add https://github.com/ASISaga/aos-kernel.git
git submodule add https://github.com/ASISaga/aos-deployment.git
git submodule add https://github.com/ASISaga/aos-intelligence.git
git submodule add https://github.com/ASISaga/aos-function-app.git
git submodule add https://github.com/ASISaga/aos-realm-of-agents.git
git submodule add https://github.com/ASISaga/aos-mcp-servers.git
git submodule add https://github.com/ASISaga/aos-client-sdk.git
git submodule add https://github.com/ASISaga/business-infinity.git
```

## License

Apache License 2.0 — see [LICENSE](LICENSE)
