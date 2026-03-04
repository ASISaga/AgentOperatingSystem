# cfo-agent

[![PyPI version](https://img.shields.io/pypi/v/cfo-agent.svg)](https://pypi.org/project/cfo-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/cfo-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/cfo-agent/actions/workflows/ci.yml)

**Dual-purpose perpetual agent for the Chief Financial Officer role.**

`cfo-agent` provides `CFOAgent` — a perpetual, purpose-driven AI agent that
maps both **Finance** and **Leadership** purposes to separate LoRA adapters,
enabling context-appropriate execution for fiscal governance tasks and
leadership decisions.

---

## Installation

```bash
pip install cfo-agent
# With Azure backends
pip install "cfo-agent[azure]"
# Development
pip install "cfo-agent[dev]"
```

**Requirements:** Python 3.10+, `leadership-agent>=1.0.0`,
`purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from cfo_agent import CFOAgent

async def main():
    cfo = CFOAgent(agent_id="cfo-001")
    await cfo.initialize()
    await cfo.start()

    # Finance task
    result = await cfo.execute_with_purpose(
        {"type": "budget_audit", "data": {"department": "Engineering"}},
        purpose_type="finance",
    )
    print(f"Status:  {result['status']}")
    print(f"Adapter: {result['adapter_used']}")  # "finance"

    # Leadership task
    result = await cfo.execute_with_purpose(
        {"type": "resource_allocation"},
        purpose_type="leadership",
    )
    print(f"Adapter: {result['adapter_used']}")  # "leadership"

    await cfo.stop()

asyncio.run(main())
```

---

## Inheritance Hierarchy

```
PurposeDrivenAgent             ← pip install purpose-driven-agent
        │
        ▼
LeadershipAgent                ← pip install leadership-agent
        │
        ▼
CFOAgent                       ← pip install cfo-agent  ← YOU ARE HERE
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=cfo_agent --cov-report=term-missing
```

---

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | Abstract base class |
| [`leadership-agent`](https://github.com/ASISaga/leadership-agent) | LeadershipAgent — direct parent |
| [`ceo-agent`](https://github.com/ASISaga/ceo-agent) | CEOAgent — boardroom orchestrator |
| [`AgentOperatingSystem`](https://github.com/ASISaga/AgentOperatingSystem) | Full AOS runtime |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
