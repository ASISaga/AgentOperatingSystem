# aos-client-sdk

Lightweight Python SDK for interacting with the **Agent Operating System** as an infrastructure service. Client applications use this SDK to browse available agents, compose orchestrations, and retrieve results — without managing agent lifecycles or infrastructure.

## Overview

The AOS Client SDK enables lean client applications (like [BusinessInfinity](https://github.com/ASISaga/business-infinity)) to:

- **Browse agents** — Query the RealmOfAgents catalog for available agents and their capabilities
- **Compose orchestrations** — Select agents and define workflows (collaborative, sequential, hierarchical)
- **Submit & monitor** — Submit orchestration requests to AOS and poll for status/results
- **Stay lean** — Client apps contain only business logic; AOS handles agent lifecycle, orchestration, messaging, storage, and monitoring

## Quick Start

```bash
pip install aos-client-sdk
```

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    # Browse the RealmOfAgents catalog
    agents = await client.list_agents()
    for agent in agents:
        print(f"{agent.agent_id}: {agent.purpose} ({agent.agent_type})")

    # Select C-suite agents and run an orchestration
    c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent")]
    result = await client.run_orchestration(
        agent_ids=c_suite,
        task={"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
    )
    print(result.summary)
```

## API Reference

### `AOSClient`

| Method | Description |
|--------|-------------|
| `list_agents(agent_type=)` | List agents from the RealmOfAgents catalog |
| `get_agent(agent_id)` | Get a single agent descriptor |
| `submit_orchestration(request)` | Submit an orchestration request |
| `get_orchestration_status(id)` | Poll orchestration status |
| `get_orchestration_result(id)` | Get final orchestration result |
| `cancel_orchestration(id)` | Cancel a running orchestration |
| `run_orchestration(...)` | Convenience: submit + poll + return result |
| `health_check()` | Check AOS health |

### Models

| Model | Description |
|-------|-------------|
| `AgentDescriptor` | Agent metadata from the RealmOfAgents catalog |
| `OrchestrationRequest` | Request to run an agent orchestration |
| `OrchestrationStatus` | Current status of an orchestration |
| `OrchestrationResult` | Final result with per-agent outputs and summary |

## Architecture

```
┌───────────────────────────┐
│  Client Application       │  ← Your app (e.g. BusinessInfinity)
│  (business logic only)    │
│  pip install aos-client-sdk
└────────────┬──────────────┘
             │ HTTPS / Service Bus
             ▼
┌───────────────────────────┐
│  Agent Operating System   │  ← AOS infrastructure service
│  ┌─────────────────────┐  │
│  │ aos-function-app     │  │  Orchestration API
│  │ aos-realm-of-agents  │  │  Agent catalog
│  │ aos-kernel           │  │  Orchestration, messaging, storage
│  └─────────────────────┘  │
└───────────────────────────┘
```

## Authentication

For Azure-hosted deployments, pass an Azure credential:

```python
from azure.identity import DefaultAzureCredential

client = AOSClient(
    endpoint="https://my-aos.azurewebsites.net",
    credential=DefaultAzureCredential(),
)
```

For local development, omit the credential for anonymous access.

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel (orchestration, messaging, storage)
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — AOS orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client application
- [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) — Agent base class

## License

Apache License 2.0 — see [LICENSE](LICENSE)
