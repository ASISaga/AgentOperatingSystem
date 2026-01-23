"""
Message Envelope - Standardized message format with correlation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class MessageEnvelope:
    """
    Standardized message envelope with:
    - Message type and version
    - Correlation and causation IDs for tracing
    - Timestamp and actor information
    - Payload with schema validation
    """

    def __init__(
        self,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        actor: Optional[str] = None,
        version: str = "1.0",
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.version = version
        self.timestamp = datetime.utcnow().isoformat()
        self.correlation_id = correlation_id or self.message_id
        self.causation_id = causation_id or self.message_id
        self.actor = actor
        self.attributes = attributes or {}
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "version": self.version,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor": self.actor,
            "attributes": self.attributes,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageEnvelope':
        """Create envelope from dictionary."""
        envelope = cls(
            message_type=data["message_type"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            actor=data.get("actor"),
            version=data.get("version", "1.0"),
            attributes=data.get("attributes", {})
        )
        envelope.message_id = data["message_id"]
        envelope.timestamp = data["timestamp"]
        return envelope
