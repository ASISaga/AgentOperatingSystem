---
name: leadership-agent
description: Expert knowledge for developing, extending, testing, and deploying LeadershipAgent in the Agent Operating System (AOS). Covers leadership-domain LoRA adapter, layer stacking, decision-making skills, and Azure deployment via PurposeDrivenAgent.deploy().
---

# LeadershipAgent — Copilot Intelligence

## Description
Expert knowledge for working with **LeadershipAgent** in the Agent Operating System (AOS).
LeadershipAgent extends `PurposeDrivenAgent` with a single leadership layer that contributes
the `"leadership"` LoRA adapter, leadership-domain context, and decision-making skills.

## When to Use This Skill
- Creating or extending LeadershipAgent-based agents
- Implementing decision-making and stakeholder coordination
- Understanding the leadership LoRA adapter configuration
- Adding new leadership skills or context entries
- Deploying a LeadershipAgent to Azure
- Writing tests for LeadershipAgent behaviour

## Architecture

### Inheritance Chain
```
PurposeDrivenAgent   (base layer — empty by default unless adapter_name is provided)
└── LeadershipAgent  (adds Layer 0: adapter="leadership", context, skills)
    └── CMOAgent     (adds Layer 1: adapter="marketing",  context, skills)
```

### What LeadershipAgent Adds
| Property | Value |
|----------|-------|
| LoRA adapter | `"leadership"` (leadership vocabulary, persona, domain knowledge) |
| Context keys | `domain`, `purpose`, `capabilities` |
| Skills | `make_decision`, `consult_stakeholders` |

### Layer Stack
```python
agent = LeadershipAgent(agent_id="ceo", purpose="Strategic oversight")
agent.get_adapters()        # ["leadership"]
agent.get_all_skills()      # ["make_decision", "consult_stakeholders"]
agent.get_layer_contexts()  # {"domain": "leadership", "purpose": "...", "capabilities": [...]}
```

## Code Patterns

### Creating a LeadershipAgent
```python
from AgentOperatingSystem.agents import LeadershipAgent

agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions, resource allocation",
    success_criteria=["Revenue growth", "Team expansion"],
    adapter_name="ceo",   # overrides default "leadership" adapter name
)

await agent.initialize()  # stores purpose + leadership layer context in MCP
await agent.start()       # begins perpetual operation
```

### Using Leadership Skills
```python
# Make a decision
decision = await agent.make_decision(
    context={"topic": "hire_engineer", "budget": 150000},
    mode="autonomous"
)

# Consult stakeholders (requires message bus integration)
responses = await agent.consult_stakeholders(
    stakeholders=["cfo", "coo"],
    topic="budget_increase",
    context={"current_budget": 1_000_000},
)
```

### Extending LeadershipAgent with a New Layer
```python
class CFOAgent(LeadershipAgent):
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            purpose="Financial oversight and capital allocation",
            adapter_name=None,   # LeadershipAgent registers its own layer
        )
        self._add_layer(
            adapter_name="finance",
            context={
                "domain": "finance",
                "capabilities": ["budget_management", "investment_analysis"],
            },
            skills=["analyze_budget", "approve_expenditure"],
        )
```

### Deploying LeadershipAgent to Azure
```python
# Called from a derived-agent GitHub workflow
agent = LeadershipAgent(
    agent_id="ceo",
    purpose="Strategic oversight",
)
return_code = agent.deploy(
    environment="prod",
    resource_group="leadership-agents-rg",
    location="eastus",
)
assert return_code == 0
```

### GitHub Workflow — Derived Agent Deployment
```yaml
# .github/workflows/deploy.yml  (in the derived-agent repository)
name: Deploy LeadershipAgent

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: Target environment
        required: true
        default: dev

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install agentoperatingsystem[full]  # published package, or adjust to your setup

      - name: Deploy LeadershipAgent to Azure
        run: |
          python - <<'EOF'
          from AgentOperatingSystem.agents import LeadershipAgent
          agent = LeadershipAgent(agent_id="${{ github.event.repository.name }}", purpose="Strategic oversight")
          rc = agent.deploy(
              environment="${{ inputs.environment || 'dev' }}",
              resource_group="${{ vars.AZURE_RESOURCE_GROUP }}",
          )
          exit(rc)
          EOF
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Testing Patterns

### Unit Tests
```python
import pytest
from AgentOperatingSystem.agents import LeadershipAgent


class TestLeadershipAgent:

    def test_leadership_layer_registered(self):
        agent = LeadershipAgent(agent_id="test_leader", purpose="Lead the team")
        assert len(agent._layers) == 1
        assert agent._layers[0]["adapter"] == "leadership"
        assert "decision_making" in agent._layers[0]["context"]["capabilities"]

    def test_purpose_in_layer_context(self):
        agent = LeadershipAgent(agent_id="test_leader", purpose="Lead the team")
        ctx = agent.get_layer_contexts()
        assert ctx["purpose"] == "Lead the team"

    def test_default_adapter_is_leadership(self):
        agent = LeadershipAgent(agent_id="l", purpose="Lead")
        assert agent.adapter_name == "leadership"

    def test_custom_adapter_name(self):
        agent = LeadershipAgent(agent_id="ceo", purpose="CEO duties", adapter_name="ceo")
        assert agent.adapter_name == "ceo"
        assert agent.get_adapters() == ["ceo"]

    @pytest.mark.asyncio
    async def test_make_decision(self):
        agent = LeadershipAgent(agent_id="l", purpose="Lead")
        await agent.initialize()
        decision = await agent.make_decision({"topic": "hire"})
        assert "decision" in decision
        assert decision["agent_id"] == "l"
        await agent.stop()
```

## Common Issues and Solutions

### Issue: Decision-making returns "pending"
**Cause**: `_evaluate_decision()` is not overridden.
**Solution**: Override `_evaluate_decision()` in your subclass with actual decision logic.

### Issue: `consult_stakeholders` raises `NotImplementedError`
**Cause**: Stakeholder consultation requires message bus integration.
**Solution**: Override `consult_stakeholders()` and inject the message bus client.

### Issue: Custom adapter not picked up
**Cause**: `adapter_name` is passed but `_add_layer()` uses the default `"leadership"`.
**Solution**: Pass `adapter_name` to `LeadershipAgent.__init__()` — it is forwarded to `_add_layer()`.

## File Locations
- `src/AgentOperatingSystem/agents/leadership_agent.py` — LeadershipAgent source
- `src/AgentOperatingSystem/agents/purpose_driven.py` — PurposeDrivenAgent base (includes `deploy()`)
- `tests/test_agent_personas.py` — Layer-stacking tests
- `tests/test_perpetual_agents.py` — Lifecycle tests

## Related Skills
- `perpetual-agents` — PurposeDrivenAgent patterns and lifecycle
- `cmo-agent` — CMOAgent (extends LeadershipAgent with a marketing layer)
- `azure-functions` — Deploying agents to Azure Functions
- `async-python-testing` — Testing async agent code
