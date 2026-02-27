# aos-kernel

The Agent Operating System Kernel — orchestration engine, messaging, storage, authentication, and all supporting system services.

## Overview

`aos-kernel` is the OS kernel for the Agent Operating System (AOS). It provides the core infrastructure that perpetual agents run on:

- **Orchestration Engine** — Workflow orchestration, decision engines, agent coordination
- **Messaging** — Message bus, routing, contracts, Azure Service Bus integration
- **Storage** — Storage backends (Azure Blob, Table, Queue)
- **Authentication** — Auth management, JWT, Azure Identity
- **MCP** — Model Context Protocol client and server
- **Reliability** — Circuit breakers, retry policies, fault tolerance patterns
- **Observability** — Logging, metrics, distributed tracing (OpenTelemetry)
- **Governance** — Audit, compliance, risk management
- **Monitoring** — System monitoring, audit trails
- **Extensibility** — Plugin framework, registries

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

aos = AgentOperatingSystem()
await aos.initialize()
await aos.start()
```

## Architecture

The kernel provides system services that perpetual agents depend on:

```
┌─────────────────────────────────────────┐
│         Agent Operating System          │
├──────────┬──────────┬──────────┬────────┤
│ Orchestr │ Messag   │ Storage  │  Auth  │
├──────────┼──────────┼──────────┼────────┤
│   MCP    │ Reliab   │ Observe  │  Gov   │
├──────────┼──────────┼──────────┼────────┤
│ Monitor  │ Extend   │ Platform │Services│
└──────────┴──────────┴──────────┴────────┘
```

## Package Dependencies

- `purpose-driven-agent>=1.0.0` — Foundational agent base class
- `agent-framework>=1.0.0rc1` — Microsoft Agent Framework
- `agent-framework-orchestrations>=1.0.0b260219` — Orchestration patterns

## Repository Structure

```
src/AgentOperatingSystem/   # Kernel source code
tests/                      # Kernel tests
examples/                   # Usage examples
docs/                       # Kernel documentation
.github/                    # CI/CD, Copilot skills, prompts, instructions
```

## Related Repositories

- [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) — Foundational agent base class
- [leadership-agent](https://github.com/ASISaga/leadership-agent) — Leadership agent
- [cmo-agent](https://github.com/ASISaga/cmo-agent) — CMO agent
- [aos-intelligence](https://github.com/ASISaga/aos-intelligence) — ML/AI intelligence layer
- [aos-deployment](https://github.com/ASISaga/aos-deployment) — Infrastructure deployment
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app
- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK for external applications
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client application

## License

Apache License 2.0 — see [LICENSE](LICENSE)
