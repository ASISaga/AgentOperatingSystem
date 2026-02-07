"""
Test that PurposeDrivenAgent is properly abstract and cannot be directly instantiated.
"""
from abc import ABC

from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent, GenericPurposeDrivenAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent

import pytest


class TestPurposeDrivenAbstract:
    """Verify PurposeDrivenAgent ABC enforcement."""

    def test_purpose_driven_agent_is_abstract(self):
        assert issubclass(PurposeDrivenAgent, ABC)

    def test_purpose_driven_agent_cannot_be_instantiated(self):
        with pytest.raises(TypeError, match="abstract|instantiate"):
            PurposeDrivenAgent(
                agent_id="test",
                purpose="test purpose",
                adapter_name="test",
            )

    def test_generic_purpose_driven_agent_is_concrete(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test",
            purpose="test purpose",
            adapter_name="test",
        )
        assert agent.agent_id == "test"
        assert agent.purpose == "test purpose"
        assert agent.adapter_name == "test"

    def test_leadership_agent_is_concrete(self):
        assert issubclass(LeadershipAgent, PurposeDrivenAgent)
        agent = LeadershipAgent(
            agent_id="test_leader",
            purpose="Leadership and decision-making",
            adapter_name="leadership",
        )
        assert agent.agent_id == "test_leader"
        assert "Leadership" in agent.purpose
