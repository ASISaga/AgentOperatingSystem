"""
AOS Core - Autonomous Orchestration

A perpetual, fully autonomous orchestration of agents comprising Investor, Founder, 
and C-Suite members. Each agent possesses legendary domain knowledge through 
LoRA adapters from FineTunedLLM AML, connected to AOS via Azure Service Bus.

The orchestration operates continuously, making strategic decisions, monitoring 
performance, and executing business operations through integration with 
conventional business systems via MCP servers.

Orchestration and decision-making components.

Integration of useful orchestration patterns from SelfLearningAgent
into the AOS orchestration system. Provides advanced multi-agent coordination,
unified orchestration, Azure integration, and comprehensive agent registry.
"""

from .state import State
from .role import Role
from .member import Member
from .decision import Decision
from .orchestration import Orchestration, create_autonomous_boardroom
from .engine import DecisionEngine
from .orchestrator import OrchestrationEngine
from .agent_registry import AgentRegistry
from .multi_agent_coordinator import MultiAgentCoordinator, CoordinationMode
from .unified_orchestrator import UnifiedOrchestrator, ExecutionMode, RequestType
# from .azure_integration import AzureIntegration, AzureServiceType  # Temporarily disabled
from .mcp_integration import MCPClientManager
from .model_orchestration import ModelOrchestrator, ModelType
from .workflow_step import WorkflowStep
from .workflow_orchestrator import WorkflowOrchestrator, WorkflowOrchestratorFactory

__all__ = [
    "State",
    "Role",
    "Member",
    "Decision",
    "Orchestration",
    "create_autonomous_boardroom",
    "DecisionEngine",
    "OrchestrationEngine",
    "AgentRegistry",
    "MultiAgentCoordinator", 
    "CoordinationMode",
    "UnifiedOrchestrator",
    "ExecutionMode",
    "RequestType", 
    # "AzureIntegration",  # Temporarily disabled  
    # "AzureServiceType",  # Temporarily disabled
    "MCPClientManager",
    "ModelOrchestrator",
    "ModelType",
    "WorkflowStep",
    "WorkflowOrchestrator",
    "WorkflowOrchestratorFactory"
]