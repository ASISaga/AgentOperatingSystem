"""
Infrastructure-Level Agent Runtime Example

This example demonstrates how the AOS infrastructure (AgentRuntimeProvider) provides
Foundry Agent Service runtime with Llama 3.3 70B Instruct transparently for agents.

Key Points:
- PurposeDrivenAgent is pure Microsoft Agent Framework code
- AgentRuntimeProvider (infrastructure) provides Foundry runtime transparently
- Llama 3.3 70B Instruct with domain-specific LoRA adapters
- Stateful threads managed by infrastructure
- Agent code remains runtime-agnostic

Prerequisites:
1. Set up Azure AI Project endpoint
2. Deploy Llama 3.3 70B models with LoRA adapters
3. Configure environment variables:
   - AZURE_AI_PROJECT_ENDPOINT
   - AZURE_AI_MODEL_DEPLOYMENT (base: llama-3.3-70b-instruct)
   - Deploy LoRA-adapted models (e.g., llama-3.3-70b-ceo, llama-3.3-70b-cfo)
"""

import asyncio
import os
from AgentOperatingSystem.agents import PurposeDrivenAgent
from AgentOperatingSystem.runtime import AgentRuntimeProvider, RuntimeConfig


async def basic_example():
    """Basic example of using infrastructure runtime with PurposeDrivenAgent."""
    
    print("=== Basic Infrastructure Runtime Example ===\n")
    
    # 1. Create agent (pure Microsoft Agent Framework)
    agent = PurposeDrivenAgent(
        agent_id="ceo",
        purpose="Strategic oversight and decision-making",
        purpose_scope="Strategic planning, major decisions",
        adapter_name="ceo"  # Infrastructure uses this for LoRA adapter
    )
    await agent.initialize()
    
    # 2. Initialize infrastructure runtime provider
    runtime_config = RuntimeConfig.from_env()
    runtime = AgentRuntimeProvider(runtime_config)
    await runtime.initialize()
    
    # 3. Deploy agent to infrastructure runtime
    # This transparently deploys to Foundry with llama-3.3-70b-ceo
    foundry_agent = await runtime.deploy_agent(
        agent_id=agent.agent_id,
        purpose=agent.purpose,
        purpose_scope=agent.purpose_scope,
        adapter_name="ceo"  # Uses Llama 3.3 70B + CEO LoRA adapter
    )
    
    if foundry_agent:
        print(f"Agent deployed to infrastructure runtime:")
        print(f"  - Agent ID: {agent.agent_id}")
        print(f"  - Foundry Agent ID: {foundry_agent.id}")
        print(f"  - Model: llama-3.3-70b-ceo (with CEO LoRA adapter)")
    else:
        print("Running in simulation mode (no Foundry endpoint configured)")
    
    print()


async def process_event_example():
    """Example of processing events through infrastructure runtime."""
    
    print("=== Process Event Example ===\n")
    
    # Create and deploy agent
    agent = PurposeDrivenAgent(
        agent_id="cfo",
        purpose="Financial oversight and strategic planning",
        adapter_name="cfo"
    )
    await agent.initialize()
    
    runtime = AgentRuntimeProvider(RuntimeConfig.from_env())
    await runtime.initialize()
    
    await runtime.deploy_agent(
        agent_id=agent.agent_id,
        purpose=agent.purpose,
        adapter_name="cfo"  # Uses Llama 3.3 70B + CFO LoRA adapter
    )
    
    # Process event through infrastructure runtime
    result = await runtime.process_event(
        agent_id=agent.agent_id,
        event_type="FinancialReportRequested",
        payload={
            "quarter": "Q4",
            "year": 2024,
            "metrics": ["revenue", "profit_margin", "cash_flow"]
        }
    )
    
    print(f"Event processed:")
    print(f"  - Success: {result.get('success')}")
    print(f"  - Response: {result.get('response')}")
    print(f"  - Latency: {result.get('latency_ms', 0):.2f}ms")
    
    print()


async def multi_agent_example():
    """Example with multiple agents, each with domain-specific LoRA adapters."""
    
    print("=== Multi-Agent with Domain LoRA Adapters ===\n")
    
    # Initialize infrastructure runtime
    runtime = AgentRuntimeProvider(RuntimeConfig.from_env())
    await runtime.initialize()
    
    # Define multiple agents with different domain expertise
    agents_config = [
        {"agent_id": "ceo", "purpose": "Strategic oversight", "adapter": "ceo"},
        {"agent_id": "cfo", "purpose": "Financial planning", "adapter": "cfo"},
        {"agent_id": "cto", "purpose": "Technology strategy", "adapter": "cto"},
    ]
    
    # Deploy all agents to infrastructure runtime
    for config in agents_config:
        agent = PurposeDrivenAgent(
            agent_id=config["agent_id"],
            purpose=config["purpose"],
            adapter_name=config["adapter"]
        )
        await agent.initialize()
        
        foundry_agent = await runtime.deploy_agent(
            agent_id=agent.agent_id,
            purpose=agent.purpose,
            adapter_name=config["adapter"]
        )
        
        if foundry_agent:
            print(f"Deployed {config['agent_id']}:")
            print(f"  - Model: llama-3.3-70b-{config['adapter']}")
            print(f"  - Purpose: {config['purpose']}")
    
    # Get runtime status
    status = runtime.get_status()
    print(f"\nRuntime Status:")
    print(f"  - Active Agents: {status['active_agents']}")
    print(f"  - LoRA Adapters Enabled: {status['lora_adapters_enabled']}")
    print(f"  - Stateful Threads: {status['stateful_threads_enabled']}")
    
    print()


async def runtime_metrics_example():
    """Example demonstrating infrastructure runtime metrics."""
    
    print("=== Runtime Metrics Example ===\n")
    
    runtime = AgentRuntimeProvider(RuntimeConfig.from_env())
    await runtime.initialize()
    
    # Deploy agent
    agent = PurposeDrivenAgent(
        agent_id="test_agent",
        purpose="Testing metrics",
        adapter_name="ceo"
    )
    await agent.initialize()
    
    await runtime.deploy_agent(
        agent_id=agent.agent_id,
        purpose=agent.purpose,
        adapter_name="ceo"
    )
    
    # Process some events
    for i in range(3):
        await runtime.process_event(
            agent_id=agent.agent_id,
            event_type="TestEvent",
            payload={"test_id": i}
        )
    
    # Get metrics
    metrics = runtime.get_metrics()
    
    print("Infrastructure Runtime Metrics:")
    print(f"  - Total Agents Deployed: {metrics['total_agents_deployed']}")
    print(f"  - Total Events Processed: {metrics['total_events_processed']}")
    print(f"  - Successful Events: {metrics['successful_events']}")
    print(f"  - Failed Events: {metrics['failed_events']}")
    print(f"  - Average Latency: {metrics['average_latency_ms']:.2f}ms")
    print(f"  - Active Agents: {metrics['active_agents']}")
    print(f"  - Active Threads: {metrics['active_threads']}")
    
    print()


async def main():
    """Run all examples."""
    
    print("\n" + "="*60)
    print("Infrastructure-Level Agent Runtime Examples")
    print("Pure Microsoft Agent Framework + Foundry Runtime")
    print("Powered by Llama 3.3 70B Instruct with LoRA Adapters")
    print("="*60 + "\n")
    
    # Check if configuration is available
    if not os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
        print("⚠️  Warning: AZURE_AI_PROJECT_ENDPOINT not configured")
        print("These examples will run with simulated responses.\n")
        print("To use real infrastructure runtime:")
        print("1. Set AZURE_AI_PROJECT_ENDPOINT")
        print("2. Deploy Llama 3.3 70B models with LoRA adapters")
        print("   - Base: llama-3.3-70b-instruct")
        print("   - CEO: llama-3.3-70b-ceo")
        print("   - CFO: llama-3.3-70b-cfo")
        print("   - CTO: llama-3.3-70b-cto")
        print("3. Configure Azure authentication (DefaultAzureCredential)\n")
    
    try:
        # Run examples
        await basic_example()
        await process_event_example()
        await multi_agent_example()
        await runtime_metrics_example()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
