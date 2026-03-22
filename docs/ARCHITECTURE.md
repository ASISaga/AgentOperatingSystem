# Agent Operating System — Architecture

**Last Updated**: 2026-03-22

## Overview

The Agent Operating System (AOS) provides **agent orchestrations as an infrastructure service** to client applications. Client apps contain only business logic; AOS handles agent lifecycle, orchestration, messaging, storage, authentication, and monitoring.

Multi-agent orchestration is managed by the **Azure AI Foundry Agent Service**. Agents inheriting from `PurposeDrivenAgent` run as Microsoft Agent Framework Python code inside Azure Functions.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Client Application  (e.g. BusinessInfinity)            │
│  business logic only · @app.workflow decorators         │
│  function_app.py = 2 lines                              │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTPS / Azure Service Bus
┌───────────────────────────▼─────────────────────────────┐
│  Agent Operating System                                  │
│                                                          │
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │  aos-dispatcher  │  │  Azure AI Foundry            │  │
│  │  POST /api/      │  │  Agent Service (internal)    │  │
│  │   orchestrations │  │  AIProjectClient             │  │
│  │  Service Bus     │  │  AzureAIAgent                │  │
│  │   trigger        │  │  Thread management           │  │
│  └────────┬────────┘  └──────────────────────────────┘  │
│           │                                              │
│  ┌────────▼──────────────────────────────────────────┐  │
│  │  Azure AI Foundry Hub & Project (internal)        │  │
│  │  Hub · Project · AI Services · Model Deployments  │  │
│  │  Entra Agent ID · Managed Identity                │  │
│  └────────┬──────────────────────────────────────────┘  │
│           │                                              │
│  ┌────────▼──────────────────────────────────────────┐  │
│  │  aos-kernel                                        │  │
│  │  Orchestration · Messaging · Storage              │  │
│  │  Auth · MCP · Monitoring                          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────┐  ┌───────────────────────────┐    │
│  │  AI Gateway       │  │  aos-realm-of-agents           │    │
│  │  (APIM)           │  │  Agent catalog & registry  │    │
│  │  Rate limiting    │  │  Browse & select agents    │    │
│  │  JWT auth         │  └───────────────────────────┘    │
│  └──────────────────┘                                    │
└──────────────────────────────────────────────────────────┘
                            │
             ┌──────────────▼──────────────┐
             │  RealmOfAgents               │
             │  purpose-driven-agent        │
             │  leadership-agent            │
             │  ceo · cfo · cto · cso · cmo │
             └─────────────────────────────┘
```

---

## Dependency Graph

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
aos-dispatcher  aos-realm-of-agents  aos-mcp-servers
       ▲                (Foundry registration)
       │
 aos-client-sdk ◄──────── app framework + HTTP/Service Bus SDK
       ▲
business-infinity ◄──────── lean client app (business logic only)

aos-infrastructure ──────── standalone Bicep: AI Hub, Project, Gateway
```

---

## Repository Map

This meta-repository coordinates **15 focused repositories** via Git submodules. Each is independently versioned, tested, and deployed.

### Agent Repositories (RealmOfAgents)

| Submodule | Description | Deployed |
|-----------|-------------|----------|
| `purpose-driven-agent/` | Foundational agent base class (`PurposeDrivenAgent`) | No — code-only library |
| `leadership-agent/` | Leadership, decision-making, multi-agent orchestration | No — code-only library |
| `ceo-agent/` | CEO agent — executive + boardroom orchestration | Azure Functions |
| `cfo-agent/` | CFO agent — finance + boardroom orchestration | Azure Functions |
| `cto-agent/` | CTO agent — technology + boardroom orchestration | Azure Functions |
| `cso-agent/` | CSO agent — security + boardroom orchestration | Azure Functions |
| `cmo-agent/` | CMO agent — marketing + boardroom orchestration | Azure Functions |

### Platform Repositories

| Submodule | Description | Version |
|-----------|-------------|---------|
| `aos-kernel/` | OS kernel — orchestration, messaging, storage, auth, MCP, monitoring | v6.0.0 |
| `aos-intelligence/` | ML/AI — LoRA/LoRAx, DPO, self-learning, knowledge, RAG, Foundry integration | v2.0.0 |
| `aos-infrastructure/` | Infrastructure — 13 Bicep modules, deployment orchestrator (3 pillars), 16 custom domains | v5.0.0+ |

### Service Repositories

| Submodule | Description | Deployment | Custom Domain |
|-----------|-------------|------------|---------------|
| `aos-dispatcher/` | Orchestration API — submit, monitor, retrieve orchestrations | Azure Functions | `aos-dispatcher.asisaga.com` |
| `aos-realm-of-agents/` | Agent catalog — browse and select agents (`/api/realm/agents`) | Azure Functions | `aos-realm-of-agents.asisaga.com` |
| `aos-mcp-servers/` | MCP server deployment & management | Azure Functions | `aos-mcp-servers.asisaga.com` |

### Client Repositories

| Submodule | Description | Version |
|-----------|-------------|---------|
| `aos-client-sdk/` | App framework & SDK — AOSApp, AOSClient, AOSAuth, AOSServiceBus, AOSRegistration, AOSDeployer, MockAOSClient | v7.0.0 |
| `business-infinity/` | Example client app — C-suite orchestrations via AOS (boardroom/ + src/) | — |

---

## Azure Infrastructure

AOS provisions the following Azure resources via Bicep (managed by `aos-infrastructure`, 13 modules):

| Resource | Azure Type | Purpose |
|----------|-----------|---------|
| AI Services | `Microsoft.CognitiveServices/accounts` | Foundation AI/ML endpoint (GPT-4o, etc.) |
| AI Foundry Hub | `Microsoft.MachineLearningServices/workspaces` (Hub) | Central governance; connections to AI Services |
| AI Foundry Project | `Microsoft.MachineLearningServices/workspaces` (Project) | Isolated workspace for agent registration; Cognitive Services User RBAC to Project MI |
| AI Gateway | `Microsoft.ApiManagement/service` | Rate limiting, JWT validation, centralized routing |
| Service Bus | `Microsoft.ServiceBus/namespaces` | Async messaging between client apps and AOS |
| Function Apps | `Microsoft.Web/sites` | Runtime for dispatcher, agents, aos-realm-of-agents, aos-mcp-servers (16 apps) |
| Managed Identities | `Microsoft.ManagedIdentity/userAssignedIdentities` | Per-app identity for RBAC |
| LoRA Inference Endpoint | Managed Online Endpoint | Llama-3.3-70B-Instruct Multi-LoRA serving |
| Model Registry | Azure ML Registry | LoRA adapter versioning and management |
| Policy + Budget | `Microsoft.Authorization/policyAssignments` + `Microsoft.Consumption/budgets` | Governance: location, HTTPS, cost controls |
| DNS + TLS | Custom hostname bindings + Managed Certificates | 16 `*.asisaga.com` hostnames with SNI TLS |

---

## Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent          (purpose-driven-agent)
            └── LeadershipAgent     (leadership-agent)
                    └── CEOAgent    (ceo-agent)
                    └── CFOAgent    (cfo-agent)
                    └── CTOAgent    (cto-agent)
                    └── CSOAgent    (cso-agent)
                    └── CMOAgent    (cmo-agent)
```

All agents inherit the full orchestration, messaging, and Foundry registration capabilities of `PurposeDrivenAgent`. Leadership agents additionally implement generic orchestration methods (`enroll_specialist_tools`, `get_specialist_tools`, `get_orchestration_instructions`) that enable boardroom-style multi-agent coordination.

---

## AOS Dispatcher — Entry Point

The `function_app.py` at the root of this meta-repository is the Azure Functions entry point for `aos-dispatcher`. It is a **thin wrapper** around the `aos_dispatcher.dispatcher` library:

- Binds HTTP routes and Service Bus triggers using `azure.functions`
- Parses `func.HttpRequest` (body, route params, query params)
- Converts `(body, status_code)` library responses to `func.HttpResponse`
- Contains **zero business logic** — all logic lives in `aos-dispatcher`

See [API-REFERENCE.md](API-REFERENCE.md) for the complete list of endpoints.

---

## Multi-Agent Orchestration Flow

```
1. Client App          POST /api/orchestrations
2. aos-dispatcher      Validates request, routes to dispatcher library
3. aos-dispatcher      Submits to Azure AI Foundry Agent Service
4. Foundry             Creates thread, assigns agents, starts orchestration
5. C-suite Agents      Execute in parallel (or sequentially/hierarchically)
6. Foundry             Aggregates results, updates thread status
7. Client App          GET /api/orchestrations/{id}/result  ← polls until done
```

Service Bus is used for scale-to-zero: the dispatcher sleeps until a message arrives on the `aos-orchestration-requests` queue, then processes it using the same code path as the HTTP endpoint.

---

## Model Context Protocol (MCP) Integration

AOS supports MCP for giving agents access to external tools (ERP, CRM, analytics):

```
Client App  →  POST /api/mcp/servers/{server}/tools/{tool}
                    ↓
           aos-dispatcher proxies to aos-mcp-servers
                    ↓
           MCP server executes tool, returns result
                    ↓
           Result returned to client / injected into agent context
```

MCP servers are managed by the `aos-mcp-servers/` submodule and registered with the Foundry Agent Service so that agents can invoke tools during their reasoning.

---

## References

- [API-REFERENCE.md](API-REFERENCE.md) — Complete dispatcher API reference
- [DEPLOYMENT.md](DEPLOYMENT.md) — Azure deployment guide
- [DEVELOPMENT.md](DEVELOPMENT.md) — Developer guide
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables & configuration
- [REPOSITORY_SPLIT_PLAN.md](REPOSITORY_SPLIT_PLAN.md) — Completed multi-repo split plan
