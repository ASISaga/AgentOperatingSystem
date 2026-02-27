# aos-client-sdk

Application framework and Python SDK for building **Azure Functions apps** powered by the **Agent Operating System**. Client applications use this SDK to define business workflows, communicate with AOS via HTTP and Azure Service Bus, handle authentication, register with AOS for infrastructure provisioning, and deploy to Azure — all while staying focused on business logic.

## Overview

The AOS Client SDK provides:

- **`AOSApp`** — Azure Functions application framework with `@workflow` decorators.  Generates HTTP triggers, Service Bus triggers, health endpoints, and auth middleware automatically.
- **`AOSClient`** — Async HTTP/Service Bus client for agent discovery and orchestration.
- **`AOSAuth`** — Azure IAM authentication and role-based access control.
- **`AOSServiceBus`** — Bidirectional async communication via Azure Service Bus (scale-to-zero).
- **`AOSRegistration`** — Client app registration with AOS (triggers infrastructure provisioning).
- **`AOSDeployer`** — Code deployment to Azure Functions.

## Quick Start

```bash
pip install aos-client-sdk[azure]
```

### Define Workflows (business logic only)

```python
# workflows.py
from aos_client import AOSApp, WorkflowRequest

app = AOSApp(name="my-app")

@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    agents = await request.client.list_agents()
    c_suite = [a.agent_id for a in agents if a.agent_type in ("LeadershipAgent", "CMOAgent")]
    return await request.client.run_orchestration(
        agent_ids=c_suite,
        task={"type": "strategic_review", "data": request.body},
    )
```

### Azure Functions entry point (zero boilerplate)

```python
# function_app.py
from my_app.workflows import app

functions = app.get_functions()
```

That's it.  The SDK creates all HTTP triggers, Service Bus triggers, health
endpoints, and authentication middleware.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Client Application (e.g. BusinessInfinity)         │
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
│  │ POST /api/        │  │ GET /api/realm/agents   │  │
│  │  orchestrations   │  │ Agent catalog           │  │
│  │ Service Bus       │  └─────────────────────────┘  │
│  │  trigger          │                               │
│  └────────┬──────────┘                               │
│  ┌────────▼──────────────────────────────────────┐   │
│  │ aos-kernel                                     │  │
│  │ Orchestration · Messaging · Storage · Auth     │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## API Reference

### `AOSApp` — Application Framework

| Method | Description |
|--------|-------------|
| `@app.workflow(name)` | Register a business workflow (creates HTTP + Service Bus triggers) |
| `app.get_functions()` | Build Azure Functions app with all registered triggers |
| `app.get_workflow_names()` | List registered workflow names |

### `AOSClient` — AOS Communication

| Method | Description |
|--------|-------------|
| `list_agents(agent_type=)` | List agents from the RealmOfAgents catalog |
| `get_agent(agent_id)` | Get a single agent descriptor |
| `submit_orchestration(request, via_service_bus=)` | Submit via HTTP or Service Bus |
| `get_orchestration_status(id)` | Poll orchestration status |
| `get_orchestration_result(id)` | Get final orchestration result |
| `cancel_orchestration(id)` | Cancel a running orchestration |
| `run_orchestration(...)` | Convenience: submit + poll + return result |
| `health_check()` | Check AOS health |

### `AOSAuth` — Authentication & Access Control

| Method | Description |
|--------|-------------|
| `validate_token(token)` | Validate Azure AD bearer token |
| `require_role(claims, role)` | Assert token has a specific role |
| `require_any_allowed_role(claims)` | Assert token has any allowed role |
| `get_credential()` | Get Azure credential for outbound calls |

### `AOSServiceBus` — Async Communication

| Method | Description |
|--------|-------------|
| `send_orchestration_request(request)` | Send orchestration via Service Bus |
| `parse_orchestration_result(body)` | Parse result from Service Bus message |
| `parse_orchestration_status(body)` | Parse status from Service Bus message |

### `AOSRegistration` — App Registration & Provisioning

| Method | Description |
|--------|-------------|
| `register_app(name, workflows)` | Register with AOS (provisions infrastructure) |
| `get_app_status(name)` | Check registration/provisioning status |
| `deregister_app(name)` | Remove registration |

### `AOSDeployer` — Deployment

| Method | Description |
|--------|-------------|
| `deploy(slot=)` | Deploy to Azure Functions |
| `ensure_host_json()` | Create host.json if missing |
| `ensure_local_settings(...)` | Create local.settings.json if missing |

### Models

| Model | Description |
|-------|-------------|
| `WorkflowRequest` | Request passed to workflow handlers |
| `AgentDescriptor` | Agent metadata from the RealmOfAgents catalog |
| `OrchestrationRequest` | Request to run an agent orchestration |
| `OrchestrationStatus` | Current status of an orchestration |
| `OrchestrationResult` | Final result with per-agent outputs and summary |
| `AppRegistration` | Client app registration record |
| `DeploymentResult` | Deployment operation result |
| `TokenClaims` | Parsed Azure AD token claims |

## Authentication

The SDK integrates Azure IAM for authentication and access control:

```python
from aos_client import AOSApp, AOSAuth

auth = AOSAuth(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    allowed_roles=["Workflows.Execute"],
)

app = AOSApp(name="my-app", auth=auth)
```

For local development, omit the auth configuration for anonymous access.

## Service Bus Communication

Both AOS and client apps scale to zero and wake on Service Bus triggers:

```python
from aos_client import AOSClient

async with AOSClient(
    endpoint="https://my-aos.azurewebsites.net",
    service_bus_connection_string="Endpoint=sb://...",
    app_name="my-app",
) as client:
    # Submit via Service Bus (async, scale-to-zero friendly)
    status = await client.submit_orchestration(request, via_service_bus=True)
```

## App Registration

Register your app with AOS to provision infrastructure automatically:

```python
from aos_client import AOSRegistration

async with AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net") as reg:
    info = await reg.register_app(
        app_name="my-app",
        workflows=["strategic-review", "market-analysis"],
    )
    print(info.service_bus_connection_string)
```

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel (orchestration, messaging, storage)
- [aos-function-app](https://github.com/ASISaga/aos-function-app) — AOS orchestration API
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client application
- [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) — Agent base class

## License

Apache License 2.0 — see [LICENSE](LICENSE)
