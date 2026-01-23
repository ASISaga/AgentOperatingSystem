"""
Envelope data model - represents a message envelope for agent communication
"""
import time
import uuid
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

MessageType = Literal["chat", "toolResult", "status", "error"]

class Envelope(BaseModel):
    """
    Message envelope for agent communication in the system
    """
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlationId: str
    traceId: str
    boardroomId: str
    conversationId: str
    senderAgentId: str
    role: str
    scope: Literal["local", "network"]
    messageType: MessageType
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=lambda: time.time())
    schemaVersion: str = "1.0.0"
