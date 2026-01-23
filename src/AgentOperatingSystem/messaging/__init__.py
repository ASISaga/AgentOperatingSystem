"""
AOS Messaging Module

Messaging infrastructure for inter-agent communication.
"""

from .bus import MessageBus

# Azure Functions Service Bus contracts and handlers
from .contracts import (
    AgentQueryPayload,
    AgentQueryResponse,
    AOSMessage,
    AOSMessageHeader,
    AOSMessageType,
    AOSQueues,
    AOSTopics,
    HealthCheckPayload,
    HealthCheckResponse,
    MCPCallPayload,
    MCPCallResponse,
    StorageOperationPayload,
    StorageOperationResponse,
    WorkflowExecutePayload,
    WorkflowExecuteResponse,
)

# New refactored classes
from .envelope import MessageEnvelope
from .reliability import CircuitBreaker, RetryPolicy
from .router import MessageRouter
from .servicebus_handlers import AOSServiceBusHandlers
from .servicebus_manager import ServiceBusManager
from .types import Message, MessagePriority, MessageType

try:
    ADVANCED_MESSAGING_AVAILABLE = True
except ImportError:
    ADVANCED_MESSAGING_AVAILABLE = False

__all__ = [
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageBus",
    "MessageRouter",
    "ServiceBusManager",
    # New refactored classes
    "MessageEnvelope",
    "RetryPolicy",
    "CircuitBreaker",
    # Azure Functions Service Bus contracts
    "AOSMessageType",
    "AOSMessageHeader",
    "AOSMessage",
    "AOSQueues",
    "AOSTopics",
    "AgentQueryPayload",
    "AgentQueryResponse",
    "WorkflowExecutePayload",
    "WorkflowExecuteResponse",
    "StorageOperationPayload",
    "StorageOperationResponse",
    "MCPCallPayload",
    "MCPCallResponse",
    "HealthCheckPayload",
    "HealthCheckResponse",
    # Service Bus handlers
    "AOSServiceBusHandlers",
]

if ADVANCED_MESSAGING_AVAILABLE:
    __all__.extend([
        "AOSConversationSystem", "Conversation", "ConversationType", "ConversationRole",
        "create_conversation_system", "create_agent_coordination_conversation", "create_decision_conversation",
        "NetworkProtocol", "NetworkMessage", "NetworkNode"
    ])

# Advanced messaging features (try-except for optional dependencies)
try:
    pass

    __all__.extend([
        "EventStream",
        "StreamProcessor",
        "ComplexEventProcessor",
        "SagaOrchestrator",
        "SagaStatus",
        "ChoreographyEngine",
        "IntelligentRouter",
        "PriorityQueueManager",
        "PriorityLevel"
    ])
except ImportError:
    pass  # Advanced features not available
