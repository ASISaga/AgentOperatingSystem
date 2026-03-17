# Architecture — cmo-agent

## Overview

`cmo-agent` provides `CMOAgent` — a dual-purpose perpetual agent that maps
both Marketing and Leadership purposes to separate LoRA adapters.

This is the reference implementation of the **multi-purpose adapter pattern**
in AOS: a single agent switching between domain-specific adapters depending on
the task type.

---

## Component Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                           CMOAgent                                 │
│               (extends LeadershipAgent)                            │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      LeadershipAgent                         │  │
│  │  make_decision() · consult_stakeholders() · decisions_made   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    PurposeDrivenAgent                        │  │
│  │  perpetual loop · ContextMCPServer · purpose alignment       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌───────────────────────────┐  ┌─────────────────────────────┐   │
│  │   Marketing Purpose       │  │   Leadership Purpose        │   │
│  │  ────────────────────     │  │  ─────────────────────────  │   │
│  │  marketing_purpose        │  │  leadership_purpose         │   │
│  │  marketing_adapter_name   │  │  leadership_adapter_name    │   │
│  │  adapter: "marketing"     │  │  adapter: "leadership"      │   │
│  └───────────────────────────┘  └─────────────────────────────┘   │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              execute_with_purpose()                          │  │
│  │  Temporarily switches adapter_name for task execution        │  │
│  │  Restores primary adapter in all cases (try/finally)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

---

## Inheritance Hierarchy

```
agent_framework.Agent          ← Microsoft Agent Framework (optional)
        │
        ▼
PurposeDrivenAgent             ← purpose-driven-agent package
        │
        ▼
LeadershipAgent                ← leadership-agent package
        │
        ▼
CMOAgent                       ← this package
```

---

## Dual-Purpose Adapter Pattern

`CMOAgent` maps two purposes to two LoRA adapters:

```python
cmo = CMOAgent(
    agent_id="cmo-001",
    marketing_adapter_name="marketing",   # Marketing domain adapter
    leadership_adapter_name="leadership", # Leadership domain adapter
)

# purpose_adapter_mapping:
# {
#   "marketing":  "marketing",
#   "leadership": "leadership",
# }
```

### Adapter Switching

When `execute_with_purpose()` is called, the agent:

1. Calls `get_adapter_for_purpose(purpose_type)` to resolve the adapter name.
2. Temporarily sets `self.adapter_name` to the resolved adapter.
3. Delegates to `handle_event(task)`.
4. Restores the original `adapter_name` in a `finally` block.

```
execute_with_purpose(task, purpose_type="marketing")
        │
        ├─ get_adapter_for_purpose("marketing") → "marketing"
        │
        ├─ self.adapter_name = "marketing"   (temporary)
        │
        ├─ handle_event(task)
        │         result["purpose_type"] = "marketing"
        │         result["adapter_used"]  = "marketing"
        │
        └─ self.adapter_name = original     (restored)
```

---

## Purpose-to-Adapter Mapping

```python
cmo.purpose_adapter_mapping
# {"marketing": "marketing", "leadership": "leadership"}

# Lookup
cmo.get_adapter_for_purpose("marketing")   # "marketing"
cmo.get_adapter_for_purpose("leadership")  # "leadership"
cmo.get_adapter_for_purpose("finance")     # ValueError
```

---

## LoRA Adapters

| Purpose | Adapter | Domain knowledge provided |
|---|---|---|
| Marketing | `"marketing"` | Brand, demand gen, customer, campaigns, growth |
| Leadership | `"leadership"` | Strategy, governance, stakeholders, decisions |

In the full AOS runtime, **LoRAx** loads both adapters and superimposes them
concurrently on the shared base model.

---

## get_status() Return Structure

```python
{
    "agent_id": "cmo-001",
    "purpose": "Marketing: ...; Leadership: ...",
    "metrics": {...},
    "active_goals": 0,
    "completed_goals": 1,
    "is_running": True,
    "total_events_processed": 5,

    # CMO-specific additions:
    "agent_type": "CMOAgent",
    "purposes": {
        "marketing": {
            "description": "Marketing: Brand strategy, ...",
            "adapter": "marketing",
        },
        "leadership": {
            "description": "Leadership: Strategic decision-making, ...",
            "adapter": "leadership",
        },
    },
    "purpose_adapter_mapping": {"marketing": "marketing", "leadership": "leadership"},
    "primary_adapter": "marketing",
}
```

---

## Extending CMOAgent

```python
from cmo_agent import CMOAgent
from typing import Any, Dict

class StartupCMOAgent(CMOAgent):
    """CMO specialised for early-stage startup context."""

    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        budget = context.get("budget_required", 0)
        runway_months = self.config.get("runway_months", 12)
        # Conservative approvals for cash-constrained startups
        return {
            "approved": budget < 10_000,
            "reason": f"Runway: {runway_months} months",
        }
```

---

## Standalone vs. Full AOS Runtime

| Feature | Standalone (`cmo-agent`) | Full AOS |
|---|---|---|
| Dual-purpose mapping | `purpose_adapter_mapping` dict | AOS + LoRAx runtime |
| Adapter switching | In-process `adapter_name` swap | LoRAx adapter superimposition |
| Marketing tools | Not included | MCP domain tools |
| Context store | In-process dict | Azure Storage |
