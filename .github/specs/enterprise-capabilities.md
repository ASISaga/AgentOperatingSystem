# Enterprise Capabilities Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

BusinessInfinity exposes a set of enterprise capability workflows that integrate directly with AOS services for knowledge management, risk governance, decision audit trails, business covenants, agent interaction, and MCP-powered tool access. These capabilities are thin delegates — each workflow calls a single SDK method and returns the result as JSON.

## Scope

- Knowledge management (`knowledge-search`)
- Risk governance (`risk-register`, `risk-assess`)
- Decision audit trail (`log-decision`)
- Business covenants (`covenant-create`)
- Direct agent interaction (`ask-agent`)
- MCP server integration (`mcp-orchestration`, `erp-search`)

## Design Principle

Enterprise capability workflows are **pure delegates**: they extract parameters from `request.body`, call the corresponding `request.client` method, and return `model.model_dump(mode="json")`. They contain no business logic beyond parameter extraction and validation.

## Knowledge Management

### `knowledge-search`

Searches the AOS knowledge base using a text query.

| Attribute | Value |
|-----------|-------|
| Workflow name | `knowledge-search` |
| SDK call | `request.client.search_documents(query, doc_type, limit)` |
| Return | `{"documents": [<DocumentModel>]}` |

**Request body**:

```json
{"query": "sustainability policy", "doc_type": "policy", "limit": 5}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | `""` | Full-text search query |
| `doc_type` | string | `null` | Optional filter by document type |
| `limit` | integer | `10` | Maximum number of results to return |

**Response**:

```json
{
    "documents": [
        {"id": "doc-abc", "title": "Sustainability Policy 2026", "content": "..."}
    ]
}
```

## Risk Governance

### `risk-register`

Registers a new organisational risk in the AOS risk registry.

| Attribute | Value |
|-----------|-------|
| Workflow name | `risk-register` |
| SDK call | `request.client.register_risk(request.body)` |
| Return | `<RiskModel>.model_dump(mode="json")` |

**Request body**:

```json
{
    "title": "Supply chain disruption",
    "description": "Key supplier may face delays due to geopolitical tensions",
    "category": "operational",
    "owner": "coo"
}
```

### `risk-assess`

Updates likelihood and impact scores for an existing registered risk.

| Attribute | Value |
|-----------|-------|
| Workflow name | `risk-assess` |
| SDK call | `request.client.assess_risk(risk_id, likelihood, impact)` |
| Return | `<RiskModel>.model_dump(mode="json")` |

**Request body**:

```json
{"risk_id": "risk-abc", "likelihood": 0.7, "impact": 0.9}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `risk_id` | string | — | ID of the risk to update |
| `likelihood` | float | 0.0–1.0 | Probability of occurrence |
| `impact` | float | 0.0–1.0 | Severity of impact if it occurs |

## Decision Audit Trail

### `log-decision`

Records a boardroom decision in the immutable AOS audit trail.

| Attribute | Value |
|-----------|-------|
| Workflow name | `log-decision` |
| SDK call | `request.client.log_decision(request.body)` |
| Return | `<DecisionRecord>.model_dump(mode="json")` |

**Request body**:

```json
{
    "title": "Expand to EU",
    "rationale": "Strong market opportunity identified by CMO analysis",
    "agent_id": "ceo"
}
```

## Business Covenants

### `covenant-create`

Creates a formal business covenant between designated parties. Covenants express binding commitments (ethical standards, service agreements, governance obligations) tracked by AOS.

| Attribute | Value |
|-----------|-------|
| Workflow name | `covenant-create` |
| SDK call | `request.client.create_covenant(request.body)` |
| Return | `<CovenantModel>.model_dump(mode="json")` |

**Request body**:

```json
{"title": "Ethics Covenant", "parties": ["business-infinity"]}
```

## Agent Interaction

### `ask-agent`

Sends a synchronous question to a single named agent and returns its response.

| Attribute | Value |
|-----------|-------|
| Workflow name | `ask-agent` |
| SDK call | `request.client.ask_agent(agent_id, message, context)` |
| Return | `<AgentResponse>.model_dump(mode="json")` |

**Request body**:

```json
{
    "agent_id": "ceo",
    "message": "What is the Q2 strategy?",
    "context": {"quarter": "Q2-2026"}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | ✓ | ID of the agent to query |
| `message` | string | ✓ | Natural-language question |
| `context` | object | — | Optional additional context for the agent |

## MCP Integration

Model Context Protocol (MCP) allows agents in an orchestration to use pre-registered external tools (ERP, CRM, analytics) during their reasoning.

### `mcp-orchestration`

Starts a C-suite orchestration where each agent is assigned specific pre-registered MCP servers. BusinessInfinity declares **only the server name and client-managed secrets** — AOS handles transport, URLs, protocol, and gateway configuration.

| Attribute | Value |
|-----------|-------|
| Workflow name | `mcp-orchestration` |
| SDK call | `request.client.submit_orchestration(OrchestrationRequest)` |
| Agents | CEO (with `erp` MCP server) + CMO (with `crm` and `analytics` MCP servers) |
| Return | `{"orchestration_id", "status", "mcp_servers_configured"}` |

**Request body**:

```json
{
    "purpose": "Drive strategic growth with real-time data",
    "erp_api_key": "secret-erp-key",
    "crm_token": "secret-crm-token"
}
```

**MCP server assignment pattern**:

```python
mcp_servers: Dict[str, List[MCPServerConfig]] = {
    "ceo": [MCPServerConfig(server_name="erp", secrets={"api_key": erp_api_key})],
    "cmo": [
        MCPServerConfig(server_name="crm", secrets={"token": crm_token}),
        MCPServerConfig(server_name="analytics"),
    ],
}
```

**Response**:

```json
{
    "orchestration_id": "orch-xyz",
    "status": "running",
    "mcp_servers_configured": {"ceo": ["erp"], "cmo": ["crm", "analytics"]}
}
```

### `erp-search` (MCP Tool)

Registered as an MCP tool exposed by this application. Delegates ERP search queries to the `erpnext` MCP server via AOS.

```python
@app.mcp_tool("erp-search")
async def erp_search(request) -> Any:
    return await request.client.call_mcp_tool("erpnext", "search", request.body)
```

## Response Conventions

| Workflow type | Response format |
|---------------|----------------|
| Single-entity workflows (`risk-register`, `log-decision`, etc.) | `<Model>.model_dump(mode="json")` |
| Collection workflows (`knowledge-search`) | `{"documents": [...]}` |
| Orchestration workflows (`mcp-orchestration`) | `{"orchestration_id", "status", ...}` |
| MCP tools | Pass-through from `call_mcp_tool` |

## Validation

```bash
# Run all enterprise capability tests
pytest tests/test_workflows.py -v

# Run MCP-specific tests
pytest tests/test_workflows.py -v -k "mcp"

# Lint
pylint src/business_infinity/workflows.py
```

## References

→ **Repository spec**: `.github/specs/repository.md`
→ **Business orchestration workflows**: `.github/specs/workflows.md`
→ **Python standards**: `.github/instructions/python.instructions.md`
→ **Azure Functions patterns**: `.github/instructions/azure-functions.instructions.md`
→ **Architecture**: `/docs/specifications/architecture.md`
