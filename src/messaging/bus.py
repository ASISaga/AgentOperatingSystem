"""
AOS Message Bus

Central message bus for AOS agent communication.
Handles message routing, queuing, delivery, and persistence.
"""

import asyncio
import logging
from typing import Dict, Any, List, Set
from ..config.messagebus import MessageBusConfig
from .types import Message, MessageType, MessagePriority


class MessageBus:
    """
    Central message bus for AOS agent communication.
    
    Handles message routing, queuing, delivery, and persistence.
    """
    
    def __init__(self, config: MessageBusConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.MessageBus")
        
        # Message queues (agent_id -> List[Message])
        self.agent_queues: Dict[str, List[Message]] = {}
        
        # Message handlers (message_type -> List[Callable])
        self.handlers: Dict[str, List[callable]] = {}
        
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