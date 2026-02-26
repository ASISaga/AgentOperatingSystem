# Agent Operating System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**A production-grade operating system for perpetual, purpose-driven AI agents.**

This meta-repository coordinates the Agent Operating System across multiple focused repositories.
Each sub-repository is independently versioned, tested, and deployed.

---

## Repository Map

| Repository | Description | Package |
|---|---|---|
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | The fundamental agent building block | `pip install purpose-driven-agent` |
| [leadership-agent](https://github.com/ASISaga/leadership-agent) | Leadership + decision-making agent | `pip install leadership-agent` |
| [cmo-agent](https://github.com/ASISaga/cmo-agent) | Chief Marketing Officer agent | `pip install cmo-agent` |
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | OS kernel: orchestration, messaging, storage, auth | `pip install aos-kernel` |
| [aos-deployment](https://github.com/ASISaga/aos-deployment) | Infrastructure: Bicep, orchestrator, CI/CD | — |
| [aos-intelligence](https://github.com/ASISaga/aos-intelligence) | ML/AI: LoRA, DPO, self-learning, knowledge | `pip install aos-intelligence` |
| [aos-function-app](https://github.com/ASISaga/aos-function-app) | Main Azure Functions host | — |
| [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) | Config-driven agent deployment | — |
| [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) | Config-driven MCP server deployment | — |

## Architecture

```
                    ┌──────────────────┐
                    │  agent_framework │  (Microsoft Agent Framework)
                    └────────┬─────────┘
                             │
                ┌────────────▼────────────┐
                │  purpose-driven-agent   │  (Foundational agent base class)
                └────────┬───────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
   ┌────────▼────────┐    ┌──────────▼──────────┐
   │ leadership-agent │    │     aos-kernel      │
   └────────┬─────────┘    └──────┬──────────────┘
            │                     │
   ┌────────▼────────┐    ┌──────┴───────────────┐
   │    cmo-agent    │    │                       │
   └─────────────────┘    ▼                       ▼
                   ┌──────────────┐    ┌────────────────────┐
                   │aos-intelligence│   │ aos-function-app   │
                   └──────────────┘    │ aos-realm-of-agents│
                                       │ aos-mcp-servers    │
                                       └────────────────────┘

              ┌──────────────────┐
              │  aos-deployment  │  (standalone — Bicep + orchestrator)
              └──────────────────┘
```

## Getting Started

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/ASISaga/AgentOperatingSystem.git

# Or update submodules after clone
git submodule update --init --recursive
```

## Cut-Paste Ready Repositories

Each sub-repository has a cut-paste-ready structure in [`docs/agent-repositories/`](docs/agent-repositories/):

```
docs/agent-repositories/
├── purpose-driven-agent/    # → github.com/ASISaga/purpose-driven-agent
├── leadership-agent/        # → github.com/ASISaga/leadership-agent
├── cmo-agent/               # → github.com/ASISaga/cmo-agent
├── aos-kernel/              # → github.com/ASISaga/aos-kernel
├── aos-deployment/          # → github.com/ASISaga/aos-deployment
├── aos-intelligence/        # → github.com/ASISaga/aos-intelligence
├── aos-function-app/        # → github.com/ASISaga/aos-function-app
├── aos-realm-of-agents/     # → github.com/ASISaga/aos-realm-of-agents
└── aos-mcp-servers/         # → github.com/ASISaga/aos-mcp-servers
```

## Split Plan

See [docs/development/REPOSITORY_SPLIT_PLAN.md](docs/development/REPOSITORY_SPLIT_PLAN.md) for the
complete migration strategy, dependency graph, and phase-by-phase plan.

## License

[MIT License](LICENSE) — © 2025 ASI Saga
