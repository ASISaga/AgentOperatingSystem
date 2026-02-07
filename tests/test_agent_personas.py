"""
Test that get_agent_type() returns list of personas/skills.
"""
from AgentOperatingSystem.agents.purpose_driven import GenericPurposeDrivenAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
from AgentOperatingSystem.agents.cmo_agent import CMOAgent


class TestAgentPersonas:
    """Verify that agents return correct persona lists."""

    def test_generic_agent_returns_generic_persona(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test1",
            purpose="General tasks",
            adapter_name="general",
        )
        types = agent.get_agent_type()
        assert isinstance(types, list)
        assert types == ["generic"]

    def test_leadership_agent_returns_leadership_persona(self):
        agent = LeadershipAgent(
            agent_id="test2",
            purpose="Leadership tasks",
            adapter_name="leadership",
        )
        types = agent.get_agent_type()
        assert isinstance(types, list)
        assert types == ["leadership"]

    def test_cmo_agent_returns_dual_personas(self):
        agent = CMOAgent(
            agent_id="test3",
            marketing_adapter_name="marketing",
            leadership_adapter_name="leadership",
        )
        types = agent.get_agent_type()
        assert isinstance(types, list)
        assert types == ["marketing", "leadership"]
