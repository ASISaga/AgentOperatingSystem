"""
AOS Agent Module

Core agent classes for the Agent Operating System.

Contains the fundamental agent classes:
- PurposeDrivenAgent: The fundamental building block of AOS — directly instantiable,
  perpetual, purpose-driven, and deployable to Azure.
- LeadershipAgent: Leadership agent extending PurposeDrivenAgent
- CMOAgent: Chief Marketing Officer agent extending LeadershipAgent

GenericPurposeDrivenAgent, BaseAgent, and PerpetualAgent are backward-compatibility
aliases for PurposeDrivenAgent.
"""

# v3.0.0 - Refactored agent classes
from .purpose_driven import PurposeDrivenAgent, GenericPurposeDrivenAgent
from .leadership_agent import LeadershipAgent
from .cmo_agent import CMOAgent

# Backward compatibility aliases
BaseAgent = PurposeDrivenAgent
PerpetualAgent = PurposeDrivenAgent

__all__ = [
    "PurposeDrivenAgent",
    "GenericPurposeDrivenAgent",  # Backward compatibility alias
    "LeadershipAgent",
    "CMOAgent",
    "BaseAgent",      # Backward compatibility
    "PerpetualAgent", # Backward compatibility
]
