# REST API for Agent Conversation (Web Client Integration)

## Overview

This API enables web clients to display and interact with agent-to-agent conversations.

## Endpoints

### `GET /conversations/{conversation_id}`
- Returns the full conversation history for a given conversation.

### `POST /conversations/{conversation_id}/message`
- Send a new message to the conversation.
- Request body: `{ "from": "agent_id", "to": "agent_id", "message": { ... } }`
- Response: `{ "status": "ok", "message_id": "..." }`

### `GET /agents`
- List all registered agents.

## Example FastAPI Implementation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class Message(BaseModel):
    from_agent: str
    to_agent: str
    message: dict
    timestamp: float

conversations: Dict[str, List[Message]] = {}

@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    return conversations.get(conversation_id, [])

@app.post("/conversations/{conversation_id}/message")
def post_message(conversation_id: str, msg: Message):
    conversations.setdefault(conversation_id, []).append(msg)
    return {"status": "ok", "message_id": len(conversations[conversation_id])}

@app.get("/agents")
def get_agents():
    # Return a list of registered agents (stub)
    return ["sales_agent", "leadership_agent"]
```
