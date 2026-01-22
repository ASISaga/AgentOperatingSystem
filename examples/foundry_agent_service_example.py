"""
Azure Foundry Agent Service Integration Example

This example demonstrates how to use the Azure Foundry Agent Service with Llama 3.3 70B
as the core reasoning engine in the Agent Operating System.

Features demonstrated:
- Stateful Threads: Maintain conversation context across multiple interactions
- Entra Agent ID: Secure agent identity management
- Foundry Tools: Access to Azure AI Foundry tools and capabilities
- Fine-tuned Llama 3.3 70B: Leverage custom fine-tuned weights

Prerequisites:
1. Set up Azure Foundry Agent Service endpoint
2. Configure environment variables:
   - FOUNDRY_AGENT_SERVICE_ENDPOINT
   - FOUNDRY_AGENT_SERVICE_API_KEY
   - FOUNDRY_AGENT_ID (optional)
"""

import asyncio
import os
from AgentOperatingSystem.ml import FoundryAgentServiceClient, FoundryAgentServiceConfig
from AgentOperatingSystem.orchestration import ModelOrchestrator, ModelType


async def basic_example():
    """Basic example of using Foundry Agent Service."""
    
    print("=== Basic Foundry Agent Service Example ===\n")
    
    # Create client with default configuration
    config = FoundryAgentServiceConfig.from_env()
    client = FoundryAgentServiceClient(config)
    
    # Initialize the client
    await client.initialize()
    
    # Send a simple message
    response = await client.send_message(
        message="What are the key features of Llama 3.3 70B?",
        domain="ai_research"
    )
    
    if response.success:
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Tokens used: {response.usage.get('total_tokens', 'N/A')}")
    else:
        print(f"Error: {response.error}")
    
    print()


async def stateful_threads_example():
    """Example using stateful threads for multi-turn conversations."""
    
    print("=== Stateful Threads Example ===\n")
    
    # Create client
    config = FoundryAgentServiceConfig.from_env()
    client = FoundryAgentServiceClient(config)
    await client.initialize()
    
    # Create a new thread
    thread_id = await client.create_thread(metadata={"purpose": "financial_analysis"})
    print(f"Created thread: {thread_id}\n")
    
    # Multi-turn conversation
    messages = [
        "What were the Q3 revenue trends for our SaaS products?",
        "How does this compare to Q2?",
        "What should be our strategy for Q4?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"Turn {i}: {message}")
        
        response = await client.send_message(
            message=message,
            thread_id=thread_id,
            domain="financial_analysis"
        )
        
        if response.success:
            print(f"Response: {response.content}\n")
        else:
            print(f"Error: {response.error}\n")
    
    # Get thread info
    thread_info = await client.get_thread_info(thread_id)
    if thread_info:
        print(f"Thread Info:")
        print(f"  - Message count: {thread_info.message_count}")
        print(f"  - Last accessed: {thread_info.last_accessed}")
    
    print()


async def foundry_tools_example():
    """Example using Foundry Tools for enhanced capabilities."""
    
    print("=== Foundry Tools Example ===\n")
    
    # Create client with Foundry Tools enabled
    config = FoundryAgentServiceConfig.from_env()
    config.enable_foundry_tools = True
    client = FoundryAgentServiceClient(config)
    await client.initialize()
    
    # Send message with specific tools
    response = await client.send_message(
        message="Analyze customer sentiment from recent feedback data",
        domain="customer_analytics",
        tools=["sentiment_analysis", "data_aggregation", "visualization"]
    )
    
    if response.success:
        print(f"Response: {response.content}")
        print(f"Tools used: {', '.join(response.tools_used)}")
    else:
        print(f"Error: {response.error}")
    
    print()


async def model_orchestrator_integration():
    """Example integrating Foundry Agent Service with ModelOrchestrator."""
    
    print("=== Model Orchestrator Integration ===\n")
    
    # Create ModelOrchestrator
    orchestrator = ModelOrchestrator()
    await orchestrator.initialize()
    
    # Process request using Foundry Agent Service
    result = await orchestrator.process_model_request(
        model_type=ModelType.FOUNDRY_AGENT_SERVICE,
        domain="leadership",
        user_input="What are the top 3 priorities for our engineering team this quarter?",
        conversation_id="conv-001"
    )
    
    print(f"Success: {result.get('success')}")
    print(f"Reply: {result.get('reply')}")
    print(f"Model: {result.get('model')}")
    print(f"Thread ID: {result.get('thread_id')}")
    print(f"Execution time: {result.get('execution_time')}s")
    
    print()


async def advanced_configuration_example():
    """Example with advanced configuration options."""
    
    print("=== Advanced Configuration Example ===\n")
    
    # Create custom configuration
    config = FoundryAgentServiceConfig(
        endpoint_url=os.getenv("FOUNDRY_AGENT_SERVICE_ENDPOINT", ""),
        api_key=os.getenv("FOUNDRY_AGENT_SERVICE_API_KEY", ""),
        agent_id=os.getenv("FOUNDRY_AGENT_ID", "aos-agent-001"),
        model="llama-3.3-70b",
        enable_stateful_threads=True,
        enable_entra_agent_id=True,
        enable_foundry_tools=True,
        temperature=0.8,  # More creative responses
        max_tokens=2048,
        top_p=0.95,
        timeout=90,
        max_retries=5
    )
    
    client = FoundryAgentServiceClient(config)
    await client.initialize()
    
    # Send message with custom parameters
    response = await client.send_message(
        message="Generate innovative ideas for improving our product roadmap",
        domain="product_strategy",
        system_prompt="You are a strategic product advisor with deep industry expertise.",
        temperature=0.9,  # Override default for this request
        max_tokens=1500
    )
    
    if response.success:
        print(f"Response: {response.content}")
        print(f"\nConfiguration:")
        print(f"  - Model: {response.model}")
        print(f"  - Stateful Threads: {config.enable_stateful_threads}")
        print(f"  - Entra Agent ID: {config.enable_entra_agent_id}")
        print(f"  - Foundry Tools: {config.enable_foundry_tools}")
    else:
        print(f"Error: {response.error}")
    
    print()


async def metrics_and_monitoring():
    """Example demonstrating metrics and monitoring."""
    
    print("=== Metrics and Monitoring Example ===\n")
    
    config = FoundryAgentServiceConfig.from_env()
    client = FoundryAgentServiceClient(config)
    await client.initialize()
    
    # Make several requests
    for i in range(3):
        await client.send_message(
            message=f"Test message {i+1}",
            domain="general"
        )
    
    # Get metrics
    metrics = client.get_metrics()
    
    print("Client Metrics:")
    print(f"  - Total requests: {metrics['total_requests']}")
    print(f"  - Successful: {metrics['successful_requests']}")
    print(f"  - Failed: {metrics['failed_requests']}")
    print(f"  - Total tokens used: {metrics['total_tokens_used']}")
    print(f"  - Average latency: {metrics['average_latency']:.3f}s")
    
    # Health check
    is_healthy = await client.health_check()
    print(f"\nHealth check: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
    
    print()


async def main():
    """Run all examples."""
    
    print("\n" + "="*60)
    print("Azure Foundry Agent Service Integration Examples")
    print("Powered by Llama 3.3 70B")
    print("="*60 + "\n")
    
    # Check if configuration is available
    if not os.getenv("FOUNDRY_AGENT_SERVICE_ENDPOINT"):
        print("⚠️  Warning: FOUNDRY_AGENT_SERVICE_ENDPOINT not configured")
        print("These examples will run with simulated responses.\n")
        print("To use real Foundry Agent Service:")
        print("1. Set FOUNDRY_AGENT_SERVICE_ENDPOINT")
        print("2. Set FOUNDRY_AGENT_SERVICE_API_KEY")
        print("3. Optionally set FOUNDRY_AGENT_ID\n")
    
    try:
        # Run examples
        await basic_example()
        await stateful_threads_example()
        await foundry_tools_example()
        await model_orchestrator_integration()
        await advanced_configuration_example()
        await metrics_and_monitoring()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
