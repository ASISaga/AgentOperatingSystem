# Agent Operating System

**Multi-Repository Architecture for AI Agent Infrastructure**

The Agent Operating System (AOS) is a production-ready operating system for AI agents, built on Microsoft Azure and the Microsoft Agent Framework. The key architectural difference from traditional AI frameworks is **persistence** — agents are perpetual entities that run indefinitely, not temporary task-based sessions.

## Repository Structure

This monorepo has been split into **9 focused repositories** under the [ASISaga](https://github.com/ASISaga) organization. Each repository is independently versioned, tested, and deployed.

### Agent Repositories

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

### Azure Functions Repositories

| Repository | Description | Deployment |
|-----------|-------------|------------|
| [aos-function-app](https://github.com/ASISaga/aos-function-app) | Main Azure Functions entry point | Azure Functions |
| [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) | Config-driven agent deployment | Azure Functions |
| [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) | Config-driven MCP server deployment | Azure Functions |

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
                              
          aos-deployment (standalone — no AOS runtime deps)
```

## Quick Start

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

```python
from AgentOperatingSystem import AgentOperatingSystem

aos = AgentOperatingSystem()
await aos.initialize()
await aos.start()
```

## Cut-Paste Ready Repositories

The `docs/agent-repositories/` directory contains **cut-paste ready** scaffolding for each of the 9 repositories. Each subdirectory is a complete, self-sufficient repository structure ready to be moved to its own Git repository:

```
docs/agent-repositories/
├── purpose-driven-agent/   # Ready to cut-paste
├── leadership-agent/       # Ready to cut-paste
├── cmo-agent/              # Ready to cut-paste
├── aos-kernel/             # Ready to cut-paste
├── aos-deployment/         # Ready to cut-paste
├── aos-intelligence/       # Ready to cut-paste
├── aos-function-app/       # Ready to cut-paste
├── aos-realm-of-agents/    # Ready to cut-paste
└── aos-mcp-servers/        # Ready to cut-paste
```

## Architecture

For detailed architecture documentation, see:
- [Repository Split Plan](docs/development/REPOSITORY_SPLIT_PLAN.md) — Complete multi-repo architecture plan
- Each repository's own `docs/architecture.md` for module-specific architecture

## Git Submodules

Once the repositories are created on GitHub, this meta-repo can reference them as submodules:

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
```

## License

Apache License 2.0 — see [LICENSE](LICENSE)
