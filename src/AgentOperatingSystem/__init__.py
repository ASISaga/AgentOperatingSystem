"""
Agent Operating System (AOS)

The foundational operating system for all agent-based applications.
Provides core infrastructure including messaging, orchestration, storage, and monitoring.
"""

from .agent_operating_system import AgentOperatingSystem
from .config import AOSConfig, default_config
from .agents import (
    BaseAgent, Agent, StatefulAgent, LeadershipAgent, PerpetualAgent,
    MultiAgentSystem, BusinessAnalystAgent, SoftwareEngineerAgent, ProductOwnerAgent
)
from .agents.agent_framework_system import AgentFrameworkSystem
from .agents.self_learning import SelfLearningAgent, SelfLearningStatefulAgent
from .messaging.types import Message, MessageType, MessagePriority
from .messaging.bus import MessageBus
from .messaging.router import MessageRouter
from .messaging.servicebus_manager import ServiceBusManager
from .orchestration.engine import DecisionEngine
from .orchestration.orchestrator import OrchestrationEngine
from .orchestration.workflow import Workflow
from .orchestration.workflow_step import WorkflowStep
from .orchestration.workflow_orchestrator import WorkflowOrchestrator, WorkflowOrchestratorFactory
from .storage.manager import StorageManager
from .monitoring.monitor import SystemMonitor
from .ml.pipeline import MLPipelineManager
from .mcp import MCPClient, MCPClientManager, MCPServerType, MCPServerConfig
from .auth.manager import AuthManager
from .environment.manager import EnvironmentManager, env_manager
from .shared.models import Envelope, MessagesQuery, UiAction
from .auth.manager import AuthManager
from .environment.manager import EnvironmentManager, env_manager
from .mcp.client import MCPClient, MCPClientManager
from .learning import KnowledgeManager, RAGEngine, InteractionLearner, SelfLearningMixin, DomainExpert, LearningPipeline

__version__ = "1.0.0"
__author__ = "ASISaga"

# Main exports
__all__ = [
    # Core system
    "AgentOperatingSystem",
    "AOSConfig",
    "default_config",
    
    # Base agent classes
    "BaseAgent",
    "Agent", 
    "StatefulAgent",
    "LeadershipAgent",
    "SelfLearningAgent",
    "SelfLearningStatefulAgent",
    "PerpetualAgent",
    "MultiAgentSystem",
    "AgentFrameworkSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    
    # Messaging
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageBus",
    "MessageRouter",
    "ServiceBusManager",
    
    # Orchestration
    "DecisionEngine",
    "OrchestrationEngine",
    "Workflow",
    "WorkflowStep",
    "WorkflowOrchestrator",
    "WorkflowOrchestratorFactory",
    
    # Storage
    "StorageManager",
    
    # Monitoring
    "SystemMonitor",
    
    # ML Pipeline
    "MLPipelineManager",
    
    # Authentication
    "AuthManager",
    
    # Environment
    "EnvironmentManager",
    "env_manager",
    
    # MCP
    "MCPClient",
    "MCPClientManager",
    "MCPServerType",
    "MCPServerConfig",
    
    # Shared Models
    "Envelope",
    "MessagesQuery",
    "UiAction",
    
    # Learning System
    "KnowledgeManager",
    "RAGEngine",
    "InteractionLearner",
    "SelfLearningMixin",
    "DomainExpert",
    "LearningPipeline",
]
