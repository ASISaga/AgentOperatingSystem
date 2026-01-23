"""
AOS Agent Module

Base agent classes and agent-related functionality.

Includes PurposeDrivenAgent - the fundamental building block of AOS.
PurposeDrivenAgent is pure Microsoft Agent Framework code. The Foundry Agent 
Service runtime with Llama 3.3 70B and LoRA adapters is provided by the AOS 
infrastructure (AgentRuntimeProvider), not as an agent extension.
"""

# v2.0.0 - Canonical implementations
from .base_agent import BaseAgent
from .leadership_agent import LeadershipAgent
from .perpetual import PerpetualAgent
from .purpose_driven import PurposeDrivenAgent
# Note: PurposeDrivenAgentFoundry removed - Foundry runtime is now infrastructure-level
from .multi_agent import (
    MultiAgentSystem, 
    BusinessAnalystAgent, 
    SoftwareEngineerAgent, 
    ProductOwnerAgent,
    ApprovalTerminationStrategy
)
from .manager import UnifiedAgentManager

__all__ = [
    "BaseAgent",
    "LeadershipAgent",
    "PerpetualAgent",
    "PurposeDrivenAgent",
    # "PurposeDrivenAgentFoundry",  # Removed - use AgentRuntimeProvider instead
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    "ApprovalTerminationStrategy",
    "UnifiedAgentManager"
]