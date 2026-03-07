---
applyTo: "src/**/*.py,function_app.py,tests/**/*.py"
description: "Azure Functions and AOS workflow patterns for Python repositories"
---

# Azure Functions & AOS Workflow Patterns

## AOSApp Setup

Every workflow module starts with a single `AOSApp` instance:

```python
from aos_client import AOSApp, ObservabilityConfig

# App name comes from repository spec — see .github/specs/repository.md
app = AOSApp(
    name="<app-name>",
    observability=ObservabilityConfig(
        structured_logging=True,
        correlation_tracking=True,
        health_checks=["aos", "service-bus"],
    ),
)
```

The SDK provisions HTTP triggers, Service Bus triggers, health endpoints, and auth — **no boilerplate needed here**.

## Workflow Registration

```python
@app.workflow("workflow-name")
async def workflow_fn(request: WorkflowRequest) -> Dict[str, Any]:
    ...
```

- Workflow names use `kebab-case`
- Return `{"orchestration_id": ..., "status": ...}` for orchestration starters
- Return plain data dicts for query/lookup workflows

## Azure Functions Entry Point

```python
# function_app.py — zero boilerplate
from <package>.workflows import app
functions = app.get_functions()
```

Never add Azure Functions decorators directly to `function_app.py`.

## Orchestration Patterns

### Perpetual orchestration (most workflows)

```python
status = await request.client.start_orchestration(
    agent_ids=agent_ids,
    purpose="Describe the ongoing goal",
    purpose_scope="Scope of responsibility",
    context=request.body,
)
return {"orchestration_id": status.orchestration_id, "status": status.status.value}
```

### Sequential workflow

```python
status = await request.client.start_orchestration(
    ...,
    workflow="sequential",
)
```

### Hierarchical workflow

```python
status = await request.client.start_orchestration(
    ...,
    workflow="hierarchical",
)
```

### Advanced: `OrchestrationRequest` with MCP servers

```python
from aos_client import MCPServerConfig, OrchestrationPurpose, OrchestrationRequest

req = OrchestrationRequest(
    agent_ids=agent_ids,
    purpose=OrchestrationPurpose(purpose=..., purpose_scope=...),
    context=request.body,
    mcp_servers={agent_id: [MCPServerConfig(server_name="erp")]},
)
status = await request.client.submit_orchestration(req)
```

## Update Handlers

```python
@app.on_orchestration_update("workflow-name")
async def handle_update(update) -> None:
    logger.info("Update from %s: %s", update.agent_id, update.output)
```

## MCP Tool Registration

```python
@app.mcp_tool("tool-name")
async def my_tool(request) -> Any:
    return await request.client.call_mcp_tool("server", "method", request.body)
```

## C-Suite Agent Selection Pattern

```python
C_SUITE_AGENT_IDS = ["ceo", "cfo", "cmo", "coo", "cto", "cso"]
C_SUITE_TYPES = {"LeadershipAgent", "CMOAgent", "CEOAgent", "CFOAgent", "CTOAgent", "CSOAgent"}

async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]:
    all_agents = await client.list_agents()
    by_id = {a.agent_id: a for a in all_agents}
    selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]
    if not selected:
        selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]
    return selected
```

## Workflow Template (Reuse Pattern)

```python
from aos_client import workflow_template

@workflow_template
async def c_suite_orchestration(request, agent_filter, purpose, purpose_scope):
    agents = await select_c_suite_agents(request.client)
    agent_ids = [a.agent_id for a in agents if agent_filter(a)]
    if not agent_ids:
        raise ValueError("No matching agents available in the catalog")
    status = await request.client.start_orchestration(
        agent_ids=agent_ids, purpose=purpose, purpose_scope=purpose_scope,
        context=request.body,
    )
    return {"orchestration_id": status.orchestration_id, "status": status.status.value}
```

## Validation

```bash
pytest tests/ -v                    # Run all tests
pytest tests/ -v -k "workflow"      # Run workflow-specific tests
pylint src/                          # Lint workflows
```

## Related Documentation

→ **Repository spec**: `.github/specs/repository.md`  
→ **Python standards**: `.github/instructions/python.instructions.md`  
→ **Conventional tools**: `.github/docs/conventional-tools.md`  
→ **Architecture**: `/docs/specifications/architecture.md`  
→ **Agent guidelines**: `/docs/specifications/github-copilot-agent-guidelines.md`  
→ **Build & deployment**: `/docs/specifications/build-deployment.md`
