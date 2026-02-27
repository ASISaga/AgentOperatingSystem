"""Agent configuration schema for RealmOfAgents.

Pydantic models defining the agent registry schema used to configure
agents for dynamic deployment.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentRegistryEntry(BaseModel):
    """Schema for a single agent in the registry."""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(
        ...,
        description="Agent class name: PurposeDrivenAgent, LeadershipAgent, CMOAgent, etc.",
    )
    purpose: str = Field(..., description="The agent's long-term purpose")
    adapter_name: str = Field(
        ..., description="LoRA adapter providing domain expertise"
    )
    capabilities: List[str] = Field(
        default_factory=list, description="Agent capabilities"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Agent-specific configuration"
    )
    enabled: bool = Field(default=True, description="Whether the agent is active")


class AgentRegistry(BaseModel):
    """Schema for the full agent registry configuration."""

    agents: List[AgentRegistryEntry] = Field(
        default_factory=list, description="List of agent configurations"
    )

    def get_enabled_agents(self) -> List[AgentRegistryEntry]:
        """Return only agents with enabled=True."""
        return [a for a in self.agents if a.enabled]

    def get_agent(self, agent_id: str) -> Optional[AgentRegistryEntry]:
        """Look up an agent by ID."""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def filter_by_type(self, agent_type: str) -> List[AgentRegistryEntry]:
        """Return agents matching the given type."""
        return [a for a in self.agents if a.agent_type == agent_type and a.enabled]
