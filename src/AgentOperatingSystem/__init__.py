"""
Agent Operating System (AOS)

The foundational operating system for all agent-based applications.
Provides core infrastructure including messaging, orchestration, storage, and monitoring.
"""

from .agent_operating_system import AgentOperatingSystem
from .config import AOSConfig, default_config

# Core agent classes (consolidated)
from .agents import (
    BaseAgent,
    PerpetualAgent,
    PurposeDrivenAgent,
    LeadershipAgent,
    CMOAgent
)

# Agent orchestration (moved from agents module)
from .orchestration import (
    UnifiedAgentManager,
    MultiAgentSystem,
    BusinessAnalystAgent,
    SoftwareEngineerAgent,
    ProductOwnerAgent,
    AgentFrameworkSystem
)

# Self-learning agents (moved from agents to learning module)
from .learning import SelfLearningAgent, SelfLearningStatefulAgent
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
from .learning import KnowledgeManager, RAGEngine, InteractionLearner, SelfLearningMixin, DomainExpert, LearningPipeline

# Infrastructure components from migration
from .reliability.patterns import CircuitBreaker, RetryPolicy, IdempotencyHandler, with_retry, with_circuit_breaker
from .observability.structured import StructuredLogger as StructuredLoggerNew, correlation_scope, get_metrics_collector, get_health_check
from .services.service_interfaces import IStorageService, IMessagingService, IWorkflowService, IAuthService
from .monitoring.audit_trail_generic import AuditTrailManager as AuditTrailManagerNew, AuditEvent as AuditEventNew, AuditSeverity

__version__ = "3.0.0"
__author__ = "ASISaga"

# Main exports
__all__ = [
    # Core system
    "AgentOperatingSystem",
    "AOSConfig",
    "default_config",

    # Core agent classes (consolidated in agents module)
    "BaseAgent",
    "PerpetualAgent",
    "PurposeDrivenAgent",
    "LeadershipAgent",
    "CMOAgent",

    # Agent orchestration (moved to orchestration module)
    "UnifiedAgentManager",
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent",
    "ProductOwnerAgent",
    "AgentFrameworkSystem",

    # Self-learning agents (in learning module)
    "SelfLearningAgent",
    "SelfLearningStatefulAgent",

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

    # Infrastructure components (from migration)
    "CircuitBreaker",
    "RetryPolicy",
    "IdempotencyHandler",
    "with_retry",
    "with_circuit_breaker",
    "StructuredLoggerNew",
    "correlation_scope",
    "get_metrics_collector",
    "get_health_check",
    "IStorageService",
    "IMessagingService",
    "IWorkflowService",
    "IAuthService",
    "AuditTrailManagerNew",
    "AuditEventNew",
    "AuditSeverity",
]
