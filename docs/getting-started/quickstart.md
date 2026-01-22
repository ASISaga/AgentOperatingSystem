# Quick Start Guide

Get started with the Agent Operating System quickly.

## Installation

```bash
# Install from GitHub
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git

# Or install with all optional dependencies
pip install "AgentOperatingSystem[full]"
```

See [Installation Guide](installation.md) for more options.

## Basic Example

```python
from AgentOperatingSystem import AgentOperatingSystem
from AgentOperatingSystem.agents import LeadershipAgent

# 1. Initialize the Operating System
config = {
    "azure": {
        "subscription_id": "your-subscription-id",
        "resource_group": "aos-resources"
    }
}
aos = AgentOperatingSystem(config)

# 2. Define a Custom Agent (extends AOS base class)
class CEOAgent(LeadershipAgent):
    def __init__(self):
        super().__init__(
            agent_id="ceo",
            name="Chief Executive Officer",
            role="CEO"
        )
    
    async def make_decision(self, context):
        # Use AOS services
        precedents = await self.knowledge.find_similar(context)
        risks = await self.governance.assess_risks(context)
        
        # Make decision
        decision = await self.analyze(context, precedents, risks)
        
        # Audit and broadcast
        await self.governance.audit(decision)
        await self.messaging.broadcast("decision_made", decision)
        
        return decision

# 3. Register and Run Agent
ceo = CEOAgent()
aos.register_agent(ceo)
aos.start()
```

## Perpetual Agent Example

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

# Create a purpose-driven perpetual agent
agent = PurposeDrivenAgent(
    agent_id="ceo",
    purpose="Strategic oversight and company growth",
    purpose_scope="Strategic planning, major decisions",
    success_criteria=["Revenue growth", "Team expansion"],
    adapter_name="ceo"
)

await agent.initialize()  # ContextMCPServer automatically created
await agent.start()       # Runs perpetually

# Purpose-driven operations
alignment = await agent.evaluate_purpose_alignment(action)
decision = await agent.make_purpose_driven_decision(context)
goal_id = await agent.add_goal("Increase revenue by 50%")
```

## Configuration-Driven Agent Deployment

Using RealmOfAgents, you can deploy agents with just configuration:

```json
{
  "agent_id": "cfo",
  "purpose": "Financial oversight and strategic planning",
  "domain_knowledge": {
    "domain": "cfo",
    "training_data_path": "training-data/cfo/scenarios.jsonl"
  },
  "mcp_tools": [
    {"server_name": "erpnext", "tool_name": "get_financial_reports"}
  ],
  "enabled": true
}
```

See [Azure Functions Infrastructure](azure-functions.md) for more details.

## Next Steps

- [Configuration Guide](../configuration.md) - Configure the system
- [Deployment Guide](deployment.md) - Deploy to production
- [Development Guide](../development.md) - Develop custom agents
- [Architecture Overview](../architecture/ARCHITECTURE.md) - Understand the architecture

## See Also

- [Installation Guide](installation.md) - Detailed installation instructions
- [System APIs](../reference/system-apis.md) - API reference
- [Perpetual Agents](../overview/perpetual-agents.md) - Understanding perpetual agents
