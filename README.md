# Agent Operating System

**Agent Orchestrations as an Infrastructure Service — powered by Azure AI Foundry**

The Agent Operating System (AOS) provides **agent orchestrations as an infrastructure service** to client applications. Client apps stay lean, containing only business logic, while AOS handles agent lifecycle, orchestration, messaging, storage, and monitoring.

Multi-agent orchestration is managed by the **Foundry Agent Service**. Agents inheriting from `PurposeDrivenAgent` continue to run as Microsoft Agent Framework Python code inside Azure Functions (`Microsoft.Web/sites`).

## How It Works

```
┌───────────────────────────────────────┐
│  Client Application                   │  ← Your app (e.g. BusinessInfinity)
│  (business logic only)                │     pip install aos-client-sdk[azure]
│  @app.workflow decorators  ───────────┼──┐
│  function_app.py = 7 lines            │  │
└───────────────────────────────────────┘  │
                                           │ HTTPS / Azure Service Bus
┌──────────────────────────────────────────┼───────────────────────┐
│  Agent Operating System                  ▼                       │
│  ┌──────────────────┐  ┌────────────────────┐  ┌──────────────┐  │
│  │ aos-dispatcher    │  │ Foundry Agent      │  │ AI Gateway   │  │
│  │ POST /api/        │  │ Service (internal) │  │ (APIM)       │  │
│  │  orchestrations   │  │ AIProjectClient    │  │ Rate limiting│  │
│  │ Service Bus       │  │ AzureAIAgent       │  │ JWT auth     │  │
│  │  trigger          │  │ Thread mgmt        │  │              │  │
│  └────────┬─────────┘  └────────────────────┘  └──────────────┘  │
│           │                                                       │
│  ┌────────▼─────────────────────────────────────────────────────┐ │
│  │ Azure AI Foundry (internal)                                   │ │
│  │ Hub · Project · AI Services · Connections · Model Deployments  │ │
│  │ Entra Agent ID · Managed Identity                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│           │                                                       │
│  ┌────────▼─────────────────────────────────────────────────────┐ │
│  │ aos-kernel                                                    │ │
│  │ Orchestration · Messaging · Storage · Auth · MCP · Monitoring │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### Azure AI Foundry Infrastructure

AOS provisions the following Azure resources via Bicep:

| Resource | Type | Purpose |
|----------|------|---------|
| AI Services | `Microsoft.CognitiveServices/accounts` | Foundation AI/ML endpoint (GPT-4o, etc.) |
| AI Foundry Hub | `Microsoft.MachineLearningServices/workspaces` (Hub) | Central governance, connections to AI Services |
| AI Foundry Project | `Microsoft.MachineLearningServices/workspaces` (Project) | Isolated workspace for agent registration |
| AI Gateway | `Microsoft.ApiManagement/service` | Rate limiting, JWT validation, centralized routing |
| Connections | Hub → AI Services (AzureOpenAI, AAD auth) | Identity-based model access |

### Example: BusinessInfinity

[BusinessInfinity](https://github.com/ASISaga/business-infinity) is a lean Azure Functions app that selects C-suite agents from the RealmOfAgents catalog and runs orchestrations via AOS — with **zero boilerplate, zero agent code, and zero infrastructure code**:

```python
# workflows.py — define business logic with @app.workflow decorators
from aos_client import AOSApp, WorkflowRequest

app = AOSApp(name="business-infinity")

@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    agents = await request.client.list_agents()
    c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent", "CEOAgent", "CFOAgent", "CTOAgent", "CSOAgent")]
    return await request.client.start_orchestration(
        agent_ids=c_suite,
        purpose="Drive strategic growth and continuous organisational improvement",
        context=request.body,
    )
```

```python
# function_app.py — the SDK handles all Azure Functions scaffolding
from business_infinity.workflows import app
functions = app.get_functions()
```

The SDK generates HTTP triggers, Service Bus triggers, health endpoints, authentication middleware, and deployment configuration automatically.

## Repository Structure

This meta-repository coordinates **15 focused repositories** under the [ASISaga](https://github.com/ASISaga) organization via Git submodules. Each is independently versioned, tested, and deployed.

### Agent Repositories (RealmOfAgents)

| Repository | Description | Package | Deployed |
|-----------|-------------|---------|----------|
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | Foundational agent base class — the building block of AOS | `pip install purpose-driven-agent` | No (code-only library) |
| [leadership-agent](https://github.com/ASISaga/leadership-agent) | Leadership, decision-making, and multi-agent orchestration | `pip install leadership-agent` | No (code-only library) |
| [ceo-agent](https://github.com/ASISaga/ceo-agent) | CEO agent — executive + leadership dual-purpose | `pip install ceo-agent` | Azure Functions |
| [cfo-agent](https://github.com/ASISaga/cfo-agent) | CFO agent — finance + leadership dual-purpose | `pip install cfo-agent` | Azure Functions |
| [cto-agent](https://github.com/ASISaga/cto-agent) | CTO agent — technology + leadership dual-purpose | `pip install cto-agent` | Azure Functions |
| [cso-agent](https://github.com/ASISaga/cso-agent) | CSO agent — security + leadership dual-purpose | `pip install cso-agent` | Azure Functions |
| [cmo-agent](https://github.com/ASISaga/cmo-agent) | CMO agent — marketing + leadership dual-purpose | `pip install cmo-agent` | Azure Functions |

### Platform Repositories

| Repository | Description | Package |
|-----------|-------------|---------|
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | OS kernel — orchestration, messaging, storage, auth | `pip install aos-kernel` |
| [aos-intelligence](https://github.com/ASISaga/aos-intelligence) | ML/AI — LoRA, DPO, self-learning, knowledge, RAG | `pip install aos-intelligence` |
| [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) | Infrastructure — Bicep, orchestrator, regional validation | Standalone CLI |

### Service Repositories (AOS Infrastructure)

| Repository | Description | Deployment | Custom Domain |
|-----------|-------------|------------|---------------|
| [aos-dispatcher](https://github.com/ASISaga/aos-dispatcher) | Orchestration API — submit, monitor, retrieve orchestrations | Azure Functions | `aos-dispatcher.asisaga.com` |
| [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) | Agent catalog — browse and select agents | Azure Functions | `aos-realm-of-agents.asisaga.com` |
| [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) | MCP server deployment & management | Azure Functions | `aos-mcp-servers.asisaga.com` |

### Client Repositories

| Repository | Description | Package |
|-----------|-------------|---------|
| [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) | App framework & SDK — Azure Functions scaffolding, Service Bus, auth, registration, deployment | `pip install aos-client-sdk[azure]` |
| [business-infinity](https://github.com/ASISaga/business-infinity) | Example client app — C-suite orchestrations via AOS | Azure Functions |

## Dependency Graph

```
                agent_framework (Microsoft)
                       │
                purpose-driven-agent  ──── as_tool(), register_with_foundry()
                    ┌──┴──┐                (code-only library, not deployed)
            leadership-agent  │            (code-only library, not deployed)
           ┌────┬───┬───┬─┴─┐│
          CEO  CFO  CTO CSO CMO
                              │
                    aos-kernel ◄──────── depends on purpose-driven-agent
                    ┌──┴──┐              azure-ai-projects, azure-ai-agents
          aos-intelligence  │
                    │       │
          aos-dispatcher  aos-realm-of-agents  aos-mcp-servers
                    ▲          (Foundry registration)
                    │
              aos-client-sdk ◄──────── app framework + HTTP/Service Bus SDK
                    ▲                   Foundry is internal to AOS
                    │
            business-infinity ◄──────── lean client app (business logic only)
                                         function_app.py = 2 lines

          aos-infrastructure (standalone — 13 Bicep modules, 16 custom *.asisaga.com domains)
```

## Quick Start

### For Client Application Developers

```bash
# Install the client SDK with Azure Functions + Service Bus + Auth
pip install aos-client-sdk[azure]
```

```python
# workflows.py — define business logic with decorators
from aos_client import AOSApp, WorkflowRequest

app = AOSApp(name="my-app")

@app.workflow("quarterly-review")
async def quarterly_review(request: WorkflowRequest):
    agents = await request.client.list_agents()
    return await request.client.start_orchestration(
        agent_ids=[a.agent_id for a in agents],
        purpose="quarterly_review",
        context=request.body,
    )
```

```python
# function_app.py — zero boilerplate
from my_app.workflows import app
functions = app.get_functions()
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

## Cut-Paste Ready Repository Scaffolding

> **Note:** The `docs/agent-repositories/` directory previously contained cut-paste ready scaffolding for each of the 15 repositories. The repositories have now been created on GitHub and are referenced as submodules. Each submodule directory at the root of this meta-repo is the live repository. See [Git Submodules](#git-submodules) below.

## Architecture

For detailed architecture documentation, see:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture, dependency graph, infrastructure
- [docs/REPOSITORY_SPLIT_PLAN.md](docs/REPOSITORY_SPLIT_PLAN.md) — Completed multi-repo architecture plan
- [docs/API-REFERENCE.md](docs/API-REFERENCE.md) — Dispatcher API endpoint reference
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Azure deployment guide
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Developer guide
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) — Environment variables & configuration
- Each repository's own `docs/` for module-specific architecture

## Git Submodules

All 15 repositories are referenced as Git submodules at the root of this meta-repo:

```bash
# Initialize and update all submodules after cloning
git submodule update --init --recursive
```

The submodule URLs are:

```bash
# Already configured in .gitmodules — to re-add if needed:
git submodule add https://github.com/ASISaga/purpose-driven-agent.git
git submodule add https://github.com/ASISaga/leadership-agent.git
git submodule add https://github.com/ASISaga/ceo-agent.git
git submodule add https://github.com/ASISaga/cfo-agent.git
git submodule add https://github.com/ASISaga/cto-agent.git
git submodule add https://github.com/ASISaga/cso-agent.git
git submodule add https://github.com/ASISaga/cmo-agent.git
git submodule add https://github.com/ASISaga/aos-kernel.git
git submodule add https://github.com/ASISaga/aos-infrastructure.git
git submodule add https://github.com/ASISaga/aos-intelligence.git
git submodule add https://github.com/ASISaga/aos-dispatcher.git
git submodule add https://github.com/ASISaga/aos-realm-of-agents.git
git submodule add https://github.com/ASISaga/aos-mcp-servers.git
git submodule add https://github.com/ASISaga/aos-client-sdk.git
git submodule add https://github.com/ASISaga/business-infinity.git
```

Required GitHub configuration per deployed repo:

| Type | Name | Value |
|------|------|-------|
| Secret | `AZURE_CLIENT_ID` | Per-app User-Assigned MI clientId (from Bicep output) |
| Secret | `AZURE_TENANT_ID` | Azure tenant ID |
| Secret | `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| Secret | `AZURE_AI_PROJECT_ID` | Azure AI Foundry project resource ID |
| Variable | `AZURE_ENV_NAME` | Existing azd environment name (e.g. `aos-prod`) |
| Variable | `AZURE_LOCATION` | Primary Azure region (e.g. `eastus`) |

## License

Apache License 2.0 — see [LICENSE](LICENSE)
