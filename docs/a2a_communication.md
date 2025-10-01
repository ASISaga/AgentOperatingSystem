# Agent-to-Agent (A2A) Communication

## Message Types

- **Task Requests**: Delegate work to specific agents
- **Capability Requests**: Query agent capabilities and availability
- **Collaboration Requests**: Multi-agent coordination for complex tasks
- **Status Updates**: Report progress and completion status

## Message Format

```python
{
    "from": "sender_agent_id",
    "to": "target_agent_id",
    "message": {
        "type": "task_request",
        "content": "Task description",
        "priority": "high",
        "parameters": {...}
    },
    "timestamp": 1234567890.123
}
```

## Implementing A2A Agents

```python
class MyAgent:
    async def handle_agent_message(self, message):
        msg_type = message["message"]["type"]
        if msg_type == "task_request":
            return await self.process_task(message["message"])
        elif msg_type == "capability_request":
            return await self.report_capabilities()
        else:
            return {"error": f"Unknown message type: {msg_type}"}
```
