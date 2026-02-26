# aos-function-app Architecture

## Overview

The AOS Function App is the primary cloud entry point for the Agent Operating
System.  It exposes AOS capabilities as Azure Functions triggered by Service Bus
messages and HTTP requests.

## Component Architecture

```
┌─────────────────────────────────────┐
│   Client Applications               │
│   (BusinessInfinity, MCP, etc.)     │
└─────────────────────────────────────┘
              │
        Azure Service Bus
              │
              ▼
┌─────────────────────────────────────┐
│   AOS Function App                  │
│   • Service Bus triggers            │
│   • HTTP endpoints                  │
│   • Timer triggers                  │
│   • Global AOS instance             │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Azure AI Agents Runtime           │
│   (Foundry Agent Service)           │
│   • Stateful agent threads          │
│   • Managed lifecycle               │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   aos-kernel                        │
│   • Storage, MCP, Messaging, Auth   │
└─────────────────────────────────────┘
```

## Key Components

### Service Bus Triggers

Service Bus triggers are the primary interface for event-driven agent activation.
Messages arrive on designated queues, and the function app routes them to the
appropriate AOS handler.

### HTTP Endpoints

HTTP endpoints provide:

- **Health check** — `GET /api/health`
- **Agent status** — `GET /api/agents/{id}/status`
- **Management** — Administrative endpoints for agent lifecycle

### Global State

The function app maintains a single `AgentOperatingSystem` instance that is
initialized on first invocation and reused across all subsequent calls. This
avoids cold-start overhead for repeated invocations.

## Configuration

| Setting | Description |
|---------|-------------|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection |
| `AZURE_SERVICEBUS_CONNECTION_STRING` | Service Bus connection |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights telemetry |
| `APP_ENVIRONMENT` | Environment name (dev/staging/prod) |

## Related Repositories

- [aos-kernel](https://github.com/ASISaga/aos-kernel) — OS kernel
- [aos-deployment](https://github.com/ASISaga/aos-deployment) — Deployment
- [aos-realm-of-agents](https://github.com/ASISaga/aos-realm-of-agents) — RealmOfAgents
- [aos-mcp-servers](https://github.com/ASISaga/aos-mcp-servers) — MCPServers
