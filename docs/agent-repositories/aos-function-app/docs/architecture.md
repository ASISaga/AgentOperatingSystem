# aos-function-app Architecture

## Overview

The AOS Function App is the **orchestration API** for the Agent Operating System.
Client applications submit orchestration requests (selecting agents from the
RealmOfAgents catalog) and retrieve results through HTTP endpoints exposed by
this function app.

## Component Architecture

```
┌─────────────────────────────────────┐
│   Client Applications               │
│   (BusinessInfinity, etc.)          │
│   pip install aos-client-sdk        │
└─────────────────────────────────────┘
              │
         HTTPS (aos-client-sdk)
              │
              ▼
┌─────────────────────────────────────┐  ┌─────────────────────────────────┐
│   AOS Function App                  │  │   RealmOfAgents                 │
│   POST /api/orchestrations          │  │   GET /api/realm/agents         │
│   GET  /api/orchestrations/{id}     │  │   Agent catalog (CEO, CFO, ...) │
│   GET  /api/orchestrations/{id}/    │  │                                 │
│         result                      │  │                                 │
│   POST /api/orchestrations/{id}/    │  │                                 │
│         cancel                      │  │                                 │
│   GET  /api/health                  │  │                                 │
└─────────────────────────────────────┘  └─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   aos-kernel                        │
│   Orchestration engine, Messaging,  │
│   Storage, Auth, MCP, Monitoring    │
└─────────────────────────────────────┘
```

## Key Principle

> AOS provides agent orchestrations as an infrastructure service.
> Client apps contain only business logic — AOS handles the rest.

## HTTP Endpoints

### Orchestration API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/orchestrations` | Submit an orchestration request |
| GET | `/api/orchestrations/{id}` | Poll orchestration status |
| GET | `/api/orchestrations/{id}/result` | Retrieve completed result |
| POST | `/api/orchestrations/{id}/cancel` | Cancel a running orchestration |
| GET | `/api/health` | Health check |

### Orchestration Request Body

```json
{
    "orchestration_id": "optional-client-id",
    "agent_ids": ["ceo", "cfo", "cmo"],
    "workflow": "collaborative",
    "task": {"type": "strategic_review", "data": {"quarter": "Q1-2026"}},
    "config": {},
    "callback_url": null
}
```

## Configuration

| Setting | Description |
|---------|-------------|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection |
| `AZURE_SERVICEBUS_CONNECTION_STRING` | Service Bus connection |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights telemetry |
| `APP_ENVIRONMENT` | Environment name (dev/staging/prod) |

## Related Repositories

- [aos-client-sdk](https://github.com/ASISaga/aos-client-sdk) — Client SDK
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — Agent catalog
- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [business-infinity](https://github.com/ASISaga/business-infinity) — Example client app
- [aos-deployment](https://github.com/ASISaga/aos-deployment) — Deployment
