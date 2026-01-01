# LoRAx Quick Reference

## What is LoRAx?

LoRAx (LoRA eXchange) enables serving multiple LoRA adapters concurrently with a shared base model, reducing ML infrastructure costs by 90-95% for multi-agent systems.

## Key Benefits

- 💰 **Cost Savings**: Serve 100+ agents on 1 GPU instead of 100 GPUs
- 🚀 **Easy Scaling**: Add agents without infrastructure changes
- ⚡ **High Performance**: Efficient batching and caching
- 🔧 **Simple Setup**: Configuration-driven deployment

## Quick Start

### 1. Enable LoRAx

```bash
# In environment or local.settings.json
AOS_ENABLE_LORAX=true
```

### 2. Initialize

```python
from AgentOperatingSystem.ml import MLPipelineManager
from AgentOperatingSystem.config.ml import MLConfig

config = MLConfig.from_env()
ml_pipeline = MLPipelineManager(config)

# Start LoRAx server
await ml_pipeline.start_lorax_server()
```

### 3. Register Adapters

```python
# Register LoRA adapters for your agents
ml_pipeline.register_lorax_adapter(
    agent_role="CEO",
    adapter_path="/models/ceo_lora_adapter"
)

ml_pipeline.register_lorax_adapter(
    agent_role="CFO",
    adapter_path="/models/cfo_lora_adapter"
)
```

### 4. Run Inference

```python
# Single agent
result = await ml_pipeline.lorax_inference(
    agent_role="CEO",
    prompt="What are our strategic priorities?"
)

# Multiple agents (batch)
results = await ml_pipeline.lorax_batch_inference([
    {"agent_role": "CEO", "prompt": "Strategic analysis"},
    {"agent_role": "CFO", "prompt": "Financial analysis"}
])
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `AOS_ENABLE_LORAX` | `true` | Enable LoRAx |
| `AOS_LORAX_BASE_MODEL` | `meta-llama/Llama-3.1-8B-Instruct` | Base model |
| `AOS_LORAX_PORT` | `8080` | Server port |
| `AOS_LORAX_ADAPTER_CACHE_SIZE` | `100` | Adapters to cache |
| `AOS_LORAX_MAX_CONCURRENT_REQUESTS` | `128` | Max concurrent requests |
| `AOS_LORAX_MAX_BATCH_SIZE` | `32` | Max batch size |
| `AOS_LORAX_GPU_MEMORY_UTILIZATION` | `0.9` | GPU memory usage (0-1) |

## Monitoring

```python
# Get server status
status = ml_pipeline.get_lorax_status()
print(f"Running: {status['running']}")
print(f"Adapters: {status['total_adapters']}")
print(f"Requests: {status['metrics']['total_requests']}")

# Get adapter stats
stats = ml_pipeline.get_lorax_adapter_stats("CEO")
print(f"Inferences: {stats['inference_count']}")
```

## Cost Comparison

### Example: 50 C-Suite Agents

**Without LoRAx:**
- 50 GPUs × $3,000/month = **$150,000/month**

**With LoRAx:**
- 1-2 GPUs × $3,000/month = **$3,000-6,000/month**

**Savings: $144,000/month (96% reduction)**

## Architecture

```
Multiple Agents (CEO, CFO, COO, CMO, etc.)
        ↓
   LoRAx Server
        ↓
Base Model (Shared) + Dynamic LoRA Adapters
        ↓
     Single GPU
```

## Best Practices

1. **Cache Size**: Set to 10-20% above your most active agents
2. **Batch Processing**: Group related requests for efficiency
3. **Monitoring**: Track cache hit rate (target 80%+)
4. **Adapter Organization**: Use clear naming conventions

## Resources

- [Full Documentation](./LORAX.md)
- [Example Code](../examples/lorax_multi_agent_example.py)
- [ML Pipeline Guide](./ml_pipeline.md)

## Support

For issues or questions:
- Review [Troubleshooting](./LORAX.md#troubleshooting) section
- Check [GitHub Issues](https://github.com/ASISaga/AgentOperatingSystem/issues)
