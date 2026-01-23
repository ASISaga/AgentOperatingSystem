# Agent Configuration YAML Schema

This document describes the YAML schema for configuring Purpose-Driven Agents in the Agent Operating System (AOS).

## Overview

Each agent derived from PurposeDrivenAgent can be configured using an `agent.yaml` file. This file defines:
- The agent's purpose(s)
- LoRA adapters required for each purpose
- MCP tools needed
- Agent capabilities
- System prompts and metadata

## Schema Structure

### Top-Level Fields

```yaml
# Required Fields
agent_id: string           # Unique identifier for the agent
agent_type: string         # Type of agent (purpose_driven, leadership, cmo, etc.)

# Agent Identity
name: string              # Human-readable name
role: string              # Agent role/title

# Purpose Configuration (array of purposes)
purposes:
  - name: string                    # Purpose identifier
    description: string             # Full purpose description (added to LLM context)
    scope: string                   # Scope/boundaries of the purpose
    adapter_name: string            # LoRA adapter name for this purpose
    success_criteria: [string]      # List of success criteria

# MCP Tools
mcp_tools:
  - server_name: string            # MCP server name
    tool_name: string              # Tool name within server
    configuration: object          # Optional tool-specific config

# Capabilities
capabilities: [string]             # List of agent capabilities

# Optional Fields
system_message: string            # Custom system message
enabled: boolean                  # Whether agent is enabled (default: true)
metadata: object                  # Additional metadata
```

## Purpose-to-Adapter Mapping

The key architectural concept is mapping purposes to LoRA adapters:

1. **LoRA Adapters** provide domain-specific knowledge (language, vocabulary, concepts, agent persona)
2. **Core Purposes** are added to the primary LLM context to guide behavior
3. **MCP Integration** provides context management and domain-specific tools

### Single-Purpose Agent Example

```yaml
agent_id: ceo
purposes:
  - name: strategic_oversight
    description: "Strategic oversight and decision-making for company growth"
    adapter_name: ceo  # Maps to "ceo" LoRA adapter
```

### Multi-Purpose Agent Example

```yaml
agent_id: cmo
purposes:
  - name: marketing
    description: "Marketing: Brand strategy and customer acquisition"
    adapter_name: marketing  # Maps to "marketing" LoRA adapter
  
  - name: leadership
    description: "Leadership: Strategic decision-making"
    adapter_name: leadership  # Maps to "leadership" LoRA adapter
```

## Agent Types

- **purpose_driven**: Generic PurposeDrivenAgent
- **leadership**: LeadershipAgent with decision-making capabilities
- **cmo**: CMOAgent with marketing and leadership purposes
- Custom agent types can be defined

## MCP Tools Configuration

MCP tools provide domain-specific capabilities to agents:

```yaml
mcp_tools:
  - server_name: "analytics"
    tool_name: "get_marketing_metrics"
    configuration:
      metrics:
        - "conversion_rate"
        - "customer_acquisition_cost"
```

## Complete Examples

See the following example configurations:
- `config/agents/ceo_agent.yaml` - Single-purpose CEO agent
- `config/agents/leadership_agent.yaml` - Leadership agent
- `config/agents/cmo_agent.yaml` - Multi-purpose CMO agent

## Usage

### Loading an Agent from YAML

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Load agent from YAML configuration
agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
await agent.initialize()
await agent.start()
```

### Creating Multi-Purpose Agents

```python
from AgentOperatingSystem.agents import CMOAgent

# Load CMO with dual purposes from YAML
cmo = CMOAgent.from_yaml("config/agents/cmo_agent.yaml")

# Execute tasks with specific purpose/adapter
await cmo.execute_with_purpose(task, purpose_type="marketing")
await cmo.execute_with_purpose(task, purpose_type="leadership")
```

## Validation

The system validates:
- Required fields are present
- Purpose-to-adapter mappings are valid
- MCP tool references are correct
- Agent type is supported

## Migration from Code-Based Configuration

Existing agents created programmatically can be converted to YAML:

```python
# Before (code-based)
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight",
    adapter_name="ceo"
)

# After (YAML-based)
# Create config/agents/ceo_agent.yaml
agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
```

Both methods are supported for backward compatibility.
