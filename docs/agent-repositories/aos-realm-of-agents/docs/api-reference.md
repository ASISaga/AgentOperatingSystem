# aos-realm-of-agents API Reference

## Agent Registry Schema

### Agent Entry

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agent_id` | string | Yes | Unique agent identifier |
| `agent_type` | string | Yes | Agent class name |
| `purpose` | string | Yes | Agent purpose statement |
| `adapter_name` | string | No | LoRA adapter name |
| `config` | object | No | Additional runtime configuration |

### Example Registry

```json
{
    "agents": [
        {
            "agent_id": "ceo",
            "agent_type": "LeadershipAgent",
            "purpose": "Strategic leadership and decision-making",
            "adapter_name": "leadership",
            "config": {
                "skills": ["make_decision", "consult_stakeholders"]
            }
        }
    ]
}
```

## Service Bus Functions

### realm_agent_handler

**Trigger**: Service Bus queue `realm-agent-requests`

Routes messages to the appropriate agent based on registry configuration.

## HTTP Endpoints

### Agent Status

```
GET /api/realm/agents
```

Returns the list of registered agents and their current status.

### Agent Configuration

```
GET /api/realm/config
```

Returns the current agent registry configuration.
