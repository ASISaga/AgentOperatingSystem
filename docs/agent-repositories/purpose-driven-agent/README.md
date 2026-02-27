# purpose-driven-agent

[![PyPI version](https://img.shields.io/pypi/v/purpose-driven-agent.svg)](https://pypi.org/project/purpose-driven-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/purpose-driven-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/purpose-driven-agent/actions/workflows/ci.yml)

**The fundamental building block of the Agent Operating System (AOS).**

`purpose-driven-agent` provides `PurposeDrivenAgent` — an abstract base class
for **perpetual, purpose-driven AI agents** that run indefinitely, maintain
rich state across every interaction, and work toward a long-term assigned
purpose rather than short-term tasks.

---

## Table of Contents

1. [What is a Purpose-Driven Agent?](#what-is-a-purpose-driven-agent)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture Overview](#architecture-overview)
5. [Inheritance Hierarchy](#inheritance-hierarchy)
6. [Usage Examples](#usage-examples)
   - [GenericPurposeDrivenAgent](#genericpurposedrivenagent)
   - [Custom Subclass](#custom-subclass)
   - [Event Handling](#event-handling)
   - [Goal Tracking](#goal-tracking)
   - [Purpose Alignment](#purpose-alignment)
   - [ML Pipeline (IMLService)](#ml-pipeline-imlservice)
7. [LoRA Adapter Pattern](#lora-adapter-pattern)
8. [MCP Context Preservation](#mcp-context-preservation)
9. [Perpetual Operation Pattern](#perpetual-operation-pattern)
10. [Configuration](#configuration)
11. [Testing](#testing)
12. [API Reference](#api-reference)
13. [Contributing](#contributing)
14. [Related Packages](#related-packages)
15. [License](#license)

---

## What is a Purpose-Driven Agent?

Traditional AI agents are **task-based**: they start, execute a task, and
terminate.  A `PurposeDrivenAgent` is different in every fundamental way:

| Dimension | Task-Based Agent | Purpose-Driven Agent |
|---|---|---|
| Lifetime | One task → terminates | Registers once → runs indefinitely |
| State | Ephemeral (per task) | Persistent (across all events) |
| Goal | Complete the task | Work toward a long-term purpose |
| Sleep | N/A | Sleeps when idle; awakens on events |
| Adapter | N/A | Mapped to a LoRA adapter for domain expertise |
| Context | Rebuilt each time | Preserved by `ContextMCPServer` (MCP) |

This is the core architectural difference that makes AOS an **operating system
for AI agents**, not just an orchestration framework.

---

## Installation

```bash
# Core (agent_framework + pydantic)
pip install purpose-driven-agent

# With Azure ML / Storage backends
pip install "purpose-driven-agent[azure]"

# Everything
pip install "purpose-driven-agent[full]"

# Development
pip install "purpose-driven-agent[dev]"
```

**Requirements:** Python 3.10 or higher.

---

## Quick Start

```python
import asyncio
from purpose_driven_agent import GenericPurposeDrivenAgent

async def main():
    agent = GenericPurposeDrivenAgent(
        agent_id="assistant",
        purpose="Assist users with information retrieval and task coordination",
        adapter_name="general",
    )

    await agent.initialize()
    await agent.start()

    # Process an event
    result = await agent.handle_event({
        "type": "user_query",
        "data": {"query": "What is AOS?"},
    })
    print(result["status"])   # "success"

    # Check status
    status = await agent.get_purpose_status()
    print(status["total_events_processed"])  # 1

    await agent.stop()

asyncio.run(main())
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        PurposeDrivenAgent                            │
│                     (abstract base class)                            │
│                                                                      │
│  ┌────────────────────────┐   ┌──────────────────────────────────┐   │
│  │    Purpose Context     │   │         LoRA Adapter             │   │
│  │  ──────────────────    │   │  ──────────────────────────      │   │
│  │  purpose               │   │  adapter_name → domain model     │   │
│  │  purpose_scope         │   │  "general", "leadership",        │   │
│  │  purpose_metrics       │   │  "marketing", "finance", ...     │   │
│  └────────────────────────┘   └──────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                   ContextMCPServer (MCP)                     │    │
│  │  Persistent context · Event history · Semantic memory       │    │
│  │  One dedicated instance per agent                            │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────┐   ┌──────────────────────────────────┐   │
│  │    Perpetual Loop      │   │          IMLService              │   │
│  │  asyncio.create_task   │   │  trigger_lora_training()         │   │
│  │  Sleep / Awaken        │   │  run_pipeline()                  │   │
│  │  Event subscriptions   │   │  infer()                         │   │
│  └────────────────────────┘   └──────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

Three foundational components work together:

1. **LoRA Adapters** — provide domain-specific vocabulary, knowledge, and
   agent persona via the `adapter_name` parameter.
2. **Core Purpose** — stored in the primary LLM context to guide all decisions.
3. **ContextMCPServer** — persists state across every event and system restart.

---

## Inheritance Hierarchy

```
agent_framework.Agent          ← Microsoft Agent Framework (optional)
        │
        ▼
PurposeDrivenAgent             ← abstract base (this package)
        │
        ├── GenericPurposeDrivenAgent   ← concrete, general-purpose
        │
        ├── LeadershipAgent            ← pip install leadership-agent
        │       └── CMOAgent           ← pip install cmo-agent
        │
        └── <YourCustomAgent>          ← extend for your domain
```

`PurposeDrivenAgent` inherits from `agent_framework.Agent` (Microsoft Agent
Framework) when the package is installed.  A transparent stub is used when the
package is absent, so the library works without it.

---

## Usage Examples

### GenericPurposeDrivenAgent

The simplest concrete implementation:

```python
from purpose_driven_agent import GenericPurposeDrivenAgent

agent = GenericPurposeDrivenAgent(
    agent_id="cfo-assistant",
    purpose="Support the CFO with financial analysis and reporting",
    purpose_scope="Financial data, budgeting, forecasting",
    adapter_name="finance",
)

await agent.initialize()
await agent.start()
```

### Custom Subclass

Extend `PurposeDrivenAgent` for domain-specific agents:

```python
from typing import List
from purpose_driven_agent import PurposeDrivenAgent

class LegalAgent(PurposeDrivenAgent):
    """Specialist legal advisory agent."""

    def get_agent_type(self) -> List[str]:
        available = self.get_available_personas()
        return ["legal"] if "legal" in available else ["legal"]

    async def review_contract(self, contract: dict) -> dict:
        alignment = await self.evaluate_purpose_alignment(
            {"type": "contract_review"}
        )
        # Domain-specific logic here …
        return {
            "status": "reviewed",
            "risk_score": 0.2,
            "alignment": alignment["alignment_score"],
        }

agent = LegalAgent(
    agent_id="legal-001",
    purpose="Provide legal analysis and contract review",
    adapter_name="legal",
)
await agent.initialize()
result = await agent.review_contract({"title": "NDA", "pages": 12})
```

### Event Handling

```python
# Subscribe before starting
async def on_budget_request(data: dict) -> dict:
    approved = data.get("amount", 0) < 50_000
    return {"approved": approved, "reason": "Within policy limits"}

await agent.subscribe_to_event("budget_request", on_budget_request)

# Trigger from anywhere
result = await agent.handle_event({
    "type": "budget_request",
    "data": {"amount": 25_000, "department": "Engineering"},
})
print(result["handler_results"][0]["approved"])  # True
```

### Goal Tracking

```python
# Add a goal
goal_id = await agent.add_goal(
    "Complete Q2 financial close",
    success_criteria=["All transactions reconciled", "Report filed"],
    deadline="2025-06-30T23:59:59",
)

# Update progress
await agent.update_goal_progress(goal_id, 0.5, notes="Reconciliation 50% done")
await agent.update_goal_progress(goal_id, 1.0, notes="All done")

# Check metrics
status = await agent.get_purpose_status()
print(status["metrics"]["goals_achieved"])  # 1
```

### Purpose Alignment

```python
# Evaluate any action before executing it
alignment = await agent.evaluate_purpose_alignment({
    "type": "approve_vendor",
    "vendor": "Acme Corp",
    "value": 120_000,
})

if alignment["aligned"]:
    print(f"Aligned (score={alignment['alignment_score']:.2f})")
    # proceed

# Make a purpose-driven decision
decision = await agent.make_purpose_driven_decision({
    "options": [
        {"type": "cut_costs", "description": "Reduce vendor spend by 15%"},
        {"type": "invest",    "description": "Invest in new tooling"},
        {"type": "hold",      "description": "Maintain current budget"},
    ]
})
print(decision["selected_option"])
```

### ML Pipeline (IMLService)

Plug in your own ML backend:

```python
from purpose_driven_agent.ml_interface import IMLService
from typing import Any, Dict, List

class MyAzureMLService(IMLService):
    async def trigger_lora_training(
        self, training_params: Dict[str, Any], adapters: List[Dict[str, Any]]
    ) -> str:
        # Call Azure ML here
        return "run-001"

    async def run_pipeline(
        self, subscription_id: str, resource_group: str, workspace_name: str
    ) -> str:
        return "pipeline-001"

    async def infer(self, agent_id: str, prompt: str) -> Dict[str, Any]:
        return {"text": f"Response for {agent_id}"}

agent = GenericPurposeDrivenAgent(
    agent_id="trained-agent",
    purpose="Fine-tuned domain reasoning",
    adapter_name="finance",
    ml_service=MyAzureMLService(),
)
await agent.act("aml_infer", {"prompt": "Summarise Q2 expenses"})
```

---

## LoRA Adapter Pattern

The `adapter_name` parameter maps the agent's purpose to a LoRA adapter:

```python
GenericPurposeDrivenAgent(adapter_name="finance")   # → finance domain
GenericPurposeDrivenAgent(adapter_name="legal")     # → legal domain
GenericPurposeDrivenAgent(adapter_name="hr")        # → HR domain
```

In the full AOS runtime, the **LoRAx** server superimposes selected adapters
concurrently on a shared base model — enabling memory-efficient multi-agent
deployments with minimal per-adapter overhead.

---

## MCP Context Preservation

Every agent has a dedicated `ContextMCPServer` instance automatically created
during `initialize()`.  It stores the agent's full state persistently:

```python
# Automatic (set by the agent on every event)
# purpose, purpose_scope, active_goals,
# completed_goals, purpose_metrics, wake_count, last_active …

# Manual — store anything
await agent.mcp_context_server.set_context("q2_budget", 500_000)
budget = await agent.mcp_context_server.get_context("q2_budget")

# Semantic memory
await agent.mcp_context_server.add_memory({
    "type": "decision", "summary": "Approved vendor contract"
})

# Event history
await agent.mcp_context_server.add_event({"type": "report_filed", "quarter": "Q2"})
```

---

## Perpetual Operation Pattern

```
initialize()  →  loads saved state from MCP
    │
start()       →  spawns _perpetual_loop() background task
    │
    ▼
[Event arrives] → _awaken() → handle_event() → _sleep()
       │
       ├── evaluate_purpose_alignment()
       ├── dispatch to subscribed handlers
       └── _save_context_to_mcp()
    │
stop()        →  saves state, exits loop
```

---

## Configuration

Pass a `config` dict to customise behaviour:

```python
agent = GenericPurposeDrivenAgent(
    agent_id="configured-agent",
    purpose="...",
    config={
        "context_server": {
            "max_history_size": 5000,   # event history limit (default 1000)
            "max_memory_size": 2000,    # memory item limit (default 500)
        }
    },
)
```

---

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=purpose_driven_agent --cov-report=term-missing

# Single test file
pytest tests/test_purpose_driven_agent.py -v
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (configured in
`pyproject.toml`).  No manual `asyncio.run()` or `@pytest.mark.asyncio` loops
needed in most cases.

---

## API Reference

Full API documentation: [`docs/api-reference.md`](docs/api-reference.md)

Key classes:

| Class | Description |
|---|---|
| `PurposeDrivenAgent` | Abstract base class |
| `GenericPurposeDrivenAgent` | Concrete general-purpose implementation |
| `ContextMCPServer` | Lightweight MCP context server |
| `IMLService` | Abstract ML service interface |
| `NoOpMLService` | No-op placeholder implementation |

---

## Contributing

See [`docs/contributing.md`](docs/contributing.md) for setup, testing,
linting, and pull-request guidelines.

Quick start:

```bash
git clone https://github.com/ASISaga/purpose-driven-agent.git
cd purpose-driven-agent
pip install -e ".[dev]"
pytest tests/ -v
pylint src/purpose_driven_agent
```

---

## Related Packages

| Package | Description |
|---|---|
| [`leadership-agent`](https://github.com/ASISaga/leadership-agent) | LeadershipAgent: decision-making, stakeholder coordination |
| [`cmo-agent`](https://github.com/ASISaga/cmo-agent) | CMOAgent: marketing + leadership dual-purpose |
| [`AgentOperatingSystem`](https://github.com/ASISaga/AgentOperatingSystem) | Full AOS runtime with Azure, LoRAx, and orchestration |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
