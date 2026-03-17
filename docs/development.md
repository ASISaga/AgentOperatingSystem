# Development & Contributing

## Adding New Orchestrator Types

1. Extend `BaseOrchestrator`:

```python
from src.core.base_orchestrator import BaseOrchestrator
class CustomOrchestrator(BaseOrchestrator):
    async def handle_request(self, request):
        return {"response": "custom response", "success": True}
    async def cleanup(self):
        await super().cleanup()
```

2. Register for A2A communication:

```python
await orchestrator.register_agent("custom_orchestrator", self)
```

## Contributing Guidelines

- Follow the BaseOrchestrator pattern
- Implement `handle_agent_message()` for A2A
- Use consistent error handling and logging
- Add validation tests for new features
- Update configuration schema as needed
