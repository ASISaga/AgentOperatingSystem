# ceo-agent

[![PyPI version](https://img.shields.io/pypi/v/ceo-agent.svg)](https://pypi.org/project/ceo-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/ceo-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/ceo-agent/actions/workflows/ci.yml)

**Dual-purpose perpetual agent for the Chief Executive Officer role.**

`ceo-agent` provides `CEOAgent` — a perpetual, purpose-driven AI agent that
maps both **Executive** and **Leadership** purposes to separate LoRA adapters,
enabling context-appropriate execution for strategic vision tasks and
leadership decisions. The CEO additionally provides **boardroom orchestration**
for routing tasks to specialist C-suite agents (CTO, CFO, CSO, CMO).

---

## Installation

```bash
pip install ceo-agent
# With Azure backends
pip install "ceo-agent[azure]"
# Development
pip install "ceo-agent[dev]"
```

**Requirements:** Python 3.10+, `leadership-agent>=1.0.0`,
`purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from ceo_agent import CEOAgent

async def main():
    ceo = CEOAgent(agent_id="ceo-001")
    await ceo.initialize()
    await ceo.start()

    # Executive task
    result = await ceo.execute_with_purpose(
        {"type": "strategic_review", "data": {"initiative": "Q3 expansion"}},
        purpose_type="executive",
    )
    print(f"Status:  {result['status']}")
    print(f"Adapter: {result['adapter_used']}")  # "executive"

    # Leadership task
    result = await ceo.execute_with_purpose(
        {"type": "org_alignment"},
        purpose_type="leadership",
    )
    print(f"Adapter: {result['adapter_used']}")  # "leadership"

    # Boardroom instructions for LLM routing
    instructions = ceo.get_boardroom_instructions()
    print(instructions)

    await ceo.stop()

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
CEOAgent                       ← pip install ceo-agent  ← YOU ARE HERE
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=ceo_agent --cov-report=term-missing
```

---

## Related Packages

| Package | Description |
|---|---|
| [`purpose-driven-agent`](https://github.com/ASISaga/purpose-driven-agent) | Abstract base class |
| [`leadership-agent`](https://github.com/ASISaga/leadership-agent) | LeadershipAgent — direct parent |
| [`cfo-agent`](https://github.com/ASISaga/cfo-agent) | CFOAgent — boardroom specialist |
| [`cto-agent`](https://github.com/ASISaga/cto-agent) | CTOAgent — boardroom specialist |
| [`cso-agent`](https://github.com/ASISaga/cso-agent) | CSOAgent — boardroom specialist |
| [`cmo-agent`](https://github.com/ASISaga/cmo-agent) | CMOAgent — boardroom specialist |

---

## License

[Apache License 2.0](LICENSE) — © 2024 ASISaga
