"""
AOS Messaging Module

Messaging infrastructure for inter-agent communication.
"""

from .types import Message, MessageType, MessagePriority
from .bus import MessageBus
from .router import MessageRouter
from .servicebus_manager import ServiceBusManager
# New refactored classes
from .envelope import MessageEnvelope
from .reliability import RetryPolicy, CircuitBreaker
# Azure Functions Service Bus contracts and handlers
from .contracts import (
    AOSMessageType,
    AOSMessageHeader,
    AOSMessage,
    AOSQueues,
    AOSTopics,
    AgentQueryPayload,
    AgentResponsePayload,
    WorkflowExecutePayload,
    WorkflowResultPayload,
    StorageOperationPayload,
    StorageResultPayload,
    ErrorPayload,
)
from .servicebus_handlers import AOSServiceBusHandlers

try:
    from .conversation_system import (
        AOSConversationSystem, Conversation, ConversationType, ConversationRole,
        create_conversation_system, create_agent_coordination_conversation, create_decision_conversation
    )
    from .network_protocol import NetworkProtocol, NetworkMessage, NetworkNode
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
    "AgentResponsePayload",
    "WorkflowExecutePayload",
    "WorkflowResultPayload",
    "StorageOperationPayload",
    "StorageResultPayload",
    "ErrorPayload",
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
    from .streaming import EventStream, StreamProcessor, ComplexEventProcessor
    from .saga import SagaOrchestrator, SagaStatus, ChoreographyEngine
    from .routing import IntelligentRouter
    from .priority import PriorityQueueManager, PriorityLevel

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