# Quick Start

## Basic Usage

```python
from src.core.base_orchestrator import BaseOrchestrator
from src.Orchestrator.orchestratorwithmcp import EnhancedOrchestrator

orchestrator = EnhancedOrchestrator()
await orchestrator.initialize()

request = {
    "domain": "leadership",
    "message": "How to motivate teams during challenging times?",
    "conversationId": "session-123"
}

response = await orchestrator.handle_request(request)
print(f"Response: {response}")
```

## A2A Communication Example

```python
sales_agent = SalesAgent()
leadership_agent = LeadershipAgent()
await orchestrator.register_agent("sales_agent", sales_agent)
await orchestrator.register_agent("leadership_agent", leadership_agent)

message = {
    "type": "collaboration_request",
    "content": "Need leadership strategy for Q4 sales targets",
    "priority": "high"
}

result = await orchestrator.send_agent_message(
    "sales_agent", "leadership_agent", message
)
await orchestrator.process_agent_messages()
```

## Self-Learning with GitHub Integration

```python
domain_config = {"erp": {"uri": "wss://erp-mcp.example.com", "api_key": "key123"}}
github_config = {"uri": "wss://github-mcp-server.example.com", "api_key": "github_token"}
self_learning = SelfLearningOrchestrator(domain_config, github_config)
await self_learning.initialize()
result = await self_learning.execute_business_process(
    domain="erp",
    function_name="create_sales_order",
    parameters={"customer": "ACME Corp", "amount": 10000}
)
```
