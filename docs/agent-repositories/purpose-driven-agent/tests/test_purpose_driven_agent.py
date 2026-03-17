"""
Tests for PurposeDrivenAgent and GenericPurposeDrivenAgent.

Coverage targets
----------------
- PurposeDrivenAgent cannot be instantiated directly (abstract).
- GenericPurposeDrivenAgent can be created with required parameters.
- initialize() returns True and sets up MCP context server.
- handle_event() processes events and returns expected structure.
- get_purpose_status() returns correct status dictionary.
- evaluate_purpose_alignment() returns alignment result.
- add_goal() creates a goal and returns a goal ID.
- get_state() returns runtime state dictionary.
"""

import pytest

from purpose_driven_agent import GenericPurposeDrivenAgent, PurposeDrivenAgent
from purpose_driven_agent.context_server import ContextMCPServer


# ---------------------------------------------------------------------------
# Instantiation tests
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_purpose_driven_agent_is_abstract(self) -> None:
        """PurposeDrivenAgent cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            PurposeDrivenAgent(  # type: ignore[abstract]
                agent_id="abstract-agent",
                purpose="Should fail",
            )

    def test_generic_agent_creation_minimal(self) -> None:
        """GenericPurposeDrivenAgent can be created with only required params."""
        agent = GenericPurposeDrivenAgent(
            agent_id="minimal-agent",
            purpose="Minimal test purpose",
        )
        assert agent.agent_id == "minimal-agent"
        assert agent.purpose == "Minimal test purpose"

    def test_generic_agent_creation_full(self) -> None:
        """GenericPurposeDrivenAgent stores all provided parameters."""
        agent = GenericPurposeDrivenAgent(
            agent_id="full-agent",
            purpose="Full test purpose",
            name="Full Agent",
            role="tester",
            purpose_scope="Testing",
            success_criteria=["All tests pass"],
            adapter_name="test",
        )
        assert agent.agent_id == "full-agent"
        assert agent.name == "Full Agent"
        assert agent.role == "tester"
        assert agent.purpose_scope == "Testing"
        assert agent.success_criteria == ["All tests pass"]
        assert agent.adapter_name == "test"

    def test_generic_agent_name_defaults_to_agent_id(self) -> None:
        agent = GenericPurposeDrivenAgent(agent_id="my-id", purpose="p")
        assert agent.name == "my-id"

    def test_generic_agent_initial_state(self) -> None:
        agent = GenericPurposeDrivenAgent(agent_id="state-agent", purpose="p")
        assert agent.state == "initialized"
        assert not agent.is_running
        assert agent.sleep_mode
        assert agent.wake_count == 0
        assert agent.total_events_processed == 0
        assert agent.mcp_context_server is None


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_generic_persona(self, basic_agent: GenericPurposeDrivenAgent) -> None:
        personas = basic_agent.get_agent_type()
        assert personas == ["generic"]

    def test_returns_list(self, basic_agent: GenericPurposeDrivenAgent) -> None:
        assert isinstance(basic_agent.get_agent_type(), list)


# ---------------------------------------------------------------------------
# Lifecycle: initialize / start / stop
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_agent: GenericPurposeDrivenAgent) -> None:
        result = await basic_agent.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_initialize_creates_mcp_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        await basic_agent.initialize()
        assert isinstance(basic_agent.mcp_context_server, ContextMCPServer)

    @pytest.mark.asyncio
    async def test_initialize_stores_purpose_in_mcp(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        stored = await initialised_agent.mcp_context_server.get_context("purpose")
        assert stored == initialised_agent.purpose

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.start()
        assert result is True
        assert initialised_agent.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        await initialised_agent.start()
        result = await initialised_agent.stop()
        assert result is True
        assert not initialised_agent.is_running

    @pytest.mark.asyncio
    async def test_health_check(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        health = await initialised_agent.health_check()
        assert health["agent_id"] == initialised_agent.agent_id
        assert health["healthy"] is True


# ---------------------------------------------------------------------------
# handle_event
# ---------------------------------------------------------------------------


class TestHandleEvent:
    @pytest.mark.asyncio
    async def test_handle_event_returns_success(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        event = {"type": "test_event", "data": {"key": "value"}}
        result = await initialised_agent.handle_event(event)
        assert result["status"] == "success"
        assert result["processed_by"] == initialised_agent.agent_id

    @pytest.mark.asyncio
    async def test_handle_event_increments_counter(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        before = initialised_agent.total_events_processed
        await initialised_agent.handle_event({"type": "ping"})
        assert initialised_agent.total_events_processed == before + 1

    @pytest.mark.asyncio
    async def test_handle_event_includes_purpose(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.handle_event({"type": "test"})
        assert result["purpose"] == initialised_agent.purpose

    @pytest.mark.asyncio
    async def test_handle_event_dispatches_to_handler(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        received: list = []

        async def handler(data: dict) -> dict:
            received.append(data)
            return {"handled": True}

        await initialised_agent.subscribe_to_event("custom_event", handler)
        await initialised_agent.handle_event(
            {"type": "custom_event", "data": {"payload": 42}}
        )
        assert len(received) == 1
        assert received[0]["payload"] == 42

    @pytest.mark.asyncio
    async def test_handle_message_delegates_to_handle_event(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.handle_message({"type": "msg_test"})
        assert result["status"] == "success"


# ---------------------------------------------------------------------------
# get_purpose_status
# ---------------------------------------------------------------------------


class TestGetPurposeStatus:
    @pytest.mark.asyncio
    async def test_status_contains_expected_keys(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        status = await initialised_agent.get_purpose_status()
        required = {
            "agent_id",
            "purpose",
            "purpose_scope",
            "success_criteria",
            "metrics",
            "active_goals",
            "completed_goals",
            "is_running",
            "total_events_processed",
        }
        assert required.issubset(status.keys())

    @pytest.mark.asyncio
    async def test_status_agent_id(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        status = await initialised_agent.get_purpose_status()
        assert status["agent_id"] == initialised_agent.agent_id

    @pytest.mark.asyncio
    async def test_status_purpose(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        status = await initialised_agent.get_purpose_status()
        assert status["purpose"] == initialised_agent.purpose


# ---------------------------------------------------------------------------
# evaluate_purpose_alignment
# ---------------------------------------------------------------------------


class TestEvaluatePurposeAlignment:
    @pytest.mark.asyncio
    async def test_alignment_returns_dict(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await basic_agent.evaluate_purpose_alignment({"type": "test_action"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_alignment_keys(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await basic_agent.evaluate_purpose_alignment({"type": "test_action"})
        assert "aligned" in result
        assert "alignment_score" in result
        assert "reasoning" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_alignment_increments_metric(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        before = basic_agent.purpose_metrics["purpose_evaluations"]
        await basic_agent.evaluate_purpose_alignment({"type": "test"})
        assert basic_agent.purpose_metrics["purpose_evaluations"] == before + 1

    @pytest.mark.asyncio
    async def test_alignment_score_range(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await basic_agent.evaluate_purpose_alignment({"type": "test"})
        assert 0.0 <= result["alignment_score"] <= 1.0


# ---------------------------------------------------------------------------
# add_goal
# ---------------------------------------------------------------------------


class TestAddGoal:
    @pytest.mark.asyncio
    async def test_add_goal_returns_id(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        goal_id = await initialised_agent.add_goal("Write comprehensive tests")
        assert goal_id.startswith("goal_")

    @pytest.mark.asyncio
    async def test_add_goal_appears_in_active(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        await initialised_agent.add_goal("Write comprehensive tests")
        assert len(initialised_agent.active_goals) == 1

    @pytest.mark.asyncio
    async def test_add_goal_multiple_increments(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        await initialised_agent.add_goal("Goal A")
        await initialised_agent.add_goal("Goal B")
        assert len(initialised_agent.active_goals) == 2

    @pytest.mark.asyncio
    async def test_update_goal_to_complete(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        goal_id = await initialised_agent.add_goal("Complete this goal")
        result = await initialised_agent.update_goal_progress(goal_id, 1.0)
        assert result is True
        assert len(initialised_agent.active_goals) == 0
        assert len(initialised_agent.completed_goals) == 1
        assert initialised_agent.purpose_metrics["goals_achieved"] == 1

    @pytest.mark.asyncio
    async def test_update_unknown_goal_returns_false(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.update_goal_progress("goal_nonexistent", 0.5)
        assert result is False


# ---------------------------------------------------------------------------
# get_state
# ---------------------------------------------------------------------------


class TestGetState:
    @pytest.mark.asyncio
    async def test_state_contains_expected_keys(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        state = await initialised_agent.get_state()
        required = {
            "agent_id",
            "adapter_name",
            "is_running",
            "sleep_mode",
            "wake_count",
            "total_events_processed",
            "subscriptions",
            "mcp_context_preserved",
        }
        assert required.issubset(state.keys())

    @pytest.mark.asyncio
    async def test_state_mcp_preserved_after_init(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        state = await initialised_agent.get_state()
        assert state["mcp_context_preserved"] is True

    @pytest.mark.asyncio
    async def test_state_adapter_name(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        await basic_agent.initialize()
        state = await basic_agent.get_state()
        assert state["adapter_name"] == "test-adapter"
