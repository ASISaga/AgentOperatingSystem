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
    "ApprovalTerminationStrategy"
]