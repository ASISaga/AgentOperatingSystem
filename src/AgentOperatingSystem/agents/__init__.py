"""
AOS Agent Module

Base agent classes and agent-related functionality.

Includes PurposeDrivenAgent - the fundamental building block of AOS.
PurposeDrivenAgentFoundry extends it with Microsoft Foundry Agent Service runtime.
"""

# v2.0.0 - Canonical implementations
from .base_agent import BaseAgent
from .leadership_agent import LeadershipAgent
from .cmo_agent import CMOAgent
from .perpetual import PerpetualAgent
from .purpose_driven import PurposeDrivenAgent
from .purpose_driven_foundry import PurposeDrivenAgentFoundry
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
    "CMOAgent",
    "PerpetualAgent",
    "PurposeDrivenAgent",
    "PurposeDrivenAgentFoundry",
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    "ApprovalTerminationStrategy",
    "UnifiedAgentManager"
]