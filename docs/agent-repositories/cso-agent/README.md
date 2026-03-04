# cso-agent

[![PyPI version](https://img.shields.io/pypi/v/cso-agent.svg)](https://pypi.org/project/cso-agent/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/ASISaga/cso-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/ASISaga/cso-agent/actions/workflows/ci.yml)

**Dual-purpose perpetual agent for the Chief Security Officer role.**

`cso-agent` provides `CSOAgent` — a perpetual, purpose-driven AI agent that
maps both **Security** and **Leadership** purposes to separate LoRA adapters,
enabling context-appropriate execution for cybersecurity strategy tasks and
leadership decisions.

---

## Installation

```bash
pip install cso-agent
# With Azure backends
pip install "cso-agent[azure]"
# Development
pip install "cso-agent[dev]"
```

**Requirements:** Python 3.10+, `leadership-agent>=1.0.0`,
`purpose-driven-agent>=1.0.0`

---

## Quick Start

```python
import asyncio
from cso_agent import CSOAgent

async def main():
    cso = CSOAgent(agent_id="cso-001")
    await cso.initialize()
    await cso.start()

    # Security task
    result = await cso.execute_with_purpose(
        {"type": "risk_assessment", "data": {"system": "payments-api"}},
        purpose_type="security",
    )
    print(f"Status:  {result['status']}")
    print(f"Adapter: {result['adapter_used']}")  # "security"

    # Leadership task
    result = await cso.execute_with_purpose(
        {"type": "compliance_review"},
        purpose_type="leadership",
    )
    print(f"Adapter: {result['adapter_used']}")  # "leadership"

    await cso.stop()

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
CSOAgent                       ← pip install cso-agent  ← YOU ARE HERE
```

---

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
pytest tests/ --cov=cso_agent --cov-report=term-missing
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
