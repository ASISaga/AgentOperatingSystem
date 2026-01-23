"""
AOS Messaging - Network Protocol for Inter-Agent Communication

Extends the basic AOS messaging to enable distributed agent communication
across networks, including agent-to-agent protocol, discovery, negotiation,
and coordination mechanisms.

This is the OS-level networking infrastructure for AOS.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from aos.messaging.message_bus import MessageBus, Message
from aos.monitoring.audit_trail import audit_log, AuditEventType, AuditSeverity


class NetworkMessageType(Enum):
    """Types of inter-agent network messages"""
    DISCOVERY = "discovery"
    NEGOTIATION = "negotiation"
    COORDINATION = "coordination"
    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"
    CAPABILITY_ANNOUNCEMENT = "capability_announcement"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_OFFER = "resource_offer"
    AGREEMENT = "agreement"
    TERMINATION = "termination"


class NetworkNodeStatus(Enum):
    """Status of a network node"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class NetworkIdentity:
    """Identity information for network nodes"""
    node_id: str
    node_name: str
    node_type: str  # "aos", "agent", "service", "external"
    version: str
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class NetworkNode:
    """Represents a node in the AOS network"""
    identity: NetworkIdentity
    endpoint_url: str
    status: NetworkNodeStatus
    last_heartbeat: datetime = field(default_factory=datetime.now)
    network_joined: datetime = field(default_factory=datetime.now)

    # Agent and capability information
    active_agents: Set[str] = field(default_factory=set)
    agent_capabilities: Dict[str, List[str]] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)

    def is_healthy(self, heartbeat_timeout: int = 300) -> bool:
        """Check if the node is healthy based on heartbeat"""
        return (datetime.now() - self.last_heartbeat).total_seconds() < heartbeat_timeout


@dataclass
class NetworkMessage:
    """Message for network communication between AOS nodes"""
    message_id: str
    message_type: NetworkMessageType
    from_node_id: str
    to_node_id: str  # Can be "*" for broadcast
    subject: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    signature: Optional[str] = None

    # Routing and delivery
    route: List[str] = field(default_factory=list)
    requires_response: bool = False
    priority: str = "medium"
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class NetworkNegotiation:
    """Represents an ongoing negotiation between nodes"""
    negotiation_id: str
    initiator_node_id: str
    target_node_id: str
    negotiation_type: str
    status: str  # "initiated", "in_progress", "agreed", "rejected", "expired"
    proposal: Dict[str, Any]
    counter_proposals: List[Dict[str, Any]] = field(default_factory=list)
    agreement: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class NetworkProtocol:
    """
    Network Protocol for AOS Agent Communication

    Handles distributed agent communication, discovery, negotiation,
    and coordination across the AOS network.
    """

    def __init__(self, local_node: NetworkNode, message_bus: MessageBus = None):
        self.local_node = local_node
        self.message_bus = message_bus or MessageBus()
        self.logger = logging.getLogger(__name__)

        # Network state
        self.connected_nodes: Dict[str, NetworkNode] = {}
        self.message_queue: List[NetworkMessage] = []
        self.pending_negotiations: Dict[str, NetworkNegotiation] = {}
        self.active_connections: Dict[str, Any] = {}

        # Configuration
        self.heartbeat_interval = 60  # seconds
        self.message_timeout = 300  # seconds
        self.max_message_queue_size = 1000

        self.logger.info(f"Network protocol initialized for node {local_node.identity.node_id}")

    async def initialize(self):
        """Initialize the network protocol"""
        try:
            # Initialize message bus if needed
            if not getattr(self.message_bus, '_initialized', False):
                await self.message_bus.initialize()

            # Set up message handlers
            await self._setup_message_handlers()

            # Start background tasks
            await self._start_background_tasks()

            await audit_log(
                AuditEventType.COMPONENT_STARTED,
                "Network protocol initialized",
                component="network_protocol",
                severity=AuditSeverity.INFO
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize network protocol: {e}")
            raise

    async def join_network(self, network_endpoint: str = None) -> bool:
        """Join the AOS network"""
        try:
            self.logger.info(f"Joining network as {self.local_node.identity.node_name}")

            # Send discovery message to announce presence
            discovery_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                message_type=NetworkMessageType.DISCOVERY,
                from_node_id=self.local_node.identity.node_id,
                to_node_id="*",  # Broadcast
                subject="Network Discovery",
                content={
                    "action": "join",
                    "identity": {
                        "name": self.local_node.identity.node_name,
                        "type": self.local_node.identity.node_type,
                        "version": self.local_node.identity.version,
                        "capabilities": list(self.local_node.identity.capabilities),
                        "agents": list(self.local_node.active_agents)
                    },
                    "endpoint": self.local_node.endpoint_url
                }
            )

            await self._send_message(discovery_message)
            self.local_node.status = NetworkNodeStatus.ACTIVE

            await audit_log(
                AuditEventType.SYSTEM_STARTUP,
                f"Node joined network: {self.local_node.identity.node_name}",
                component="network_protocol",
                severity=AuditSeverity.INFO,
                metadata={"node_id": self.local_node.identity.node_id}
            )

            self.logger.info("Successfully joined network")
            return True

        except Exception as e:
            self.logger.error(f"Failed to join network: {e}")
            return False

    async def discover_nodes(self, criteria: Dict[str, Any] = None) -> List[NetworkNode]:
        """Discover other nodes in the network"""
        try:
            discovery_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                message_type=NetworkMessageType.DISCOVERY,
                from_node_id=self.local_node.identity.node_id,
                to_node_id="*",  # Broadcast
                subject="Node Discovery",
                content={
                    "action": "discover",
                    "criteria": criteria or {}
                },
                requires_response=True,
                expires_at=datetime.now() + timedelta(seconds=30)
            )

            await self._send_message(discovery_message)

            # Wait for responses
            await asyncio.sleep(5)

            discovered_nodes = [
                node for node in self.connected_nodes.values()
                if self._matches_criteria(node, criteria or {})
            ]

            self.logger.info(f"Discovered {len(discovered_nodes)} nodes")
            return discovered_nodes

        except Exception as e:
            self.logger.error(f"Failed to discover nodes: {e}")
            return []

    async def initiate_negotiation(self, target_node_id: str, negotiation_type: str,
                                 proposal: Dict[str, Any]) -> str:
        """Initiate negotiation with another node"""
        try:
            negotiation_id = str(uuid.uuid4())

            # Create negotiation record
            negotiation = NetworkNegotiation(
                negotiation_id=negotiation_id,
                initiator_node_id=self.local_node.identity.node_id,
                target_node_id=target_node_id,
                negotiation_type=negotiation_type,
                status="initiated",
                proposal=proposal,
                expires_at=datetime.now() + timedelta(hours=1)
            )

            self.pending_negotiations[negotiation_id] = negotiation

            # Send negotiation message
            negotiation_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                message_type=NetworkMessageType.NEGOTIATION,
                from_node_id=self.local_node.identity.node_id,
                to_node_id=target_node_id,
                subject=f"Negotiation: {negotiation_type}",
                content={
                    "negotiation_id": negotiation_id,
                    "type": negotiation_type,
                    "proposal": proposal,
                    "from_node": self.local_node.identity.node_name
                },
                requires_response=True,
                expires_at=negotiation.expires_at
            )

            await self._send_message(negotiation_message)

            await audit_log(
                AuditEventType.MESSAGE_SENT,
                f"Negotiation initiated: {negotiation_type}",
                component="network_protocol",
                severity=AuditSeverity.INFO,
                metadata={
                    "negotiation_id": negotiation_id,
                    "target_node": target_node_id,
                    "type": negotiation_type
                }
            )

            return negotiation_id

        except Exception as e:
            self.logger.error(f"Failed to initiate negotiation: {e}")
            raise

    async def send_heartbeat(self):
        """Send heartbeat to maintain network presence"""
        try:
            heartbeat_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                message_type=NetworkMessageType.HEARTBEAT,
                from_node_id=self.local_node.identity.node_id,
                to_node_id="*",  # Broadcast
                subject="Node Heartbeat",
                content={
                    "status": self.local_node.status.value,
                    "active_agents": list(self.local_node.active_agents),
                    "resource_usage": self.local_node.resource_usage,
                    "timestamp": datetime.now().isoformat()
                }
            )

            await self._send_message(heartbeat_message)
            self.local_node.last_heartbeat = datetime.now()

        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")

    async def _send_message(self, message: NetworkMessage):
        """Send a network message"""
        try:
            # Add to message queue if needed
            if len(self.message_queue) >= self.max_message_queue_size:
                # Remove oldest message
                self.message_queue.pop(0)

            self.message_queue.append(message)

            # Convert to internal message format and send
            internal_message = Message(
                id=message.message_id,
                type=f"network.{message.message_type.value}",
                content=message.content,
                sender=message.from_node_id,
                timestamp=message.timestamp,
                metadata={
                    "network_message": True,
                    "to_node_id": message.to_node_id,
                    "subject": message.subject,
                    "requires_response": message.requires_response,
                    "priority": message.priority
                }
            )

            if message.to_node_id == "*":
                await self.message_bus.broadcast(internal_message)
            else:
                await self.message_bus.send(internal_message, message.to_node_id)

        except Exception as e:
            self.logger.error(f"Failed to send message {message.message_id}: {e}")
            raise

    async def _setup_message_handlers(self):
        """Set up handlers for different message types"""
        handlers = {
            NetworkMessageType.DISCOVERY: self._handle_discovery,
            NetworkMessageType.NEGOTIATION: self._handle_negotiation,
            NetworkMessageType.HEARTBEAT: self._handle_heartbeat,
            NetworkMessageType.STATUS_UPDATE: self._handle_status_update,
            NetworkMessageType.CAPABILITY_ANNOUNCEMENT: self._handle_capability_announcement
        }

        for message_type, handler in handlers.items():
            await self.message_bus.subscribe(f"network.{message_type.value}", handler)

    async def _handle_discovery(self, message: Message):
        """Handle discovery messages"""
        try:
            content = message.content

            if content.get("action") == "join":
                # Another node is joining
                await self._handle_node_join(message)
            elif content.get("action") == "discover":
                # Respond to discovery request
                await self._respond_to_discovery(message)

        except Exception as e:
            self.logger.error(f"Error handling discovery message: {e}")

    async def _handle_node_join(self, message: Message):
        """Handle a node joining the network"""
        try:
            identity_data = message.content.get("identity", {})
            endpoint = message.content.get("endpoint")

            # Create network node
            node = NetworkNode(
                identity=NetworkIdentity(
                    node_id=message.sender,
                    node_name=identity_data.get("name", "Unknown"),
                    node_type=identity_data.get("type", "unknown"),
                    version=identity_data.get("version", "unknown"),
                    capabilities=set(identity_data.get("capabilities", []))
                ),
                endpoint_url=endpoint or "",
                status=NetworkNodeStatus.ACTIVE,
                active_agents=set(identity_data.get("agents", []))
            )

            self.connected_nodes[message.sender] = node

            self.logger.info(f"Node joined network: {node.identity.node_name}")

        except Exception as e:
            self.logger.error(f"Error handling node join: {e}")

    async def _respond_to_discovery(self, message: Message):
        """Respond to a discovery request"""
        try:
            response_message = NetworkMessage(
                message_id=str(uuid.uuid4()),
                message_type=NetworkMessageType.DISCOVERY,
                from_node_id=self.local_node.identity.node_id,
                to_node_id=message.sender,
                subject="Discovery Response",
                content={
                    "action": "response",
                    "identity": {
                        "name": self.local_node.identity.node_name,
                        "type": self.local_node.identity.node_type,
                        "version": self.local_node.identity.version,
                        "capabilities": list(self.local_node.identity.capabilities),
                        "agents": list(self.local_node.active_agents)
                    },
                    "endpoint": self.local_node.endpoint_url,
                    "status": self.local_node.status.value
                }
            )

            await self._send_message(response_message)

        except Exception as e:
            self.logger.error(f"Error responding to discovery: {e}")

    async def _handle_negotiation(self, message: Message):
        """Handle negotiation messages"""
        # Implementation for negotiation handling
        pass

    async def _handle_heartbeat(self, message: Message):
        """Handle heartbeat messages"""
        try:
            sender_id = message.sender
            if sender_id in self.connected_nodes:
                node = self.connected_nodes[sender_id]
                node.last_heartbeat = datetime.now()

                # Update node status
                content = message.content
                if "status" in content:
                    try:
                        node.status = NetworkNodeStatus(content["status"])
                    except ValueError:
                        pass

                # Update resource usage
                if "resource_usage" in content:
                    node.resource_usage = content["resource_usage"]

        except Exception as e:
            self.logger.error(f"Error handling heartbeat from {message.sender}: {e}")

    async def _handle_status_update(self, message: Message):
        """Handle status update messages"""
        pass

    async def _handle_capability_announcement(self, message: Message):
        """Handle capability announcement messages"""
        pass

    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Start heartbeat task
        asyncio.create_task(self._heartbeat_task())

        # Start node health monitoring
        asyncio.create_task(self._monitor_node_health())

        # Start message cleanup
        asyncio.create_task(self._cleanup_expired_messages())

    async def _heartbeat_task(self):
        """Background task to send heartbeats"""
        while True:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _monitor_node_health(self):
        """Monitor health of connected nodes"""
        while True:
            try:
                # Check for unhealthy nodes
                unhealthy_nodes = [
                    node_id for node_id, node in self.connected_nodes.items()
                    if not node.is_healthy()
                ]

                # Remove unhealthy nodes
                for node_id in unhealthy_nodes:
                    self.logger.warning(f"Removing unhealthy node: {node_id}")
                    del self.connected_nodes[node_id]

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error monitoring node health: {e}")
                await asyncio.sleep(60)

    async def _cleanup_expired_messages(self):
        """Clean up expired messages"""
        while True:
            try:
                now = datetime.now()
                self.message_queue = [
                    msg for msg in self.message_queue
                    if msg.expires_at is None or msg.expires_at > now
                ]

                # Clean up expired negotiations
                expired_negotiations = [
                    neg_id for neg_id, neg in self.pending_negotiations.items()
                    if neg.expires_at and neg.expires_at < now
                ]

                for neg_id in expired_negotiations:
                    del self.pending_negotiations[neg_id]

                await asyncio.sleep(300)  # Clean up every 5 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up messages: {e}")
                await asyncio.sleep(300)

    def _matches_criteria(self, node: NetworkNode, criteria: Dict[str, Any]) -> bool:
        """Check if a node matches discovery criteria"""
        # Implement criteria matching logic
        return True

    async def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            "local_node": {
                "id": self.local_node.identity.node_id,
                "name": self.local_node.identity.node_name,
                "status": self.local_node.status.value,
                "active_agents": list(self.local_node.active_agents)
            },
            "connected_nodes": len(self.connected_nodes),
            "active_negotiations": len(self.pending_negotiations),
            "message_queue_size": len(self.message_queue),
            "last_heartbeat": self.local_node.last_heartbeat.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the network protocol"""
        return {
            "status": "healthy" if self.local_node.status == NetworkNodeStatus.ACTIVE else "degraded",
            "connected_nodes": len(self.connected_nodes),
            "message_bus_healthy": await self.message_bus.health_check(),
            "last_heartbeat": self.local_node.last_heartbeat.isoformat()
        }
