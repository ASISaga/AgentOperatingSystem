# RealmOfAgents

The **RealmOfAgents** is the agent catalog for the Agent Operating System.  It
provides a config-driven registry of available agents that client applications
query when composing orchestrations.

## Purpose

RealmOfAgents serves as the centralized agent catalog that:

- **Publishes available agents** — C-suite agents (CEO, CFO, CMO, COO, CTO) and custom agents
- **Describes capabilities** — Each agent's purpose, LoRA adapter, and capabilities
- **Enables agent selection** — Client applications browse the catalog and select agents for orchestrations
- **Supports dynamic configuration** — Agents defined in JSON, deployable without code changes

## How It Fits

```
┌─────────────────────┐         ┌──────────────────────────┐
│  Client Application │ ──GET──▶│  RealmOfAgents           │
│  (BusinessInfinity) │         │  GET /api/realm/agents   │
│                     │         │  Agent catalog:           │
│  aos-client-sdk     │         │   • CEO (LeadershipAgent)│
└─────────┬───────────┘         │   • CFO (LeadershipAgent)│
          │                     │   • CMO (CMOAgent)       │
          │ POST                │   • COO (LeadershipAgent)│
          ▼                     │   • CTO (LeadershipAgent)│
┌─────────────────────┐         └──────────────────────────┘
│  AOS Function App   │
│  POST /api/         │
│    orchestrations   │
└─────────────────────┘
```

## Agent Registry Format

Agents are defined in `example_agent_registry.json`:

```json
{
    "agents": [
        {
            "agent_id": "ceo",
            "agent_type": "LeadershipAgent",
            "purpose": "Strategic leadership and executive decision-making",
            "adapter_name": "leadership",
            "capabilities": ["strategic_planning", "decision_making"],
            "config": {"decision_mode": "autonomous"},
            "enabled": true
        }
    ]
}
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/realm/agents` | List all enabled agents |
| GET | `/api/realm/agents?agent_type=CMOAgent` | Filter by agent type |
| GET | `/api/realm/agents/{agent_id}` | Get a single agent |
| GET | `/api/realm/config` | Full registry (admin) |
| GET | `/api/health` | Health check |

