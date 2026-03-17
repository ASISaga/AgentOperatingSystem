# aos-function-app API Reference

## HTTP Endpoints

### Health Check

```
GET /api/health
```

**Response** (`200 OK`):

```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "3.0.0"
}
```

**Response** (`503 Service Unavailable`):

```json
{
    "status": "unhealthy",
    "error": "description of issue"
}
```

## Service Bus Functions

### agent_request_handler

**Trigger**: Service Bus queue `agent-requests`

Processes incoming agent requests. The message body must be valid JSON.

**Message Schema**:

```json
{
    "type": "agent_request",
    "agent_id": "string",
    "action": "string",
    "data": {}
}
```

## Configuration

### host.json

```json
{
    "version": "2.0",
    "extensions": {
        "serviceBus": {
            "prefetchCount": 100,
            "maxConcurrentCalls": 16
        }
    }
}
```

### Application Settings

| Setting | Required | Description |
|---------|----------|-------------|
| `AZURE_STORAGE_CONNECTION_STRING` | Yes | Azure Storage connection string |
| `AZURE_SERVICEBUS_CONNECTION_STRING` | Yes | Service Bus connection string |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | No | App Insights for telemetry |
| `APP_ENVIRONMENT` | No | Environment name (default: production) |

## Global Initialization

The `initialize_aos()` function creates a singleton `AgentOperatingSystem`
instance that is reused across all function invocations:

```python
async def initialize_aos() -> AgentOperatingSystem:
    """Initialize or return existing AOS instance."""
    global aos_instance
    if aos_instance:
        return aos_instance
    aos_instance = AgentOperatingSystem(config)
    await aos_instance.initialize()
    return aos_instance
```
