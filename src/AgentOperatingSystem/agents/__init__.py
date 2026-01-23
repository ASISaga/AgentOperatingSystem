"""
AOS Agent Module

Core agent classes for the Agent Operating System.

Contains the fundamental agent classes:
- PurposeDrivenAgent: Abstract base class - the fundamental building block of AOS
- GenericPurposeDrivenAgent: Concrete implementation for general-purpose agents
- LeadershipAgent: Leadership agent extending PurposeDrivenAgent
- CMOAgent: Chief Marketing Officer agent extending LeadershipAgent

All orchestration-related classes have been moved to the orchestration module.
"""

# v3.0.0 - Refactored agent classes
from .purpose_driven import PurposeDrivenAgent, GenericPurposeDrivenAgent
from .leadership_agent import LeadershipAgent
from .cmo_agent import CMOAgent

# Backward compatibility aliases
# BaseAgent and PerpetualAgent point to GenericPurposeDrivenAgent for compatibility
BaseAgent = GenericPurposeDrivenAgent
PerpetualAgent = GenericPurposeDrivenAgent

__all__ = [
    "PurposeDrivenAgent",
    "GenericPurposeDrivenAgent",
    "LeadershipAgent",
    "CMOAgent",
    "BaseAgent",  # Backward compatibility
    "PerpetualAgent",  # Backward compatibility
]