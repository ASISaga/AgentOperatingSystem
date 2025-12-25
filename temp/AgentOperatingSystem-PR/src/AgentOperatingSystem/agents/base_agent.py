"""
Base Agent - Generic agent with lifecycle, messaging, and state management.
Foundation for all specialized agents.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import uuid

class BaseAgent(ABC):
    """
    Generic base agent providing:
    - Unique identity and metadata
    - Lifecycle management (initialize, start, stop, health)
    - Message handling and routing
    - State persistence
    - Event publishing
    - Health monitoring
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        config: Dict[str, Any] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role/type
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.config = config or {}
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        self.state = "initialized"
        self.logger = logging.getLogger(f"aos.agent.{agent_id}")
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize agent resources and connections."""
        pass
    
    @abstractmethod
    async def start(self) -> bool:
        """Start agent operations."""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop agent operations gracefully."""
        pass
    
    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message.
        
        Args:
            message: Message payload with type, data, metadata
            
        Returns:
            Response dictionary
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Health status with state, metrics, issues
        """
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "healthy": self.state in ["initialized", "running"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "metadata": self.metadata
        }
