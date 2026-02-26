# Architecture — leadership-agent

## Overview

`leadership-agent` extends `PurposeDrivenAgent` with leadership-specific
capabilities: decision-making with provenance, stakeholder coordination, and
consensus building.

The Leadership purpose is mapped to the **"leadership" LoRA adapter**, which
provides leadership-specific domain knowledge and agent persona.  The core
purpose is added to the primary LLM context.

---

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         LeadershipAgent                              │
│              (extends PurposeDrivenAgent)                            │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     PurposeDrivenAgent                         │  │
│  │  (perpetual loop · ContextMCPServer · purpose alignment)       │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────────────┐  ┌─────────────────────────────────┐  │
│  │    Decision Engine        │  │    Stakeholder Coordination     │  │
│  │  ─────────────────────    │  │  ─────────────────────────────  │  │
│  │  make_decision()          │  │  consult_stakeholders()         │  │
│  │  _evaluate_decision()     │  │  (message bus required)         │  │
│  │  Decision provenance      │  │                                 │  │
│  │  decisions_made list      │  │                                 │  │
│  └───────────────────────────┘  └─────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                   LoRA Adapter: "leadership"                    │  │
│  │  Domain knowledge: strategy, management, org design            │  │
│  │  Persona: strategic, decisive, collaborative                   │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
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
LeadershipAgent                ← this package
        │
        └── CMOAgent           ← cmo-agent package
```

---

## Decision Engine

`make_decision()` orchestrates the full decision lifecycle:

```
make_decision(context, stakeholders, mode)
        │
        ├─ _evaluate_decision(context)    ← override for custom logic
        │         returns decision outcome
        │
        ├─ Record decision with unique ID + timestamp
        │         appended to decisions_made list
        │
        └─ Return full decision dict (id, context, mode, outcome, …)
```

### Decision Modes

| Mode | Description |
|---|---|
| `"autonomous"` | Agent decides independently (default) |
| `"consensus"` | Consult stakeholders before deciding |
| `"delegated"` | Delegate the decision to another agent |

### Overriding `_evaluate_decision`

```python
class BudgetApproverAgent(LeadershipAgent):
    async def _evaluate_decision(self, context: dict) -> Any:
        threshold = self.config.get("approval_threshold", 100_000)
        amount = context.get("budget_required", 0)
        return {
            "approved": amount <= threshold,
            "reason": f"Threshold: ${threshold:,}",
        }
```

---

## Stakeholder Consultation

`consult_stakeholders()` is intentionally left unimplemented.  It requires
integration with a message bus (Azure Service Bus, etc.) to send consultation
requests to other agents and collect responses.

```python
# Override to integrate with your message bus:
class MessageBusLeadershipAgent(LeadershipAgent):
    async def consult_stakeholders(self, stakeholders, topic, context):
        responses = []
        for agent_id in stakeholders:
            response = await self.message_bus.send_and_wait(
                target=agent_id,
                payload={"topic": topic, "context": context},
            )
            responses.append(response)
        return responses
```

---

## Decision Provenance

Every call to `make_decision()` is recorded in `decisions_made`:

```python
decision = await agent.make_decision(context={"proposal": "Hire 10 engineers"})
history  = await agent.get_decision_history(limit=10)

# Each decision contains:
# {
#   "id":           "uuid-string",
#   "agent_id":     "ceo-001",
#   "context":      {...},
#   "mode":         "autonomous",
#   "stakeholders": [],
#   "timestamp":    "2025-01-01T00:00:00",
#   "decision":     {"decision": "pending", ...},
#   "confidence":   0.0,
#   "rationale":    "",
# }
```

---

## LoRA Adapter: "leadership"

```python
LeadershipAgent(
    agent_id="ceo",
    adapter_name="leadership",    # ← "leadership" LoRA adapter
)
```

The adapter provides:
- **Domain vocabulary**: strategy, governance, stakeholders, consensus, …
- **Domain knowledge**: leadership frameworks, decision theory, org design, …
- **Agent persona**: decisive, collaborative, visionary communication style

---

## Extending LeadershipAgent

```python
from typing import Any, Dict, List
from leadership_agent import LeadershipAgent

class COOAgent(LeadershipAgent):
    """Chief Operating Officer agent."""

    def get_agent_type(self) -> List[str]:
        return ["operations", "leadership"]

    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        # Operational logic here
        return {"approved": True, "operational_impact": "medium"}
```

---

## Standalone vs. Full AOS Runtime

| Feature | Standalone (`leadership-agent`) | Full AOS |
|---|---|---|
| Decision engine | In-process | In-process + LLM reasoning |
| Stakeholder consultation | `NotImplementedError` | Azure Service Bus |
| LoRA adapter | `adapter_name` config | AOS + LoRAx runtime |
| Context persistence | In-process dict | Azure Storage |
