"""Agents compatibility shim — re-exports from published agent packages."""
from purpose_driven_agent import PurposeDrivenAgent, GenericPurposeDrivenAgent
from leadership_agent import LeadershipAgent
from cmo_agent import CMOAgent

# Backward-compatibility aliases
BaseAgent = PurposeDrivenAgent
PerpetualAgent = PurposeDrivenAgent
