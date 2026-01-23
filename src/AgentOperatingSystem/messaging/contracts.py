"""
AOS Service Bus Message Contracts

Defines the message contracts for communication between applications
(e.g., BusinessInfinity) and the AgentOperatingSystem via Azure Service Bus.

These contracts ensure consistent message formats across the distributed system.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AOSMessageType(str, Enum):
    """Message types for AOS Service Bus communication."""

    # Agent Operations
    AGENT_QUERY = "aos.agent.query"
    AGENT_RESPONSE = "aos.agent.response"
    AGENT_REGISTER = "aos.agent.register"
    AGENT_UNREGISTER = "aos.agent.unregister"
    AGENT_LIST = "aos.agent.list"
    AGENT_STATUS = "aos.agent.status"

    # Workflow Operations
    WORKFLOW_EXECUTE = "aos.workflow.execute"
    WORKFLOW_RESULT = "aos.workflow.result"
    WORKFLOW_STATUS = "aos.workflow.status"
    WORKFLOW_CANCEL = "aos.workflow.cancel"

    # Storage Operations
    STORAGE_GET = "aos.storage.get"
    STORAGE_SET = "aos.storage.set"
    STORAGE_DELETE = "aos.storage.delete"
    STORAGE_LIST = "aos.storage.list"
    STORAGE_RESULT = "aos.storage.result"

    # Orchestration Operations
    DECISION_REQUEST = "aos.decision.request"
    DECISION_RESULT = "aos.decision.result"

    # MCP Operations
    MCP_CALL = "aos.mcp.call"
    MCP_RESULT = "aos.mcp.result"

    # System Operations
    HEALTH_CHECK = "aos.system.health"
    HEALTH_RESPONSE = "aos.system.health.response"
    PING = "aos.system.ping"
    PONG = "aos.system.pong"

    # Events
    EVENT_NOTIFICATION = "aos.event.notification"
    ERROR = "aos.error"


class MessagePriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AOSMessageHeader:
    """Standard message header for all AOS messages."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = "unknown"
    target: str = "aos"
    message_type: str = ""
    priority: str = MessagePriority.NORMAL.value
    ttl_seconds: int = 300  # 5 minutes default

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AOSMessageHeader":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AOSMessage:
    """
    Base message format for AOS Service Bus communication.

    All messages follow this structure:
    - header: Metadata about the message
    - payload: The actual message content
    """

    header: AOSMessageHeader
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            "header": self.header.to_dict(),
            "payload": self.payload
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "header": self.header.to_dict(),
            "payload": self.payload
        }

    @classmethod
    def from_json(cls, json_str: str) -> "AOSMessage":
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        return cls(
            header=AOSMessageHeader.from_dict(data.get("header", {})),
            payload=data.get("payload", {})
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AOSMessage":
        """Create message from dictionary."""
        return cls(
            header=AOSMessageHeader.from_dict(data.get("header", {})),
            payload=data.get("payload", {})
        )

    @classmethod
    def create_request(
        cls,
        message_type: AOSMessageType,
        payload: Dict[str, Any],
        source: str,
        reply_to: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> "AOSMessage":
        """Create a new request message."""
        return cls(
            header=AOSMessageHeader(
                message_type=message_type.value,
                source=source,
                target="aos",
                reply_to=reply_to,
                correlation_id=correlation_id or str(uuid.uuid4()),
                priority=priority.value
            ),
            payload=payload
        )

    @classmethod
    def create_response(
        cls,
        original_message: "AOSMessage",
        message_type: AOSMessageType,
        payload: Dict[str, Any],
        source: str = "aos"
    ) -> "AOSMessage":
        """Create a response message for a request."""
        return cls(
            header=AOSMessageHeader(
                message_type=message_type.value,
                source=source,
                target=original_message.header.source,
                correlation_id=original_message.header.correlation_id,
                reply_to=None
            ),
            payload=payload
        )


# Specific payload schemas

@dataclass
class AgentQueryPayload:
    """Payload for agent query messages."""
    agent_id: str
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 1000
    temperature: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentResponsePayload:
    """Payload for agent response messages."""
    agent_id: str
    response: str
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowExecutePayload:
    """Payload for workflow execution request."""
    workflow_id: str
    workflow_name: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowResultPayload:
    """Payload for workflow execution result."""
    workflow_id: str
    status: str  # "completed", "failed", "cancelled"
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StorageOperationPayload:
    """Payload for storage operations."""
    operation: str  # "get", "set", "delete", "list"
    container: str
    key: Optional[str] = None
    value: Optional[Any] = None
    prefix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StorageResultPayload:
    """Payload for storage operation results."""
    operation: str
    success: bool
    data: Optional[Any] = None
    keys: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorPayload:
    """Payload for error messages."""
    error_code: str
    error_message: str
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Queue and Topic names

class AOSQueues:
    """Standard queue names for AOS communication."""

    # Request queues (BI -> AOS)
    AOS_REQUESTS = "aos-requests"

    # Response queues (AOS -> specific app)
    BUSINESS_INFINITY_RESPONSES = "businessinfinity-responses"

    # Event topics
    AOS_EVENTS = "aos-events"
    AGENT_EVENTS = "aos-agent-events"
    WORKFLOW_EVENTS = "aos-workflow-events"


class AOSTopics:
    """Standard topic names for AOS event broadcasting."""

    # Main event topics
    AOS_EVENTS = "aos-events"
    AGENT_EVENTS = "aos-agent-events"
    WORKFLOW_EVENTS = "aos-workflow-events"
    SYSTEM_EVENTS = "aos-system-events"


__all__ = [
    "AOSMessageType",
    "MessagePriority",
    "AOSMessageHeader",
    "AOSMessage",
    "AgentQueryPayload",
    "AgentResponsePayload",
    "WorkflowExecutePayload",
    "WorkflowResultPayload",
    "StorageOperationPayload",
    "StorageResultPayload",
    "ErrorPayload",
    "AOSQueues",
    "AOSTopics",
]
