# AOS Configuration Reference

**Last Updated**: 2026-03-22

## Overview

The AOS Dispatcher function app is configured via Azure App Configuration or environment variables. This document lists all supported settings for `function_app.py` and the `aos-dispatcher` library.

---

## Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `SERVICE_BUS_CONNECTION` | Azure Service Bus connection string (or managed identity connection name) | `Endpoint=sb://aos-prod.servicebus.windows.net/;SharedAccessKeyName=...` |
| `AZURE_AI_PROJECT_ID` | Azure AI Foundry project resource ID | `/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<project>` |

---

## Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVERS_BASE_URL` | *(unset)* | Base URL of the `aos-mcp-servers` function app. When unset, MCP endpoints return stub responses. |
| `REALM_OF_AGENTS_BASE_URL` | *(unset)* | Base URL of the `aos-realm-of-agents` function app. When unset, agent catalog endpoints return stub responses. |
| `AZURE_CLIENT_ID` | *(unset)* | User-Assigned Managed Identity client ID for workload identity auth (required in production; optional in local dev with `az login`). |
| `AZURE_TENANT_ID` | *(auto)* | Azure tenant ID (auto-detected when using Azure CLI; required in CI/CD). |
| `AZURE_SUBSCRIPTION_ID` | *(auto)* | Azure subscription ID (auto-detected when using Azure CLI; required in CI/CD). |
| `AOS_LOG_LEVEL` | `Information` | Log level for the dispatcher: `Debug`, `Information`, `Warning`, `Error`. |

---

## host.json

The `host.json` file configures the Azure Functions v4 runtime:

```json
{
    "version": "2.0",
    "logging": {
        "applicationInsights": {
            "samplingSettings": {
                "isEnabled": true,
                "excludedTypes": "Request"
            }
        },
        "logLevel": {
            "default": "Information",
            "Host.Results": "Error",
            "Function": "Information",
            "Host.Aggregator": "Trace"
        }
    },
    "functionTimeout": "00:10:00",
    "extensions": {
        "serviceBus": {
            "prefetchCount": 0,
            "autoCompleteMessages": true
        },
        "http": {
            "routePrefix": "api",
            "maxConcurrentRequests": 100,
            "maxOutstandingRequests": 200
        }
    },
    "retry": {
        "strategy": "exponentialBackoff",
        "maxRetryCount": 3,
        "minimumInterval": "00:00:02",
        "maximumInterval": "00:00:30"
    }
}
```

| Setting | Value | Description |
|---------|-------|-------------|
| `functionTimeout` | `00:10:00` | Max execution time per function invocation (10 minutes). |
| `routePrefix` | `api` | All HTTP routes are prefixed with `/api/`. |
| `maxConcurrentRequests` | `100` | Maximum concurrent HTTP requests per instance. |
| `maxOutstandingRequests` | `200` | Queue depth before returning `429 Too Many Requests`. |
| `autoCompleteMessages` | `true` | Service Bus messages are auto-completed on successful processing. |
| `maxRetryCount` | `3` | Retry count for failed Service Bus message processing. |

---

## Azure AI Gateway (APIM) Configuration

The AI Gateway validates JWT tokens and enforces rate limits. Configure the following APIM policies:

| Policy | Description |
|--------|-------------|
| `validate-jwt` | Validates bearer tokens issued by Entra ID for the configured tenant. |
| `rate-limit-by-key` | Per-client rate limiting (default: 100 req/min per subscription key). |
| `cors` | CORS policy for browser-based clients. |

The gateway rewrites `Authorization` headers before forwarding requests to the dispatcher.

---

## Azure AI Foundry Settings

The `aos-dispatcher` library uses `azure-ai-projects` to communicate with the Foundry Agent Service. Connection is established via Managed Identity (production) or Azure CLI (local development):

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    project_endpoint=os.environ["AZURE_AI_PROJECT_ID"],
    credential=DefaultAzureCredential(),
)
```

`DefaultAzureCredential` automatically uses:
1. Managed Identity (when running in Azure Functions)
2. Azure CLI credentials (when running locally with `az login`)
3. Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)

---

## Service Bus Configuration

AOS uses two Service Bus resources:

### Queues

| Queue | Direction | Description |
|-------|-----------|-------------|
| `aos-orchestration-requests` | Inbound | Client apps send orchestration requests here. |
| `aos-<app-name>-requests` | Per-app inbound | Per-app queue provisioned at registration. |

### Topics & Subscriptions

| Topic | Subscription | Description |
|-------|-------------|-------------|
| `aos-orchestration-results` | `<app-name>` | Per-app subscription for orchestration results. |

---

## Local Development `.env` File

For local development, create a `.env` file at the root of the repository (excluded from git via `.gitignore`):

```env
SERVICE_BUS_CONNECTION=Endpoint=sb://localhost:5671/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=...
AZURE_AI_PROJECT_ID=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/aos-dev/providers/Microsoft.MachineLearningServices/workspaces/aos-dev-project
MCP_SERVERS_BASE_URL=
REALM_OF_AGENTS_BASE_URL=
AOS_LOG_LEVEL=Debug
```

When `MCP_SERVERS_BASE_URL` and `REALM_OF_AGENTS_BASE_URL` are empty, the dispatcher uses stubs — ideal for working on the orchestration endpoints without deploying all services.

---

## References

- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment guide with provisioning steps
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [API-REFERENCE.md](API-REFERENCE.md) — API endpoint documentation
