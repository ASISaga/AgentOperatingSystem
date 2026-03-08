# cmo-agent Repository Specification

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-03-08

## Overview

`cmo-agent` is a **deployed Python package** that provides `CMOAgent` — the Chief Marketing Officer agent of the Agent Operating System. `CMOAgent` extends `LeadershipAgent` with marketing strategy, brand management, market analysis, and boardroom orchestration capabilities. It is deployed as an Azure Functions app and registered with the Foundry Agent Service.

## Scope

- Repository role in the AOS ecosystem
- Technology stack and coding patterns
- Testing and validation workflows
- Key design principles for agents and contributors

## Repository Role

| Concern | Owner |
|---------|-------|
| Marketing leadership agent (`CMOAgent`) | **cmo-agent** |
| Marketing-domain boardroom participation | **cmo-agent** |
| Leadership base class and generic boardroom tooling | `leadership-agent` |
| Abstract agent base class (`PurposeDrivenAgent`) | `purpose-driven-agent` |
| AOS runtime, orchestration, messaging, storage | AOS ecosystem |
| Azure Functions deployment scaffolding | `azure.yaml` (azd) |

`cmo-agent` is **deployed** — it runs as an Azure Functions app registered with the Foundry Agent Service as the marketing specialist in boardroom orchestrations.

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
cmo-agent/
├── src/
│   └── cmo_agent/
│       ├── __init__.py          # Public API exports
│       └── agent.py             # CMOAgent — marketing and leadership dual-purpose
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   └── test_cmo_agent.py        # pytest unit tests
├── docs/
│   ├── api-reference.md
│   └── contributing.md
├── examples/                    # Usage examples
├── pyproject.toml               # Build config, dependencies, pytest settings
└── azure.yaml                   # Azure Developer CLI deployment config
```

## Core Patterns

### CMOAgent Instantiation

```python
from cmo_agent import CMOAgent

agent = CMOAgent(
    agent_id="cmo",
    purpose="Marketing strategy, brand management, and market analysis",
    adapter_name="marketing",
)

await agent.initialize()
await agent.start()
```

### Agent Inheritance Chain

```
agent_framework.Agent (Microsoft)
    └── PurposeDrivenAgent  (purpose-driven-agent)
            └── LeadershipAgent  (leadership-agent)
                    └── CMOAgent  (this package)
```

### Agent Type Declaration

```python
from leadership_agent import LeadershipAgent

class CMOAgent(LeadershipAgent):
    """Chief Marketing Officer — marketing and leadership dual-purpose agent."""

    def get_agent_type(self) -> list[str]:
        return ["marketing", "leadership"]
```

### LoRA Adapter

`CMOAgent` uses the `marketing` LoRA adapter, enabling domain-specific marketing reasoning:

```python
CMOAgent(adapter_name="marketing")  # → marketing domain LoRA adapter
```

## Testing Workflow

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v --rootdir=.

# With coverage
pytest tests/ --cov=cmo_agent --cov-report=term-missing --rootdir=.

# Lint
pylint src/cmo_agent

# Type check
mypy src/cmo_agent

# Specific test
pytest tests/test_cmo_agent.py -v -k "test_initialize" --rootdir=.
```

**Note**: Use `--rootdir=.` to avoid pytest namespace conflicts when running multiple C-suite agent repos in the same environment.

**CI**: GitHub Actions runs `pytest` across Python 3.10, 3.11, and 3.12 on every push/PR to `main`.

→ **CI workflow**: `.github/workflows/ci.yml`

## Deployment

```bash
# Deploy via the aos-infrastructure orchestrator (recommended), or directly:
azd deploy cmo-agent
```

→ **Deploy workflow**: `.github/workflows/deploy.yml`  
→ **Azure config**: `azure.yaml`

## Related Repositories

| Repository | Role |
|-----------|------|
| [leadership-agent](https://github.com/ASISaga/leadership-agent) | `LeadershipAgent` base class and boardroom tooling |
| [purpose-driven-agent](https://github.com/ASISaga/purpose-driven-agent) | `PurposeDrivenAgent` foundational base class |
| [ceo-agent](https://github.com/ASISaga/ceo-agent) | CEO boardroom coordinator |
| [cfo-agent](https://github.com/ASISaga/cfo-agent) | CFO boardroom specialist |
| [cto-agent](https://github.com/ASISaga/cto-agent) | CTO boardroom specialist |
| [cso-agent](https://github.com/ASISaga/cso-agent) | CSO boardroom specialist |
| [aos-kernel](https://github.com/ASISaga/aos-kernel) | AOS kernel (orchestration, A2A tooling) |
| [realm-of-agents](https://github.com/ASISaga/realm-of-agents) | Agent catalog (registers this agent) |
| [aos-infrastructure](https://github.com/ASISaga/aos-infrastructure) | Infrastructure deployment |

## Key Design Principles

1. **Perpetual** — Runs indefinitely as an Azure Functions app; awakens on boardroom events
2. **Marketing-first** — Decisions are evaluated through a marketing strategy and brand management lens
3. **Boardroom specialist** — Participates as the marketing domain expert in CEO-coordinated boardroom sessions
4. **Thin delegation** — Inherits all boardroom capabilities from `LeadershipAgent`
5. **Foundry-registered** — Registered once with the Foundry Agent Service; participates in A2A orchestrations

## References

→ **Agent framework**: `.github/specs/agent-intelligence-framework.md`  
→ **Conventional tools**: `.github/docs/conventional-tools.md`  
→ **Python coding standards**: `.github/instructions/python.instructions.md`  
→ **Azure Functions patterns**: `.github/instructions/azure-functions.instructions.md`
