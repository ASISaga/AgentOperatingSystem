# Azure Foundry Agent Service Integration

## Overview

Agent Operating System (AOS) now includes native support for **Microsoft Azure Foundry Agent Service** with **Llama 3.3 70B** as the core reasoning engine. This integration enables you to leverage Azure's enterprise-grade AI infrastructure with advanced features designed for production agent workloads.

## What is Azure Foundry Agent Service?

Azure Foundry Agent Service is Microsoft's official managed service for deploying and orchestrating AI agents at scale. It provides:

- **Llama 3.3 70B Support**: Use Llama 3.3 70B as your core reasoning engine with support for fine-tuned weights
- **Stateful Threads**: Maintain conversation context across multiple interactions automatically
- **Entra Agent ID**: Secure agent identity management integrated with Microsoft Entra ID
- **Foundry Tools**: Access to Azure AI Foundry's comprehensive toolset and capabilities
- **Enterprise Scale**: Production-ready infrastructure with high availability and performance
- **Security**: Built-in security, compliance, and governance features

## Key Features

### 1. Llama 3.3 70B as Core Reasoning Engine

Foundry Agent Service supports Llama 3.3 70B, providing:

- **High-Quality Reasoning**: State-of-the-art language understanding and generation
- **Fine-Tuned Weights**: Use your custom fine-tuned Llama 3.3 weights
- **Cost-Effective**: Optimized inference infrastructure reduces operational costs
- **Scalable**: Handle thousands of concurrent requests

### 2. Stateful Threads

Maintain conversation context seamlessly:

```python
# Create a persistent thread
thread_id = await client.create_thread(metadata={"purpose": "customer_support"})

# All messages in this thread maintain context
response1 = await client.send_message("What's our Q3 revenue?", thread_id=thread_id)
response2 = await client.send_message("How does that compare to Q2?", thread_id=thread_id)
response3 = await client.send_message("What's the forecast for Q4?", thread_id=thread_id)
```

### 3. Entra Agent ID

Secure identity management for your agents:

- Integrated with Microsoft Entra ID (formerly Azure AD)
- Fine-grained access control
- Audit trail for all agent actions
- Compliance with enterprise security policies

### 4. Foundry Tools

Access powerful Azure AI capabilities:

- **Data Analysis**: Built-in tools for data processing and analysis
- **Knowledge Retrieval**: Integrate with Azure AI Search and knowledge bases
- **Custom Tools**: Define and deploy your own tools
- **Multi-Modal**: Support for text, images, and structured data

## Quick Start

### Prerequisites

1. Azure subscription with Foundry Agent Service enabled
2. Foundry Agent Service endpoint URL
3. API key for authentication
4. Optional: Agent ID for Entra integration

### Environment Configuration

Set the following environment variables:

```bash
# Required
export FOUNDRY_AGENT_SERVICE_ENDPOINT="https://your-endpoint.azure.com"
export FOUNDRY_AGENT_SERVICE_API_KEY="your-api-key"

# Optional
export FOUNDRY_AGENT_ID="your-agent-id"
export FOUNDRY_MODEL="llama-3.3-70b"

# Feature flags (default: true)
export FOUNDRY_ENABLE_STATEFUL_THREADS="true"
export FOUNDRY_ENABLE_ENTRA_AGENT_ID="true"
export FOUNDRY_ENABLE_FOUNDRY_TOOLS="true"

# Performance tuning
export FOUNDRY_TIMEOUT="60"
export FOUNDRY_TEMPERATURE="0.7"
export FOUNDRY_MAX_TOKENS="4096"
```

### Basic Usage

```python
import asyncio
from AgentOperatingSystem.ml import FoundryAgentServiceClient, FoundryAgentServiceConfig

async def main():
    # Initialize client
    config = FoundryAgentServiceConfig.from_env()
    client = FoundryAgentServiceClient(config)
    await client.initialize()
    
    # Send a message
    response = await client.send_message(
        message="Analyze the customer feedback trends from last quarter",
        domain="customer_analytics"
    )
    
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.get('total_tokens')}")

asyncio.run(main())
```

## Integration with Model Orchestrator

Use Foundry Agent Service through the AOS Model Orchestrator:

```python
from AgentOperatingSystem.orchestration import ModelOrchestrator, ModelType

async def use_with_orchestrator():
    orchestrator = ModelOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.process_model_request(
        model_type=ModelType.FOUNDRY_AGENT_SERVICE,
        domain="leadership",
        user_input="What are the top 3 strategic priorities?",
        conversation_id="conv-001"
    )
    
    print(f"Reply: {result['reply']}")
    print(f"Thread ID: {result['thread_id']}")
```

## Advanced Configuration

### Custom Configuration

```python
config = FoundryAgentServiceConfig(
    endpoint_url="https://your-endpoint.azure.com",
    api_key="your-api-key",
    agent_id="aos-agent-001",
    model="llama-3.3-70b",
    enable_stateful_threads=True,
    enable_entra_agent_id=True,
    enable_foundry_tools=True,
    temperature=0.8,
    max_tokens=2048,
    top_p=0.95,
    timeout=90,
    max_retries=5
)

client = FoundryAgentServiceClient(config)
```

### Thread Management

```python
# Create a thread with metadata
thread_id = await client.create_thread(
    metadata={
        "purpose": "financial_analysis",
        "user_id": "user-123",
        "department": "finance"
    }
)

# Get thread information
thread_info = await client.get_thread_info(thread_id)
print(f"Messages in thread: {thread_info.message_count}")
print(f"Last accessed: {thread_info.last_accessed}")

# Delete a thread when done
await client.delete_thread(thread_id)
```

### Using Foundry Tools

```python
response = await client.send_message(
    message="Analyze sales data and create a visualization",
    domain="sales_analytics",
    tools=["data_analysis", "visualization", "statistical_modeling"]
)

print(f"Tools used: {', '.join(response.tools_used)}")
```

## Configuration Reference

### MLConfig Settings

Add to your AOS configuration:

```python
from AgentOperatingSystem.config import MLConfig

ml_config = MLConfig(
    # Foundry Agent Service
    enable_foundry_agent_service=True,
    foundry_agent_service_endpoint="https://your-endpoint.azure.com",
    foundry_agent_service_api_key="your-api-key",
    foundry_agent_id="your-agent-id",
    foundry_model="llama-3.3-70b",
    foundry_enable_stateful_threads=True,
    foundry_enable_entra_agent_id=True,
    foundry_enable_foundry_tools=True
)
```

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FOUNDRY_AGENT_SERVICE_ENDPOINT` | - | Required: Service endpoint URL |
| `FOUNDRY_AGENT_SERVICE_API_KEY` | - | Required: API authentication key |
| `FOUNDRY_AGENT_ID` | - | Optional: Agent identity for Entra ID |
| `FOUNDRY_MODEL` | `llama-3.3-70b` | Model to use |
| `FOUNDRY_ENABLE_STATEFUL_THREADS` | `true` | Enable stateful conversations |
| `FOUNDRY_ENABLE_ENTRA_AGENT_ID` | `true` | Enable Entra ID integration |
| `FOUNDRY_ENABLE_FOUNDRY_TOOLS` | `true` | Enable Foundry Tools |
| `FOUNDRY_TIMEOUT` | `60` | Request timeout in seconds |
| `FOUNDRY_TEMPERATURE` | `0.7` | Sampling temperature (0.0-1.0) |
| `FOUNDRY_MAX_TOKENS` | `4096` | Maximum tokens in response |
| `FOUNDRY_TOP_P` | `0.9` | Nucleus sampling parameter |
| `FOUNDRY_MAX_RETRIES` | `3` | Maximum retry attempts |

## Best Practices

### 1. Thread Management

- **Create threads for related conversations**: Group related interactions in a single thread
- **Use meaningful metadata**: Add context to threads for better tracking
- **Clean up old threads**: Delete threads when conversations are complete
- **Monitor thread count**: Keep track of active threads to manage resources

### 2. Performance Optimization

- **Adjust timeout**: Increase timeout for complex reasoning tasks
- **Batch requests**: Use thread-based batching for efficiency
- **Monitor metrics**: Track token usage and latency
- **Use appropriate temperature**: Lower for factual tasks, higher for creative tasks

### 3. Security

- **Rotate API keys**: Regularly update your API keys
- **Use Entra Agent ID**: Enable for enterprise security requirements
- **Validate inputs**: Sanitize user inputs before sending
- **Audit logging**: Monitor all agent interactions

### 4. Cost Management

- **Monitor token usage**: Track total tokens consumed
- **Optimize prompts**: Reduce unnecessary context
- **Set max_tokens wisely**: Avoid unnecessarily large responses
- **Use threads**: Leverage stateful threads to reduce context repetition

## Monitoring and Metrics

### Client Metrics

```python
# Get client metrics
metrics = client.get_metrics()

print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['successful_requests'] / metrics['total_requests'] * 100:.1f}%")
print(f"Average latency: {metrics['average_latency']:.3f}s")
print(f"Total tokens: {metrics['total_tokens_used']}")
```

### Health Checks

```python
# Check service health
is_healthy = await client.health_check()
if not is_healthy:
    print("⚠️ Foundry Agent Service is unhealthy")
```

## Examples

See the complete example file at `examples/foundry_agent_service_example.py` which demonstrates:

- Basic message sending
- Stateful thread management
- Foundry Tools usage
- Model Orchestrator integration
- Advanced configuration
- Metrics and monitoring

Run the example:

```bash
python examples/foundry_agent_service_example.py
```

## Troubleshooting

### Common Issues

**1. "Foundry Agent Service endpoint URL not configured"**
- Solution: Set `FOUNDRY_AGENT_SERVICE_ENDPOINT` environment variable

**2. "Foundry Agent Service API key not configured"**
- Solution: Set `FOUNDRY_AGENT_SERVICE_API_KEY` environment variable

**3. Request timeouts**
- Solution: Increase `FOUNDRY_TIMEOUT` for complex requests
- Solution: Check network connectivity to Azure

**4. "Agent ID not configured" warning**
- Impact: Entra Agent ID features may be limited
- Solution: Set `FOUNDRY_AGENT_ID` if using Entra integration

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration Guide

### From Other Model Types

If you're currently using other model types in AOS:

```python
# Before - using VLLM or AZURE_ML
result = await orchestrator.process_model_request(
    model_type=ModelType.VLLM,
    domain="leadership",
    user_input="Your prompt",
    conversation_id="conv-001"
)

# After - using Foundry Agent Service
result = await orchestrator.process_model_request(
    model_type=ModelType.FOUNDRY_AGENT_SERVICE,
    domain="leadership",
    user_input="Your prompt",
    conversation_id="conv-001"
)
```

### Model Preference Update

The Model Orchestrator now prefers Foundry Agent Service when available:

```python
# Automatic selection will choose Foundry Agent Service if configured
model_type = await orchestrator.select_optimal_model(domain="leadership")
# Returns ModelType.FOUNDRY_AGENT_SERVICE if available
```

## API Reference

### FoundryAgentServiceConfig

```python
@dataclass
class FoundryAgentServiceConfig:
    endpoint_url: str           # Service endpoint
    api_key: str                # API authentication key
    agent_id: str               # Agent identity (optional)
    model: str                  # Model name (default: llama-3.3-70b)
    enable_stateful_threads: bool
    enable_entra_agent_id: bool
    enable_foundry_tools: bool
    timeout: int                # Request timeout
    temperature: float          # Sampling temperature
    max_tokens: int             # Max response tokens
    top_p: float                # Nucleus sampling
```

### FoundryAgentServiceClient

```python
class FoundryAgentServiceClient:
    async def initialize() -> None
    async def send_message(message, thread_id, domain, ...) -> FoundryResponse
    async def create_thread(metadata) -> str
    async def get_thread_info(thread_id) -> ThreadInfo
    async def delete_thread(thread_id) -> bool
    async def health_check() -> bool
    def get_metrics() -> Dict[str, Any]
```

### FoundryResponse

```python
@dataclass
class FoundryResponse:
    content: str                # Response content
    thread_id: str              # Thread identifier
    agent_id: str               # Agent identifier
    model: str                  # Model used
    tools_used: List[str]       # Tools utilized
    usage: Dict[str, Any]       # Token usage stats
    success: bool               # Request success
    error: Optional[str]        # Error message if failed
```

## Support

For issues or questions:

1. Check this documentation
2. Review example code in `examples/foundry_agent_service_example.py`
3. Run tests: `pytest tests/test_foundry_agent_service.py`
4. Open an issue on GitHub

## Related Documentation

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Model Orchestration](./model_orchestration.md)
- [AOS ML Pipeline](./ml.md)
- [Configuration Guide](./configuration.md)
