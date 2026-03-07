# Business Orchestration Workflows Specification

**Version**: 1.0.0
**Status**: Active
**Last Updated**: 2026-03-07

## Overview

BusinessInfinity exposes purpose-driven, perpetual orchestration workflows via Azure Functions. Each workflow starts a long-running orchestration in which C-suite agents work toward a declared `purpose` indefinitely. Workflows are defined by `@app.workflow` decorators in `src/business_infinity/workflows.py` — no Azure Functions boilerplate is written here; the SDK provisions all triggers, auth, and Service Bus infrastructure.

## Scope

- Core business orchestration workflows (`strategic-review`, `market-analysis`, `budget-approval`)
- C-suite agent selection pattern
- Reusable `c_suite_orchestration` workflow template
- Orchestration update handler pattern
- Workflow variants: perpetual (default), hierarchical, sequential

## C-Suite Agent Selection

All orchestration workflows rely on selecting the correct C-suite agents from the RealmOfAgents catalog before starting an orchestration.

### Agent Constants

```python
C_SUITE_AGENT_IDS = ["ceo", "cfo", "cmo", "coo", "cto", "cso"]
C_SUITE_TYPES = {"LeadershipAgent", "CMOAgent", "CEOAgent", "CFOAgent", "CTOAgent", "CSOAgent"}
```

### Selection Algorithm

```python
async def select_c_suite_agents(client: AOSClient) -> List[AgentDescriptor]:
    all_agents = await client.list_agents()
    by_id = {a.agent_id: a for a in all_agents}
    # Prefer explicit IDs for deterministic selection
    selected = [by_id[aid] for aid in C_SUITE_AGENT_IDS if aid in by_id]
    if not selected:
        # Fall back to agent_type matching if IDs not in catalog
        selected = [a for a in all_agents if a.agent_type in C_SUITE_TYPES]
    return selected
```

**Rule**: Always prefer explicit `agent_id` matching. Fall back to `agent_type` only when no IDs are found. Raise `ValueError` when no agents are returned by either method.

## Workflow Template

`c_suite_orchestration` is a reusable `@workflow_template` that encapsulates the standard pattern: select agents → filter → validate → start orchestration.

```python
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
```

Use this template for any new workflow that follows the select → filter → orchestrate pattern.

## Core Orchestration Workflows

### `strategic-review`

**Purpose**: Perpetual strategic alignment, review, and improvement across the organisation.

| Attribute | Value |
|-----------|-------|
| Workflow name | `strategic-review` |
| Agent selection | All C-suite agents (`agent_filter=lambda a: True`) |
| Workflow variant | Default (perpetual) |
| Purpose | `"Drive strategic review and continuous organisational improvement"` |
| Purpose scope | `"C-suite strategic alignment and cross-functional coordination"` |

**Request body**:

```json
{"quarter": "Q1-2026", "focus_areas": ["revenue", "growth"]}
```

**Response**:

```json
{"orchestration_id": "orch-abc123", "status": "running"}
```

### `market-analysis`

**Purpose**: Continuous market monitoring, competitor analysis, and opportunity identification led by the CMO.

| Attribute | Value |
|-----------|-------|
| Workflow name | `market-analysis` |
| Agent selection | CMO agent (primary) + CEO (strategic oversight, if available) |
| Workflow variant | `"hierarchical"` |
| Purpose | `"Continuously analyse markets and surface competitive insights"` |
| Purpose scope | `"Market intelligence, competitor monitoring, and opportunity identification"` |

**Agent selection rule**: Select `CMOAgent` first; if CEO (`agent_id == "ceo"`) is available and not already selected, insert it at index 0.

**Request body**:

```json
{"market": "EU SaaS", "competitors": ["AcmeCorp", "Globex"]}
```

**Response**:

```json
{"orchestration_id": "orch-xyz789", "status": "running"}
```

### `budget-approval`

**Purpose**: Perpetual budget governance, spend monitoring, and financial decision oversight.

| Attribute | Value |
|-----------|-------|
| Workflow name | `budget-approval` |
| Agent selection | CEO (`agent_id == "ceo"`) + CFO (`agent_id == "cfo"`) |
| Workflow variant | `"sequential"` |
| Purpose | `"Govern budget allocation and ensure fiscal responsibility"` |
| Purpose scope | `"Financial governance, budget oversight, and resource allocation"` |

**Request body**:

```json
{"department": "Marketing", "amount": 500000, "justification": "Q2 campaign"}
```

**Response**:

```json
{"orchestration_id": "orch-def456", "status": "running"}
```

## Orchestration Update Handler

Workflows may register a handler for intermediate agent updates via `@app.on_orchestration_update`. The `strategic-review` workflow registers one to log progress:

```python
@app.on_orchestration_update("strategic-review")
async def handle_strategic_review_update(update) -> None:
    logger.info(
        "Strategic review update from agent %s: %s",
        getattr(update, "agent_id", "unknown"),
        getattr(update, "output", ""),
    )
```

**Convention**: Update handlers log at `INFO` level. They must not raise exceptions as this would affect orchestration delivery.

## Workflow Variants

| Variant | `workflow=` parameter | When to use |
|---------|----------------------|-------------|
| Perpetual (default) | *(omit)* | General strategic and cross-functional orchestrations |
| `hierarchical` | `"hierarchical"` | Analysis workflows where one agent leads and coordinates others |
| `sequential` | `"sequential"` | Approval workflows requiring ordered agent participation |

## Response Schema

All orchestration-starting workflows return:

```json
{
    "orchestration_id": "<string>",
    "status": "<OrchestrationStatus.value>"
}
```

Raise `ValueError` with a descriptive message when no agents match the selection criteria — never return an empty orchestration.

## Validation

```bash
# Run all workflow tests
pytest tests/test_workflows.py -v

# Run workflow registration tests only
pytest tests/test_workflows.py -v -k "registered"

# Lint workflows module
pylint src/business_infinity/workflows.py
```

## References

→ **Repository spec**: `.github/specs/repository.md`
→ **Enterprise capabilities**: `.github/specs/enterprise-capabilities.md`
→ **Python standards**: `.github/instructions/python.instructions.md`
→ **Azure Functions patterns**: `.github/instructions/azure-functions.instructions.md`
→ **Architecture**: `/docs/specifications/architecture.md`
