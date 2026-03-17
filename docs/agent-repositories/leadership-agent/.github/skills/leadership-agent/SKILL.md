---
name: leadership-agent
description: >
  Expert knowledge for working with LeadershipAgent — a perpetual, purpose-driven
  agent that extends PurposeDrivenAgent with leadership and decision-making
  capabilities. Covers make_decision(), consult_stakeholders(), decision
  provenance tracking, custom decision logic (_evaluate_decision()), and
  integration with the purpose-driven-agent package.
---

# Leadership Agent Skill

## Overview

`LeadershipAgent` extends `PurposeDrivenAgent` with strategic decision-making
and stakeholder coordination capabilities.

```python
from leadership_agent import LeadershipAgent

agent = LeadershipAgent(
    agent_id="ceo-001",
    purpose="Drive strategic growth through decisive, aligned leadership",
)
await agent.initialize()
```

## Key Concepts

### Default Configuration

```python
# Defaults (no need to specify):
agent.adapter_name  # "leadership"
agent.role          # "leader"
agent.purpose       # "Leadership: Strategic decision-making, ..."
```

### Decision Making

```python
decision = await agent.make_decision(
    context={"proposal": "Launch EU operations", "budget": 2_000_000},
    mode="autonomous",           # or "consensus" / "delegated"
    stakeholders=["cfo", "cto"], # consulted in consensus mode
)
# Returns: {"id", "agent_id", "context", "mode", "stakeholders",
#           "timestamp", "decision", "confidence", "rationale"}
```

### Decision Modes

| Mode | Description |
|---|---|
| `"autonomous"` | Agent decides independently |
| `"consensus"` | Consult stakeholders (needs message bus) |
| `"delegated"` | Delegate to another agent |

### Custom Decision Logic

Override `_evaluate_decision()`:

```python
class ApprovalAgent(LeadershipAgent):
    async def _evaluate_decision(self, context: dict) -> Any:
        approved = context.get("budget_required", 0) < 100_000
        return {"approved": approved}
```

### Stakeholder Consultation

```python
# Raises NotImplementedError — must integrate a message bus:
await agent.consult_stakeholders(
    stakeholders=["cfo-agent"],
    topic="Budget approval",
    context={"amount": 500_000},
)
```

Override to integrate your message bus implementation.

### Decision History

```python
history = await agent.get_decision_history(limit=10)
# Returns list of decision dicts, newest last
```

## Inheritance

```
PurposeDrivenAgent
        ↓
LeadershipAgent    ← this package
        ↓
CMOAgent           ← cmo-agent package
```

All `PurposeDrivenAgent` methods are available (events, goals, MCP, etc.).

## Common Patterns

```python
# Custom adapter name
agent = LeadershipAgent(agent_id="cto", adapter_name="technology")

# With config for custom decision thresholds
agent = LeadershipAgent(
    agent_id="approver",
    config={"approval_threshold": 50_000},
)
```

## Installation

```bash
pip install leadership-agent
```
