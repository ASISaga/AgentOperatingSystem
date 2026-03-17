---
name: purpose-driven-agent
description: >
  Expert knowledge for working with PurposeDrivenAgent — the abstract base
  class and fundamental building block of the Agent Operating System (AOS).
  Covers perpetual operation, LoRA adapter mapping, MCP context preservation,
  purpose alignment, goal tracking, and the GenericPurposeDrivenAgent
  concrete implementation. Enables efficient development, debugging, and
  testing of purpose-driven perpetual agent implementations.
---

# Purpose-Driven Agent Skill

## Overview

`PurposeDrivenAgent` is the **fundamental abstract building block** of AOS.
It cannot be instantiated directly — use a concrete subclass.

```python
# ❌ Raises TypeError — PurposeDrivenAgent is abstract
agent = PurposeDrivenAgent(agent_id="x", purpose="y")

# ✅ Use the concrete generic implementation
from purpose_driven_agent import GenericPurposeDrivenAgent
agent = GenericPurposeDrivenAgent(
    agent_id="assistant",
    purpose="General assistance and task execution",
    adapter_name="general",
)
```

## Key Concepts

### Perpetual Operation

Agents run indefinitely, not as one-off tasks:

```python
await agent.initialize()   # set up MCP context server
await agent.start()        # spawn perpetual loop — runs forever
# ...
await agent.stop()         # graceful shutdown, saves state
```

### LoRA Adapter Mapping

The `adapter_name` connects the agent to domain knowledge & persona:

```python
GenericPurposeDrivenAgent(
    agent_id="cfo",
    purpose="Manage fiscal health and long-term strategy",
    adapter_name="finance",   # → "finance" LoRA adapter
)
```

### MCP Context Preservation

Every agent has a dedicated `ContextMCPServer` for cross-restart state:

```python
# Automatically stored on each event
await agent.mcp_context_server.set_context("current_quarter", "Q2-2025")
value = await agent.mcp_context_server.get_context("current_quarter")
```

### Event Handling

```python
async def on_budget_request(data: dict) -> dict:
    return {"approved": data.get("amount", 0) < 10_000}

await agent.subscribe_to_event("budget_request", on_budget_request)
await agent.handle_event({"type": "budget_request", "data": {"amount": 5000}})
```

### Purpose Alignment

```python
alignment = await agent.evaluate_purpose_alignment({"type": "action"})
# {"aligned": True, "alignment_score": 0.85, "reasoning": "...", "timestamp": "..."}
```

### Goal Tracking

```python
goal_id = await agent.add_goal(
    "Launch new product",
    success_criteria=["Beta testers recruited", "Launch date set"],
)
await agent.update_goal_progress(goal_id, 0.5)
await agent.update_goal_progress(goal_id, 1.0)  # marks complete
```

## Creating a Custom Agent

```python
from typing import List
from purpose_driven_agent import PurposeDrivenAgent

class HRAgent(PurposeDrivenAgent):
    def get_agent_type(self) -> List[str]:
        available = self.get_available_personas()
        return ["hr"] if "hr" in available else ["hr"]
```

## IMLService Interface

Plug in your ML backend:

```python
from purpose_driven_agent.ml_interface import IMLService

class MyMLService(IMLService):
    async def trigger_lora_training(self, training_params, adapters):
        ...
    async def run_pipeline(self, subscription_id, resource_group, workspace_name):
        ...
    async def infer(self, agent_id, prompt):
        ...

agent = GenericPurposeDrivenAgent(
    agent_id="trained-agent",
    purpose="...",
    ml_service=MyMLService(),
)
```

## Status & State

```python
status = await agent.get_purpose_status()
# {"agent_id", "purpose", "metrics", "active_goals", ...}

state = await agent.get_state()
# {"is_running", "sleep_mode", "wake_count", "mcp_context_preserved", ...}
```

## Common Pitfalls

- **Forgetting `await agent.initialize()`** before `start()` — the MCP server
  won't be set up and context won't persist.
- **Direct instantiation of `PurposeDrivenAgent`** raises `TypeError` —
  always use a concrete subclass.
- **Not awaiting async methods** — almost every operation is async.
- **Missing `adapter_name`** — without it, ML pipeline operations target no
  adapter; provide `adapter_name` matching a registered LoRA adapter.

## Installation

```bash
pip install purpose-driven-agent
# or with Azure ML backend
pip install "purpose-driven-agent[azure]"
```
