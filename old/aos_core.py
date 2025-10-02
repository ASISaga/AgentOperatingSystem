"""
Agent Operating System (AOS) - Core Infrastructure

This is the foundational operating system for all leadership agents.
It provides generic, reusable infrastructure including:
- Agent lifecycle management
- Message routing and communication
- Decision engine integration
- Service orchestration
- Resource management
- Monitoring and telemetry
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from abc import ABC, abstractmethod

from .messaging import MessageBus, MessageRouter
from .decision_engine import DecisionEngine
from .orchestration import OrchestrationEngine
from .storage import StorageManager
from .monitoring import SystemMonitor
from .config import AOSConfig

logger = logging.getLogger(__name__)


class AgentOperatingSystem:
    """
    Core Agent Operating System providing foundational infrastructure for all agents.
    
    This class serves as the kernel of the agent ecosystem, providing:
    - Agent registration and lifecycle management
    - Inter-agent communication via message bus
    - Centralized decision engine
    - Resource orchestration and scheduling
    - System monitoring and telemetry
    - Storage abstraction
    """
    
    def __init__(self, config: AOSConfig = None):
        self.config = config or AOSConfig()
        self.agents = {}  # Registry of active agents
        self.services = {}  # Registry of system services
        self.logger = logging.getLogger("AOS.Kernel")
        
        # Initialize core components
        self._initialize_core_components()
        
        # System state
        self.is_running = False
        self.startup_time = None
        
    def _initialize_core_components(self):
        """Initialize core AOS components"""
        try:
            # Message bus for inter-agent communication
            self.message_bus = MessageBus(self.config.message_bus_config)
            
            # Message router for intelligent message routing
            self.message_router = MessageRouter(self.message_bus)
            
            # Decision engine for intelligent decision making
            self.decision_engine = DecisionEngine(self.config.decision_config)
            
            # Orchestration engine for workflow management
            self.orchestration_engine = OrchestrationEngine(self.config.orchestration_config)
            
            # Storage manager for persistence
            self.storage_manager = StorageManager(self.config.storage_config)
            
            # System monitor for telemetry
            self.system_monitor = SystemMonitor(self.config.monitoring_config)
            
            self.logger.info("AOS core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AOS core components: {e}")
            raise
    
    async def start(self):
        """Start the Agent Operating System"""
        if self.is_running:
            self.logger.warning("AOS is already running")
            return
        
        try:
            self.startup_time = datetime.utcnow()
            
            # Start core services
            await self.message_bus.start()
            await self.orchestration_engine.start()
            await self.system_monitor.start()
            
            # Register system message handlers
            await self._register_system_handlers()
            
            self.is_running = True
            self.logger.info(f"AOS started successfully at {self.startup_time}")
            
        except Exception as e:
            self.logger.error(f"Failed to start AOS: {e}")
            raise
    
    async def stop(self):
        """Stop the Agent Operating System"""
        if not self.is_running:
            return
        
        try:
            # Stop all registered agents
            for agent_id in list(self.agents.keys()):
                await self.unregister_agent(agent_id)
            
            # Stop core services
            await self.system_monitor.stop()
            await self.orchestration_engine.stop()
            await self.message_bus.stop()
            
            self.is_running = False
            self.logger.info("AOS stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping AOS: {e}")
    
    async def register_agent(self, agent: 'BaseAgent') -> bool:
        """
        Register an agent with the operating system.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            bool: Success status
        """
        try:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent {agent.agent_id} already registered")
                return False
            
            # Register agent
            self.agents[agent.agent_id] = agent
            
            # Initialize agent with AOS context
            await agent._set_aos_context(self)
            
            # Start agent if AOS is running
            if self.is_running:
                await agent.start()
            
            # Register agent with message router
            await self.message_router.register_agent(agent.agent_id, agent.get_message_handlers())
            
            self.logger.info(f"Agent {agent.agent_id} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the operating system.
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            bool: Success status
        """
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found")
                return False
            
            agent = self.agents[agent_id]
            
            # Stop agent
            await agent.stop()
            
            # Unregister from message router
            await self.message_router.unregister_agent(agent_id)
            
            # Remove from registry
            del self.agents[agent_id]
            
            self.logger.info(f"Agent {agent_id} unregistered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> bool:
        """Send a message between agents via the message bus"""
        return await self.message_bus.send_message(from_agent, to_agent, message)
    
    async def broadcast_message(self, from_agent: str, message: Dict[str, Any], agent_filter: str = None) -> bool:
        """Broadcast a message to multiple agents"""
        return await self.message_bus.broadcast_message(from_agent, message, agent_filter)
    
    async def make_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision using the centralized decision engine"""
        return await self.decision_engine.decide(decision_context)
    
    async def orchestrate_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Start a workflow orchestration"""
        return await self.orchestration_engine.start_workflow(workflow_config)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_status = {
            agent_id: await agent.get_status() 
            for agent_id, agent in self.agents.items()
        }
        
        return {
            "aos": {
                "is_running": self.is_running,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds() if self.startup_time else 0,
            },
            "agents": agent_status,
            "message_bus": await self.message_bus.get_status(),
            "orchestration": await self.orchestration_engine.get_status(),
            "system_metrics": await self.system_monitor.get_metrics()
        }
    
    async def _register_system_handlers(self):
        """Register system-level message handlers"""
        handlers = {
            "system.ping": self._handle_ping,
            "system.status": self._handle_status,
            "system.shutdown": self._handle_shutdown
        }
        
        for message_type, handler in handlers.items():
            await self.message_router.register_handler(message_type, handler)
    
    async def _handle_ping(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system ping messages"""
        return {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "system": "AOS"
        }
    
    async def _handle_status(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system status requests"""
        return await self.get_system_status()
    
    async def _handle_shutdown(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system shutdown requests"""
        await self.stop()
        return {"status": "shutting_down"}


# Base agent class that all agents should inherit from
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
    
    async def _set_aos_context(self, aos: AgentOperatingSystem):
        """Set AOS context (called by AOS during registration)"""
        self.aos_context = aos
    
    @abstractmethod
    async def start(self):
        """Start the agent (called by AOS)"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the agent (called by AOS)"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message from another agent"""
        pass
    
    @abstractmethod
    def get_message_handlers(self) -> Dict[str, callable]:
        """Return dict of message types this agent can handle"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "is_running": self.is_running,
            "type": self.__class__.__name__
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


# Export main classes
__all__ = ['AgentOperatingSystem', 'BaseAgent']