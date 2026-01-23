"""
AOS Messaging - Core Conversation System

Implements the conversation infrastructure for agent coordination,
decision-making, and formal agreement protocols within AOS.

This provides the OS-level conversation and coordination mechanisms
that agents can use for structured interactions.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from aos.monitoring.audit_trail import AuditEventType, AuditSeverity, audit_log


class ConversationType(Enum):
    """Types of conversations for agent coordination"""
    # Agent coordination
    AGENT_COORDINATION = "agent_coordination"
    TASK_ASSIGNMENT = "task_assignment"
    RESOURCE_ALLOCATION = "resource_allocation"
    CAPABILITY_NEGOTIATION = "capability_negotiation"

    # Decision making
    COLLECTIVE_DECISION = "collective_decision"
    CONSENSUS_BUILDING = "consensus_building"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PRIORITY_SETTING = "priority_setting"

    # System operations
    SYSTEM_HANDOFF = "system_handoff"
    WORKFLOW_COORDINATION = "workflow_coordination"
    STATUS_REPORTING = "status_reporting"
    ERROR_HANDLING = "error_handling"

    # Agreements and commitments
    SERVICE_AGREEMENT = "service_agreement"
    RESOURCE_COMMITMENT = "resource_commitment"
    PERFORMANCE_COVENANT = "performance_covenant"
    TERMINATION_AGREEMENT = "termination_agreement"

    # Network and external
    NETWORK_NEGOTIATION = "network_negotiation"
    EXTERNAL_INTEGRATION = "external_integration"
    PROTOCOL_ESTABLISHMENT = "protocol_establishment"
    BOUNDARY_DEFINITION = "boundary_definition"


class ConversationRole(Enum):
    """Roles that can participate in conversations"""
    # Core AOS roles
    SYSTEM = "system"
    ORCHESTRATOR = "orchestrator"
    AGENT_MANAGER = "agent_manager"
    RESOURCE_MANAGER = "resource_manager"

    # Agent roles (generic)
    AGENT = "agent"
    COORDINATOR_AGENT = "coordinator_agent"
    SPECIALIST_AGENT = "specialist_agent"
    MONITOR_AGENT = "monitor_agent"

    # Service roles
    MCP_SERVER = "mcp_server"
    EXTERNAL_SERVICE = "external_service"
    NETWORK_NODE = "network_node"

    # Administrative
    ADMIN = "admin"
    OBSERVER = "observer"


class ConversationStatus(Enum):
    """Status of a conversation"""
    DRAFT = "draft"
    INITIATED = "initiated"
    ACTIVE = "active"
    PENDING_RESPONSE = "pending_response"
    PENDING_SIGNATURE = "pending_signature"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class ConversationPriority(Enum):
    """Priority levels for conversations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class ConversationSignature:
    """Represents a signature on a conversation"""
    signer_agent: ConversationRole
    signer_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signature_type: str = "digital"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationMessage:
    """A message within a conversation"""
    message_id: str
    sender_role: ConversationRole
    sender_name: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_type: str = "standard"
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Core conversation data structure for AOS agent coordination"""
    id: str
    type: ConversationType
    title: str
    description: str
    champion: ConversationRole
    status: ConversationStatus = ConversationStatus.DRAFT
    priority: ConversationPriority = ConversationPriority.MEDIUM

    # Participation
    participants: List[ConversationRole] = field(default_factory=list)
    required_signers: List[ConversationRole] = field(default_factory=list)
    signatures: List[ConversationSignature] = field(default_factory=list)

    # Content and context
    messages: List[ConversationMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    agreements: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    # AOS-specific fields
    workflow_id: Optional[str] = None
    task_ids: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    # Flags and controls
    requires_consensus: bool = False
    requires_human_oversight: bool = False
    is_automated: bool = True
    delegation_allowed: bool = True

    def add_message(self, sender_role: ConversationRole, sender_name: str,
                   content: str, message_type: str = "standard") -> str:
        """Add a message to the conversation"""
        message_id = str(uuid.uuid4())
        message = ConversationMessage(
            message_id=message_id,
            sender_role=sender_role,
            sender_name=sender_name,
            content=content,
            message_type=message_type
        )
        self.messages.append(message)
        self.updated_at = datetime.now(timezone.utc)
        return message_id

    def add_signature(self, signer_role: ConversationRole, signer_name: str) -> bool:
        """Add a signature to the conversation"""
        if signer_role not in self.required_signers:
            return False

        if self.is_signed_by(signer_role):
            return False

        signature = ConversationSignature(
            signer_agent=signer_role,
            signer_name=signer_name
        )
        self.signatures.append(signature)
        self.updated_at = datetime.now(timezone.utc)

        # Check if all signatures are collected
        if self.is_fully_signed():
            self.status = ConversationStatus.COMPLETED

        return True

    def is_signed_by(self, role: ConversationRole) -> bool:
        """Check if conversation is signed by specific role"""
        return any(sig.signer_agent == role for sig in self.signatures)

    def is_fully_signed(self) -> bool:
        """Check if all required signatures are collected"""
        signed_roles = {sig.signer_agent for sig in self.signatures}
        required_roles = set(self.required_signers)
        return required_roles.issubset(signed_roles)

    def get_pending_signers(self) -> List[ConversationRole]:
        """Get list of roles that still need to sign"""
        signed_roles = {sig.signer_agent for sig in self.signatures}
        return [role for role in self.required_signers if role not in signed_roles]

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "champion": self.champion.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "participants": [p.value for p in self.participants],
            "required_signers": [r.value for r in self.required_signers],
            "signatures": [
                {
                    "signer_agent": sig.signer_agent.value,
                    "signer_name": sig.signer_name,
                    "timestamp": sig.timestamp.isoformat(),
                    "signature_type": sig.signature_type
                }
                for sig in self.signatures
            ],
            "messages": [
                {
                    "message_id": msg.message_id,
                    "sender_role": msg.sender_role.value,
                    "sender_name": msg.sender_name,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type
                }
                for msg in self.messages
            ],
            "context": self.context,
            "agreements": self.agreements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "workflow_id": self.workflow_id,
            "task_ids": self.task_ids,
            "resource_requirements": self.resource_requirements,
            "performance_metrics": self.performance_metrics,
            "requires_consensus": self.requires_consensus,
            "requires_human_oversight": self.requires_human_oversight,
            "is_automated": self.is_automated,
            "delegation_allowed": self.delegation_allowed
        }


class ConversationSystem(ABC):
    """Abstract base class for conversation system implementations"""

    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation"""

    @abstractmethod
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID"""

    @abstractmethod
    async def update_conversation(self, conversation: Conversation) -> None:
        """Update an existing conversation"""

    @abstractmethod
    async def list_conversations_by_role(self, role: ConversationRole) -> List[Conversation]:
        """List conversations where role is participant"""

    @abstractmethod
    async def list_pending_signatures(self, signer: ConversationRole) -> List[Conversation]:
        """List conversations pending signature from a specific role"""

    @abstractmethod
    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole,
                              signer_name: str) -> bool:
        """Sign a conversation"""

    @abstractmethod
    async def add_message(self, conversation_id: str, sender_role: ConversationRole,
                         sender_name: str, content: str, message_type: str = "standard") -> Optional[str]:
        """Add a message to a conversation"""


class AOSConversationSystem(ConversationSystem):
    """AOS implementation of the conversation system"""

    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    async def initialize(self):
        """Initialize the conversation system"""
        if self._initialized:
            return

        self.logger.info("Initializing AOS Conversation System")

        # Set up background tasks
        asyncio.create_task(self._cleanup_expired_conversations())

        self._initialized = True

        await audit_log(
            AuditEventType.COMPONENT_STARTED,
            "Conversation system initialized",
            component="conversation_system",
            severity=AuditSeverity.INFO
        )

    async def create_conversation(self, conversation: Conversation) -> str:
        """Create a new conversation"""
        try:
            if not conversation.id:
                conversation.id = str(uuid.uuid4())

            conversation.created_at = datetime.now(timezone.utc)
            conversation.updated_at = datetime.now(timezone.utc)

            self.conversations[conversation.id] = conversation

            await audit_log(
                AuditEventType.MESSAGE_SENT,  # Using closest available event type
                f"Conversation created: {conversation.title}",
                subject_id=conversation.champion.value,
                subject_type="role",
                component="conversation_system",
                severity=AuditSeverity.INFO,
                metadata={
                    "conversation_id": conversation.id,
                    "type": conversation.type.value,
                    "champion": conversation.champion.value,
                    "participants": [p.value for p in conversation.participants]
                }
            )

            self.logger.info("Created conversation %s of type %s", conversation.id, conversation.type.value)
            return conversation.id

        except Exception as error:
            self.logger.error("Failed to create conversation: %s", str(error))
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID"""
        return self.conversations.get(conversation_id)

    async def update_conversation(self, conversation: Conversation) -> None:
        """Update an existing conversation"""
        try:
            conversation.updated_at = datetime.now(timezone.utc)
            self.conversations[conversation.id] = conversation

            self.logger.info("Updated conversation %s", conversation.id)

        except Exception as error:
            self.logger.error("Failed to update conversation %s: %s", conversation.id, str(error))
            raise

    async def list_conversations_by_role(self, role: ConversationRole) -> List[Conversation]:
        """List conversations where role is participant"""
        return [
            conv for conv in self.conversations.values()
            if conv.champion == role or role in conv.participants
        ]

    async def list_pending_signatures(self, signer: ConversationRole) -> List[Conversation]:
        """List conversations pending signature from a specific role"""
        pending = []
        for conv in self.conversations.values():
            if (signer in conv.required_signers and
                not conv.is_signed_by(signer) and
                conv.status in [ConversationStatus.PENDING_SIGNATURE, ConversationStatus.ACTIVE]):
                pending.append(conv)
        return pending

    async def sign_conversation(self, conversation_id: str, signer_role: ConversationRole,
                              signer_name: str) -> bool:
        """Sign a conversation"""
        try:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                self.logger.warning("Conversation %s not found", conversation_id)
                return False

            if signer_role not in conversation.required_signers:
                self.logger.warning("Role %s not required to sign conversation %s", signer_role.value, conversation_id)
                return False

            if conversation.is_signed_by(signer_role):
                self.logger.warning("Conversation %s already signed by %s", conversation_id, signer_role.value)
                return False

            success = conversation.add_signature(signer_role, signer_name)

            if success:
                await audit_log(
                    AuditEventType.MESSAGE_RECEIVED,  # Using closest available event type
                    f"Conversation signed: {conversation.title}",
                    subject_id=signer_name,
                    subject_type="agent",
                    component="conversation_system",
                    severity=AuditSeverity.INFO,
                    metadata={
                        "conversation_id": conversation_id,
                        "signer_role": signer_role.value,
                        "fully_signed": conversation.is_fully_signed()
                    }
                )

                self.logger.info("Conversation %s signed by %s[%s]", conversation_id, signer_name, signer_role.value)

            return success

        except Exception as error:
            self.logger.error("Failed to sign conversation %s: %s", conversation_id, str(error))
            return False

    async def add_message(self, conversation_id: str, sender_role: ConversationRole,
                         sender_name: str, content: str, message_type: str = "standard") -> Optional[str]:
        """Add a message to a conversation"""
        try:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                self.logger.warning("Conversation %s not found", conversation_id)
                return None

            message_id = conversation.add_message(sender_role, sender_name, content, message_type)

            self.logger.debug("Added message to conversation %s", conversation_id)
            return message_id

        except Exception as error:
            self.logger.error("Failed to add message to conversation %s: %s", conversation_id, str(error))
            return None

    async def get_active_conversations(self) -> List[Conversation]:
        """Get all active conversations"""
        return [
            conv for conv in self.conversations.values()
            if conv.status in [ConversationStatus.ACTIVE, ConversationStatus.PENDING_RESPONSE,
                             ConversationStatus.PENDING_SIGNATURE]
        ]

    async def get_conversation_metrics(self) -> Dict[str, Any]:
        """Get conversation system metrics"""
        total = len(self.conversations)
        status_counts = {}
        type_counts = {}

        for conv in self.conversations.values():
            status_counts[conv.status.value] = status_counts.get(conv.status.value, 0) + 1
            type_counts[conv.type.value] = type_counts.get(conv.type.value, 0) + 1

        return {
            "total_conversations": total,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "active_conversations": len(await self.get_active_conversations())
        }

    async def _cleanup_expired_conversations(self):
        """Background task to clean up expired conversations"""
        while True:
            try:
                now = datetime.now(timezone.utc)
                expired_ids = []

                for conv_id, conv in self.conversations.items():
                    if conv.expires_at and conv.expires_at < now:
                        expired_ids.append(conv_id)

                for conv_id in expired_ids:
                    conv = self.conversations[conv_id]
                    conv.status = ConversationStatus.EXPIRED

                    await audit_log(
                        AuditEventType.SYSTEM_ERROR,  # Using closest available
                        f"Conversation expired: {conv.title}",
                        component="conversation_system",
                        severity=AuditSeverity.WARNING,
                        metadata={"conversation_id": conv_id}
                    )

                if expired_ids:
                    self.logger.info("Marked %s conversations as expired", len(expired_ids))

                # Sleep for 5 minutes
                await asyncio.sleep(300)

            except Exception as error:
                self.logger.error("Error in conversation cleanup task: %s", str(error))
                await asyncio.sleep(300)

    async def health_check(self) -> Dict[str, Any]:
        """Get health status of conversation system"""
        try:
            metrics = await self.get_conversation_metrics()
            return {
                "initialized": self._initialized,
                "total_conversations": metrics["total_conversations"],
                "active_conversations": metrics["active_conversations"],
                "status": "healthy"
            }
        except Exception as error:
            return {
                "initialized": self._initialized,
                "status": "error",
                "error": str(error)
            }


# Factory function for creating conversation system
def create_conversation_system() -> AOSConversationSystem:
    """Create and return an AOS conversation system instance"""
    return AOSConversationSystem()


# Helper functions for common conversation patterns
async def create_agent_coordination_conversation(
    title: str,
    description: str,
    champion: ConversationRole,
    participants: List[ConversationRole],
    context: Dict[str, Any] = None
) -> Conversation:
    """Create a standard agent coordination conversation"""
    return Conversation(
        id="",  # Will be set when created
        type=ConversationType.AGENT_COORDINATION,
        title=title,
        description=description,
        champion=champion,
        participants=participants,
        context=context or {},
        is_automated=True,
        delegation_allowed=True
    )


async def create_decision_conversation(
    title: str,
    description: str,
    champion: ConversationRole,
    required_signers: List[ConversationRole],
    requires_consensus: bool = False,
    context: Dict[str, Any] = None
) -> Conversation:
    """Create a decision-making conversation"""
    return Conversation(
        id="",  # Will be set when created
        type=ConversationType.COLLECTIVE_DECISION,
        title=title,
        description=description,
        champion=champion,
        participants=required_signers,
        required_signers=required_signers,
        requires_consensus=requires_consensus,
        context=context or {},
        priority=ConversationPriority.HIGH
    )
