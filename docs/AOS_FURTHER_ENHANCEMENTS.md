# AOS Further Enhancements — SDK & Platform

**Last Updated**: 2026-03-22  
**Tracking**: Enhancement requests that go beyond the initial BusinessInfinity-to-SDK requests, covering the broader AOS platform.

---

## Overview

This document captures enhancement requests for the AOS platform that span multiple repositories or address systemic improvements identified through ongoing usage.

---

## FENH-001: Streaming orchestration results

**Status**: Proposed  
**Priority**: High  
**Target**: `aos-dispatcher`, `aos-client-sdk`

### Problem

Long-running orchestrations currently require polling `GET /api/orchestrations/{id}` to check completion, or wait for a Service Bus result. Neither provides real-time streaming of intermediate agent outputs to browser-based clients.

### Proposed Solution

Add a `GET /api/orchestrations/{id}/stream` endpoint that returns a Server-Sent Events (SSE) stream:

```http
GET /api/orchestrations/orch-abc123/stream
Accept: text/event-stream

data: {"agent_id": "ceo", "output": "Initiating strategic review..."}
data: {"agent_id": "cfo", "output": "Reviewing Q1 financials..."}
data: {"status": "completed", "result": {...}}
```

SDK support:

```python
async for update in request.client.stream_orchestration(orchestration_id):
    yield update  # SSE or WebSocket frame to browser client
```

---

## FENH-002: Agent capability discovery

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-kernel`, `aos-realm-of-agents`, `aos-client-sdk`

### Problem

Client apps select agents by `agent_id` or `agent_type`, but have no way to discover what an agent can do (tools, supported task types, specializations). This makes it hard to build dynamic agent selection logic.

### Proposed Solution

Extend the `AgentDescriptor` returned by `GET /api/agents/{agent_id}` with a capabilities schema:

```json
{
    "agent_id": "cmo",
    "agent_type": "CMOAgent",
    "capabilities": {
        "tasks": ["market_analysis", "brand_strategy", "campaign_planning"],
        "tools": ["crm", "analytics"],
        "workflow_types": ["hierarchical", "collaborative"],
        "max_concurrency": 5
    }
}
```

SDK method:

```python
capabilities = await client.get_agent_capabilities("cmo")
```

---

## FENH-003: Multi-region orchestration routing

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-infrastructure`, `aos-dispatcher`

### Problem

AOS is currently single-region. Enterprise customers require multi-region deployments for latency, data residency, and disaster recovery. The dispatcher needs to route orchestrations to the nearest region while ensuring data sovereignty compliance.

### Proposed Solution

- Extend `aos-infrastructure` Bicep to support multi-region deployments (hub in primary region, spokes in regional regions)
- Add `preferred_region` to `OrchestrationRequest`
- Dispatcher routes to regional Foundry project based on preference and compliance tags
- Cross-region result aggregation via Service Bus federation

---

## FENH-004: Orchestration cost tracking

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-kernel`, `aos-dispatcher`

### Problem

There is no visibility into the token consumption and compute cost of individual orchestrations. Enterprise customers need this for cost allocation, budgeting, and optimization.

### Proposed Solution

Return cost metadata in orchestration results:

```json
{
    "orchestration_id": "orch-abc123",
    "status": "completed",
    "result": { ... },
    "cost": {
        "total_tokens": 45200,
        "prompt_tokens": 32100,
        "completion_tokens": 13100,
        "estimated_usd": 0.45,
        "agents": {
            "ceo": {"tokens": 15000, "estimated_usd": 0.15},
            "cfo": {"tokens": 12000, "estimated_usd": 0.12},
            "cmo": {"tokens": 18200, "estimated_usd": 0.18}
        }
    }
}
```

---

## FENH-005: Agent memory persistence

**Status**: Proposed  
**Priority**: High  
**Target**: `purpose-driven-agent`, `aos-kernel`

### Problem

Agents currently have no persistent memory across orchestrations. A CEO agent that participated in a strategic review last week has no recollection of it in a new orchestration. This limits the quality of long-term strategic reasoning.

### Proposed Solution

- Add an `AgentMemory` class to `purpose-driven-agent` backed by Azure AI Search or Cosmos DB
- Agents retrieve relevant memories at the start of each orchestration using semantic search
- Memory is scoped per agent and per organisation (not cross-tenant)
- Memories are automatically summarised when they exceed a token budget

```python
class PurposeDrivenAgent:
    async def recall(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories for the current task."""
        ...

    async def remember(self, content: str, tags: List[str]) -> None:
        """Store a memory from the current orchestration."""
        ...
```

---

## FENH-006: Covenant enforcement during orchestrations

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-kernel`, `aos-dispatcher`

### Problem

Covenants are currently stored and validated on-demand but are not enforced during orchestration execution. An agent could take an action that violates a signed covenant with no automatic prevention.

### Proposed Solution

- Inject active covenant rules into each agent's system prompt at orchestration start
- The dispatcher checks covenant compliance before submitting the orchestration to Foundry
- Violations are recorded in the audit trail automatically
- Add a `covenant_check` step to the orchestration lifecycle

---

## FENH-007: Self-healing orchestrations

**Status**: Proposed  
**Priority**: Low  
**Target**: `aos-kernel`

### Problem

When an agent in an orchestration fails (connection timeout, token limit exceeded, model error), the entire orchestration fails. There is no automatic recovery mechanism.

### Proposed Solution

- Add a `reliability_config` to `OrchestrationRequest`:

```python
status = await client.start_orchestration(
    agent_ids=agent_ids,
    purpose=purpose,
    reliability_config={
        "retry_failed_agents": True,
        "max_agent_retries": 2,
        "fallback_agents": {"cmo": "cmo-backup"},
        "timeout_per_agent": 120,  # seconds
    }
)
```

- The kernel monitors individual agent health during orchestration
- Failed agents are automatically retried or replaced with fallback agents
- Timeouts are enforced per agent (not just per orchestration)

---

## FENH-008: LoRA adapter assignment per orchestration

**Status**: Proposed  
**Priority**: Medium  
**Target**: `aos-intelligence`, `aos-kernel`

### Problem

`aos-intelligence` includes LoRA adapter infrastructure but there is no API for client apps to request specific LoRA adapters for agents in an orchestration. Fine-tuned adapters (e.g., `finance-v2`, `legal-compliance-v1`) cannot be selected per agent.

### Proposed Solution

Extend `MCPServerConfig` or create a separate `AdapterConfig`:

```python
from aos_client import AdapterConfig

req = OrchestrationRequest(
    agent_ids=["cfo"],
    adapters={
        "cfo": AdapterConfig(adapter_name="finance-v2", version="2.1.0"),
    },
    ...
)
```

The kernel resolves the adapter from the `aos-intelligence` LoRA registry and injects it into the Foundry agent configuration.

---

## References

- [AOS_ENHANCEMENT_REQUESTS.md](AOS_ENHANCEMENT_REQUESTS.md) — BusinessInfinity-to-SDK enhancement requests
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- `.github/docs/future-roadmap.md` — Long-term roadmap items
