"""
leadership_agent — Public API.

Exports:
    LeadershipAgent: Perpetual agent with leadership, decision-making,
        and multi-agent orchestration capabilities.
"""

from leadership_agent.agent import LeadershipAgent
from purpose_driven_agent import A2AAgentTool

__all__ = ["LeadershipAgent", "A2AAgentTool"]

__version__ = "1.0.0"
