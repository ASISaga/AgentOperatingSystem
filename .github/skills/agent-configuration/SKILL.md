# Agent Configuration Skill

## Overview

This skill covers configuring Purpose-Driven Agents using YAML configuration files. Learn how to:
- Create agent.yaml files
- Map purposes to LoRA adapters
- Configure MCP tools
- Load agents from YAML

## Key Concepts

### Purpose-to-Adapter Mapping

The fundamental architectural concept is mapping agent purposes to LoRA adapters:

1. **LoRA Adapters** - Provide domain-specific knowledge (language, vocabulary, concepts, agent persona)
2. **Core Purposes** - Added to primary LLM context to guide agent behavior
3. **MCP Integration** - Provides context management and domain-specific tools

### YAML Configuration Structure

Every agent configuration includes:
- `agent_id` - Unique identifier
- `agent_type` - Type of agent (purpose_driven, leadership, cmo, etc.)
- `purposes` - Array of purpose definitions with adapter mappings
- `mcp_tools` - MCP tools required by the agent
- `capabilities` - List of agent capabilities

## Examples

### Single-Purpose Agent (CEO)

```yaml
agent_id: ceo
agent_type: purpose_driven

purposes:
  - name: strategic_oversight
    description: "Strategic oversight and decision-making for company growth"
    adapter_name: ceo  # Maps to "ceo" LoRA adapter
    success_criteria:
      - "Achieve quarterly revenue targets"
      - "Maintain strategic alignment"

mcp_tools:
  - server_name: "analytics"
    tool_name: "get_company_metrics"

capabilities:
  - "Strategic planning and oversight"
  - "Company-wide decision-making"
```

### Multi-Purpose Agent (CMO)

```yaml
agent_id: cmo
agent_type: cmo

# CMO has TWO purposes mapped to TWO LoRA adapters
purposes:
  - name: marketing
    description: "Marketing: Brand strategy and customer acquisition"
    adapter_name: marketing  # Maps to "marketing" LoRA adapter
    
  - name: leadership
    description: "Leadership: Strategic decision-making"
    adapter_name: leadership  # Maps to "leadership" LoRA adapter

mcp_tools:
  - server_name: "analytics"
    tool_name: "get_marketing_metrics"
  - server_name: "crm"
    tool_name: "get_customer_insights"

capabilities:
  - "Marketing strategy development"
  - "Cross-functional team leadership"
```

## Usage

### Loading Agents from YAML

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent, CMOAgent

# Load single-purpose agent
ceo = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
await ceo.initialize()
await ceo.start()

# Load multi-purpose agent
cmo = CMOAgent.from_yaml("config/agents/cmo_agent.yaml")
await cmo.initialize()

# Execute with specific purpose/adapter
await cmo.execute_with_purpose(task, purpose_type="marketing")
await cmo.execute_with_purpose(task, purpose_type="leadership")
```

### Backward Compatibility

Code-based agent creation still works for backward compatibility:

```python
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    adapter_name="ceo"
)
```

## Implementation Details

### PurposeDrivenAgent

The base class supports:
- `from_yaml(yaml_path)` - Class method to load from YAML
- Multi-purpose configuration via `purposes` parameter
- Automatic purpose-to-adapter mapping

### CMOAgent & LeadershipAgent

Extended classes that:
- Support loading from YAML with `from_yaml(yaml_path)`
- Maintain purpose-adapter mappings
- Allow switching between adapters for different tasks

## Files

- **Agent Classes**:
  - `src/AgentOperatingSystem/agents/purpose_driven.py`
  - `src/AgentOperatingSystem/agents/leadership_agent.py`
  - `src/AgentOperatingSystem/agents/cmo_agent.py`

- **Example Configurations**:
  - `config/agents/ceo_agent.yaml`
  - `config/agents/leadership_agent.yaml`
  - `config/agents/cmo_agent.yaml`

- **Documentation**:
  - `docs/agent-configuration-schema.md` - Complete schema reference

## Testing

Test YAML configuration loading:

```bash
# Test YAML parsing
python tests/test_yaml_parsing.py

# Test agent loading (requires dependencies)
pytest tests/test_agent_yaml_config.py -v
```

## Common Tasks

### Creating a New Agent Configuration

1. Copy an existing agent.yaml file
2. Update `agent_id` and `agent_type`
3. Define `purposes` with appropriate adapter mappings
4. List required `mcp_tools`
5. Specify agent `capabilities`
6. Load and test:
   ```python
   agent = PurposeDrivenAgent.from_yaml("config/agents/new_agent.yaml")
   ```

### Adding a Purpose to an Existing Agent

1. Add new purpose entry to the `purposes` array:
   ```yaml
   purposes:
     - name: new_purpose
       description: "Purpose description"
       adapter_name: new_adapter
       success_criteria:
         - "Success metric 1"
   ```
2. Ensure corresponding LoRA adapter exists
3. Update agent class if needed for multi-purpose support

## Best Practices

1. **Purpose-Adapter Alignment**: Ensure each purpose has a corresponding LoRA adapter
2. **Clear Descriptions**: Write descriptive purposes that guide agent behavior
3. **Success Criteria**: Define measurable success criteria for each purpose
4. **MCP Tool Selection**: Only include MCP tools the agent actually needs
5. **Capability Documentation**: List all agent capabilities for discoverability

## References

- [Agent Configuration Schema](../../docs/agent-configuration-schema.md)
- [PurposeDrivenAgent Source](../../src/AgentOperatingSystem/agents/purpose_driven.py)
- [CMOAgent Source](../../src/AgentOperatingSystem/agents/cmo_agent.py)
