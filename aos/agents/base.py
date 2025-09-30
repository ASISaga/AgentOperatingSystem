"""
AOS Base Agent Classes

Base classes for all agents in the Agent Operating System.
Provides standard agent lifecycle, messaging, and integration with AOS.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime


class BaseAgent(ABC):
    """
    Base class for all agents in the Agent Operating System.
    
    Provides standard agent lifecycle, messaging, and integration with AOS.
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.aos_context = None
        self.is_running = False
        self.logger = logging.getLogger(f"AOS.Agent.{agent_id}")
        self.created_at = datetime.utcnow()
    
    async def _set_aos_context(self, aos):
        """Set AOS context (called by AOS during registration)"""
        self.aos_context = aos
    
    @abstractmethod
    async def start(self):
        """Start the agent (called by AOS)"""
        self.is_running = True
        self.logger.info(f"Agent {self.agent_id} started")
    
    @abstractmethod
    async def stop(self):
        """Stop the agent (called by AOS)"""
        self.is_running = False
        self.logger.info(f"Agent {self.agent_id} stopped")
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message from another agent"""
        pass
    
    @abstractmethod
    def get_message_handlers(self) -> Dict[str, callable]:
        """Return dict of message types this agent can handle"""
        return {}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "is_running": self.is_running,
            "type": self.__class__.__name__,
            "created_at": self.created_at.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds() if self.is_running else 0
        }
    
    # Convenience methods for interacting with AOS
    async def send_message(self, to_agent: str, message: Dict[str, Any]) -> bool:
        """Send message to another agent via AOS"""
        if self.aos_context:
            return await self.aos_context.send_message(self.agent_id, to_agent, message)
        return False
    
    async def broadcast_message(self, message: Dict[str, Any], agent_filter: str = None) -> bool:
        """Broadcast message via AOS"""
        if self.aos_context:
            return await self.aos_context.broadcast_message(self.agent_id, message, agent_filter)
        return False
    
    async def make_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision via AOS decision engine"""
        if self.aos_context:
            return await self.aos_context.make_decision(decision_context)
        return {}


class Agent(BaseAgent):
    """
    Concrete implementation of BaseAgent with basic functionality.
    
    This can be used as a simple agent or extended for specific functionality.
    """
    
    def __init__(self, agent_id: str, name: str = None, config: Dict[str, Any] = None):
        super().__init__(agent_id, config)
        self.name = name or agent_id
        self.message_handlers = {}
    
    async def start(self):
        """Start the agent"""
        await super().start()
        
    async def stop(self):
        """Stop the agent"""
        await super().stop()
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message from another agent"""
        message_type = message.get('type', 'unknown')
        
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            return await handler(message)
        
        self.logger.warning(f"No handler for message type: {message_type}")
        return {"status": "error", "message": f"Unknown message type: {message_type}"}
    
    def get_message_handlers(self) -> Dict[str, callable]:
        """Return dict of message types this agent can handle"""
        return self.message_handlers
    
    def register_message_handler(self, message_type: str, handler: callable):
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type] = handler
        self.logger.info(f"Registered handler for message type: {message_type}")


class StatefulAgent(Agent):
    """
    Agent with built-in state management capabilities.
    """
    
    def __init__(self, agent_id: str, name: str = None, config: Dict[str, Any] = None):
        super().__init__(agent_id, name, config)
        self.state = {}
        self.state_history = []
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self.state.copy()
    
    def set_state(self, new_state: Dict[str, Any], save_history: bool = True):
        """Set agent state"""
        if save_history:
            self.state_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "state": self.state.copy()
            })
        
        self.state.update(new_state)
        self.logger.debug(f"State updated: {new_state}")
    
    def clear_state(self):
        """Clear agent state"""
        self.state = {}
        self.logger.info("State cleared")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status including state information"""
        status = await super().get_status()
        status.update({
            "state": self.state,
            "state_history_size": len(self.state_history)
        })
        return status