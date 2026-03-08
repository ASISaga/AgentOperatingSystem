# leadership-agent Repository Specification

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-03-08

## Overview

`leadership-agent` is a **code-only Python library** that provides `LeadershipAgent` — the second level of the AOS agent inheritance hierarchy, extending `PurposeDrivenAgent` with leadership, decision-making, and multi-agent boardroom orchestration capabilities. All C-suite agents (CEO, CFO, CTO, CSO, CMO) inherit from `LeadershipAgent`.

## Scope

- Repository role in the AOS ecosystem
- Technology stack and coding patterns
- Testing and validation workflows
- Key design principles for agents and contributors

## Repository Role

| Concern | Owner |
|---------|-------|
| Leadership base class (`LeadershipAgent`) | **leadership-agent** |
| Generic boardroom orchestration tools (`enroll_specialist_tools`, `get_specialist_tools`, `get_orchestration_instructions`) | **leadership-agent** |
| Abstract agent base class (`PurposeDrivenAgent`) | `purpose-driven-agent` |
| Domain-specific agents (CEO, CFO, CTO, CSO, CMO) | Downstream C-suite packages |
| AOS runtime, orchestration, messaging, storage | AOS ecosystem |

`leadership-agent` is **library-only** — it is not deployed as its own service. It is consumed by C-suite agent repos (e.g. `ceo-agent`, `cfo-agent`) that are deployed.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.10+ |
| Base class dependency | `purpose-driven-agent>=1.0.0` — `PurposeDrivenAgent` base class |
| Azure extras | `purpose-driven-agent[azure]>=1.0.0` |
| Tests | `pytest>=8.0.0` + `pytest-asyncio>=0.23.0` |
| Linter | `pylint>=3.0.0` |
| Type checking | `mypy>=1.8.0` |
| Formatter | `black>=24.0.0` + `isort>=5.13.0` |
| Build | `hatchling` |

## Directory Structure

```
leadership-agent/
├── src/
│   └── leadership_agent/
│       ├── __init__.py          # Public API exports
│       └── agent.py             # LeadershipAgent — decision-making, boardroom orchestration
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_leadership_agent.py # pytest unit tests
├── docs/
│   ├── api-reference.md
│   └── contributing.md
├── examples/                    # Usage examples
└── pyproject.toml               # Build config, dependencies, pytest settings
```

## Core Patterns

### LeadershipAgent Instantiation

```python
from leadership_agent import LeadershipAgent

agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic leadership and executive decision-making",
    adapter_name="leadership",
)

await agent.initialize()
await agent.start()
```

### Boardroom Orchestration Tools

`LeadershipAgent` exposes generic boardroom orchestration methods that C-suite agents delegate to:

```python
# Enroll specialist agents as boardroom tools
agent.enroll_specialist_tools(
    specialist_ids=["cfo", "cto", "cso"],
    thread_id="thread-001",
)

# Retrieve enrolled tool definitions
tools = agent.get_specialist_tools()

# Get orchestration system instructions
instructions = agent.get_orchestration_instructions(
    purpose="Quarterly strategic review",
)
```

### Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent  (purpose-driven-agent)
            └── LeadershipAgent  (this package)
                    └── CEOAgent / CFOAgent / CTOAgent / CSOAgent / CMOAgent
```

### Custom Subclass Pattern

```python
from leadership_agent import LeadershipAgent

class CFOAgent(LeadershipAgent):
    """Chief Financial Officer — finance and leadership dual-purpose agent."""

    def get_agent_type(self) -> list[str]:
        return ["finance", "leadership"]
```

## Testing Workflow

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=leadership_agent --cov-report=term-missing

# Lint
pylint src/leadership_agent

# Type check
mypy src/leadership_agent

# Specific test
pytest tests/test_leadership_agent.py -v -k "test_initialize"
```

**CI**: GitHub Actions runs `pytest` across Python 3.10, 3.11, and 3.12 on every push/PR to `main`.

→ **CI workflow**: `.github/workflows/ci.yml`

## Related Repositories

| Repository | Role |
|-----------|------|
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | `PurposeDrivenAgent` base class |
| [ceo-agent](https://github.com/ASISaga/ceo-agent) | CEOAgent: executive + leadership dual-purpose |
| [cfo-agent](https://github.com/ASISaga/cfo-agent) | CFOAgent: finance + leadership dual-purpose |
| [cto-agent](https://github.com/ASISaga/cto-agent) | CTOAgent: technology + leadership dual-purpose |
| [cso-agent](https://github.com/ASISaga/cso-agent) | CSOAgent: security + leadership dual-purpose |
| [cmo-agent](https://github.com/ASISaga/cmo-agent) | CMOAgent: marketing + leadership dual-purpose |
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | AOS kernel (orchestration, A2A tooling) |

## Key Design Principles

1. **Perpetual** — Agents run indefinitely; there is no finite task completion
2. **Purpose-driven** — Every decision is evaluated against a long-term purpose
3. **Boardroom-capable** — Generic orchestration tools enable any leadership agent to coordinate specialists
4. **Library-only** — No deployment scaffolding; consumed by C-suite agent repositories
5. **Thin delegation** — C-suite agents delegate boardroom methods to `LeadershipAgent`'s generic implementations

## References

→ **Agent framework**: `.github/specs/agent-intelligence-framework.md`  
→ **Conventional tools**: `.github/docs/conventional-tools.md`  
→ **Python coding standards**: `.github/instructions/python.instructions.md`  
→ **Leadership agent patterns**: `.github/instructions/leadership-agent.instructions.md`
