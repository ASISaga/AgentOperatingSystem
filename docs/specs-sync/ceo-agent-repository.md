# ceo-agent Repository Specification

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-03-08

## Overview

`ceo-agent` is a **deployed Python package** that provides `CEOAgent` — the Chief Executive Officer agent of the Agent Operating System. `CEOAgent` extends `LeadershipAgent` with executive decision-making, strategic vision, and boardroom orchestration capabilities. It is deployed as an Azure Functions app and registered with the Foundry Agent Service.

## Scope

- Repository role in the AOS ecosystem
- Technology stack and coding patterns
- Testing and validation workflows
- Key design principles for agents and contributors

## Repository Role

| Concern | Owner |
|---------|-------|
| Executive leadership agent (`CEOAgent`) | **ceo-agent** |
| Boardroom orchestration (`enroll_boardroom_tools`, `get_boardroom_tools`, `get_boardroom_instructions`) | **ceo-agent** (delegating to `LeadershipAgent`) |
| Leadership base class and generic boardroom tooling | `leadership-agent` |
| Abstract agent base class (`PurposeDrivenAgent`) | `purpose-driven-agent` |
| AOS runtime, orchestration, messaging, storage | AOS ecosystem |
| Azure Functions deployment scaffolding | `azure.yaml` (azd) |

`ceo-agent` is **deployed** — it runs as an Azure Functions app registered with the Foundry Agent Service as the executive coordinator for boardroom orchestrations.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.10+ |
| Base class dependency | `leadership-agent>=1.0.0` — `LeadershipAgent` base class |
| Azure extras | `leadership-agent[azure]>=1.0.0` |
| Tests | `pytest>=8.0.0` + `pytest-asyncio>=0.23.0` |
| Linter | `pylint>=3.0.0` |
| Type checking | `mypy>=1.8.0` |
| Formatter | `black>=24.0.0` + `isort>=5.13.0` |
| Build | `hatchling` |
| Build / deploy | `azure.yaml` (Azure Developer CLI) |

## Directory Structure

```
ceo-agent/
├── src/
│   └── ceo_agent/
│       ├── __init__.py          # Public API exports
│       └── agent.py             # CEOAgent — executive + boardroom orchestration
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_ceo_agent.py        # pytest unit tests
├── docs/
│   ├── api-reference.md
│   └── contributing.md
├── examples/                    # Usage examples
├── pyproject.toml               # Build config, dependencies, pytest settings
└── azure.yaml                   # Azure Developer CLI deployment config
```

## Core Patterns

### CEOAgent Instantiation

```python
from ceo_agent import CEOAgent

agent = CEOAgent(
    agent_id="ceo",
    purpose="Strategic leadership, vision setting, and executive decision-making",
    adapter_name="leadership",
)

await agent.initialize()
await agent.start()
```

### Boardroom Orchestration

`CEOAgent` exposes boardroom orchestration methods that delegate to `LeadershipAgent`'s generic implementations:

```python
# Enroll C-suite specialists as boardroom tools
agent.enroll_boardroom_tools(
    specialist_ids=["cfo", "cto", "cso"],
    thread_id="thread-001",
)

# Retrieve enrolled boardroom tool definitions
tools = agent.get_boardroom_tools()

# Get system instructions for boardroom orchestration
instructions = agent.get_boardroom_instructions(
    purpose="Quarterly strategic review",
)
```

### Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent  (purpose-driven-agent)
            └── LeadershipAgent  (leadership-agent)
                    └── CEOAgent  (this package)
```

### Agent Type Declaration

```python
from leadership_agent import LeadershipAgent

class CEOAgent(LeadershipAgent):
    """Chief Executive Officer — executive and leadership dual-purpose agent."""

    def get_agent_type(self) -> list[str]:
        return ["executive", "leadership"]
```

## Testing Workflow

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v --rootdir=.

# With coverage
pytest tests/ --cov=ceo_agent --cov-report=term-missing --rootdir=.

# Lint
pylint src/ceo_agent

# Type check
mypy src/ceo_agent

# Specific test
pytest tests/test_ceo_agent.py -v -k "test_initialize" --rootdir=.
```

**Note**: Use `--rootdir=.` to avoid pytest namespace conflicts when running multiple C-suite agent repos in the same environment.

**CI**: GitHub Actions runs `pytest` across Python 3.10, 3.11, and 3.12 on every push/PR to `main`.

→ **CI workflow**: `.github/workflows/ci.yml`

## Deployment

```bash
# Deploy via the aos-infrastructure orchestrator (recommended), or directly:
azd deploy ceo-agent
```

→ **Deploy workflow**: `.github/workflows/deploy.yml`  
→ **Azure config**: `azure.yaml`

## Related Repositories

| Repository | Role |
|-----------|------|
| [leadership-agent](https://github.com/ASISaga/leadership-agent) | `LeadershipAgent` base class and boardroom tooling |
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | `PurposeDrivenAgent` foundational base class |
| [cfo-agent](https://github.com/ASISaga/cfo-agent) | CFO boardroom specialist |
| [cto-agent](https://github.com/ASISaga/cto-agent) | CTO boardroom specialist |
| [cso-agent](https://github.com/ASISaga/cso-agent) | CSO boardroom specialist |
| [cmo-agent](https://github.com/ASISaga/cmo-agent) | CMO boardroom specialist |
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | AOS kernel (orchestration, A2A tooling) |
| [realm-of-agents](https://github.com/ASISaga/realm-of-agents) | Agent catalog (registers this agent) |
| [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) | Infrastructure deployment |

## Key Design Principles

1. **Perpetual** — Runs indefinitely as an Azure Functions app; awakens on boardroom events
2. **Executive-first** — Decisions are always evaluated through an executive strategic lens
3. **Boardroom coordinator** — Coordinates C-suite specialist agents via boardroom tool enrollment
4. **Thin delegation** — Boardroom methods delegate to `LeadershipAgent`'s generic implementations
5. **Foundry-registered** — Registered once with the Foundry Agent Service; participates in A2A orchestrations

## References

→ **Agent framework**: `.github/specs/agent-intelligence-framework.md`  
→ **Conventional tools**: `.github/docs/conventional-tools.md`  
→ **Python coding standards**: `.github/instructions/python.instructions.md`  
→ **Azure Functions patterns**: `.github/instructions/azure-functions.instructions.md`
