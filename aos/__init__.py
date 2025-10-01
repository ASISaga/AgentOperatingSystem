"""
Agent Operating System (AOS)

The foundational operating system for all agent-based applications.
Provides core infrastructure including messaging, orchestration, storage, and monitoring.
"""

from .core.system import AgentOperatingSystem
from .core.config import AOSConfig, default_config
from .agents.base import BaseAgent, Agent, StatefulAgent
from .agents.leadership import LeadershipAgent
from .agents.self_learning import SelfLearningAgent, SelfLearningStatefulAgent
from .messaging.types import Message, MessageType, MessagePriority
from .messaging.bus import MessageBus
from .messaging.router import MessageRouter
from .orchestration.engine import DecisionEngine
from .orchestration.orchestrator import OrchestrationEngine
from .storage.manager import StorageManager
from .monitoring.monitor import SystemMonitor
from .ml.pipeline import MLPipelineManager
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
    
    # Messaging
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageBus",
    "MessageRouter",
    
    # Orchestration
    "DecisionEngine",
    "OrchestrationEngine",
    
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
    
    # Learning System
    "KnowledgeManager",
    "RAGEngine",
    "InteractionLearner",
    "SelfLearningMixin",
    "DomainExpert",
    "LearningPipeline",
]