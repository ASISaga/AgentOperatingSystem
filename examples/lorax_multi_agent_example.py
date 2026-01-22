"""
LoRAx Multi-Agent Inference Example

This example demonstrates how to use LoRAx for cost-effective multi-agent inference
in the Agent Operating System (AOS).

Scenario:
- Multiple C-suite agents (CEO, CFO, COO, CMO) need to analyze a strategic issue
- Each agent has a specialized LoRA adapter
- All agents share the same base model via LoRAx
- This approach reduces infrastructure costs by 90%+ compared to separate model deployments
"""

import asyncio
import sys
from pathlib import Path

# Add AOS to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from AgentOperatingSystem.ml import MLPipelineManager
from AgentOperatingSystem.config.ml import MLConfig


async def main():
    print("=" * 80)
    print("LoRAx Multi-Agent Inference Example")
    print("=" * 80)
    print()
    
    # Step 1: Initialize ML Pipeline with LoRAx
    print("Step 1: Initializing ML Pipeline with LoRAx")
    print("-" * 80)
    
    config = MLConfig(
        enable_lorax=True,
        lorax_base_model="meta-llama/Llama-3.3-70B-Instruct",
        lorax_port=8080,
        lorax_adapter_cache_size=10,
        lorax_max_concurrent_requests=64,
        lorax_max_batch_size=16
    )
    
    ml_pipeline = MLPipelineManager(config)
    
    # Start LoRAx server
    print("Starting LoRAx server...")
    success = await ml_pipeline.start_lorax_server()
    
    if not success:
        print("ERROR: Failed to start LoRAx server")
        return
    
    print("✓ LoRAx server started successfully")
    print()
    
    # Step 2: Register LoRA Adapters for C-Suite Agents
    print("Step 2: Registering LoRA Adapters")
    print("-" * 80)
    
    agents = [
        {
            "role": "CEO",
            "path": "models/ceo_lora_adapter",
            "domain": "Strategic Planning & Leadership"
        },
        {
            "role": "CFO",
            "path": "models/cfo_lora_adapter",
            "domain": "Financial Analysis & Planning"
        },
        {
            "role": "COO",
            "path": "models/coo_lora_adapter",
            "domain": "Operations & Efficiency"
        },
        {
            "role": "CMO",
            "path": "models/cmo_lora_adapter",
            "domain": "Marketing & Brand Strategy"
        }
    ]
    
    for agent in agents:
        ml_pipeline.register_lorax_adapter(
            agent_role=agent["role"],
            adapter_path=agent["path"],
            version="1.0.0",
            metadata={"domain": agent["domain"]}
        )
        print(f"✓ Registered {agent['role']} adapter - Domain: {agent['domain']}")
    
    print()
    
    # Step 3: Check LoRAx Status
    print("Step 3: LoRAx Server Status")
    print("-" * 80)
    
    status = ml_pipeline.get_lorax_status()
    print(f"Server Running: {status['running']}")
    print(f"Base Model: {status['base_model']}")
    print(f"Total Adapters Registered: {status['total_adapters']}")
    print(f"Adapters Loaded in Cache: {status['loaded_adapters']}")
    print(f"Cache Size: {status['cache_size']}")
    print(f"Max Concurrent Requests: {status['config']['max_concurrent_requests']}")
    print()
    
    # Step 4: Single Agent Inference
    print("Step 4: Single Agent Inference Example")
    print("-" * 80)
    
    print("Asking CEO agent about strategic priorities...")
    
    ceo_result = await ml_pipeline.lorax_inference(
        agent_role="CEO",
        prompt="What should be our top 3 strategic priorities for Q2 2025?",
        max_new_tokens=256,
        temperature=0.7
    )
    
    print(f"\nCEO Response:")
    print(f"  {ceo_result['generated_text']}")
    print(f"  Latency: {ceo_result['latency_ms']:.2f}ms")
    print(f"  Adapter Loaded: {ceo_result['adapter_loaded']}")
    print()
    
    # Step 5: Batch Multi-Agent Inference
    print("Step 5: Batch Multi-Agent Inference Example")
    print("-" * 80)
    
    print("Coordinating strategic decision across all C-suite agents...")
    print()
    
    # Strategic issue requiring input from all agents
    strategic_issue = "Proposal: Launch a new AI-powered product line with $10M investment"
    
    # Prepare requests for all agents
    batch_requests = [
        {
            "agent_role": "CEO",
            "prompt": f"From a strategic leadership perspective, analyze this proposal: {strategic_issue}"
        },
        {
            "agent_role": "CFO",
            "prompt": f"From a financial perspective, analyze this proposal: {strategic_issue}"
        },
        {
            "agent_role": "COO",
            "prompt": f"From an operational perspective, analyze this proposal: {strategic_issue}"
        },
        {
            "agent_role": "CMO",
            "prompt": f"From a marketing perspective, analyze this proposal: {strategic_issue}"
        }
    ]
    
    # Process all agents concurrently
    results = await ml_pipeline.lorax_batch_inference(batch_requests)
    
    print("Strategic Analysis Results:")
    print()
    
    for i, result in enumerate(results):
        agent_role = batch_requests[i]["agent_role"]
        print(f"{agent_role} Analysis:")
        print(f"  {result['generated_text']}")
        print(f"  Latency: {result['latency_ms']:.2f}ms")
        print()
    
    # Step 6: Performance Metrics
    print("Step 6: Performance Metrics")
    print("-" * 80)
    
    status = ml_pipeline.get_lorax_status()
    metrics = status['metrics']
    
    print(f"Total Requests Processed: {metrics['total_requests']}")
    print(f"Successful Requests: {metrics['successful_requests']}")
    print(f"Failed Requests: {metrics['failed_requests']}")
    print(f"Average Latency: {metrics['average_latency_ms']:.2f}ms")
    print(f"Cache Hits: {metrics['cache_hits']}")
    print(f"Cache Misses: {metrics['cache_misses']}")
    
    if metrics['total_requests'] > 0:
        cache_hit_rate = metrics['cache_hits'] / metrics['total_requests']
        print(f"Cache Hit Rate: {cache_hit_rate:.1%}")
    
    print()
    
    # Step 7: Adapter Statistics
    print("Step 7: Adapter Usage Statistics")
    print("-" * 80)
    
    for agent in agents:
        stats = ml_pipeline.get_lorax_adapter_stats(agent["role"])
        if stats:
            print(f"{agent['role']}:")
            print(f"  Inference Count: {stats['inference_count']}")
            print(f"  Load Count: {stats['load_count']}")
            print(f"  Currently Loaded: {stats['loaded']}")
            print(f"  Last Used: {stats['last_used']}")
            print()
    
    # Step 8: Cost Comparison
    print("Step 8: Cost Comparison")
    print("-" * 80)
    
    num_agents = len(agents)
    gpu_cost_per_month = 3000  # Example cloud GPU cost
    
    separate_models_cost = num_agents * gpu_cost_per_month
    lorax_cost = 1 * gpu_cost_per_month  # Single GPU for all agents
    savings = separate_models_cost - lorax_cost
    savings_percent = (savings / separate_models_cost) * 100
    
    print("Infrastructure Cost Analysis:")
    print()
    print(f"Scenario: {num_agents} C-suite agents")
    print(f"GPU Cost: ${gpu_cost_per_month:,}/month per GPU")
    print()
    print("Without LoRAx (Separate Models):")
    print(f"  GPUs Required: {num_agents}")
    print(f"  Monthly Cost: ${separate_models_cost:,}")
    print()
    print("With LoRAx (Shared Base Model):")
    print(f"  GPUs Required: 1")
    print(f"  Monthly Cost: ${lorax_cost:,}")
    print()
    print(f"💰 Monthly Savings: ${savings:,} ({savings_percent:.0f}% reduction)")
    print()
    
    # Step 9: Cleanup
    print("Step 9: Cleanup")
    print("-" * 80)
    
    print("Stopping LoRAx server...")
    await ml_pipeline.stop_lorax_server()
    print("✓ LoRAx server stopped")
    print()
    
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("1. LoRAx enables serving multiple LoRA adapters with a single base model")
    print("2. Significant cost savings (90%+) compared to separate model deployments")
    print("3. Efficient batch processing for multi-agent scenarios")
    print("4. Easy adapter management and dynamic loading")
    print("5. Production-ready solution for AOS multi-agent systems")


if __name__ == "__main__":
    asyncio.run(main())
