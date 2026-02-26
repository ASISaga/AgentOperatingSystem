---
name: cmo-agent
description: >
  Expert knowledge for working with CMOAgent — a dual-purpose perpetual agent
  that maps both Marketing and Leadership purposes to separate LoRA adapters.
  Covers execute_with_purpose(), get_adapter_for_purpose(), get_status(),
  the purpose-to-adapter mapping pattern, adapter switching internals, and
  integration with LeadershipAgent and PurposeDrivenAgent.
---

# CMO Agent Skill

## Overview

`CMOAgent` is a **dual-purpose agent** that executes tasks through either the
Marketing or Leadership LoRA adapter based on the task type.

```python
from cmo_agent import CMOAgent

cmo = CMOAgent(agent_id="cmo-001")
await cmo.initialize()
```

## Key Concepts

### Dual Purpose Mapping

```python
cmo.purpose_adapter_mapping
# {"marketing": "marketing", "leadership": "leadership"}

cmo.get_adapter_for_purpose("marketing")   # "marketing"
cmo.get_adapter_for_purpose("leadership")  # "leadership"
cmo.get_adapter_for_purpose("finance")     # ValueError!
```

### execute_with_purpose()

The core CMO capability — execute a task using a specific adapter:

```python
# Marketing task (brand, campaigns, demand gen, …)
result = await cmo.execute_with_purpose(
    {"type": "brand_audit", "data": {"brand": "Acme"}},
    purpose_type="marketing",
)
# result["purpose_type"] == "marketing"
# result["adapter_used"] == "marketing"

# Leadership task (decisions, strategy, governance, …)
result = await cmo.execute_with_purpose(
    {"type": "budget_review"},
    purpose_type="leadership",
)
```

**Important:** `adapter_name` is always restored after execution, even on error.

### Default Purpose Type

```python
# Default is "marketing"
result = await cmo.execute_with_purpose({"type": "campaign"})
# result["purpose_type"] == "marketing"
```

### Custom Adapter Names

```python
cmo = CMOAgent(
    agent_id="cmo-001",
    marketing_adapter_name="brand-v2",
    leadership_adapter_name="exec-leadership-v2",
)
```

### get_status()

Returns full dual-purpose status:

```python
status = await cmo.get_status()
status["agent_type"]    # "CMOAgent"
status["primary_adapter"]  # "marketing" (always restores to this)
status["purposes"]["marketing"]["adapter"]   # "marketing"
status["purposes"]["leadership"]["adapter"]  # "leadership"
status["purpose_adapter_mapping"]  # {"marketing": "marketing", "leadership": "leadership"}
```

### get_agent_type()

```python
cmo.get_agent_type()  # ["marketing", "leadership"]
```

## Inheritance Chain

```
PurposeDrivenAgent → LeadershipAgent → CMOAgent
```

All `LeadershipAgent` methods (`make_decision`, `get_decision_history`, …)
and all `PurposeDrivenAgent` methods (events, goals, MCP, …) are available.

## Common Patterns

```python
# Leadership decision using CMO
decision = await cmo.make_decision(
    context={"campaign_budget": 500_000},
    mode="autonomous",
)

# Marketing event handling
await cmo.subscribe_to_event("campaign_update", handler)
await cmo.handle_event({"type": "campaign_update", "data": {}})
```

## Installation

```bash
pip install cmo-agent
```
