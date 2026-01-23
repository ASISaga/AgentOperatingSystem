"""
AOS Message Types and Core Message Classes

Standard message types and message structure for AOS inter-agent communication.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(Enum):
    """Standard message types for AOS"""
    SYSTEM = "system"
    AGENT_TO_AGENT = "agent_to_agent"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    WORKFLOW = "workflow"
    DECISION = "decision"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Standard message structure for AOS"""
    id: str
    type: MessageType
    from_agent: str
    to_agent: Optional[str]  # None for broadcast messages
    content: Dict[str, Any]
    timestamp: datetime
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    @classmethod
    def create(cls,
               message_type: MessageType,
               from_agent: str,
               content: Dict[str, Any],
               to_agent: Optional[str] = None,
               priority: MessagePriority = MessagePriority.NORMAL,
               correlation_id: Optional[str] = None,
               expires_in_seconds: int = 300) -> 'Message':
        """Create a new message with auto-generated ID and timestamp"""
        return cls(
            id=str(uuid.uuid4()),
            type=message_type,
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            timestamp=datetime.utcnow(),
            priority=priority,
            correlation_id=correlation_id,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        )

    def is_expired(self) -> bool:
        """Check if message has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            id=data["id"],
            type=MessageType(data["type"]),
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=MessagePriority(data["priority"]),
            correlation_id=data.get("correlation_id"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )
