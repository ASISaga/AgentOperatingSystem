# Agent Configuration Skill

## Overview

This skill covers configuring Purpose-Driven Agents using YAML configuration files. 

**PurposeDrivenAgent is the fundamental agent class in AOS.** All specialized agents (LeadershipAgent, CMOAgent, etc.) are lean wrappers that inherit from PurposeDrivenAgent and are primarily configured via YAML.

Learn how to:
- Create agent.yaml files
- Map purposes to LoRA adapters
- Configure MCP tools
- Load agents from YAML
- Understand the lean agent architecture

## Key Concepts

### PurposeDrivenAgent as the Fundamental Agent

**PurposeDrivenAgent** contains all core functionality:
- Multi-purpose support and adapter switching
- YAML configuration loading
- Purpose-to-adapter mapping
- MCP tools integration
- Goal tracking and metrics
- All repetitive/core agent operations

**Derived agents** (LeadershipAgent, CMOAgent) are lean wrappers that:
- Provide domain-specific defaults
- Add domain-specific methods (if needed)
- Are primarily YAML-configured
- Inherit all core functionality from PurposeDrivenAgent

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

### PurposeDrivenAgent - The Fundamental Agent

PurposeDrivenAgent is the core agent class that contains ALL core functionality:

**Core Features:**
- `from_yaml(yaml_path)` - Load any agent type from YAML
- Multi-purpose configuration via `purposes` parameter
- Automatic purpose-to-adapter mapping via `purpose_adapter_mapping`
- `get_adapter_for_purpose(type)` - Retrieve adapter for a specific purpose
- `execute_with_purpose(task, type)` - Execute with specific adapter
- Goal tracking and progress management
- Purpose alignment evaluation
- Decision-making infrastructure
- MCP tools integration

**All repetitive/core functionality lives here.** Derived agents should only add domain-specific logic.

### LeadershipAgent & CMOAgent - Lean Wrappers

These are minimal wrappers over PurposeDrivenAgent:

**LeadershipAgent** (~143 lines):
- Provides leadership domain defaults
- Adds domain-specific methods: `make_decision()`, `consult_stakeholders()`
- Inherits all core functionality from PurposeDrivenAgent

**CMOAgent** (~61 lines):  
- Extends LeadershipAgent (inherits leadership capabilities)
- Provides CMO domain defaults
- Primarily YAML-configured
- No additional methods needed - uses inherited `execute_with_purpose()`

**Key principle:** Derived agents are lean. They provide defaults and domain-specific methods, but all core/repetitive functionality is in PurposeDrivenAgent.

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
