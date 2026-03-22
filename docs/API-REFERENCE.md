# AOS Dispatcher — API Reference

**Last Updated**: 2026-03-22  
**Base URL**: `https://<your-function-app>.azurewebsites.net/api`  
**Authentication**: JWT bearer token validated by the AI Gateway (APIM)

All endpoints return `application/json`. Error responses follow the schema `{"error": "<message>"}`.

---

## Orchestrations

### `POST /api/orchestrations`

Submit a new multi-agent orchestration request.

**Request Body** (`OrchestrationRequest`):

```json
{
    "orchestration_id": "optional-client-id",
    "agent_ids": ["ceo", "cfo", "cmo"],
    "workflow": "collaborative",
    "task": {
        "type": "strategic_review",
        "data": {}
    },
    "config": {},
    "callback_url": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `orchestration_id` | string | No | Client-supplied ID. Auto-generated if omitted. |
| `agent_ids` | array[string] | Yes | IDs of agents to include in the orchestration. |
| `workflow` | string | No | Workflow variant: `"collaborative"` (default), `"sequential"`, `"hierarchical"`. |
| `task` | object | Yes | Task descriptor with `type` and `data`. |
| `config` | object | No | Override orchestration configuration. |
| `callback_url` | string | No | URL to call when orchestration completes (future). |

**Response** `202 Accepted`:

```json
{
    "orchestration_id": "orch-abc123",
    "status": "submitted"
}
```

---

### `GET /api/orchestrations/{orchestration_id}`

Poll the current status of a submitted orchestration.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `orchestration_id` | string | The orchestration ID returned by `POST /api/orchestrations`. |

**Response** `200 OK`:

```json
{
    "orchestration_id": "orch-abc123",
    "status": "running",
    "created_at": "2026-03-22T10:00:00Z",
    "updated_at": "2026-03-22T10:01:30Z"
}
```

**Status values**: `submitted`, `running`, `completed`, `failed`, `cancelled`

---

### `GET /api/orchestrations/{orchestration_id}/result`

Retrieve the final result of a completed orchestration.

**Response** `200 OK` (when `status == "completed"`):

```json
{
    "orchestration_id": "orch-abc123",
    "status": "completed",
    "result": { ... },
    "completed_at": "2026-03-22T10:05:00Z"
}
```

**Response** `409 Conflict` (when orchestration is not yet complete):

```json
{
    "error": "Orchestration not yet complete",
    "status": "running"
}
```

---

### `POST /api/orchestrations/{orchestration_id}/cancel`

Cancel a running orchestration.

**Response** `200 OK`:

```json
{
    "orchestration_id": "orch-abc123",
    "status": "cancelled"
}
```

---

## App Registration

### `POST /api/apps/register`

Register a client application with AOS. Provisions Service Bus queues, topics, and subscriptions for asynchronous communication.

**Request Body**:

```json
{
    "app_name": "business-infinity",
    "workflows": ["strategic-review", "market-analysis"],
    "app_id": "optional-azure-ad-app-id"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | string | Yes | Unique application name (kebab-case). |
| `workflows` | array[string] | Yes | Workflow names to register. |
| `app_id` | string | No | Azure AD application (client) ID for identity-based auth. |

**Response** `201 Created`:

```json
{
    "app_name": "business-infinity",
    "status": "registered",
    "service_bus": {
        "queue": "aos-business-infinity-requests",
        "topic": "aos-orchestration-results",
        "subscription": "business-infinity"
    }
}
```

---

### `GET /api/apps/{app_name}`

Get the registration status of a client application.

**Response** `200 OK`:

```json
{
    "app_name": "business-infinity",
    "status": "registered",
    "registered_at": "2026-03-22T09:00:00Z",
    "workflows": ["strategic-review", "market-analysis"]
}
```

**Response** `404 Not Found`:

```json
{
    "error": "App not registered"
}
```

---

### `DELETE /api/apps/{app_name}`

Deregister a client application and remove its Service Bus resources.

**Response** `200 OK`:

```json
{
    "app_name": "business-infinity",
    "status": "deregistered"
}
```

---

## Knowledge Base

### `POST /api/knowledge/documents`

Create a knowledge document in the AOS knowledge base.

**Request Body**:

```json
{
    "title": "Sustainability Policy 2026",
    "content": "Our commitment to sustainable operations...",
    "doc_type": "policy",
    "tags": ["sustainability", "governance"]
}
```

**Response** `201 Created`:

```json
{
    "id": "doc-abc123",
    "title": "Sustainability Policy 2026",
    "doc_type": "policy",
    "created_at": "2026-03-22T10:00:00Z"
}
```

---

### `GET /api/knowledge/documents`

Search knowledge documents.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | `""` | Full-text search query. |
| `doc_type` | string | — | Filter by document type. |
| `limit` | integer | `10` | Maximum number of results. |

**Response** `200 OK`:

```json
{
    "documents": [
        {
            "id": "doc-abc123",
            "title": "Sustainability Policy 2026",
            "content": "...",
            "score": 0.95
        }
    ]
}
```

---

### `GET /api/knowledge/documents/{document_id}`

Get a specific knowledge document by ID.

**Response** `200 OK`:

```json
{
    "id": "doc-abc123",
    "title": "Sustainability Policy 2026",
    "content": "Our commitment to sustainable operations...",
    "doc_type": "policy",
    "tags": ["sustainability", "governance"],
    "created_at": "2026-03-22T10:00:00Z",
    "updated_at": "2026-03-22T10:00:00Z"
}
```

---

### `POST /api/knowledge/documents/{document_id}`

Update an existing knowledge document.

**Request Body**:

```json
{
    "content": "Updated content...",
    "tags": ["sustainability", "governance", "2026"]
}
```

**Response** `200 OK`: Updated document object.

---

### `DELETE /api/knowledge/documents/{document_id}`

Delete a knowledge document.

**Response** `204 No Content`

---

## Risk Registry

### `POST /api/risks`

Register a new organisational risk.

**Request Body**:

```json
{
    "title": "Supply chain disruption",
    "description": "Key supplier may face delays due to geopolitical tensions",
    "category": "operational",
    "owner": "coo"
}
```

**Response** `201 Created`:

```json
{
    "id": "risk-abc123",
    "title": "Supply chain disruption",
    "category": "operational",
    "status": "open",
    "created_at": "2026-03-22T10:00:00Z"
}
```

---

### `GET /api/risks`

List risks with optional filters.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `open`, `mitigated`, `closed`. |
| `category` | string | Filter by category: `operational`, `financial`, `strategic`, `compliance`. |

**Response** `200 OK`:

```json
{
    "risks": [ ... ]
}
```

---

### `POST /api/risks/{risk_id}/assess`

Assess likelihood and impact for a registered risk.

**Request Body**:

```json
{
    "likelihood": 0.7,
    "impact": 0.9,
    "rationale": "High probability given current geopolitical tensions"
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `likelihood` | float | 0.0–1.0 | Probability of occurrence. |
| `impact` | float | 0.0–1.0 | Severity if it occurs. |

**Response** `200 OK`: Updated risk object.

---

### `POST /api/risks/{risk_id}/status`

Update the status of a risk.

**Request Body**:

```json
{
    "status": "mitigated",
    "reason": "Alternative supplier contract signed"
}
```

**Response** `200 OK`: Updated risk object.

---

### `POST /api/risks/{risk_id}/mitigate`

Add a mitigation plan to a risk.

**Request Body**:

```json
{
    "plan": "Onboard two additional suppliers by Q2",
    "owner": "coo",
    "due_date": "2026-06-30"
}
```

**Response** `200 OK`: Updated risk object.

---

## Audit Trail

### `POST /api/audit/decisions`

Log a decision in the immutable AOS audit trail.

**Request Body**:

```json
{
    "title": "Expand to EU",
    "rationale": "Strong market opportunity identified by CMO analysis",
    "agent_id": "ceo",
    "orchestration_id": "orch-abc123"
}
```

**Response** `201 Created`:

```json
{
    "id": "decision-abc123",
    "title": "Expand to EU",
    "agent_id": "ceo",
    "timestamp": "2026-03-22T10:00:00Z"
}
```

---

### `GET /api/audit/decisions`

Get decision history with optional filters.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `orchestration_id` | string | Filter by orchestration. |
| `agent_id` | string | Filter by agent. |

**Response** `200 OK`:

```json
{
    "decisions": [ ... ]
}
```

---

### `GET /api/audit/trail`

Get the complete audit trail.

**Response** `200 OK`:

```json
{
    "trail": [
        {
            "id": "decision-abc123",
            "title": "Expand to EU",
            "agent_id": "ceo",
            "timestamp": "2026-03-22T10:00:00Z"
        }
    ]
}
```

---

## Covenants

### `POST /api/covenants`

Create a formal business covenant.

**Request Body**:

```json
{
    "title": "Ethics Covenant",
    "description": "Binding commitment to ethical AI use",
    "parties": ["business-infinity", "aos"],
    "obligations": ["fair-use", "transparency"]
}
```

**Response** `201 Created`:

```json
{
    "id": "cov-abc123",
    "title": "Ethics Covenant",
    "status": "unsigned",
    "created_at": "2026-03-22T10:00:00Z"
}
```

---

### `GET /api/covenants`

List covenants.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by: `unsigned`, `signed`, `violated`, `expired`. |

**Response** `200 OK`:

```json
{
    "covenants": [ ... ]
}
```

---

### `GET /api/covenants/{covenant_id}/validate`

Validate a covenant (check compliance).

**Response** `200 OK`:

```json
{
    "id": "cov-abc123",
    "valid": true,
    "violations": []
}
```

---

### `POST /api/covenants/{covenant_id}/sign`

Sign a covenant.

**Request Body**:

```json
{
    "signatory": "ceo",
    "signature": "digital-signature-or-acknowledgement"
}
```

**Response** `200 OK`: Updated covenant object.

---

## Analytics & Metrics

### `POST /api/metrics`

Record a metric data point.

**Request Body**:

```json
{
    "name": "revenue_growth",
    "value": 12.5,
    "unit": "percent",
    "dimensions": {"region": "EU", "quarter": "Q1-2026"}
}
```

**Response** `201 Created`: Recorded metric object.

---

### `GET /api/metrics`

Retrieve a metric time series.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Metric name to retrieve. |

**Response** `200 OK`:

```json
{
    "name": "revenue_growth",
    "series": [
        {"timestamp": "2026-03-22T10:00:00Z", "value": 12.5}
    ]
}
```

---

### `POST /api/kpis`

Create a KPI definition.

**Request Body**:

```json
{
    "name": "revenue_growth",
    "target": 15.0,
    "unit": "percent",
    "owner": "cfo",
    "period": "Q1-2026"
}
```

**Response** `201 Created`: KPI object.

---

### `GET /api/kpis/dashboard`

Get the KPI dashboard with all active KPIs and their current values.

**Response** `200 OK`:

```json
{
    "kpis": [
        {
            "name": "revenue_growth",
            "target": 15.0,
            "current": 12.5,
            "status": "on_track"
        }
    ]
}
```

---

## MCP Server Integration

These endpoints proxy to the `aos-mcp-servers` function app. Configure `MCP_SERVERS_BASE_URL` to point at the deployed instance; when unset, stub responses are returned for local development.

### `GET /api/mcp/servers`

List available MCP servers.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `server_type` | string | Filter by type (e.g., `"erp"`, `"crm"`). |

**Response** `200 OK`:

```json
{
    "servers": [
        {"name": "erpnext", "type": "erp", "status": "online"},
        {"name": "salesforce", "type": "crm", "status": "online"}
    ]
}
```

---

### `POST /api/mcp/servers/{server}/tools/{tool}`

Invoke a tool on an MCP server.

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `server` | string | MCP server name (e.g., `"erpnext"`). |
| `tool` | string | Tool name to invoke (e.g., `"search"`). |

**Request Body**: Tool-specific parameters (passed through to MCP server).

**Response**: Tool-specific response (passed through from MCP server).

---

### `GET /api/mcp/servers/{server}/status`

Get the status of an MCP server.

**Response** `200 OK`:

```json
{
    "server": "erpnext",
    "status": "online",
    "tools": ["search", "create", "update"],
    "last_health_check": "2026-03-22T10:00:00Z"
}
```

---

## Agent Catalog

These endpoints proxy to the `aos-realm-of-agents` function app. Configure `REALM_OF_AGENTS_BASE_URL`; stub responses are returned when unset.

### `GET /api/agents`

List agents from the RealmOfAgents catalog.

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_type` | string | Filter by agent type (e.g., `"CEOAgent"`, `"CMOAgent"`). |

**Response** `200 OK`:

```json
{
    "agents": [
        {
            "agent_id": "ceo",
            "name": "CEO Agent",
            "agent_type": "CEOAgent",
            "capabilities": ["strategic_planning", "decision_making"]
        }
    ]
}
```

---

### `GET /api/agents/{agent_id}`

Get a specific agent descriptor.

**Response** `200 OK`:

```json
{
    "agent_id": "ceo",
    "name": "CEO Agent",
    "agent_type": "CEOAgent",
    "capabilities": ["strategic_planning", "decision_making"],
    "model": "gpt-4o",
    "status": "online"
}
```

---

### `POST /api/agents/register`

Register a `PurposeDrivenAgent` with the Foundry Agent Service.

**Request Body**:

```json
{
    "agent_id": "ceo",
    "purpose": "Strategic leadership and executive decision-making",
    "name": "CEO Agent",
    "adapter_name": "leadership",
    "capabilities": ["strategic_planning", "decision_making"],
    "model": "gpt-4o"
}
```

**Response** `201 Created`:

```json
{
    "agent_id": "ceo",
    "foundry_agent_id": "foundry-abc123",
    "status": "registered"
}
```

---

## Agent Interaction

### `POST /api/agents/{agent_id}/ask`

Send a synchronous question to an agent and receive its response.

**Request Body**:

```json
{
    "message": "What is the Q2 strategic direction?",
    "context": {"quarter": "Q2-2026"}
}
```

**Response** `200 OK`:

```json
{
    "agent_id": "ceo",
    "response": "For Q2 2026, we should focus on...",
    "confidence": 0.95
}
```

---

### `POST /api/agents/{agent_id}/send`

Fire-and-forget message to an agent (no response returned).

**Response** `202 Accepted`

---

### `POST /api/agents/{agent_id}/message`

Send a message to an agent via the Foundry message bridge.

**Request Body**:

```json
{
    "message": "What is the strategic direction?",
    "orchestration_id": "orch-abc123",
    "direction": "foundry_to_agent"
}
```

**Response** `200 OK`:

```json
{
    "message_id": "msg-abc123",
    "status": "delivered"
}
```

---

## Network Discovery

### `POST /api/network/discover`

Discover peer AOS applications.

**Response** `200 OK`:

```json
{
    "peers": [
        {"app_name": "business-infinity", "status": "online"}
    ]
}
```

---

### `POST /api/network/{network_id}/join`

Join a network.

**Response** `200 OK`:

```json
{
    "network_id": "aos-primary",
    "status": "joined"
}
```

---

### `GET /api/network`

List available networks.

**Response** `200 OK`:

```json
{
    "networks": [
        {"network_id": "aos-primary", "members": 3}
    ]
}
```

---

## Health

### `GET /api/health`

Check the health of the AOS dispatcher.

**Response** `200 OK`:

```json
{
    "status": "healthy",
    "version": "4.0.0",
    "timestamp": "2026-03-22T10:00:00Z",
    "components": {
        "dispatcher": "healthy",
        "service_bus": "healthy"
    }
}
```

**Response** `503 Service Unavailable` (when unhealthy):

```json
{
    "status": "unhealthy",
    "components": {
        "dispatcher": "healthy",
        "service_bus": "degraded"
    }
}
```

---

## Service Bus Trigger

### Queue: `aos-orchestration-requests`

Processes orchestration requests received asynchronously via Service Bus. Enables scale-to-zero: the function sleeps until a message arrives, then processes it using the same logic as `POST /api/orchestrations`.

**Message schema**:

```json
{
    "app_name": "business-infinity",
    "payload": {
        "agent_ids": ["ceo", "cfo"],
        "task": { ... }
    }
}
```

---

## Error Responses

All endpoints return structured errors:

| HTTP Status | Meaning |
|-------------|---------|
| `400 Bad Request` | Invalid JSON body or missing required field. |
| `404 Not Found` | Resource not found (orchestration, document, risk, etc.). |
| `409 Conflict` | Operation not valid for current resource state. |
| `500 Internal Server Error` | Unexpected error in the dispatcher or Foundry service. |
| `503 Service Unavailable` | Dependency unavailable (Foundry, Service Bus). |

**Error body**:

```json
{
    "error": "Human-readable error message"
}
```

---

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables & authentication setup
- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment guide
