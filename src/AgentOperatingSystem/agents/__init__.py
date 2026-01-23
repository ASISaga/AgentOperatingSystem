"""
AOS Agent Module

Core agent classes for the Agent Operating System.

Contains only the fundamental agent classes:
- PurposeDrivenAgent: The fundamental building block of AOS (includes BaseAgent, 
  PerpetualAgent, and LeadershipAgent functionality)
- CMOAgent: Chief Marketing Officer agent extending PurposeDrivenAgent

All orchestration-related classes have been moved to the orchestration module.
"""

# v2.0.0 - Consolidated agent classes
from .purpose_driven import (
    BaseAgent,
    PerpetualAgent,
    PurposeDrivenAgent,
    LeadershipAgent
)
from .cmo_agent import CMOAgent

__all__ = [
    "BaseAgent",
    "PerpetualAgent", 
    "PurposeDrivenAgent",
    "LeadershipAgent",
    "CMOAgent",
]