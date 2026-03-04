# aos-kernel

The Agent Operating System Kernel — orchestration engine, messaging, storage, authentication, and all supporting system services.

## Overview

`aos-kernel` is the OS kernel for the Agent Operating System (AOS). It provides the core infrastructure that perpetual agents run on:

- **Foundry Agent Service** — Agent registration, thread/run lifecycle via Azure AI Foundry
- **A2A Tool Enrollment** — Enroll specialist agents as A2A tools for coordinator agents
- **Orchestration Engine** — Workflow orchestration, decision engines, agent coordination
- **Messaging** — Message bridge (bidirectional PurposeDrivenAgent ↔ Foundry)
- **Multi-LoRA** — LoRA adapter registry, inference client, orchestration router
- **Reliability** — Circuit breakers, retry policies, fault tolerance patterns
- **Observability** — Logging, metrics, distributed tracing (OpenTelemetry)
- **Governance** — Audit, compliance, risk management

## Installation

```bash
pip install aos-kernel

# With Azure service backends
pip install aos-kernel[azure]

# With all optional dependencies
pip install aos-kernel[full]
```

## Quick Start

```python
from AgentOperatingSystem import AgentOperatingSystem

kernel = AgentOperatingSystem()
await kernel.initialize()

# Register agents
await kernel.register_agent("ceo", "Strategic leadership", adapter_name="leadership")
await kernel.register_agent("cfo", "Financial oversight", adapter_name="finance")

# Create an orchestration
orch = await kernel.create_orchestration(
    agent_ids=["ceo", "cfo"],
    purpose="Quarterly strategic review",
)

# Enroll specialists as A2A tools for a coordinator
tools = kernel.enroll_agent_tools(
    coordinator_id="ceo",
    specialist_ids=["cfo"],
    thread_id="thread-001",
)
```

## Architecture

The kernel provides system services that perpetual agents depend on:

```
┌──────────────────────────────────────────────────┐
│              Agent Operating System               │
├────────────────┬────────────────┬────────────────┤
│  FoundryAgent  │  A2A Tool     │   Multi-LoRA   │
│  Manager       │  Enrollment   │   Inference    │
├────────────────┼────────────────┼────────────────┤
│  Orchestration │  Message      │  Observability │
│  Engine        │  Bridge       │  (OTel)        │
└────────────────┴────────────────┴────────────────┘
```

### Core Dependencies

| Package | Purpose |
|---|---|
| `azure-ai-projects>=2.0.0b4` | Primary SDK for Foundry Agent Service (agent, thread, run lifecycle) |
| `azure-ai-agents>=1.1.0` | AgentsClient within the Azure AI project |
| `azure-identity>=1.25.0` | Managed Identity authentication for Function App ↔ Foundry |
| `purpose-driven-agent>=1.0.0` | Foundational agent base class |
| `leadership-agent>=1.0.0` | Leadership agent with orchestration capabilities |
| `aos-intelligence>=2.0.0` | ML layer — LoRA adapters, inference, training |

## Repository Structure

```
src/AgentOperatingSystem/   # Kernel source code
tests/                      # Kernel tests
examples/                   # Usage examples
docs/                       # Kernel documentation
.github/                    # CI/CD, Copilot skills, prompts, instructions
```

## Related Repositories

- [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) — Foundational agent base class (code-only library)
- [leadership-agent](https://github.com/ASISaga/leadership-agent) — Leadership agent with orchestration (code-only library)
- [ceo-agent](https://github.com/ASISaga/ceo-agent) — CEO agent (executive + leadership)
- [cfo-agent](https://github.com/ASISaga/cfo-agent) — CFO agent (finance + leadership)
- [cto-agent](https://github.com/ASISaga/cto-agent) — CTO agent (technology + leadership)
- [cso-agent](https://github.com/ASISaga/cso-agent) — CSO agent (security + leadership)
- [cmo-agent](https://github.com/ASISaga/cmo-agent) — CMO agent (marketing + leadership)
- [aos-intelligence](https://github.com/ASISaga/aos-intelligence) — ML/AI intelligence layer
- [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) — Infrastructure deployment
- [aos-dispatcher](https://github.com/ASISaga/aos-dispatcher) — Orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app
- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK for external applications
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client application

## License

Apache License 2.0 — see [LICENSE](LICENSE)
