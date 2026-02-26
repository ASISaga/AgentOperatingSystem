# aos-function-app

Main Azure Functions entry point for the Agent Operating System. Exposes AOS as cloud services via Service Bus triggers and HTTP endpoints.

## Overview

This function app is the primary AOS cloud entry point, providing:

- **Service Bus Triggers** — Event-driven agent activation via Azure Service Bus
- **HTTP Endpoints** — REST API for agent management and status
- **Agent Lifecycle** — Agent initialization, event processing, and health monitoring

## Prerequisites

- Azure Functions Core Tools v4
- Python 3.10+
- Azure subscription with Service Bus namespace

## Local Development

```bash
pip install -r requirements.txt
func start
```

## Deployment

Deploy via the [aos-deployment](https://github.com/ASISaga/aos-deployment) repository's orchestrator, or directly:

```bash
func azure functionapp publish <app-name>
```

## Dependencies

- `aos-kernel[azure]>=3.0.0` — AOS kernel with Azure backends
- `aos-intelligence[foundry]>=1.0.0` — (Optional) ML-backed agents
- `azure-functions>=1.21.0`

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-deployment](https://github.com/ASISaga/aos-deployment) — Infrastructure deployment
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents function app
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers function app

## License

Apache License 2.0 — see [LICENSE](LICENSE)
