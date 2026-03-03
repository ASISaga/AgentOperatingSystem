# aos-dispatcher

**Central Dispatcher** for the Agent Operating System — the component that receives all inbound requests and dispatches them to the AOS kernel, analogous to the dispatcher in a traditional operating system.

Exposes AOS as an infrastructure service via Azure Functions: client applications submit orchestration requests, monitor progress, and stop perpetual orchestrations through HTTP and Service Bus endpoints.

## Overview

The dispatcher is the AOS entry point for all external requests, providing:

- **Orchestration Submission** — `POST /api/orchestrations` to start perpetual agent orchestrations
- **Status Monitoring** — `GET /api/orchestrations/{id}` to poll progress
- **Stop Orchestration** — `POST /api/orchestrations/{id}/stop` to stop perpetual orchestrations
- **Cancellation** — `POST /api/orchestrations/{id}/cancel` to cancel an orchestration
- **Health Check** — `GET /api/health`

## How Client Apps Use It

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    status = await client.start_orchestration(
        agent_ids=["ceo", "cfo", "cmo"],
        purpose="strategic_review",
        context={"quarter": "Q1-2026"},
    )
    print(status.orchestration_id)  # perpetual — no final result
```

## Prerequisites

- Azure Functions Core Tools v4
- Python 3.10+
- Azure subscription with Service Bus namespace

## Local Development

```bash
pip install -e ".[dev]"
func start
```

## Deployment

Deploy via the [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) repository's orchestrator, or directly:

```bash
func azure functionapp publish <app-name>
```

## Dependencies

- `aos-kernel[azure]>=4.0.0` — AOS kernel with Azure backends (includes `aos-intelligence`)
- `azure-functions>=1.21.0`

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-intelligence](https://github.com/ASISaga/aos-intelligence) — ML / intelligence layer
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client app
- [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) — Infrastructure deployment

## License

Apache License 2.0 — see [LICENSE](LICENSE)
