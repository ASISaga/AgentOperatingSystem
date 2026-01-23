"""
AOS Agent Module

Core agent classes for the Agent Operating System.

Contains only the fundamental agent classes:
- PurposeDrivenAgent: The fundamental building block of AOS (standalone, consolidated class)
- LeadershipAgent: Leadership agent extending PurposeDrivenAgent
- CMOAgent: Chief Marketing Officer agent extending LeadershipAgent

All orchestration-related classes have been moved to the orchestration module.
"""

# v3.0.0 - Refactored agent classes
from .purpose_driven import PurposeDrivenAgent
from .leadership_agent import LeadershipAgent
from .cmo_agent import CMOAgent

# Backward compatibility aliases
# BaseAgent and PerpetualAgent have been merged into PurposeDrivenAgent
BaseAgent = PurposeDrivenAgent
PerpetualAgent = PurposeDrivenAgent

__all__ = [
    "PurposeDrivenAgent",
    "LeadershipAgent",
    "CMOAgent",
    "BaseAgent",  # Backward compatibility
    "PerpetualAgent",  # Backward compatibility
]