# leadership-agent

[![PyPI version](https://img.shields.io/pypi/v/leadership-agent.svg)](https://pypi.org/project/leadership-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/leadership-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/leadership-agent/actions/workflows/ci.yml)

**Perpetual leadership agent with decision-making and stakeholder coordination.**

`leadership-agent` extends `PurposeDrivenAgent` with leadership-specific
capabilities: autonomous and consensus-based decision-making, decision
provenance tracking, stakeholder coordination, and the "leadership" LoRA
adapter for domain expertise.

---

## Table of Contents

1. [What is LeadershipAgent?](#what-is-leadershipagent)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture Overview](#architecture-overview)
5. [Inheritance Hierarchy](#inheritance-hierarchy)
6. [Usage Examples](#usage-examples)
   - [Creating a LeadershipAgent](#creating-a-leadershipagent)
   - [Making Decisions](#making-decisions)
   - [Custom Decision Logic](#custom-decision-logic)
   - [Decision History](#decision-history)
   - [Stakeholder Consultation](#stakeholder-consultation)
   - [Event Handling (inherited)](#event-handling-inherited)
   - [Goal Tracking (inherited)](#goal-tracking-inherited)
7. [Decision Modes](#decision-modes)
8. [LoRA Adapter: "leadership"](#lora-adapter-leadership)
9. [Configuration](#configuration)
10. [Testing](#testing)
11. [API Reference](#api-reference)
12. [Contributing](#contributing)
13. [Related Packages](#related-packages)
14. [License](#license)

---

## What is LeadershipAgent?

`LeadershipAgent` is a **perpetual, purpose-driven agent** specialised for
leadership roles.  It builds on `PurposeDrivenAgent` and adds:

| Capability | Description |
|---|---|
| `make_decision()` | Make autonomous, consensus, or delegated decisions |
| `_evaluate_decision()` | Override to inject domain-specific decision logic |
| `consult_stakeholders()` | Consult other agents (message bus integration point) |
| `get_decision_history()` | Retrieve decision provenance |
| `decisions_made` | Full audit trail of every decision made |

Like all `PurposeDrivenAgent` subclasses, `LeadershipAgent` runs **indefinitely**,
preserves state via `ContextMCPServer`, and awakens on events.

---

## Installation

```bash
pip install leadership-agent
# With Azure backends
pip install "leadership-agent[azure]"
# Development
pip install "leadership-agent[dev]"
```

**Requirements:** Python 3.10+, `purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from leadership_agent import LeadershipAgent

async def main():
    agent = LeadershipAgent(agent_id="ceo-001")
    await agent.initialize()
    await agent.start()

    decision = await agent.make_decision(
        context={"proposal": "Expand to EU market", "budget": 2_000_000},
        mode="autonomous",
    )
    print(f"Decision: {decision['decision']}")
    print(f"Mode:     {decision['mode']}")

    await agent.stop()

asyncio.run(main())
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      LeadershipAgent                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               PurposeDrivenAgent                    │   │
│  │  perpetual loop · ContextMCPServer · purpose        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────┐    │
│  │   Decision Engine    │  │  Stakeholder Coordinator │    │
│  │  make_decision()     │  │  consult_stakeholders()  │    │
│  │  _evaluate_decision()│  │  (message bus required)  │    │
│  │  decisions_made list │  │                          │    │
│  └──────────────────────┘  └──────────────────────────┘    │
│                                                             │
│  LoRA Adapter: "leadership"                                 │
│  Domain: strategy · governance · org design                 │
└─────────────────────────────────────────────────────────────┘
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
LeadershipAgent                ← pip install leadership-agent  ← YOU ARE HERE
        │
        └── CMOAgent           ← pip install cmo-agent
```

---

## Usage Examples

### Creating a LeadershipAgent

```python
from leadership_agent import LeadershipAgent

# Minimal — all defaults applied
agent = LeadershipAgent(agent_id="ceo")

# Custom purpose and adapter
agent = LeadershipAgent(
    agent_id="cto",
    purpose="Technology strategy: Build world-class engineering organisation",
    adapter_name="technology",
    purpose_scope="Engineering, architecture, technical strategy",
    success_criteria=[
        "Ship 3 major releases per year",
        "Maintain 99.9% uptime",
        "Grow engineering headcount by 30%",
    ],
)
await agent.initialize()
await agent.start()
```

### Making Decisions

```python
# Autonomous decision
decision = await agent.make_decision(
    context={
        "proposal": "Migrate infrastructure to Kubernetes",
        "cost": 150_000,
        "timeline": "6 months",
    },
    mode="autonomous",
)
print(decision["id"])       # UUID
print(decision["mode"])     # "autonomous"
print(decision["decision"]) # outcome dict

# Consensus decision (with stakeholder IDs)
decision = await agent.make_decision(
    context={"topic": "Hire 20 engineers"},
    stakeholders=["cfo-agent", "coo-agent"],
    mode="consensus",
)
```

### Custom Decision Logic

Override `_evaluate_decision()` for real domain logic:

```python
from typing import Any, Dict
from leadership_agent import LeadershipAgent

class BudgetApproverAgent(LeadershipAgent):
    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        threshold = self.config.get("approval_threshold", 100_000)
        amount = context.get("cost", context.get("budget_required", 0))
        return {
            "approved": amount <= threshold,
            "amount": amount,
            "threshold": threshold,
            "reason": "Within policy" if amount <= threshold else "Exceeds policy",
        }

approver = BudgetApproverAgent(
    agent_id="budget-approver",
    config={"approval_threshold": 75_000},
)
await approver.initialize()

for amount in [50_000, 100_000]:
    d = await approver.make_decision(context={"cost": amount})
    print(f"  ${amount:,} → {d['decision']['approved']}")
```

### Decision History

Every decision is recorded for provenance:

```python
# After several decisions:
history = await agent.get_decision_history(limit=5)
for d in history:
    print(f"[{d['timestamp'][:10]}] {d['mode']} → {d['id'][:8]}…")

# Direct access
all_decisions = agent.decisions_made
```

### Stakeholder Consultation

The `consult_stakeholders()` method is a deliberate integration point — it
requires a message bus and raises `NotImplementedError` until you wire one up:

```python
# Raises NotImplementedError out of the box:
await agent.consult_stakeholders(["cfo"], "budget", {"amount": 500_000})

# Wire up your message bus by overriding:
class MessageBusLeadershipAgent(LeadershipAgent):
    async def consult_stakeholders(self, stakeholders, topic, context):
        responses = []
        for agent_id in stakeholders:
            resp = await self.bus.query(agent_id, topic, context)
            responses.append(resp)
        return responses
```

### Event Handling (inherited)

```python
async def on_escalation(data: dict) -> dict:
    return {"acknowledged": True, "escalated_to": "executive-team"}

await agent.subscribe_to_event("escalation", on_escalation)
result = await agent.handle_event({
    "type": "escalation",
    "data": {"severity": "critical", "issue": "Production outage"},
})
```

### Goal Tracking (inherited)

```python
goal_id = await agent.add_goal(
    "Launch EU product line",
    success_criteria=["Legal entity registered", "Website localised"],
)
await agent.update_goal_progress(goal_id, 0.5, "Legal entity registered")
await agent.update_goal_progress(goal_id, 1.0, "Launch complete!")
```

---

## Decision Modes

| Mode | Description | Use when |
|---|---|---|
| `"autonomous"` | Agent decides alone (default) | Time-sensitive, unambiguous decisions |
| `"consensus"` | Consult stakeholders first | High-impact, cross-functional decisions |
| `"delegated"` | Delegate to another agent | Specialised domain decisions |

---

## LoRA Adapter: "leadership"

```python
# Default — adapter_name="leadership"
agent = LeadershipAgent(agent_id="ceo")

# Override for specialised roles
agent = LeadershipAgent(agent_id="cto", adapter_name="technology")
```

The "leadership" adapter provides:
- **Vocabulary**: strategy, governance, stakeholders, consensus, delegation
- **Knowledge**: leadership frameworks, decision theory, organisational design
- **Persona**: decisive, collaborative, visionary communication style

---

## Configuration

```python
agent = LeadershipAgent(
    agent_id="approver",
    config={
        "approval_threshold": 50_000,    # custom business logic
        "context_server": {
            "max_history_size": 2000,
        },
    },
)
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=leadership_agent --cov-report=term-missing
```

---

## API Reference

Full API: [`docs/api-reference.md`](docs/api-reference.md)

| Method | Description |
|---|---|
| `make_decision(context, stakeholders, mode)` | Make and record a decision |
| `_evaluate_decision(context)` | Override for custom decision logic |
| `consult_stakeholders(stakeholders, topic, context)` | Stub — override with message bus |
| `get_decision_history(limit)` | Return recent decisions |
| `get_agent_type()` | Returns `["leadership"]` |
| *(+ all PurposeDrivenAgent methods)* | Lifecycle, events, goals, MCP, ML |

---

## Contributing

See [`docs/contributing.md`](docs/contributing.md).

```bash
git clone https://github.com/ASISaga/leadership-agent.git
cd leadership-agent
pip install -e ".[dev]"
pytest tests/ -v
pylint src/leadership_agent
```

---

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | PurposeDrivenAgent — abstract base class |
| [`cmo-agent`](https://github.com/ASISaga/cmo-agent) | CMOAgent — marketing + leadership dual-purpose |
| [`AgentOperatingSystem`](https://github.com/ASISaga/AgentOperatingSystem) | Full AOS runtime with Azure, LoRAx, orchestration |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
