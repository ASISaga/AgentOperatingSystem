# aos-realm-of-agents

The **agent catalog** for the Agent Operating System. RealmOfAgents provides a config-driven registry of available agents (CEO, CFO, CMO, COO, CTO, and custom agents) that client applications query when composing orchestrations.

## Overview

RealmOfAgents provides:

- **Agent Catalog API** — HTTP endpoints for browsing available agents and their capabilities
- **Config-Driven Registry** — Agents defined in JSON, deployable without code changes
- **C-Suite Agents** — Pre-configured CEO, CFO, CMO, COO, CTO agents using LeadershipAgent and CMOAgent
- **Extensible** — Add custom agents by editing the registry JSON

## How Client Apps Use It

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    # Browse the agent catalog
    agents = await client.list_agents()
    for agent in agents:
        print(f"{agent.agent_id}: {agent.purpose}")

    # Filter by agent type
    cmo_agents = await client.list_agents(agent_type="CMOAgent")
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/realm/agents` | List all enabled agents |
| GET | `/api/realm/agents?agent_type=CMOAgent` | Filter by agent type |
| GET | `/api/realm/agents/{agent_id}` | Get a single agent |
| GET | `/api/realm/config` | Full registry (admin) |
| GET | `/api/health` | Health check |

## Agent Registry

The `example_agent_registry.json` file defines the available agents:

| Agent ID | Type | Purpose | LoRA Adapter |
|----------|------|---------|-------------|
| ceo | LeadershipAgent | Strategic leadership and executive decision-making | leadership |
| cfo | LeadershipAgent | Financial strategy, budgeting, and fiscal oversight | finance |
| cmo | CMOAgent | Marketing strategy, brand management, market analysis | marketing |
| coo | LeadershipAgent | Operations management and process optimisation | operations |
| cto | LeadershipAgent | Technology strategy, innovation, digital transformation | technology |

## Local Development

```bash
pip install -e ".[dev]"
func start
```

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK for browsing agents
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — Orchestration API
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client app
- [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) — Agent base class

## License

Apache License 2.0 — see [LICENSE](LICENSE)
