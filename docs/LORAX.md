# LoRAx Integration for Low-Cost Multi-Agent ML

## Overview

LoRAx (LoRA eXchange) is a powerful framework for serving multiple LoRA adapters concurrently with a shared base model, providing significant cost savings for multi-agent scenarios in the Agent Operating System (AOS).

### What is LoRAx?

LoRAx is an inference server that enables dynamic loading and serving of multiple LoRA (Low-Rank Adaptation) adapters with a single base model. Instead of deploying separate models for each agent (CEO, CFO, COO, etc.), LoRAx allows all agents to share the same base model while using their own specialized LoRA adapters.

### Key Benefits

1. **Cost Efficiency**: Serve 100+ agents with different LoRA adapters on a single GPU
2. **Reduced Infrastructure**: Eliminate the need for separate model deployments per agent
3. **Lower Memory Footprint**: Dynamic adapter loading reduces memory requirements
4. **Improved Throughput**: Efficient batching of requests with different adapters
5. **Easy Scaling**: Add new agents without deploying new infrastructure

### Cost Comparison

| Approach | GPU Cost (per month) | Agents Supported | Cost per Agent |
|----------|---------------------|------------------|----------------|
| **Separate Models** | $3,000 per GPU × 10 GPUs | 10 agents | $3,000 |
| **LoRAx (Shared Base)** | $3,000 per GPU × 1 GPU | 100+ agents | $30 |
| **Savings** | **90% reduction** | **10x capacity** | **99% reduction** |

*Based on typical cloud GPU pricing for inference workloads*

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   AOS Multi-Agent System                │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │
│  │  CEO   │  │  CFO   │  │  COO   │  │  CMO   │  ...  │
│  │ Agent  │  │ Agent  │  │ Agent  │  │ Agent  │       │
│  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘       │
│       │           │           │           │            │
│       └───────────┴───────────┴───────────┘            │
│                       │                                 │
└───────────────────────┼─────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │    LoRAx Inference Server     │
        ├───────────────────────────────┤
        │  ┌─────────────────────────┐  │
        │  │   Base Model (Shared)   │  │
        │  │  Llama-3.1-8B-Instruct  │  │
        │  └─────────────────────────┘  │
        │                               │
        │  ┌─────────────────────────┐  │
        │  │   Adapter Cache (LRU)   │  │
        │  ├─────────────────────────┤  │
        │  │ ✓ CEO LoRA              │  │
        │  │ ✓ CFO LoRA              │  │
        │  │ ✓ COO LoRA              │  │
        │  │ ✓ CMO LoRA              │  │
        │  │ ⋮ (100+ adapters)       │  │
        │  └─────────────────────────┘  │
        │                               │
        │  ┌─────────────────────────┐  │
        │  │  Intelligent Batching   │  │
        │  │  & Request Scheduler    │  │
        │  └─────────────────────────┘  │
        └───────────────────────────────┘
                        │
                        ▼
                    ┌───────┐
                    │  GPU  │
                    └───────┘
```

## Quick Start

### 1. Enable LoRAx in Configuration

Add to your environment variables or `local.settings.json`:

```bash
AOS_ENABLE_LORAX=true
AOS_LORAX_BASE_MODEL=meta-llama/Llama-3.1-8B-Instruct
AOS_LORAX_PORT=8080
AOS_LORAX_ADAPTER_CACHE_SIZE=100
```

### 2. Initialize ML Pipeline with LoRAx

```python
from AgentOperatingSystem.ml import MLPipelineManager
from AgentOperatingSystem.config.ml import MLConfig

# Create ML configuration
config = MLConfig.from_env()

# Initialize ML pipeline (includes LoRAx)
ml_pipeline = MLPipelineManager(config)

# Start LoRAx server
await ml_pipeline.start_lorax_server()
```

### 3. Register LoRA Adapters for Your Agents

```python
# Register adapters for different agents
ml_pipeline.register_lorax_adapter(
    agent_role="CEO",
    adapter_path="/models/ceo_lora_adapter",
    version="1.0.0",
    metadata={"domain": "strategic_planning", "trained_on": "2024-12-01"}
)

ml_pipeline.register_lorax_adapter(
    agent_role="CFO",
    adapter_path="/models/cfo_lora_adapter",
    version="1.0.0",
    metadata={"domain": "financial_analysis", "trained_on": "2024-12-01"}
)

ml_pipeline.register_lorax_adapter(
    agent_role="COO",
    adapter_path="/models/coo_lora_adapter",
    version="1.0.0",
    metadata={"domain": "operations", "trained_on": "2024-12-01"}
)
```

### 4. Run Inference for Agents

```python
# Single agent inference
result = await ml_pipeline.lorax_inference(
    agent_role="CEO",
    prompt="What are our strategic priorities for Q2 2025?",
    max_new_tokens=256,
    temperature=0.7
)

print(f"CEO Response: {result['generated_text']}")
print(f"Latency: {result['latency_ms']}ms")
```

### 5. Batch Inference for Multiple Agents

```python
# Process multiple agents concurrently
requests = [
    {
        "agent_role": "CEO",
        "prompt": "Review our Q1 performance and recommend strategic adjustments"
    },
    {
        "agent_role": "CFO",
        "prompt": "Analyze the budget variance for Q1 and provide recommendations"
    },
    {
        "agent_role": "COO",
        "prompt": "Assess operational efficiency and suggest improvements"
    }
]

results = await ml_pipeline.lorax_batch_inference(requests)

for result in results:
    print(f"{result['adapter_id']}: {result['generated_text']}")
```

## Advanced Usage

### Monitoring LoRAx Status

```python
# Get comprehensive status
status = ml_pipeline.get_lorax_status()

print(f"Server Running: {status['running']}")
print(f"Total Adapters: {status['total_adapters']}")
print(f"Loaded Adapters: {status['loaded_adapters']}")
print(f"Active Requests: {status['active_requests']}")
print(f"Average Latency: {status['metrics']['average_latency_ms']}ms")
print(f"Cache Hit Rate: {status['metrics']['cache_hits'] / status['metrics']['total_requests']}")
```

### Adapter Statistics

```python
# Get statistics for a specific adapter
stats = ml_pipeline.get_lorax_adapter_stats("CEO")

print(f"Adapter: {stats['adapter_id']}")
print(f"Load Count: {stats['load_count']}")
print(f"Inference Count: {stats['inference_count']}")
print(f"Last Used: {stats['last_used']}")
print(f"Currently Loaded: {stats['loaded']}")
```

### Configuration Options

LoRAx can be configured via environment variables:

```bash
# Server Configuration
AOS_LORAX_HOST=0.0.0.0                    # Server host
AOS_LORAX_PORT=8080                       # Server port
AOS_LORAX_BASE_MODEL=meta-llama/Llama-3.1-8B-Instruct

# Performance Tuning
AOS_LORAX_ADAPTER_CACHE_SIZE=100          # Number of adapters to cache
AOS_LORAX_MAX_CONCURRENT_REQUESTS=128     # Max concurrent requests
AOS_LORAX_MAX_BATCH_SIZE=32               # Max batch size
AOS_LORAX_GPU_MEMORY_UTILIZATION=0.9      # GPU memory usage (0.0-1.0)
```

## Best Practices

### 1. Adapter Organization

Organize your LoRA adapters by agent role and version:

```
models/
├── ceo_lora_adapter/
│   ├── v1.0.0/
│   └── v1.1.0/
├── cfo_lora_adapter/
│   └── v1.0.0/
└── coo_lora_adapter/
    └── v1.0.0/
```

### 2. Cache Management

Configure cache size based on your most frequently used agents:

```python
# If you have 10 highly active agents and 90 occasional agents
# Set cache size to 15-20 to ensure active agents are always cached
config.lorax_adapter_cache_size = 20
```

### 3. Batch Processing

Group requests by priority and timing for optimal batching:

```python
# Group strategic planning queries
strategic_requests = [
    {"agent_role": "CEO", "prompt": "..."},
    {"agent_role": "COO", "prompt": "..."},
    {"agent_role": "CTO", "prompt": "..."}
]

# Process as a batch
results = await ml_pipeline.lorax_batch_inference(strategic_requests)
```

### 4. Monitoring and Alerting

Set up monitoring for LoRAx metrics:

```python
# Monitor cache hit rate
status = ml_pipeline.get_lorax_status()
cache_hit_rate = (
    status['metrics']['cache_hits'] / 
    max(status['metrics']['total_requests'], 1)
)

if cache_hit_rate < 0.8:
    # Consider increasing cache size
    print("Warning: Cache hit rate is low, consider increasing cache size")

# Monitor latency
if status['metrics']['average_latency_ms'] > 500:
    print("Warning: High latency detected, check GPU utilization")
```

## Integration with Agent Operating System

### PurposeDrivenAgent Integration

LoRAx seamlessly integrates with PurposeDrivenAgent:

```python
from AgentOperatingSystem.agents import PurposeDrivenAgent

class CEOAgent(PurposeDrivenAgent):
    def __init__(self):
        super().__init__(
            agent_id="ceo",
            purpose="Strategic oversight and company growth",
            adapter_name="CEO"  # Links to LoRAx adapter
        )
    
    async def make_decision(self, context):
        # Use LoRAx for inference
        result = await self.ml_pipeline.lorax_inference(
            agent_role=self.adapter_name,
            prompt=f"Analyze and decide: {context}",
            temperature=0.7
        )
        
        return result['generated_text']
```

### Multi-Agent Coordination

LoRAx enables efficient multi-agent coordination:

```python
# Coordinate decision across multiple C-suite agents
async def coordinate_strategic_decision(issue):
    # Prepare requests for all relevant agents
    requests = [
        {
            "agent_role": "CEO",
            "prompt": f"Strategic perspective on: {issue}"
        },
        {
            "agent_role": "CFO",
            "prompt": f"Financial impact of: {issue}"
        },
        {
            "agent_role": "CTO",
            "prompt": f"Technical feasibility of: {issue}"
        }
    ]
    
    # Process all agents concurrently with LoRAx
    results = await ml_pipeline.lorax_batch_inference(requests)
    
    # Aggregate insights
    decision = aggregate_agent_inputs(results)
    return decision
```

## Performance Optimization

### GPU Memory Management

LoRAx automatically manages GPU memory, but you can tune it:

```python
# For systems with limited GPU memory
config.lorax_gpu_memory_utilization = 0.8  # Use 80% of GPU memory

# For high-throughput scenarios
config.lorax_gpu_memory_utilization = 0.95  # Use 95% of GPU memory
```

### Request Batching

Optimize batch size based on your workload:

```python
# For low-latency requirements
config.lorax_max_batch_size = 8

# For high-throughput requirements
config.lorax_max_batch_size = 64
```

## Troubleshooting

### Server Won't Start

```python
# Check LoRAx status
status = ml_pipeline.get_lorax_status()
print(status)

# Common issues:
# 1. GPU not available - check CUDA installation
# 2. Insufficient memory - reduce cache size or GPU utilization
# 3. Port already in use - change port in configuration
```

### High Latency

```python
# Check for:
# 1. Cache misses - increase cache size
# 2. Large batch size - reduce max_batch_size
# 3. GPU overload - reduce concurrent requests

status = ml_pipeline.get_lorax_status()
print(f"Cache hit rate: {status['metrics']['cache_hits'] / status['metrics']['total_requests']}")
print(f"Active requests: {status['active_requests']}")
```

### Adapter Not Found

```python
# Verify adapter registration
adapters = ml_pipeline.lorax_server.registry.list_adapters()
for adapter in adapters:
    print(f"{adapter.agent_role}: {adapter.adapter_id} - {adapter.adapter_path}")

# Re-register if needed
ml_pipeline.register_lorax_adapter(
    agent_role="CFO",
    adapter_path="/models/cfo_lora_adapter"
)
```

## Migration from Single-Model Deployments

### Step 1: Train LoRA Adapters

```python
# Train LoRA adapters for each agent
for agent_role in ["CEO", "CFO", "COO", "CMO", "CTO"]:
    await ml_pipeline.train_lora_adapter(
        agent_role=agent_role,
        training_params={
            "base_model": "meta-llama/Llama-3.1-8B-Instruct",
            "training_data": f"data/{agent_role.lower()}_training.jsonl",
            "hyperparameters": {
                "r": 16,
                "lora_alpha": 32,
                "learning_rate": 3e-4
            }
        }
    )
```

### Step 2: Register Adapters with LoRAx

```python
# Register all trained adapters
for agent_role in ["CEO", "CFO", "COO", "CMO", "CTO"]:
    ml_pipeline.register_lorax_adapter(
        agent_role=agent_role,
        adapter_path=f"/models/{agent_role.lower()}_lora_adapter"
    )
```

### Step 3: Update Agent Inference Code

```python
# Before: Direct model inference
result = await agent.model.generate(prompt)

# After: LoRAx inference
result = await ml_pipeline.lorax_inference(
    agent_role=agent.role,
    prompt=prompt
)
```

### Step 4: Monitor and Optimize

```python
# Monitor performance
status = ml_pipeline.get_lorax_status()

# Adjust cache size based on usage patterns
most_used = ml_pipeline.lorax_server.registry.get_most_used_adapters(10)
print(f"Consider caching at least {len(most_used)} adapters")
```

## Cost Analysis

### Example Scenario: 50 C-Suite Agents

**Without LoRAx (Separate Models):**
- 50 agents × $3,000/month per GPU = **$150,000/month**
- Total infrastructure: 50 GPUs
- Complexity: High (managing 50 deployments)

**With LoRAx (Shared Base Model):**
- 1-2 GPUs × $3,000/month = **$3,000-$6,000/month**
- Total infrastructure: 1-2 GPUs
- Complexity: Low (single deployment)

**Savings: $144,000/month (96% reduction)**

## Conclusion

LoRAx integration in AOS provides:

1. ✅ **Massive Cost Savings**: 90-95% reduction in GPU costs
2. ✅ **Simplified Operations**: Single deployment for all agents
3. ✅ **High Performance**: Efficient batching and caching
4. ✅ **Easy Scaling**: Add agents without new infrastructure
5. ✅ **Production Ready**: Built on proven LoRA technology

For production deployments, LoRAx is the recommended approach for multi-agent ML inference in AOS.

## Resources

- [AOS ML Pipeline Documentation](./ml_pipeline.md)
- [LoRA Training Guide](./lora_training.md)
- [Agent Development Guide](../README.md#agent-development-model)
- [Configuration Reference](./configuration.md)

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [GitHub Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)
- Consult AOS documentation
