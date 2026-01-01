# LoRAx Orchestration Integration

## Overview

LoRAx has been integrated with the AOS orchestration layer to provide cost-effective multi-agent ML inference. This integration enables the orchestration system to leverage LoRAx's multi-adapter serving capabilities for parallel agent workflows.

## Key Integration Points

### 1. Orchestration Layer (`orchestration.py`)

**LoRAx Initialization:**
- LoRAx server starts automatically during boardroom initialization
- Adapters are registered for all board members based on their roles
- LoRAx status is included in system health checks

**Configuration:**
```python
{
    "enable_lorax": True,  # Enable/disable LoRAx (default: True)
    # ... other config
}
```

### 2. Multi-Agent Coordinator (`multi_agent_coordinator.py`)

**Automatic LoRAx Detection:**
- Coordinator automatically detects if LoRAx is available
- Uses LoRAx batch inference for parallel workflows when possible
- Falls back to standard execution if LoRAx is unavailable

**Batch Inference Optimization:**
- Parallel workflows with 2+ agents automatically use LoRAx batch inference
- Single adapter GPU serves all agents concurrently
- Reduces latency and cost compared to sequential processing

## Usage

### Automatic Integration

LoRAx integration is automatic and transparent to users:

```python
from AgentOperatingSystem.orchestration import create_autonomous_boardroom

# LoRAx starts automatically
boardroom = await create_autonomous_boardroom()

# Multi-agent workflows automatically use LoRAx when appropriate
coordinator = MultiAgentCoordinator(
    ml_pipeline=boardroom.ml_pipeline,
    registered_agents=boardroom.members
)

# This will use LoRAx batch inference for parallel execution
result = await coordinator.handle_multiagent_request(
    agent_id="ceo_agent",
    domain="strategy",
    user_input="Analyze Q2 performance",
    conv_id="conv_123",
    coordination_mode=CoordinationMode.PARALLEL  # Uses LoRAx!
)
```

### Manual Control

You can also manually control LoRAx usage:

```python
# Disable LoRAx for specific workflows
coordinator.use_lorax = False

# Or configure at initialization
config = {
    "enable_lorax": False  # Disable globally
}
```

## Benefits

### Cost Savings
- **Parallel Workflows**: Use 1 GPU for all agents vs. N GPUs
- **Example**: 5-agent parallel workflow
  - Without LoRAx: 5 GPUs × inference time
  - With LoRAx: 1 GPU × inference time
  - **Savings**: 80% GPU cost reduction

### Performance
- **Lower Latency**: Batch processing reduces overhead
- **Better Throughput**: Efficient GPU utilization
- **Automatic Fallback**: Graceful degradation if LoRAx fails

### Transparency
- **Automatic Detection**: Works out of the box
- **No Code Changes**: Existing workflows benefit automatically
- **Monitoring**: LoRAx metrics included in system health

## Monitoring

### System Health

Check LoRAx status in system health:

```python
status = await boardroom.get_boardroom_status()

# LoRAx status included
print(status["system_health"]["lorax"])
# {
#     "running": True,
#     "total_adapters": 5,
#     "loaded_adapters": 5,
#     "metrics": {
#         "total_requests": 100,
#         "average_latency_ms": 250,
#         ...
#     }
# }
```

### Workflow Metrics

Workflow results include LoRAx usage:

```python
result = await coordinator.handle_multiagent_request(...)

print(result["used_lorax"])  # True if LoRAx was used
print(result["execution_time"])  # Actual execution time
```

## Architecture

```
┌─────────────────────────────────────────┐
│     Orchestration Layer                 │
│  ┌────────────────────────────────────┐ │
│  │  Autonomous Boardroom              │ │
│  │  - Initializes LoRAx               │ │
│  │  - Registers member adapters       │ │
│  │  - Monitors LoRAx health           │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  Multi-Agent Coordinator           │ │
│  │  - Detects LoRAx availability      │ │
│  │  - Uses LoRAx for parallel work    │ │
│  │  - Falls back if needed            │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     ML Pipeline Layer                   │
│  ┌────────────────────────────────────┐ │
│  │  MLPipelineManager                 │ │
│  │  - Manages LoRAx server            │ │
│  │  - Handles batch inference         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│     LoRAx Server                        │
│  - Shared base model                    │
│  - Multiple LoRA adapters (CEO, CFO...) │
│  - Batch request processing             │
└─────────────────────────────────────────┘
```

## Implementation Details

### Adapter Registration

When a board member is added:

1. Member role is identified (e.g., "CEO", "CFO")
2. LoRA adapter path is constructed: `/models/{role}_lora_adapter`
3. Adapter is registered with LoRAx server
4. Member metadata is included for tracking

### Parallel Workflow Execution

When a parallel workflow is executed:

1. Coordinator checks if LoRAx is available
2. If yes and 2+ agents:
   - Prepare batch requests for all agents
   - Execute LoRAx batch inference
   - Return formatted results
3. If no or 1 agent:
   - Use standard parallel execution
   - Execute agents independently

### Error Handling

LoRAx integration includes robust error handling:

1. **Initialization Failure**: Falls back to standard inference
2. **Batch Inference Failure**: Falls back to parallel execution
3. **Adapter Missing**: Logs warning, continues with available agents

## Configuration

### Environment Variables

```bash
# Enable/disable LoRAx
AOS_ENABLE_LORAX=true

# LoRAx server configuration
AOS_LORAX_PORT=8080
AOS_LORAX_ADAPTER_CACHE_SIZE=100
AOS_LORAX_MAX_CONCURRENT_REQUESTS=128
```

### Orchestration Configuration

```python
config = {
    "enable_lorax": True,  # Master switch
    "max_members": 15,     # Board members
    # ... other config
}
```

## Best Practices

### 1. Use Parallel Mode for Multi-Agent Tasks

```python
# Good: Uses LoRAx batch inference
result = await coordinator.handle_multiagent_request(
    coordination_mode=CoordinationMode.PARALLEL
)

# Less efficient: Sequential doesn't use batch inference
result = await coordinator.handle_multiagent_request(
    coordination_mode=CoordinationMode.SEQUENTIAL
)
```

### 2. Monitor LoRAx Performance

```python
# Check LoRAx metrics regularly
status = boardroom.ml_pipeline.get_lorax_status()
if status["metrics"]["average_latency_ms"] > 500:
    logger.warning("High LoRAx latency detected")
```

### 3. Register Adapters for All Agents

```python
# Ensure all agents have adapters
for member in boardroom.members.values():
    await boardroom._register_member_adapter(member)
```

## Troubleshooting

### LoRAx Not Starting

**Problem**: LoRAx server fails to start

**Solution**:
1. Check logs for initialization errors
2. Verify LoRAx configuration
3. Ensure GPU is available
4. System will fall back to standard inference automatically

### Adapters Not Loading

**Problem**: Adapter registration fails

**Solution**:
1. Verify adapter paths exist
2. Check adapter format compatibility
3. Review LoRAx logs
4. Missing adapters are logged as warnings

### High Latency

**Problem**: LoRAx inference is slow

**Solution**:
1. Check GPU utilization
2. Reduce batch size if needed
3. Increase cache size for frequently used adapters
4. Monitor cache hit rate

## Performance Metrics

### Expected Performance

| Scenario | Without LoRAx | With LoRAx | Improvement |
|----------|--------------|------------|-------------|
| 3-agent parallel | 3× cost | 1× cost | 67% savings |
| 5-agent parallel | 5× cost | 1× cost | 80% savings |
| 10-agent parallel | 10× cost | 1× cost | 90% savings |

### Real-World Example

**5-Agent Strategy Discussion:**
- Agents: CEO, CFO, COO, CMO, CTO
- Without LoRAx: 5 GPUs, 2s each = 10 GPU-seconds
- With LoRAx: 1 GPU, 2.5s batch = 2.5 GPU-seconds
- **Savings**: 75% GPU utilization reduction

## Next Steps

1. Monitor LoRAx performance in production
2. Tune cache size based on usage patterns
3. Add more agent adapters as needed
4. Consider implementing custom adapter selection logic

## Support

For issues or questions:
- Check system health: `boardroom.get_boardroom_status()`
- Review LoRAx logs
- Consult [LoRAx Documentation](./LORAX.md)
- Report issues on GitHub

---

**Last Updated**: December 31, 2025
**Version**: 1.0.0
