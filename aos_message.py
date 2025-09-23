"""
AOS Messaging Models: Envelope, MessagesQuery, UiAction
Unified message and action models for agent communication and UI integration.
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal, List
import time
import uuid

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

class MessagesQuery(BaseModel):
    """
    Query parameters for retrieving messages from a conversation
    """
    boardroomId: str
    conversationId: str
    since: Optional[str] = None  # RowKey (ULID/timestamp) high-watermark

class UiAction(BaseModel):
    """
    Represents a user interface action for agent interactions
    """
    boardroomId: str
    conversationId: str
    agentId: str
    action: str
    args: Dict[str, Any]
    scope: Literal["local", "network"] = "local"
    correlationId: Optional[str] = None