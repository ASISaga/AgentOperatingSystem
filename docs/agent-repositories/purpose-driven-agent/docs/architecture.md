# Architecture — purpose-driven-agent

## Overview

`purpose-driven-agent` provides the fundamental building block of the **Agent
Operating System (AOS)**: a **Purpose-Driven, Perpetual Agent**.

Unlike traditional task-based agents that start, execute, and terminate,
`PurposeDrivenAgent` runs indefinitely, maintaining rich state across every
interaction.

---

## Core Design Principles

| Principle | Description |
|---|---|
| **Perpetual** | Agent registers once; runs indefinitely |
| **Event-driven** | Awakens on events; sleeps when idle |
| **Purpose-driven** | Works toward a long-term, assigned purpose |
| **Stateful** | Full state preserved via `ContextMCPServer` (MCP) |
| **Adapter-mapped** | Purpose linked to a LoRA adapter for domain expertise |
| **Autonomous** | Evaluates and aligns decisions with its purpose |

---

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PurposeDrivenAgent                            │
│                     (abstract base class)                            │
│                                                                      │
│  ┌──────────────────────┐   ┌──────────────────────────────────────┐ │
│  │   Purpose Context    │   │          LoRA Adapter                │ │
│  │  ─────────────────   │   │  ──────────────────────────          │ │
│  │  purpose (string)    │   │  adapter_name → domain model         │ │
│  │  purpose_scope       │   │  e.g. "general", "leadership",       │ │
│  │  purpose_metrics     │   │       "marketing", "finance"         │ │
│  └──────────────────────┘   └──────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    ContextMCPServer (MCP)                        │ │
│  │  ─────────────────────────────────────────────────────────────  │ │
│  │  Persistent key/value context store                              │ │
│  │  Event history tracking                                          │ │
│  │  Semantic memory management                                      │ │
│  │  One dedicated instance per agent                                │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────────┐   ┌──────────────────────────────────────┐ │
│  │   Perpetual Loop     │   │          IMLService                  │ │
│  │  ─────────────────   │   │  ──────────────────────────          │ │
│  │  asyncio.create_task │   │  trigger_lora_training()             │ │
│  │  Sleep / Awaken      │   │  run_pipeline()                      │ │
│  │  Event subscriptions │   │  infer()                             │ │
│  └──────────────────────┘   └──────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Inheritance Hierarchy

```
agent_framework.Agent   (Microsoft Agent Framework — optional)
        │
        ▼
PurposeDrivenAgent      ← abstract base class (this package)
        │
        ├── GenericPurposeDrivenAgent   ← concrete, general-purpose
        │
        ├── LeadershipAgent             ← leadership-agent package
        │       └── CMOAgent            ← cmo-agent package
        │
        └── <YourCustomAgent>           ← extend for your domain
```

---

## LoRA Adapter Pattern

The `adapter_name` parameter maps the agent's purpose to a LoRA (Low-Rank
Adaptation) adapter that provides:

- **Domain vocabulary** — terminology natural to the role.
- **Domain knowledge** — facts, heuristics, and reasoning patterns.
- **Agent persona** — communication style, decision tendencies.

In the full AOS runtime, the AgentOperatingSystem uses **LoRAx** to
superimpose multiple adapters concurrently on a shared base model, enabling
memory-efficient multi-agent deployments.

```python
agent = GenericPurposeDrivenAgent(
    agent_id="cfo",
    purpose="Manage financial health and long-term fiscal strategy",
    adapter_name="finance",   # → LoRA adapter: finance domain knowledge + CFO persona
)
```

---

## MCP (Model Context Protocol) Integration

Every `PurposeDrivenAgent` holds a dedicated `ContextMCPServer` instance that
preserves full state across events and restarts.

### Context stored automatically

| Key | Description |
|---|---|
| `purpose` | Agent's purpose string |
| `purpose_scope` | Scope/boundaries |
| `active_goals` | Currently tracked goals |
| `completed_goals` | Completed goal history |
| `purpose_metrics` | Counters for aligned actions, decisions, etc. |
| `wake_count` | Number of awaken cycles |
| `total_events_processed` | Cumulative event count |
| `last_active` | ISO timestamp of last activity |

### Custom context

```python
await agent.mcp_context_server.set_context("custom_key", {"data": 42})
value = await agent.mcp_context_server.get_context("custom_key")
```

---

## Perpetual Operation Pattern

```
  ┌──────────────────────────────────────┐
  │           initialize()               │  → sets up MCP, loads saved state
  └────────────────────┬─────────────────┘
                       │
  ┌────────────────────▼─────────────────┐
  │              start()                 │  → spawns _perpetual_loop() task
  └────────────────────┬─────────────────┘
                       │
  ┌────────────────────▼─────────────────┐
  │          _perpetual_loop()           │  → runs forever until stop()
  │                                      │
  │  ┌────────────────────────────────┐  │
  │  │  Event received → _awaken()    │  │
  │  │  handle_event(event)           │  │
  │  │  evaluate_purpose_alignment()  │  │
  │  │  dispatch to handlers          │  │
  │  │  _save_context_to_mcp()        │  │
  │  │  _sleep()                      │  │
  │  └────────────────────────────────┘  │
  └────────────────────┬─────────────────┘
                       │ (stop() called)
  ┌────────────────────▼─────────────────┐
  │               stop()                 │  → saves state, sets is_running=False
  └──────────────────────────────────────┘
```

---

## Extending PurposeDrivenAgent

```python
from typing import List
from purpose_driven_agent import PurposeDrivenAgent

class FinanceAgent(PurposeDrivenAgent):
    """Domain-specific agent for financial operations."""

    def get_agent_type(self) -> List[str]:
        available = self.get_available_personas()
        return ["finance"] if "finance" in available else ["finance"]

    async def analyse_budget(self, budget: dict) -> dict:
        alignment = await self.evaluate_purpose_alignment(
            {"type": "budget_analysis"}
        )
        # ... domain logic ...
        return {"status": "analysed", "alignment": alignment}
```

---

## Standalone vs. Full AOS Runtime

| Feature | Standalone (`purpose-driven-agent`) | Full AOS |
|---|---|---|
| ContextMCPServer | In-process dict store | Azure Table / Blob Storage |
| ML Service | `NoOpMLService` (plug in your own) | Azure ML + LoRAx |
| Event bus | In-process subscriptions | Azure Service Bus |
| Multi-agent | Not included | Full orchestration engine |
| Personas | Configurable list | AOS persona registry |

The standalone package is designed for development, testing, and environments
where Azure services are not available.  Swap each component by providing an
implementation of the relevant interface.
