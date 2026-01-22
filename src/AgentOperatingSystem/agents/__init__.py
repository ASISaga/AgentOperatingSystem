"""
AOS Agent Module

Base agent classes and agent-related functionality.

Includes PurposeDrivenAgent - the fundamental building block of AOS.
"""

# v2.0.0 - Canonical implementations
from .base_agent import BaseAgent
from .leadership_agent import LeadershipAgent
from .perpetual import PerpetualAgent
from .purpose_driven import PurposeDrivenAgent
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
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    "ApprovalTerminationStrategy",
    "UnifiedAgentManager"
]