# Agent Configuration Skill - LLM-First Architecture

## Overview

This skill covers configuring LLM-First Purpose-Driven Agents using YAML with verbose purpose descriptions.

**PurposeDrivenAgent is the fundamental LLM-first agent class in AOS.** Unlike conventional logic-based agents, PurposeDrivenAgents operate through LLM reasoning over comprehensive purpose descriptions, not hard-coded decision logic.

Learn how to:
- Create YAML files with verbose purpose descriptions
- Understand LLM-first architecture (purposes as LLM context, not code)
- Map verbose purposes to LoRA adapters
- Configure MCP tools
- Load LLM-first agents from YAML

## Key Concepts

### LLM-First Architecture

**PurposeDrivenAgents are LLM-first, not conventional logic-based agents:**

- **Verbose Purposes**: Comprehensive, multi-line purpose descriptions (not brief summaries)
- **LLM Context Conversion**: Purposes converted to LLM context and passed to LoRA adapters
- **LLM Reasoning**: All behavior emerges from LLM reasoning over purpose context
- **No Hard-Coded Logic**: Decisions come from LLM, not conditional statements
- **Configuration-Driven**: Agents created from YAML only (no code-based initialization)

### PurposeDrivenAgent as the Fundamental LLM-First Agent

**PurposeDrivenAgent** contains all core LLM-first functionality:
- Converts verbose purposes to LLM context
- Passes purpose context to LoRA adapters
- Multi-purpose support and adapter switching
- YAML configuration loading
- Purpose-to-adapter mapping
- All repetitive/core agent operations

**Derived agents** (LeadershipAgent, CMOAgent) are lean wrappers that:
- Provide domain-specific defaults only
- Add minimal domain-specific methods (if needed)
- Are YAML-configured with verbose purposes
- Inherit all LLM-first core functionality

### Verbose Purposes for LLM Context

The fundamental principle: **purposes must be verbose and comprehensive** to provide rich LLM context.

**Bad (too brief):**
```yaml
description: "Marketing: Brand strategy and customer acquisition"
```

**Good (verbose for LLM):**
```yaml
description: |
  You are the Chief Marketing Officer with deep expertise in marketing strategy.
  
  Your Purpose:
  Develop and execute comprehensive marketing strategies that drive sustainable 
  brand growth and customer acquisition. You operate at the intersection of data 
  analytics, creative storytelling, and strategic business planning.
  
  Key Responsibilities:
  - Develop data-driven marketing strategies
  - Build strong brand identity and positioning
  - Design customer acquisition programs
  - Conduct market research and analysis
  ...
  
  Decision-Making Approach:
  - Base decisions on data and insights
  - Balance short-term wins with long-term brand building
  - Consider customer lifetime value
  ...
```

### Purpose-to-Adapter Mapping

1. **Verbose Purposes** - Comprehensive descriptions become LLM context
2. **LoRA Adapters** - Receive purpose context and provide domain knowledge
3. **LLM Reasoning** - LLM reasons over purpose context to guide behavior
4. **MCP Integration** - Provides state preservation and tool access

### YAML Configuration Structure

Every LLM-first agent configuration includes:
- `agent_id` - Unique identifier
- `agent_type` - Type of agent
- `purposes` - Array with **verbose** descriptions (multi-line, comprehensive)
- `mcp_tools` - MCP tools required
- `capabilities` - List of capabilities

## Examples

### Verbose Purpose Agent (CEO)

```yaml
agent_id: ceo
agent_type: purpose_driven

purposes:
  - name: strategic_oversight
    description: |
      You are the Chief Executive Officer (CEO), responsible for overall 
      strategic direction and operational success.
      
      Your Purpose:
      Provide visionary leadership and strategic oversight to drive sustainable 
      company growth while balancing stakeholder interests...
      
      Core Responsibilities:
      - Set and communicate company vision and strategic objectives
      - Make high-impact decisions on direction and investments
      - Ensure alignment across all departments
      - Manage board, investor, and stakeholder relationships
      
      Decision-Making Framework:
      - Balance short-term performance with long-term sustainability
      - Consider impact on all stakeholders
      - Base decisions on data and strategic foresight
      ...
    adapter_name: ceo  # Receives verbose purpose as LLM context

mcp_tools:
  - server_name: "analytics"
    tool_name: "get_company_metrics"

capabilities:
  - "Strategic planning and vision setting"
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
