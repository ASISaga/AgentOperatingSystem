# aos-function-app

**Orchestration API** for the Agent Operating System. Exposes AOS as an infrastructure service — client applications submit orchestration requests, monitor progress, and retrieve results through HTTP endpoints.

## Overview

This function app is the AOS orchestration API, providing:

- **Orchestration Submission** — `POST /api/orchestrations` to run agent workflows
- **Status Monitoring** — `GET /api/orchestrations/{id}` to poll progress
- **Result Retrieval** — `GET /api/orchestrations/{id}/result` for completed results
- **Cancellation** — `POST /api/orchestrations/{id}/cancel` to stop running orchestrations
- **Health Check** — `GET /api/health`

## How Client Apps Use It

```python
from aos_client import AOSClient

async with AOSClient(endpoint="https://my-aos.azurewebsites.net") as client:
    result = await client.run_orchestration(
        agent_ids=["ceo", "cfo", "cmo"],
        task={"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
    )
    print(result.summary)
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

Deploy via the [aos-deployment](https://github.com/ASISaga/aos-deployment) repository's orchestrator, or directly:

```bash
func azure functionapp publish <app-name>
```

## Dependencies

- `aos-kernel[azure]>=3.0.0` — AOS kernel with Azure backends
- `aos-intelligence[foundry]>=1.0.0` — (Optional) ML-backed agents
- `azure-functions>=1.21.0`

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client app
- [aos-deployment](https://github.com/ASISaga/aos-deployment) — Infrastructure deployment

## License

Apache License 2.0 — see [LICENSE](LICENSE)
