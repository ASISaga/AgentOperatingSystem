"""
AOS Messaging System

Provides message bus and routing capabilities for inter-agent communication.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid


class MessageType(Enum):
    """Standard message types for AOS"""
    SYSTEM = "system"
    AGENT_TO_AGENT = "agent_to_agent"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


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
            correlation_id=data["correlation_id"],
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            retry_count=data["retry_count"],
            max_retries=data["max_retries"]
        )


class MessageBus:
    """
    Central message bus for AOS agent communication.
    
    Handles message routing, queuing, delivery, and persistence.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AOS.MessageBus")
        
        # Message queues (agent_id -> List[Message])
        self.agent_queues: Dict[str, List[Message]] = {}
        
        # Message handlers (message_type -> List[Callable])
        self.handlers: Dict[str, List[Callable]] = {}
        
        # Active subscriptions (agent_id -> Set[message_types])
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # Message history for auditing
        self.message_history: List[Message] = []
        
        # Processing state
        self.is_running = False
        self.processing_task = None
        
    async def start(self):
        """Start the message bus"""
        if self.is_running:
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_messages())
        self.logger.info("MessageBus started")
    
    async def stop(self):
        """Stop the message bus"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("MessageBus stopped")
    
    async def register_agent(self, agent_id: str):
        """Register an agent with the message bus"""
        if agent_id not in self.agent_queues:
            self.agent_queues[agent_id] = []
            self.subscriptions[agent_id] = set()
            self.logger.info(f"Agent {agent_id} registered with message bus")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from the message bus"""
        if agent_id in self.agent_queues:
            del self.agent_queues[agent_id]
            del self.subscriptions[agent_id]
            self.logger.info(f"Agent {agent_id} unregistered from message bus")
    
    async def subscribe(self, agent_id: str, message_types: List[str]):
        """Subscribe agent to specific message types"""
        if agent_id not in self.subscriptions:
            await self.register_agent(agent_id)
        
        self.subscriptions[agent_id].update(message_types)
        self.logger.debug(f"Agent {agent_id} subscribed to {message_types}")
    
    async def unsubscribe(self, agent_id: str, message_types: List[str] = None):
        """Unsubscribe agent from message types"""
        if agent_id not in self.subscriptions:
            return
        
        if message_types is None:
            # Unsubscribe from all
            self.subscriptions[agent_id].clear()
        else:
            self.subscriptions[agent_id].difference_update(message_types)
        
        self.logger.debug(f"Agent {agent_id} unsubscribed from {message_types}")
    
    async def send_message(self, from_agent: str, to_agent: str, content: Dict[str, Any], 
                          message_type: MessageType = MessageType.AGENT_TO_AGENT,
                          priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Send a direct message to an agent"""
        message = Message.create(
            message_type=message_type,
            from_agent=from_agent,
            content=content,
            to_agent=to_agent,
            priority=priority
        )
        
        await self._enqueue_message(message)
        return message.id
    
    async def broadcast_message(self, from_agent: str, content: Dict[str, Any],
                               agent_filter: str = None,
                               message_type: MessageType = MessageType.BROADCAST,
                               priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Broadcast a message to multiple agents"""
        message = Message.create(
            message_type=message_type,
            from_agent=from_agent,
            content=content,
            to_agent=None,  # Broadcast
            priority=priority
        )
        
        # Add to queues of all interested agents
        target_agents = self._get_broadcast_targets(message, agent_filter)
        for agent_id in target_agents:
            await self._enqueue_message_for_agent(agent_id, message)
        
        return message.id
    
    async def get_messages(self, agent_id: str, max_messages: int = 10) -> List[Message]:
        """Get pending messages for an agent"""
        if agent_id not in self.agent_queues:
            return []
        
        # Get messages sorted by priority and timestamp
        queue = self.agent_queues[agent_id]
        queue.sort(key=lambda m: (-m.priority.value, m.timestamp))
        
        messages = queue[:max_messages]
        self.agent_queues[agent_id] = queue[max_messages:]
        
        return messages
    
    async def get_status(self) -> Dict[str, Any]:
        """Get message bus status"""
        total_queued = sum(len(queue) for queue in self.agent_queues.values())
        
        return {
            "is_running": self.is_running,
            "registered_agents": len(self.agent_queues),
            "total_queued_messages": total_queued,
            "total_handlers": sum(len(handlers) for handlers in self.handlers.values()),
            "message_history_size": len(self.message_history)
        }
    
    async def _enqueue_message(self, message: Message):
        """Enqueue message for delivery"""
        if message.to_agent:
            # Direct message
            await self._enqueue_message_for_agent(message.to_agent, message)
        else:
            # Broadcast - handle in broadcast_message method
            pass
        
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > 1000:  # Limit history size
            self.message_history = self.message_history[-1000:]
    
    async def _enqueue_message_for_agent(self, agent_id: str, message: Message):
        """Enqueue message for specific agent"""
        if agent_id not in self.agent_queues:
            await self.register_agent(agent_id)
        
        # Check if agent is interested in this message type
        if self._agent_interested_in_message(agent_id, message):
            self.agent_queues[agent_id].append(message)
            
            # Limit queue size
            max_size = self.config.max_queue_size
            if len(self.agent_queues[agent_id]) > max_size:
                self.agent_queues[agent_id] = self.agent_queues[agent_id][-max_size:]
    
    def _agent_interested_in_message(self, agent_id: str, message: Message) -> bool:
        """Check if agent is interested in this message"""
        if agent_id not in self.subscriptions:
            return True  # Default to interested if no subscriptions
        
        subscribed_types = self.subscriptions[agent_id]
        if not subscribed_types:
            return True  # Subscribed to all if empty
        
        return message.type.value in subscribed_types
    
    def _get_broadcast_targets(self, message: Message, agent_filter: str = None) -> List[str]:
        """Get list of agents that should receive broadcast message"""
        targets = []
        
        for agent_id in self.agent_queues.keys():
            if agent_id == message.from_agent:
                continue  # Don't send to sender
            
            if agent_filter and agent_filter not in agent_id:
                continue  # Filter by agent ID pattern
            
            if self._agent_interested_in_message(agent_id, message):
                targets.append(agent_id)
        
        return targets
    
    async def _process_messages(self):
        """Background task to process message cleanup"""
        while self.is_running:
            try:
                await self._cleanup_expired_messages()
                await asyncio.sleep(60)  # Cleanup every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in message processing: {e}")
    
    async def _cleanup_expired_messages(self):
        """Remove expired messages from queues"""
        for agent_id, queue in self.agent_queues.items():
            original_size = len(queue)
            queue[:] = [msg for msg in queue if not msg.is_expired()]
            removed = original_size - len(queue)
            if removed > 0:
                self.logger.debug(f"Removed {removed} expired messages for agent {agent_id}")


class MessageRouter:
    """
    Intelligent message router for AOS.
    
    Routes messages based on content, agent capabilities, and routing rules.
    """
    
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.routing_rules: Dict[str, Callable] = {}
        self.agent_handlers: Dict[str, Dict[str, Callable]] = {}
        self.logger = logging.getLogger("AOS.MessageRouter")
    
    async def register_agent(self, agent_id: str, handlers: Dict[str, Callable]):
        """Register agent message handlers"""
        self.agent_handlers[agent_id] = handlers
        
        # Subscribe agent to message types it can handle
        message_types = list(handlers.keys())
        await self.message_bus.subscribe(agent_id, message_types)
        
        self.logger.info(f"Registered handlers for agent {agent_id}: {message_types}")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister agent handlers"""
        if agent_id in self.agent_handlers:
            del self.agent_handlers[agent_id]
        
        await self.message_bus.unregister_agent(agent_id)
        self.logger.info(f"Unregistered agent {agent_id}")
    
    async def register_handler(self, message_type: str, handler: Callable):
        """Register a global message handler"""
        self.routing_rules[message_type] = handler
        self.logger.info(f"Registered global handler for {message_type}")
    
    def add_routing_rule(self, rule_name: str, rule_func: Callable):
        """Add custom routing rule"""
        self.routing_rules[rule_name] = rule_func
    
    async def route_message(self, message: Message) -> bool:
        """Route message to appropriate handlers"""
        try:
            # Check for global handlers first
            if message.type.value in self.routing_rules:
                handler = self.routing_rules[message.type.value]
                await handler(message)
                return True
            
            # Route to specific agent handlers
            if message.to_agent and message.to_agent in self.agent_handlers:
                agent_handlers = self.agent_handlers[message.to_agent]
                if message.type.value in agent_handlers:
                    handler = agent_handlers[message.type.value]
                    await handler(message)
                    return True
            
            # For broadcast messages, route to all interested agents
            if message.type == MessageType.BROADCAST:
                success_count = 0
                for agent_id, handlers in self.agent_handlers.items():
                    if message.type.value in handlers:
                        try:
                            await handlers[message.type.value](message)
                            success_count += 1
                        except Exception as e:
                            self.logger.error(f"Error routing message to {agent_id}: {e}")
                
                return success_count > 0
            
            self.logger.warning(f"No handler found for message {message.id} of type {message.type.value}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error routing message {message.id}: {e}")
            return False