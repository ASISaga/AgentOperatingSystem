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
    "CircuitBreaker"
]

if ADVANCED_MESSAGING_AVAILABLE:
    __all__.extend([
        "AOSConversationSystem", "Conversation", "ConversationType", "ConversationRole",
        "create_conversation_system", "create_agent_coordination_conversation", "create_decision_conversation",
        "NetworkProtocol", "NetworkMessage", "NetworkNode"
    ])