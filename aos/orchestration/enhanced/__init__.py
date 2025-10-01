"""
Enhanced AOS Orchestration Components

Integration of useful orchestration patterns from SelfLearningAgent
into the AOS orchestration system. Provides advanced multi-agent coordination,
unified orchestration, Azure integration, and comprehensive agent registry.
"""

from .agent_registry import AgentRegistry
from .multi_agent_coordinator import MultiAgentCoordinator, CoordinationMode
from .unified_orchestrator import UnifiedOrchestrator, ExecutionMode, RequestType
from .azure_integration import AzureIntegration, AzureServiceType
from .mcp_integration import MCPClientManager
from .model_orchestration import ModelOrchestrator, ModelType

__all__ = [
    "AgentRegistry",
    "MultiAgentCoordinator", 
    "CoordinationMode",
    "UnifiedOrchestrator",
    "ExecutionMode",
    "RequestType", 
    "AzureIntegration",
    "AzureServiceType",
    "MCPClientManager",
    "ModelOrchestrator",
    "ModelType"
]