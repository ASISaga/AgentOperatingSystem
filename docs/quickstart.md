# Quick Start Guide

Get up and running with the Agent Operating System (AOS) in minutes.

---

## Prerequisites

- Python 3.9 or later
- Azure subscription (for production deployment)
- pip package manager

---

## Installation

### Option 1: Install from GitHub

```bash
# Basic installation
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git

# Install with all optional dependencies
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git[all]

# Install specific service groups
pip install git+https://github.com/ASISaga/AgentOperatingSystem.git[ml,mcp,azure]
```

### Option 2: Clone and Install Locally

```bash
# Clone the repository
git clone https://github.com/ASISaga/AgentOperatingSystem.git
cd AgentOperatingSystem

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e .[all]
```

### Verify Installation

```python
import AgentOperatingSystem
print(f"AOS Version: {AgentOperatingSystem.__version__}")
```

---

## Quick Start Examples

### 1. Create Your First Purpose-Driven Agent

```python
import asyncio
from AgentOperatingSystem.agents import PurposeDrivenAgent

async def main():
    # Create a purpose-driven perpetual agent
    agent = PurposeDrivenAgent(
        agent_id="assistant",
        purpose="Help users accomplish their daily tasks",
        purpose_scope="Task management, scheduling, reminders",
        success_criteria=["User satisfaction", "Task completion rate"],
        adapter_name="assistant"
    )
    
    # Initialize the agent (creates ContextMCPServer)
    await agent.initialize()
    
    # Start the agent (runs perpetually)
    await agent.start()
    
    # Evaluate purpose alignment
    action = "Schedule a meeting for tomorrow"
    alignment_score = await agent.evaluate_purpose_alignment(action)
    print(f"Purpose alignment: {alignment_score}")
    
    # Make a purpose-driven decision
    context = {
        "task": "Should I send a reminder email?",
        "user_preference": "minimal notifications"
    }
    decision = await agent.make_purpose_driven_decision(context)
    print(f"Decision: {decision}")
    
    # Add a goal aligned with purpose
    goal_id = await agent.add_goal(
        description="Increase user task completion rate by 20%",
        target_date="2026-12-31"
    )
    print(f"Goal added: {goal_id}")

# Run the example
asyncio.run(main())
```

### 2. Multi-Agent System with Orchestration

```python
import asyncio
from AgentOperatingSystem.agents import PurposeDrivenAgent, LeadershipAgent
from AgentOperatingSystem.orchestration import MultiAgentCoordinator

async def main():
    # Create coordinator
    coordinator = MultiAgentCoordinator()
    
    # Create specialized agents
    ceo_agent = PurposeDrivenAgent(
        agent_id="ceo",
        purpose="Strategic oversight and company growth",
        purpose_scope="Strategic planning, major decisions",
        adapter_name="ceo"
    )
    
    cfo_agent = PurposeDrivenAgent(
        agent_id="cfo",
        purpose="Financial management and fiscal responsibility",
        purpose_scope="Budgets, financial planning, cost control",
        adapter_name="cfo"
    )
    
    # Register agents with coordinator
    await coordinator.register_agent(ceo_agent)
    await coordinator.register_agent(cfo_agent)
    
    # Execute coordinated workflow
    workflow = {
        "name": "quarterly_planning",
        "tasks": [
            {"agent": "cfo", "action": "prepare_budget_forecast"},
            {"agent": "ceo", "action": "review_strategic_goals"},
            {"agent": "cfo", "action": "allocate_resources"}
        ]
    }
    
    result = await coordinator.execute_workflow(workflow)
    print(f"Workflow result: {result}")

asyncio.run(main())
```

### 3. Agent-to-Agent Communication (A2A)

```python
import asyncio
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.messaging import MessageBus

async def main():
    # Create message bus
    message_bus = MessageBus()
    
    # Create agents
    sales_agent = PurposeDrivenAgent(
        agent_id="sales",
        purpose="Drive revenue and customer acquisition",
        adapter_name="sales"
    )
    
    marketing_agent = PurposeDrivenAgent(
        agent_id="marketing",
        purpose="Brand awareness and lead generation",
        adapter_name="marketing"
    )
    
    # Initialize agents
    await sales_agent.initialize()
    await marketing_agent.initialize()
    
    # Register agents with message bus
    await message_bus.register_agent(sales_agent)
    await message_bus.register_agent(marketing_agent)
    
    # Send message from sales to marketing
    message = {
        "type": "collaboration_request",
        "content": "Need campaign for Q2 product launch",
        "priority": "high",
        "deadline": "2026-03-01"
    }
    
    await message_bus.send_message(
        from_agent="sales",
        to_agent="marketing",
        message=message
    )
    
    # Process messages
    await message_bus.process_messages()

asyncio.run(main())
```

### 4. ML Pipeline Integration with LoRAx

```python
import asyncio
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.ml import LoRAXServer, MLPipelineManager

async def main():
    # Initialize LoRAx server for multi-adapter serving
    lorax = LoRAXServer(
        base_model="meta-llama/Llama-3.1-8B-Instruct",
        max_adapters=100,
        gpu_memory_utilization=0.9
    )
    
    # Start LoRAx server
    await lorax.start()
    
    # Register LoRA adapters for different agents
    await lorax.register_adapter("ceo", "path/to/ceo_adapter")
    await lorax.register_adapter("cfo", "path/to/cfo_adapter")
    await lorax.register_adapter("cto", "path/to/cto_adapter")
    
    # Create agents (they'll use LoRAx automatically)
    ceo = PurposeDrivenAgent(
        agent_id="ceo",
        purpose="Strategic leadership",
        adapter_name="ceo"
    )
    
    # Perform inference (uses LoRAx)
    response = await ceo.infer(
        "What are our strategic priorities for Q2?"
    )
    print(f"CEO response: {response}")
    
    # Train a new adapter using ML Pipeline
    ml_manager = MLPipelineManager()
    
    await ml_manager.train_adapter(
        agent_role="cmo",
        training_params={
            "model_name": "meta-llama/Llama-3.1-8B-Instruct",
            "data_path": "./data/marketing_train.jsonl",
            "output_dir": "./outputs/cmo"
        },
        adapter_config={
            "task_type": "causal_lm",
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj"]
        }
    )

asyncio.run(main())
```

### 5. Self-Learning System with MCP Integration

```python
import asyncio
from AgentOperatingSystem.learning import SelfLearningAgent
from AgentOperatingSystem.mcp import MCPServiceBusClient

async def main():
    # Configure MCP servers
    domain_mcp_config = {
        "erp": {
            "uri": "wss://erp-mcp.example.com",
            "api_key": "your_erp_key"
        },
        "crm": {
            "uri": "wss://crm-mcp.example.com",
            "api_key": "your_crm_key"
        }
    }
    
    github_mcp_config = {
        "uri": "wss://github-mcp-server.example.com",
        "api_key": "your_github_token"
    }
    
    # Create self-learning agent
    agent = SelfLearningAgent(
        agent_id="business_assistant",
        purpose="Automate business processes",
        domain_mcp_config=domain_mcp_config,
        github_mcp_config=github_mcp_config
    )
    
    # Initialize agent
    await agent.initialize()
    
    # Execute business process (auto-learns if capability missing)
    result = await agent.execute_business_process(
        domain="erp",
        function_name="create_sales_order",
        parameters={
            "customer": "ACME Corp",
            "amount": 10000,
            "items": [{"sku": "PROD-001", "quantity": 5}]
        }
    )
    
    print(f"Process result: {result}")

asyncio.run(main())
```

### 6. Azure Foundry Integration (Llama 3.3 70B)

```python
import asyncio
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.ml import FoundryAgentServiceClient

async def main():
    # Initialize Foundry Agent Service client
    foundry_client = FoundryAgentServiceClient(
        endpoint="https://your-foundry-endpoint.azure.com",
        api_key="your-api-key",
        model="llama-3.3-70b"
    )
    
    # Create stateful thread for persistent conversations
    thread = await foundry_client.create_thread(
        metadata={"purpose": "strategic_planning"}
    )
    
    # Multi-turn conversation with context preservation
    response1 = await foundry_client.chat(
        thread_id=thread.id,
        message="What are the key trends in AI for 2026?"
    )
    
    print(f"Response 1: {response1}")
    
    # Context is preserved automatically
    response2 = await foundry_client.chat(
        thread_id=thread.id,
        message="How can we leverage these trends?"
    )
    
    print(f"Response 2: {response2}")

asyncio.run(main())
```

---

## Configuration

### Basic Configuration File

Create `config/aos_config.json`:

```json
{
  "orchestrator": {
    "type": "production",
    "version": "3.0.0"
  },
  "agents": {
    "max_concurrent": 100,
    "default_timeout": 300,
    "health_check_interval": 60
  },
  "storage": {
    "connection_string": "${AZURE_STORAGE_CONNECTION_STRING}",
    "container_name": "aos-data"
  },
  "messaging": {
    "connection_string": "${AZURE_SERVICEBUS_CONNECTION_STRING}",
    "topic_name": "agent-events"
  },
  "ml": {
    "enable_lorax": true,
    "base_model": "meta-llama/Llama-3.1-8B-Instruct",
    "cache_enabled": true
  }
}
```

### Environment Variables

Create `.env` file:

```bash
# Azure Services
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_SERVICEBUS_CONNECTION_STRING=Endpoint=sb://...
AZURE_KEYVAULT_URL=https://your-vault.vault.azure.net/

# Application Settings
AOS_ENV=development
LOG_LEVEL=INFO
ENABLE_SELF_LEARNING=true

# ML Settings
AZURE_ML_WORKSPACE=your-workspace
ENABLE_ML_CACHING=true
```

---

## Next Steps

### Learn More
- **[Architecture Guide](../ARCHITECTURE.md)** - Understand AOS architecture
- **[Agent Development](Implementation.md)** - Build custom agents
- **[Deployment Guide](deployment.md)** - Deploy to production
- **[Performance Guide](performance.md)** - Optimize for scale

### Explore Features
- **[ML Pipeline](LORAX.md)** - Machine learning integration
- **[MCP Integration](self_learning.md)** - Model Context Protocol
- **[Self-Learning](self_learning.md)** - Automatic capability enhancement
- **[A2A Communication](a2a_communication.md)** - Agent messaging

### Advanced Topics
- **[Extensibility](extensibility.md)** - Plugin framework
- **[Security](../ARCHITECTURE.md#security-architecture)** - Security best practices
- **[Testing](testing.md)** - Testing strategies

---

## Getting Help

- **[Documentation](.)** - Browse all documentation
- **[Examples](../examples/)** - See code examples
- **[Discussions](https://github.com/ASISaga/AgentOperatingSystem/discussions)** - Ask questions
- **[Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)** - Report bugs

---

**Ready to build?** Check out our [comprehensive examples](../examples/) or dive into the [full documentation](.).

