"""
Test that get_agent_type() returns list of personas/skills,
and that the _layers stack is built correctly by each class in the hierarchy.
"""
from AgentOperatingSystem.agents.purpose_driven import GenericPurposeDrivenAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
from AgentOperatingSystem.agents.cmo_agent import CMOAgent


class TestAgentPersonas:
    """Verify that agents return correct persona lists via layer stacking."""

    def test_generic_agent_returns_generic_persona(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test1",
            purpose="General tasks",
            adapter_name="generic",
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

    def test_cmo_agent_returns_dual_personas_in_hierarchy_order(self):
        """Leadership layer is added first (by LeadershipAgent), marketing second (by CMOAgent)."""
        agent = CMOAgent(
            agent_id="test3",
            marketing_adapter_name="marketing",
            leadership_adapter_name="leadership",
        )
        types = agent.get_agent_type()
        assert isinstance(types, list)
        assert types == ["leadership", "marketing"]


class TestLayerStacking:
    """Verify the _layers registry is populated correctly by each class in the chain."""

    def test_generic_agent_has_one_layer(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="g1",
            purpose="Test",
            adapter_name="generic",
        )
        assert len(agent._layers) == 1
        assert agent._layers[0]["adapter"] == "generic"

    def test_leadership_agent_has_one_layer(self):
        agent = LeadershipAgent(agent_id="l1", purpose="Lead")
        assert len(agent._layers) == 1
        assert agent._layers[0]["adapter"] == "leadership"
        assert "leadership" in agent._layers[0]["context"]["domain"]

    def test_cmo_agent_has_two_layers(self):
        agent = CMOAgent(agent_id="c1")
        assert len(agent._layers) == 2
        assert agent._layers[0]["adapter"] == "leadership"
        assert agent._layers[1]["adapter"] == "marketing"

    def test_leadership_layer_context_keys(self):
        agent = LeadershipAgent(agent_id="l2", purpose="Lead")
        ctx = agent._layers[0]["context"]
        assert "domain" in ctx
        assert "capabilities" in ctx

    def test_cmo_marketing_layer_context_keys(self):
        agent = CMOAgent(agent_id="c2")
        ctx = agent._layers[1]["context"]
        assert "domain" in ctx
        assert "marketing_purpose" in ctx
        assert "capabilities" in ctx

    def test_get_adapters_reflects_all_layers(self):
        agent = CMOAgent(agent_id="c3")
        adapters = agent.get_adapters()
        assert adapters == ["leadership", "marketing"]

    def test_get_all_skills_union_of_layers(self):
        agent = CMOAgent(agent_id="c4")
        skills = agent.get_all_skills()
        # Leadership skills
        assert "make_decision" in skills
        # CMO/marketing skills
        assert "execute_with_purpose" in skills

    def test_get_layer_contexts_merges_all_layers(self):
        agent = CMOAgent(agent_id="c5")
        ctx = agent.get_layer_contexts()
        # From leadership layer
        assert ctx.get("domain") == "marketing"   # marketing layer overrides
        assert "capabilities" in ctx
        # marketing_purpose only in marketing layer
        assert "marketing_purpose" in ctx

    def test_adapter_name_points_to_last_layer(self):
        """adapter_name always reflects the most recently added (most specific) adapter."""
        agent = CMOAgent(agent_id="c6")
        assert agent.adapter_name == "marketing"

        agent2 = LeadershipAgent(agent_id="l3", purpose="Lead")
        assert agent2.adapter_name == "leadership"

    def test_custom_adapter_name_propagated(self):
        agent = LeadershipAgent(agent_id="l4", purpose="Lead", adapter_name="exec-leadership")
        assert agent.adapter_name == "exec-leadership"
        assert agent.get_adapters() == ["exec-leadership"]
