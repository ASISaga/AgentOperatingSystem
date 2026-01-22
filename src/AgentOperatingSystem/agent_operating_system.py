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
from typing import Dict, Any, List, Optional, Type, TYPE_CHECKING
from datetime import datetime
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .agents.base_agent import BaseAgent

from .messaging.bus import MessageBus
from .messaging.router import MessageRouter
from .orchestration.engine import DecisionEngine
from .orchestration.orchestrator import OrchestrationEngine, WorkflowStatus
from .storage.manager import StorageManager
from .monitoring.monitor import SystemMonitor
from .ml.pipeline import MLPipelineManager
from .auth.manager import AuthManager
from .environment.manager import EnvironmentManager
from .mcp.client import MCPClientManager
from .learning.knowledge_manager import KnowledgeManager
from .learning.rag_engine import RAGEngine
from .learning.interaction_learner import InteractionLearner
from .learning.learning_pipeline import LearningPipeline
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
            
            # ML pipeline manager
            self.ml_pipeline = MLPipelineManager(self.config.ml_config)
            
            # Authentication manager
            self.auth_manager = AuthManager(self.config.auth_config)
            
            # Environment manager
            self.env_manager = EnvironmentManager()
            
            # MCP client manager
            self.mcp_manager = MCPClientManager()
            
            # Learning system components
            self._initialize_learning_system()
            
            self.logger.info("AOS core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AOS core components: {e}")
            raise
    
    def _initialize_learning_system(self):
        """Initialize the learning system components"""
        try:
            # Knowledge manager for domain knowledge
            self.knowledge_manager = KnowledgeManager(
                storage_manager=self.storage_manager,
                config=self.config.learning_config.knowledge
            )
            
            # RAG engine for vector-based retrieval
            self.rag_engine = RAGEngine(
                config=self.config.learning_config.rag
            )
            
            # Interaction learner for learning from feedback
            self.interaction_learner = InteractionLearner(
                storage_manager=self.storage_manager,
                config=self.config.learning_config.interaction
            )
            
            # Learning pipeline for orchestrating learning processes
            self.learning_pipeline = LearningPipeline(
                knowledge_manager=self.knowledge_manager,
                rag_engine=self.rag_engine,
                interaction_learner=self.interaction_learner,
                config=self.config.learning_config.pipeline
            )
            
            self.logger.info("Learning system components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize learning system: {e}")
            # Don't raise - allow AOS to continue without learning system
    
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
            
            # Start learning system
            await self._start_learning_system()
            
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
            # Stop learning system
            await self._stop_learning_system()
            
            await self.system_monitor.stop()
            await self.orchestration_engine.stop()
            await self.message_bus.stop()
            await self.mcp_manager.disconnect_all()
            
            self.is_running = False
            self.logger.info("AOS stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping AOS: {e}")
    
    async def _start_learning_system(self):
        """Start the learning system components"""
        try:
            if hasattr(self, 'knowledge_manager'):
                await self.knowledge_manager.initialize()
            
            if hasattr(self, 'rag_engine'):
                await self.rag_engine.initialize()
            
            if hasattr(self, 'interaction_learner'):
                await self.interaction_learner.initialize()
            
            if hasattr(self, 'learning_pipeline'):
                await self.learning_pipeline.initialize()
            
            self.logger.info("Learning system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start learning system: {e}")
    
    async def _stop_learning_system(self):
        """Stop the learning system components"""
        try:
            if hasattr(self, 'learning_pipeline'):
                await self.learning_pipeline.cleanup()
            
            if hasattr(self, 'rag_engine'):
                await self.rag_engine.cleanup()
            
            self.logger.info("Learning system stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping learning system: {e}")
    
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
            
            # Initialize learning components for self-learning agents
            if hasattr(agent, '_initialize_learning_components'):
                await agent._initialize_learning_components(self)
            
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
    
    async def train_agent_model(self, agent_role: str, training_params: Dict[str, Any]) -> str:
        """Train an ML model for a specific agent role"""
        return await self.ml_pipeline.train_lora_adapter(agent_role, training_params)
    
    async def get_agent_inference(self, agent_role: str, prompt: str) -> Dict[str, Any]:
        """Get ML inference for a specific agent role"""
        return await self.ml_pipeline.get_agent_inference(agent_role, prompt)
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate a user"""
        return await self.auth_manager.authenticate(credentials)
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate an authentication token"""
        return await self.auth_manager.validate_token(token)
    
    async def add_mcp_server(self, server_name: str, config: Dict[str, Any] = None) -> bool:
        """Add an MCP server connection"""
        return await self.mcp_manager.add_client(server_name, config)
    
    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on an MCP server"""
        return await self.mcp_manager.call_tool(server_name, tool_name, arguments)
    
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
                "version": "1.0.0"
            },
            "agents": agent_status,
            "message_bus": await self.message_bus.get_status(),
            "orchestration": await self.orchestration_engine.get_status(),
            "system_metrics": await self.system_monitor.get_metrics(),
            "ml_pipeline": self.ml_pipeline.get_ml_status(),
            "auth": self.auth_manager.get_auth_status(),
            "mcp": self.mcp_manager.get_status()
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


# Export main classes
__all__ = ['AgentOperatingSystem']