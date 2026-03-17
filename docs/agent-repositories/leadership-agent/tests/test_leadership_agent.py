"""
Tests for LeadershipAgent.

Coverage targets
----------------
- LeadershipAgent can be created with default parameters.
- Default purpose and adapter_name are set correctly.
- make_decision() returns a well-formed decision dict.
- consult_stakeholders() raises NotImplementedError.
- get_agent_type() returns ["leadership"].
- initialize() succeeds (inherits from PurposeDrivenAgent).
- Decisions are tracked in decisions_made list.
- get_decision_history() returns recent decisions.
"""

import pytest

from leadership_agent import LeadershipAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """LeadershipAgent can be created with only agent_id."""
        agent = LeadershipAgent(agent_id="leader-001")
        assert agent.agent_id == "leader-001"

    def test_default_purpose_set(self) -> None:
        agent = LeadershipAgent(agent_id="leader-001")
        assert "Leadership" in agent.purpose
        assert "decision" in agent.purpose.lower()

    def test_default_adapter_name(self) -> None:
        agent = LeadershipAgent(agent_id="leader-001")
        assert agent.adapter_name == "leadership"

    def test_default_role(self) -> None:
        agent = LeadershipAgent(agent_id="leader-001")
        assert agent.role == "leader"

    def test_custom_purpose_overrides_default(self) -> None:
        agent = LeadershipAgent(
            agent_id="custom-leader",
            purpose="Custom strategic purpose",
        )
        assert agent.purpose == "Custom strategic purpose"

    def test_custom_adapter_name(self) -> None:
        agent = LeadershipAgent(agent_id="l", adapter_name="ceo")
        assert agent.adapter_name == "ceo"

    def test_decisions_made_initially_empty(self) -> None:
        agent = LeadershipAgent(agent_id="leader-001")
        assert agent.decisions_made == []

    def test_stakeholders_initially_empty(self) -> None:
        agent = LeadershipAgent(agent_id="leader-001")
        assert agent.stakeholders == []


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_leadership_list(self, basic_agent: LeadershipAgent) -> None:
        assert basic_agent.get_agent_type() == ["leadership"]

    def test_returns_list(self, basic_agent: LeadershipAgent) -> None:
        assert isinstance(basic_agent.get_agent_type(), list)


# ---------------------------------------------------------------------------
# Lifecycle (inherited)
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_agent: LeadershipAgent) -> None:
        result = await basic_agent.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        result = await initialised_agent.start()
        assert result is True
        assert initialised_agent.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        await initialised_agent.start()
        result = await initialised_agent.stop()
        assert result is True
        assert not initialised_agent.is_running


# ---------------------------------------------------------------------------
# make_decision
# ---------------------------------------------------------------------------


class TestMakeDecision:
    @pytest.mark.asyncio
    async def test_returns_dict(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(
            context={"proposal": "Expand to EU"}
        )
        assert isinstance(decision, dict)

    @pytest.mark.asyncio
    async def test_decision_has_required_keys(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(
            context={"proposal": "Launch new product"}
        )
        required = {"id", "agent_id", "context", "mode", "stakeholders", "timestamp", "decision"}
        assert required.issubset(decision.keys())

    @pytest.mark.asyncio
    async def test_decision_agent_id_matches(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(context={"item": "x"})
        assert decision["agent_id"] == initialised_agent.agent_id

    @pytest.mark.asyncio
    async def test_default_mode_is_autonomous(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(context={})
        assert decision["mode"] == "autonomous"

    @pytest.mark.asyncio
    async def test_custom_mode(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(
            context={}, mode="consensus"
        )
        assert decision["mode"] == "consensus"

    @pytest.mark.asyncio
    async def test_stakeholders_included(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        decision = await initialised_agent.make_decision(
            context={}, stakeholders=["cfo", "cto"]
        )
        assert "cfo" in decision["stakeholders"]
        assert "cto" in decision["stakeholders"]

    @pytest.mark.asyncio
    async def test_decision_appended_to_history(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        before = len(initialised_agent.decisions_made)
        await initialised_agent.make_decision(context={"topic": "budget"})
        assert len(initialised_agent.decisions_made) == before + 1

    @pytest.mark.asyncio
    async def test_multiple_decisions_tracked(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        for i in range(3):
            await initialised_agent.make_decision(context={"idx": i})
        assert len(initialised_agent.decisions_made) == 3

    @pytest.mark.asyncio
    async def test_decision_id_is_unique(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        d1 = await initialised_agent.make_decision(context={})
        d2 = await initialised_agent.make_decision(context={})
        assert d1["id"] != d2["id"]

    @pytest.mark.asyncio
    async def test_decision_increments_metric(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        before = initialised_agent.purpose_metrics["decisions_made"]
        await initialised_agent.make_decision(context={})
        assert initialised_agent.purpose_metrics["decisions_made"] == before + 1


# ---------------------------------------------------------------------------
# consult_stakeholders
# ---------------------------------------------------------------------------


class TestConsultStakeholders:
    @pytest.mark.asyncio
    async def test_raises_not_implemented(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        with pytest.raises(NotImplementedError):
            await initialised_agent.consult_stakeholders(
                stakeholders=["cfo"],
                topic="budget",
                context={"quarter": "Q2"},
            )


# ---------------------------------------------------------------------------
# get_decision_history
# ---------------------------------------------------------------------------


class TestGetDecisionHistory:
    @pytest.mark.asyncio
    async def test_empty_initially(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        history = await initialised_agent.get_decision_history()
        assert history == []

    @pytest.mark.asyncio
    async def test_history_grows(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        await initialised_agent.make_decision(context={"a": 1})
        await initialised_agent.make_decision(context={"b": 2})
        history = await initialised_agent.get_decision_history()
        assert len(history) == 2

    @pytest.mark.asyncio
    async def test_history_respects_limit(
        self, initialised_agent: LeadershipAgent
    ) -> None:
        for i in range(15):
            await initialised_agent.make_decision(context={"i": i})
        history = await initialised_agent.get_decision_history(limit=5)
        assert len(history) == 5
