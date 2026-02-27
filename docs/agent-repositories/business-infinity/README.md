# BusinessInfinity

A lean Azure Functions application that demonstrates using the **Agent Operating System** as an infrastructure service. BusinessInfinity contains only business logic — all agent management, orchestration, and infrastructure concerns are delegated to AOS.

## Architecture

```
┌───────────────────────────────────────────────┐
│  BusinessInfinity (this app)                  │
│  ┌─────────────────────────────────────────┐  │
│  │  function_app.py    HTTP triggers       │  │
│  │  workflows.py       Business logic      │  │
│  │    └─ aos-client-sdk   SDK calls only   │  │
│  └─────────────────────────────────────────┘  │
│  Zero agent code. Zero infrastructure code.   │
└──────────────────┬────────────────────────────┘
                   │ HTTPS
                   ▼
┌───────────────────────────────────────────────┐
│  Agent Operating System (infrastructure)      │
│  ┌──────────────────┐  ┌───────────────────┐  │
│  │ aos-function-app  │  │ aos-realm-of-     │  │
│  │ Orchestration API │  │ agents            │  │
│  │                   │  │ Agent catalog:    │  │
│  │ POST /api/        │  │  • CEO            │  │
│  │   orchestrations  │  │  • CFO            │  │
│  │ GET /api/         │  │  • CMO            │  │
│  │   orchestrations/ │  │  • COO            │  │
│  │   {id}            │  │  • CTO            │  │
│  └──────────────────┘  └───────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ aos-kernel                               │  │
│  │ Orchestration · Messaging · Storage      │  │
│  └──────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

## Key Principle

> **BusinessInfinity focuses only on business logic.  AOS takes care of the rest.**

| Concern | Owner |
|---------|-------|
| Business workflows (strategic review, market analysis, budget approval) | BusinessInfinity |
| Agent lifecycle, orchestration, messaging, storage, monitoring | AOS |
| Agent catalog (C-suite agents, capabilities, LoRA adapters) | RealmOfAgents |

## Workflows

### Strategic Review
```bash
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/strategic-review \
  -H "Content-Type: application/json" \
  -d '{"quarter": "Q1-2026", "focus_areas": ["revenue", "growth", "efficiency"]}'
```

### Market Analysis
```bash
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/market-analysis \
  -H "Content-Type: application/json" \
  -d '{"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}'
```

### Budget Approval
```bash
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/budget-approval \
  -H "Content-Type: application/json" \
  -d '{"department": "Marketing", "amount": 500000, "justification": "Q2 brand campaign"}'
```

## Local Development

```bash
pip install -e ".[dev]"
func start
```

Set environment variables:
```
AOS_ENDPOINT=http://localhost:7071       # AOS Function App
REALM_ENDPOINT=http://localhost:7072     # RealmOfAgents (if separate)
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `aos-client-sdk` | SDK for AOS interaction |
| `azure-functions` | Azure Functions runtime |

**No AOS kernel, agent, or infrastructure dependencies.** BusinessInfinity knows nothing about agent internals.

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — AOS orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel

## License

Apache License 2.0 — see [LICENSE](LICENSE)
