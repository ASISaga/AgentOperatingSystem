"""
Test that PurposeDrivenAgent is directly instantiable and that GenericPurposeDrivenAgent
is a transparent alias for it.
"""
from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent, GenericPurposeDrivenAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent

import pytest


class TestPurposeDrivenConcrete:
    """Verify PurposeDrivenAgent is directly instantiable (merged with GenericPurposeDrivenAgent)."""

    def test_purpose_driven_agent_is_directly_instantiable(self):
        agent = PurposeDrivenAgent(
            agent_id="test",
            purpose="test purpose",
            adapter_name="test",
        )
        assert agent.agent_id == "test"
        assert agent.purpose == "test purpose"
        assert agent.adapter_name == "test"

    def test_generic_purpose_driven_agent_is_same_class(self):
        """GenericPurposeDrivenAgent is a backward-compat alias for PurposeDrivenAgent."""
        assert GenericPurposeDrivenAgent is PurposeDrivenAgent

    def test_generic_purpose_driven_agent_instantiation(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test",
            purpose="test purpose",
            adapter_name="test",
        )
        assert agent.agent_id == "test"
        assert agent.purpose == "test purpose"
        assert agent.adapter_name == "test"

    def test_leadership_agent_is_subclass(self):
        assert issubclass(LeadershipAgent, PurposeDrivenAgent)
        agent = LeadershipAgent(
            agent_id="test_leader",
            purpose="Leadership and decision-making",
            adapter_name="leadership",
        )
        assert agent.agent_id == "test_leader"
        assert "Leadership" in agent.purpose

    def test_purpose_is_added_to_layer_context(self):
        agent = PurposeDrivenAgent(
            agent_id="ctx-test",
            purpose="My important purpose",
            adapter_name="generic",
        )
        ctx = agent.get_layer_contexts()
        assert ctx.get("purpose") == "My important purpose"

