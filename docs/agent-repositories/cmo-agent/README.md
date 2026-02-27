# cmo-agent

[![PyPI version](https://img.shields.io/pypi/v/cmo-agent.svg)](https://pypi.org/project/cmo-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/cmo-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/cmo-agent/actions/workflows/ci.yml)

**Dual-purpose perpetual agent for the Chief Marketing Officer role.**

`cmo-agent` provides `CMOAgent` — a perpetual, purpose-driven AI agent that
maps both **Marketing** and **Leadership** purposes to separate LoRA adapters,
enabling context-appropriate execution for marketing strategy tasks and
leadership decisions.

---

## Table of Contents

1. [What is CMOAgent?](#what-is-cmoagent)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture Overview](#architecture-overview)
5. [Inheritance Hierarchy](#inheritance-hierarchy)
6. [Usage Examples](#usage-examples)
   - [Creating a CMOAgent](#creating-a-cmoagent)
   - [execute_with_purpose()](#execute_with_purpose)
   - [get_adapter_for_purpose()](#get_adapter_for_purpose)
   - [get_status()](#get_status)
   - [Decisions (inherited)](#decisions-inherited)
   - [Event Handling (inherited)](#event-handling-inherited)
   - [Goal Tracking (inherited)](#goal-tracking-inherited)
7. [Dual-Purpose Adapter Pattern](#dual-purpose-adapter-pattern)
8. [LoRA Adapters](#lora-adapters)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [API Reference](#api-reference)
12. [Contributing](#contributing)
13. [Related Packages](#related-packages)
14. [License](#license)

---

## What is CMOAgent?

`CMOAgent` extends `LeadershipAgent` with a **dual-purpose design**: the same
agent can execute tasks through either the Marketing or Leadership LoRA adapter
depending on the task type.

| Feature | Description |
|---|---|
| Dual-purpose mapping | Marketing purpose → `"marketing"` adapter; Leadership → `"leadership"` |
| `execute_with_purpose()` | Switch adapter at call time; auto-restore on completion |
| `get_adapter_for_purpose()` | Explicit adapter lookup |
| `get_status()` | Full status with both purposes and adapter details |
| All LeadershipAgent capabilities | `make_decision()`, decision history, etc. |
| All PurposeDrivenAgent capabilities | Perpetual loop, events, goals, MCP context |

---

## Installation

```bash
pip install cmo-agent
# With Azure backends
pip install "cmo-agent[azure]"
# Development
pip install "cmo-agent[dev]"
```

**Requirements:** Python 3.10+, `leadership-agent>=1.0.0`,
`purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from cmo_agent import CMOAgent

async def main():
    cmo = CMOAgent(agent_id="cmo-001")
    await cmo.initialize()
    await cmo.start()

    # Marketing task
    result = await cmo.execute_with_purpose(
        {"type": "brand_audit", "data": {"brand": "AcmeCorp"}},
        purpose_type="marketing",
    )
    print(f"Status:  {result['status']}")
    print(f"Adapter: {result['adapter_used']}")  # "marketing"

    # Leadership task
    result = await cmo.execute_with_purpose(
        {"type": "budget_review"},
        purpose_type="leadership",
    )
    print(f"Adapter: {result['adapter_used']}")  # "leadership"

    status = await cmo.get_status()
    print(status["purposes"])

    await cmo.stop()

asyncio.run(main())
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                          CMOAgent                                │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    LeadershipAgent                         │  │
│  │  make_decision() · decisions_made · consult_stakeholders() │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  PurposeDrivenAgent                        │  │
│  │  perpetual loop · ContextMCPServer · purpose alignment     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │   Marketing Adapter     │  │   Leadership Adapter         │  │
│  │  "marketing"            │  │  "leadership"                │  │
│  │  brand, demand gen,     │  │  strategy, governance,       │  │
│  │  campaigns, growth, …   │  │  decisions, org design, …    │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
│                                                                  │
│  execute_with_purpose(task, purpose_type)                        │
│    → switch adapter → handle_event → restore adapter             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Inheritance Hierarchy

```
agent_framework.Agent          ← Microsoft Agent Framework (optional)
        │
        ▼
PurposeDrivenAgent             ← pip install purpose-driven-agent
        │
        ▼
LeadershipAgent                ← pip install leadership-agent
        │
        ▼
CMOAgent                       ← pip install cmo-agent  ← YOU ARE HERE
```

---

## Usage Examples

### Creating a CMOAgent

```python
from cmo_agent import CMOAgent

# Minimal — all defaults applied
cmo = CMOAgent(agent_id="cmo-001")

# Fully specified
cmo = CMOAgent(
    agent_id="cmo-001",
    name="Chief Marketing Officer",
    marketing_purpose=(
        "Marketing: Build category leadership, drive demand generation, "
        "and deliver outstanding customer experiences"
    ),
    leadership_purpose=(
        "Leadership: Lead the marketing organisation and align growth initiatives"
    ),
    purpose_scope="Marketing and cross-functional leadership",
    marketing_adapter_name="marketing",
    leadership_adapter_name="leadership",
)
await cmo.initialize()
await cmo.start()
```

### execute_with_purpose()

```python
# Marketing task
result = await cmo.execute_with_purpose(
    {"type": "campaign_launch", "data": {"name": "Summer Promo"}},
    purpose_type="marketing",
)
print(result["purpose_type"])   # "marketing"
print(result["adapter_used"])   # "marketing"

# Leadership task
result = await cmo.execute_with_purpose(
    {"type": "org_restructure", "data": {"teams": 3}},
    purpose_type="leadership",
)
print(result["adapter_used"])   # "leadership"

# Default purpose is "marketing"
result = await cmo.execute_with_purpose({"type": "market_analysis"})
print(result["purpose_type"])   # "marketing"

# adapter_name always restored after execution
print(cmo.adapter_name)  # "marketing" (primary)
```

### get_adapter_for_purpose()

```python
cmo.get_adapter_for_purpose("marketing")   # "marketing"
cmo.get_adapter_for_purpose("leadership")  # "leadership"
cmo.get_adapter_for_purpose("MARKETING")   # "marketing" (case-insensitive)

try:
    cmo.get_adapter_for_purpose("finance")
except ValueError as exc:
    print(exc)  # "Unknown purpose type 'finance'. Valid types: ['marketing', 'leadership']"
```

### get_status()

```python
status = await cmo.get_status()

print(status["agent_type"])       # "CMOAgent"
print(status["primary_adapter"])  # "marketing"
print(status["purposes"])
# {
#   "marketing":  {"description": "Marketing: ...", "adapter": "marketing"},
#   "leadership": {"description": "Leadership: ...", "adapter": "leadership"},
# }
print(status["purpose_adapter_mapping"])
# {"marketing": "marketing", "leadership": "leadership"}
```

### Decisions (inherited)

```python
decision = await cmo.make_decision(
    context={"campaign_budget": 500_000, "expected_leads": 10_000},
    mode="autonomous",
)
print(decision["id"])       # UUID
print(decision["decision"]) # outcome dict

history = await cmo.get_decision_history(limit=5)
```

### Event Handling (inherited)

```python
async def on_brand_update(data: dict) -> dict:
    return {"acknowledged": True}

await cmo.subscribe_to_event("brand_update", on_brand_update)
result = await cmo.handle_event({
    "type": "brand_update",
    "data": {"new_logo": True},
})
```

### Goal Tracking (inherited)

```python
goal_id = await cmo.add_goal(
    "Launch Q3 awareness campaign",
    success_criteria=["Creative approved", "Ads live", "10K impressions"],
)
await cmo.update_goal_progress(goal_id, 0.5, "Creative approved, ads live")
await cmo.update_goal_progress(goal_id, 1.0, "10K impressions reached!")
```

---

## Dual-Purpose Adapter Pattern

The `purpose_adapter_mapping` dict maps purpose types to LoRA adapters:

```python
cmo.purpose_adapter_mapping
# {"marketing": "marketing", "leadership": "leadership"}
```

`execute_with_purpose()` temporarily sets `adapter_name` to the resolved
adapter, executes the task, then **always restores** the original adapter
via `try/finally`:

```
execute_with_purpose(task, "leadership")
    │
    ├── adapter_name = "leadership"  (temporary)
    ├── handle_event(task)
    └── adapter_name = "marketing"   (always restored)
```

---

## LoRA Adapters

| Adapter | Domain knowledge |
|---|---|
| `"marketing"` | Brand, demand generation, campaigns, customer, growth, NPS |
| `"leadership"` | Strategy, governance, stakeholders, org design, decisions |

Custom adapters:

```python
cmo = CMOAgent(
    agent_id="cmo-custom",
    marketing_adapter_name="brand-specialist-v2",
    leadership_adapter_name="executive-leadership-v2",
)
```

---

## Configuration

```python
cmo = CMOAgent(
    agent_id="cmo-001",
    config={
        "approval_threshold": 100_000,  # for _evaluate_decision override
        "context_server": {
            "max_history_size": 5000,
        },
    },
)
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=cmo_agent --cov-report=term-missing
```

---

## API Reference

Full API: [`docs/api-reference.md`](docs/api-reference.md)

| Method | Description |
|---|---|
| `execute_with_purpose(task, purpose_type)` | Execute with specific adapter |
| `get_adapter_for_purpose(purpose_type)` | Lookup adapter name |
| `get_status()` | Full dual-purpose status |
| `get_agent_type()` | Returns `["marketing", "leadership"]` |
| *(+ all LeadershipAgent methods)* | `make_decision`, decision history, etc. |
| *(+ all PurposeDrivenAgent methods)* | Lifecycle, events, goals, MCP, ML |

---

## Contributing

See [`docs/contributing.md`](docs/contributing.md).

```bash
git clone https://github.com/ASISaga/cmo-agent.git
cd cmo-agent
pip install -e ".[dev]"
pytest tests/ -v
pylint src/cmo_agent
```

---

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | Abstract base class |
| [`leadership-agent`](https://github.com/ASISaga/leadership-agent) | LeadershipAgent — direct parent |
| [`AgentOperatingSystem`](https://github.com/ASISaga/AgentOperatingSystem) | Full AOS runtime |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
