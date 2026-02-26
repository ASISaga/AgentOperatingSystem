---
name: cmo-agent
description: Expert knowledge for developing, extending, testing, and deploying CMOAgent in the Agent Operating System (AOS). Covers marketing-domain LoRA adapter, dual-layer stacking (leadership + marketing), purpose-driven execution, and Azure deployment via PurposeDrivenAgent.deploy().
---

# CMOAgent — Copilot Intelligence

## Description
Expert knowledge for working with **CMOAgent** (Chief Marketing Officer) in the Agent Operating System (AOS).
CMOAgent extends `LeadershipAgent` with a marketing layer that contributes the `"marketing"` LoRA adapter,
marketing-domain context, and marketing skills — resulting in a two-layer agent.

## When to Use This Skill
- Creating or extending CMOAgent-based agents
- Implementing marketing strategy and brand management
- Understanding the dual-layer (leadership + marketing) LoRA adapter configuration
- Switching between leadership and marketing adapter contexts at runtime
- Deploying a CMOAgent to Azure
- Writing tests for CMOAgent behaviour

## Architecture

### Inheritance Chain
```
PurposeDrivenAgent   (base)
└── LeadershipAgent  (Layer 0: adapter="leadership", domain context, decision skills)
    └── CMOAgent     (Layer 1: adapter="marketing",  domain context, marketing skills)
```

### What Each Layer Contributes
| Layer | Class | LoRA Adapter | Context Keys | Skills |
|-------|-------|--------------|--------------|--------|
| 0 | LeadershipAgent | `"leadership"` | `domain`, `purpose`, `capabilities` | `make_decision`, `consult_stakeholders` |
| 1 | CMOAgent | `"marketing"` | `domain`, `marketing_purpose`, `capabilities` | `analyze_market`, `execute_with_purpose`, `manage_brand` |

### Layer Stack
```python
cmo = CMOAgent(agent_id="cmo")
cmo.get_adapters()        # ["leadership", "marketing"]
cmo.get_all_skills()      # ["make_decision", "consult_stakeholders", "analyze_market", ...]
cmo.get_layer_contexts()  # merged dict from both layers; "domain" = "marketing" (last wins)
cmo.adapter_name          # "marketing"  (most specific / last added)
```

## Code Patterns

### Creating a CMOAgent
```python
from AgentOperatingSystem.agents import CMOAgent

cmo = CMOAgent(
    agent_id="cmo",
    marketing_purpose="Brand strategy and customer acquisition",
    leadership_purpose="Strategic decision-making and team guidance",
    marketing_adapter_name="marketing",
    leadership_adapter_name="leadership",
)

await cmo.initialize()  # stores both layer contexts in MCP
await cmo.start()       # begins perpetual operation
```

### Purpose-Scoped Execution
```python
# Execute a task using the marketing adapter
result = await cmo.execute_with_purpose(
    task={"type": "campaign_launch", "budget": 50_000},
    purpose_type="marketing",
)

# Execute a task using the leadership adapter
decision = await cmo.execute_with_purpose(
    task={"type": "resource_allocation"},
    purpose_type="leadership",
)
```

### Getting the Active Adapter for a Purpose
```python
marketing_adapter = cmo.get_adapter_for_purpose("marketing")  # "marketing"
leadership_adapter = cmo.get_adapter_for_purpose("leadership") # "leadership"
```

### Status Reporting
```python
status = await cmo.get_status()
# {
#   "agent_id": "cmo",
#   "adapters": ["leadership", "marketing"],
#   "purposes": {
#     "marketing": {"description": "...", "adapter": "marketing"},
#     "leadership": {"description": "...", "adapter": "leadership"},
#   },
#   ...
# }
```

### Deploying CMOAgent to Azure
```python
# Called from the derived-agent GitHub workflow
cmo = CMOAgent(agent_id="cmo")
return_code = cmo.deploy(
    environment="prod",
    resource_group="marketing-agents-rg",
    location="eastus",
)
assert return_code == 0
```

### GitHub Workflow — Derived Agent Deployment
```yaml
# .github/workflows/deploy.yml  (in the derived CMOAgent repository)
name: Deploy CMOAgent

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

      - name: Deploy CMOAgent to Azure
        run: |
          python - <<'EOF'
          from AgentOperatingSystem.agents import CMOAgent
          cmo = CMOAgent(agent_id="${{ github.event.repository.name }}")
          rc = cmo.deploy(
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
from AgentOperatingSystem.agents import CMOAgent


class TestCMOAgent:

    def test_two_layers_registered(self):
        cmo = CMOAgent(agent_id="cmo")
        assert len(cmo._layers) == 2
        assert cmo._layers[0]["adapter"] == "leadership"
        assert cmo._layers[1]["adapter"] == "marketing"

    def test_get_adapters_order(self):
        """Leadership layer is registered first, then marketing."""
        cmo = CMOAgent(agent_id="cmo")
        assert cmo.get_adapters() == ["leadership", "marketing"]

    def test_adapter_name_is_most_specific(self):
        """adapter_name always reflects the last-added layer."""
        cmo = CMOAgent(agent_id="cmo")
        assert cmo.adapter_name == "marketing"

    def test_marketing_purpose_in_context(self):
        cmo = CMOAgent(agent_id="cmo", marketing_purpose="Grow the brand")
        ctx = cmo.get_layer_contexts()
        assert ctx["marketing_purpose"] == "Grow the brand"

    def test_get_adapter_for_purpose(self):
        cmo = CMOAgent(agent_id="cmo")
        assert cmo.get_adapter_for_purpose("marketing") == "marketing"
        assert cmo.get_adapter_for_purpose("leadership") == "leadership"

    def test_invalid_purpose_raises(self):
        cmo = CMOAgent(agent_id="cmo")
        with pytest.raises(ValueError, match="Unknown purpose type"):
            cmo.get_adapter_for_purpose("unknown")

    def test_marketing_skills_present(self):
        cmo = CMOAgent(agent_id="cmo")
        skills = cmo.get_all_skills()
        assert "make_decision" in skills          # from leadership layer
        assert "execute_with_purpose" in skills   # from marketing layer

    @pytest.mark.asyncio
    async def test_get_status(self):
        cmo = CMOAgent(agent_id="cmo")
        await cmo.initialize()
        status = await cmo.get_status()
        assert status["adapters"] == ["leadership", "marketing"]
        assert "marketing" in status["purposes"]
        assert "leadership" in status["purposes"]
        await cmo.stop()
```

## Common Issues and Solutions

### Issue: `execute_with_purpose` resets adapter after error
**Cause**: The method uses a try/finally block to restore `adapter_name` — this is by design.
**Solution**: No action needed; the original adapter is always restored.

### Issue: `get_layer_contexts()["domain"]` returns `"marketing"` not `"leadership"`
**Cause**: The marketing layer (added last) overrides the `"domain"` key from the leadership layer.
**Solution**: This is expected — access individual layers via `cmo._layers[0]` and `cmo._layers[1]`.

### Issue: Custom adapter names not propagated
**Cause**: `marketing_adapter_name` / `leadership_adapter_name` default to `"marketing"` / `"leadership"`.
**Solution**: Pass explicit names in the constructor: `CMOAgent(marketing_adapter_name="brand", leadership_adapter_name="exec")`.

## File Locations
- `src/AgentOperatingSystem/agents/cmo_agent.py` — CMOAgent source
- `src/AgentOperatingSystem/agents/leadership_agent.py` — LeadershipAgent (parent)
- `src/AgentOperatingSystem/agents/purpose_driven.py` — PurposeDrivenAgent base (includes `deploy()`)
- `tests/test_agent_personas.py` — Layer-stacking tests for CMOAgent
- `tests/test_perpetual_agents.py` — Lifecycle tests

## Related Skills
- `perpetual-agents` — PurposeDrivenAgent patterns and lifecycle
- `leadership-agent` — LeadershipAgent (parent of CMOAgent)
- `azure-functions` — Deploying agents to Azure Functions
- `async-python-testing` — Testing async agent code
