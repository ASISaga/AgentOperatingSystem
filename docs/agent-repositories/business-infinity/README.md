# BusinessInfinity

A lean Azure Functions application that demonstrates using the **Agent Operating System** as an infrastructure service. BusinessInfinity contains only business logic — all Azure Functions scaffolding, Service Bus communication, authentication, and deployment are handled by the `aos-client-sdk`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  BusinessInfinity (this app)                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  workflows.py       @app.workflow decorators  │  │
│  │  function_app.py    app.get_functions()       │  │
│  │    └─ aos-client-sdk handles everything else  │  │
│  └───────────────────────────────────────────────┘  │
│  Zero Azure Functions boilerplate.                  │
│  Zero agent code. Zero infrastructure code.         │
└──────────────┬───────────────────┬──────────────────┘
               │ HTTPS             │ Azure Service Bus
               ▼                   ▼
┌─────────────────────────────────────────────────────┐
│  Agent Operating System (infrastructure)            │
│  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ aos-function-app  │  │ aos-realm-of-agents     │  │
│  │ Orchestration API │  │ Agent catalog:          │  │
│  │ + Service Bus     │  │  CEO · CFO · CMO        │  │
│  │   triggers        │  │  COO · CTO              │  │
│  └──────────────────┘  └─────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │ aos-kernel                                      │ │
│  │ Orchestration · Messaging · Storage · Auth      │ │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Key Principle

> **BusinessInfinity focuses only on business logic.  The SDK handles the rest.**

| Concern | Owner |
|---------|-------|
| Business workflows (strategic review, market analysis, budget approval) | BusinessInfinity |
| Azure Functions scaffolding, HTTP/Service Bus triggers, auth | aos-client-sdk |
| Agent lifecycle, perpetual orchestration, messaging, storage, monitoring | AOS |
| Agent catalog (C-suite agents, capabilities, LoRA adapters) | RealmOfAgents |

## Workflows

### Define workflows with decorators

```python
# workflows.py
from aos_client import AOSApp, WorkflowRequest

app = AOSApp(name="business-infinity")

@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    agents = await request.client.list_agents()
    c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent")]
    return await request.client.start_orchestration(
        agent_ids=c_suite,
        purpose="strategic_review",
        context=request.body,
    )
```

### Azure Functions entry point (zero boilerplate)

```python
# function_app.py
from business_infinity.workflows import app
functions = app.get_functions()
```

### Invoke via HTTP

```bash
# Strategic Review — returns orchestration_id + status (perpetual)
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/strategic-review \
  -H "Content-Type: application/json" \
  -d '{"quarter": "Q1-2026", "focus_areas": ["revenue", "growth", "efficiency"]}'
# → {"orchestration_id": "...", "status": "ACTIVE"}

# Market Analysis
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/market-analysis \
  -H "Content-Type: application/json" \
  -d '{"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}'
# → {"orchestration_id": "...", "status": "ACTIVE"}

# Budget Approval
curl -X POST https://business-infinity.azurewebsites.net/api/workflows/budget-approval \
  -H "Content-Type: application/json" \
  -d '{"department": "Marketing", "amount": 500000, "justification": "Q2 brand campaign"}'
# → {"orchestration_id": "...", "status": "ACTIVE"}
```

## Registration with AOS

Register this app with AOS to provision Service Bus infrastructure:

```python
from aos_client import AOSRegistration

async with AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net") as reg:
    info = await reg.register_app(
        app_name="business-infinity",
        workflows=["strategic-review", "market-analysis", "budget-approval"],
    )
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
SERVICE_BUS_CONNECTION=                  # Service Bus (optional for local dev)
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `aos-client-sdk[azure]` | SDK + Azure Functions + Service Bus + Auth |

**No AOS kernel, agent, or infrastructure dependencies.** BusinessInfinity knows nothing about agent internals.

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK & App Framework
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — AOS orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel

## License

Apache License 2.0 — see [LICENSE](LICENSE)
