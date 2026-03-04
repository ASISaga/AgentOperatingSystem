# cto-agent

[![PyPI version](https://img.shields.io/pypi/v/cto-agent.svg)](https://pypi.org/project/cto-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/cto-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/cto-agent/actions/workflows/ci.yml)

**Dual-purpose perpetual agent for the Chief Technology Officer role.**

`cto-agent` provides `CTOAgent` — a perpetual, purpose-driven AI agent that
maps both **Technology** and **Leadership** purposes to separate LoRA adapters,
enabling context-appropriate execution for technical infrastructure tasks and
leadership decisions.

---

## Installation

```bash
pip install cto-agent
# With Azure backends
pip install "cto-agent[azure]"
# Development
pip install "cto-agent[dev]"
```

**Requirements:** Python 3.10+, `leadership-agent>=1.0.0`,
`purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from cto_agent import CTOAgent

async def main():
    cto = CTOAgent(agent_id="cto-001")
    await cto.initialize()
    await cto.start()

    # Technology task
    result = await cto.execute_with_purpose(
        {"type": "architecture_review", "data": {"service": "auth-api"}},
        purpose_type="technology",
    )
    print(f"Status:  {result['status']}")
    print(f"Adapter: {result['adapter_used']}")  # "technology"

    # Leadership task
    result = await cto.execute_with_purpose(
        {"type": "team_restructure"},
        purpose_type="leadership",
    )
    print(f"Adapter: {result['adapter_used']}")  # "leadership"

    await cto.stop()

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
CTOAgent                       ← pip install cto-agent  ← YOU ARE HERE
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=cto_agent --cov-report=term-missing
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
