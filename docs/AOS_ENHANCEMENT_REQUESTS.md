# AOS Enhancement Requests — BusinessInfinity → aos-client-sdk

**Last Updated**: 2026-03-22  
**Tracking**: Enhancement requests identified during BusinessInfinity development that require changes to `aos-client-sdk`.

---

## Overview

BusinessInfinity is the reference client application for AOS. As it evolves, feature gaps and friction points in the SDK are identified here. Each request describes the pain point, the proposed API change, and the target repository.

---

## ENH-001: `AOSApp.on_orchestration_update` decorator

**Status**: Proposed  
**Priority**: High  
**Target**: `aos-client-sdk`

### Problem

Client apps need to receive intermediate updates from long-running orchestrations. Currently there is no SDK mechanism for registering update handlers. Client apps would need to poll, which defeats the purpose of perpetual orchestrations.

### Proposed API

```python
@app.on_orchestration_update("strategic-review")
async def handle_strategic_review_update(update) -> None:
    logger.info(
        "Strategic review update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )
```

The `@app.on_orchestration_update(workflow_name)` decorator registers an async handler that is called whenever an agent in the specified workflow emits an update. The `update` object exposes at least `agent_id` and `output` attributes.

### Implementation Notes

- The SDK provisions a Service Bus subscription on `aos-orchestration-results` filtered to the workflow name.
- The handler is called by a Service Bus trigger in the generated `function_app.py`.
- Errors in the handler must be caught and logged; they must not fail the trigger.

---

## ENH-002: `AOSApp.mcp_tool` decorator

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-client-sdk`

### Problem

Client apps want to expose their own MCP tools to agents in an orchestration. Currently there is no SDK mechanism for registering outbound MCP tools.

### Proposed API

```python
@app.mcp_tool("erp-search")
async def erp_search(request) -> Any:
    return await request.client.call_mcp_tool("erpnext", "search", request.body)
```

The `@app.mcp_tool(tool_name)` decorator registers an async function as an MCP tool that agents can invoke during orchestrations. The SDK registers the tool with the Foundry MCP catalog at startup.

### Implementation Notes

- The SDK must call `aos-mcp-servers` to register the tool at function app startup.
- The `request` object must expose `body` (raw tool input) and `client` (AOSClient instance).
- Tools are unregistered when the function app is stopped.

---

## ENH-003: `workflow_template` decorator

**Status**: Proposed  
**Priority**: High  
**Target**: `aos-client-sdk`

### Problem

Multiple workflows follow the same pattern: select agents → filter → validate → start orchestration. Copy-pasting this pattern leads to inconsistencies. A `@workflow_template` decorator would allow defining reusable workflow skeletons.

### Proposed API

```python
from aos_client import workflow_template, WorkflowRequest

@workflow_template
async def c_suite_orchestration(
    request: WorkflowRequest,
    agent_filter: Callable[[AgentDescriptor], bool],
    purpose: str,
    purpose_scope: str,
) -> Dict[str, Any]:
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    if not agent_ids:
        raise ValueError("No matching agents available in the catalog")
    status = await request.client.start_orchestration(
        agent_ids=agent_ids,
        purpose=purpose,
        purpose_scope=purpose_scope,
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}

# Usage in a workflow
@app.workflow("strategic-review")
async def strategic_review(request: WorkflowRequest):
    return await c_suite_orchestration(
        request,
        agent_filter=lambda a: True,
        purpose="Drive strategic review",
        purpose_scope="C-suite strategic alignment",
    )
```

---

## ENH-004: `OrchestrationRequest` with MCP server assignment

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-client-sdk`

### Problem

The `start_orchestration()` method does not support assigning specific MCP servers to individual agents. This is needed for the `mcp-orchestration` workflow where the CEO uses the ERP server and the CMO uses CRM + analytics.

### Proposed API

```python
from aos_client import MCPServerConfig, OrchestrationPurpose, OrchestrationRequest

req = OrchestrationRequest(
    agent_ids=["ceo", "cmo"],
    purpose=OrchestrationPurpose(
        purpose="Drive strategic growth with real-time data",
        purpose_scope="C-suite strategy with live ERP and CRM data",
    ),
    context=request.body,
    mcp_servers={
        "ceo": [MCPServerConfig(server_name="erp", secrets={"api_key": erp_key})],
        "cmo": [
            MCPServerConfig(server_name="crm", secrets={"token": crm_token}),
            MCPServerConfig(server_name="analytics"),
        ],
    },
)
status = await request.client.submit_orchestration(req)
```

### Implementation Notes

- `MCPServerConfig.secrets` values must be encrypted before being sent to Foundry.
- The SDK should use Azure Key Vault references for secrets in production deployments.
- `submit_orchestration()` is the lower-level method used when `OrchestrationRequest` is needed; `start_orchestration()` is the higher-level convenience method.

---

## ENH-005: `AOSClient.assess_risk` convenience method

**Status**: Proposed  
**Priority**: Low  
**Target**: `aos-client-sdk`

### Problem

The `assess_risk` workflow passes raw `likelihood` and `impact` values directly to the SDK. The SDK should expose a typed convenience method rather than accepting a raw dict.

### Proposed API

```python
# Current (too raw)
result = await request.client.assess_risk(risk_id, request.body)

# Proposed
result = await request.client.assess_risk(
    risk_id=risk_id,
    likelihood=request.body["likelihood"],
    impact=request.body["impact"],
    rationale=request.body.get("rationale"),
)
```

---

## ENH-006: `ObservabilityConfig` in `AOSApp`

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-client-sdk`

### Problem

Client apps need a way to configure structured logging, correlation tracking, and health checks without writing boilerplate. The SDK should accept an `ObservabilityConfig` at construction time.

### Proposed API

```python
from aos_client import AOSApp, ObservabilityConfig

app = AOSApp(
    name="business-infinity",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)
```

---

## References

- [AOS_FURTHER_ENHANCEMENTS.md](AOS_FURTHER_ENHANCEMENTS.md) — Additional enhancement requests
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [API-REFERENCE.md](API-REFERENCE.md) — Current dispatcher API
