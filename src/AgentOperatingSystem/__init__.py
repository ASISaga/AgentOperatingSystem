"""
Agent Operating System (AOS)

The foundational operating system for all agent-based applications.
Provides core infrastructure including messaging, orchestration, storage, and monitoring.
"""

from .agent_operating_system import AgentOperatingSystem

# Core agent classes (consolidated)
from .agents import (
    BaseAgent,
    CMOAgent,
    LeadershipAgent,
    PerpetualAgent,
    PurposeDrivenAgent,
)
from .auth.manager import AuthManager
from .config import AOSConfig, default_config
from .environment.manager import EnvironmentManager, env_manager

# Self-learning agents (moved from agents to learning module)
from .learning import (
    DomainExpert,
    InteractionLearner,
    KnowledgeManager,
    LearningPipeline,
    RAGEngine,
    SelfLearningAgent,
    SelfLearningMixin,
    SelfLearningStatefulAgent,
)
from .mcp import MCPClient, MCPClientManager, MCPServerConfig, MCPServerType
from .messaging.bus import MessageBus
from .messaging.router import MessageRouter
from .messaging.servicebus_manager import ServiceBusManager
from .messaging.types import Message, MessagePriority, MessageType
from .ml.pipeline import MLPipelineManager
from .monitoring.audit_trail_generic import AuditEvent as AuditEventNew
from .monitoring.audit_trail_generic import AuditSeverity
from .monitoring.audit_trail_generic import AuditTrailManager as AuditTrailManagerNew
from .monitoring.monitor import SystemMonitor
from .observability.structured import StructuredLogger as StructuredLoggerNew
from .observability.structured import (
    correlation_scope,
    get_health_check,
    get_metrics_collector,
)

# Agent orchestration (moved from agents module)
from .orchestration import (
    AgentFrameworkSystem,
    BusinessAnalystAgent,
    MultiAgentSystem,
    ProductOwnerAgent,
    SoftwareEngineerAgent,
    UnifiedAgentManager,
)
from .orchestration.engine import DecisionEngine
from .orchestration.orchestrator import OrchestrationEngine
from .orchestration.workflow import Workflow
from .orchestration.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowOrchestratorFactory,
)
from .orchestration.workflow_step import WorkflowStep

# Infrastructure components from migration
from .reliability.patterns import (
    CircuitBreaker,
    IdempotencyHandler,
    RetryPolicy,
    with_circuit_breaker,
    with_retry,
)
from .services.service_interfaces import (
    IAuthService,
    IMessagingService,
    IStorageService,
    IWorkflowService,
)
from .shared.models import Envelope, MessagesQuery, UiAction
from .storage.manager import StorageManager

__version__ = "1.1.0"
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
