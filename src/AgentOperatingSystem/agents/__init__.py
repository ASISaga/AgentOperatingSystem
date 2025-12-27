"""
AOS Agent Module

Base agent classes and agent-related functionality.
"""

from .base import BaseAgent, Agent, StatefulAgent
from .leadership import LeadershipAgent
from .perpetual import PerpetualAgent
from .multi_agent import (
    MultiAgentSystem, 
    BusinessAnalystAgent, 
    SoftwareEngineerAgent, 
    ProductOwnerAgent,
    ApprovalTerminationStrategy
)
# New refactored classes
from .base_agent import BaseAgent as BaseAgentNew
from .leadership_agent import LeadershipAgent as LeadershipAgentNew
from .manager import UnifiedAgentManager

__all__ = [
    "BaseAgent",
    "Agent",
    "StatefulAgent", 
    "LeadershipAgent",
    "PerpetualAgent",
    "MultiAgentSystem",
    "BusinessAnalystAgent",
    "SoftwareEngineerAgent", 
    "ProductOwnerAgent",
    "ApprovalTerminationStrategy",
    # New refactored classes
    "BaseAgentNew",
    "LeadershipAgentNew",
    "UnifiedAgentManager"
]