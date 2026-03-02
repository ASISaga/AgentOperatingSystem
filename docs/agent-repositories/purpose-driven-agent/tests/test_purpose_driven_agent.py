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
            adapter_name="test",
        )
        assert agent.agent_id == "full-agent"
        assert agent.name == "Full Agent"
        assert agent.role == "tester"
        assert agent.purpose_scope == "Testing"
        assert agent.adapter_name == "test"

    def test_no_success_criteria_attribute(self) -> None:
        """Perpetual agents do not have success criteria."""
        agent = GenericPurposeDrivenAgent(
            agent_id="perpetual-agent",
            purpose="Perpetual purpose",
        )
        assert not hasattr(agent, "success_criteria")

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


# ---------------------------------------------------------------------------
# align_purpose_to_orchestration
# ---------------------------------------------------------------------------


class TestAlignPurposeToOrchestration:
    @pytest.mark.asyncio
    async def test_alignment_returns_expected_keys(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Execute Q1 strategic review",
        )
        required = {
            "agent_id",
            "original_purpose",
            "aligned_purpose",
            "orchestration_purpose",
            "alignment_strategy",
            "timestamp",
        }
        assert required.issubset(result.keys())

    @pytest.mark.asyncio
    async def test_alignment_preserves_original_purpose(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        original = initialised_agent.purpose
        result = await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Budget approval workflow",
        )
        assert result["original_purpose"] == original
        assert initialised_agent.purpose != original

    @pytest.mark.asyncio
    async def test_aligned_purpose_includes_domain(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Evaluate market expansion",
        )
        # Aligned purpose should reference the adapter domain
        assert "test-adapter" in initialised_agent.purpose
        assert "Evaluate market expansion" in initialised_agent.purpose

    @pytest.mark.asyncio
    async def test_alignment_has_no_criteria_parameter(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        """Perpetual orchestrations do not merge success criteria."""
        await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Review budget",
        )
        # Agent should not have success_criteria attribute
        assert not hasattr(initialised_agent, "success_criteria")

    @pytest.mark.asyncio
    async def test_alignment_stores_in_mcp(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Strategic alignment",
        )
        stored = await initialised_agent.mcp_context_server.get_context(
            "orchestration_purpose"
        )
        assert stored == "Strategic alignment"
        original = await initialised_agent.mcp_context_server.get_context(
            "original_purpose"
        )
        assert original is not None

    @pytest.mark.asyncio
    async def test_restore_original_purpose(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        original = initialised_agent.purpose
        await initialised_agent.align_purpose_to_orchestration(
            orchestration_purpose="Temporary orchestration goal",
        )
        assert initialised_agent.purpose != original

        restored = await initialised_agent.restore_original_purpose()
        assert restored is True
        assert initialised_agent.purpose == original

    @pytest.mark.asyncio
    async def test_restore_without_alignment_returns_false(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await initialised_agent.restore_original_purpose()
        assert result is False


# ---------------------------------------------------------------------------
# Dynamic MCP server routing
# ---------------------------------------------------------------------------


class StubMCPServer:
    """Minimal MCP server stub with a call_tool coroutine."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list = []

    async def call_tool(self, tool_name: str, params: dict) -> dict:
        self.calls.append({"tool": tool_name, "params": params})
        return {"server": self.name, "tool": tool_name, "result": "ok"}


class TestMCPServerRegistration:
    def test_initial_mcp_servers_empty(self, basic_agent: GenericPurposeDrivenAgent) -> None:
        assert basic_agent.mcp_servers == {}

    def test_register_mcp_server_stores_entry(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        server = StubMCPServer("s1")
        basic_agent.register_mcp_server("search", server, tags=["web_search"])
        assert "search" in basic_agent.mcp_servers

    def test_register_stores_tags(self, basic_agent: GenericPurposeDrivenAgent) -> None:
        server = StubMCPServer("s1")
        basic_agent.register_mcp_server("search", server, tags=["web_search", "query"])
        assert basic_agent.mcp_servers["search"]["tags"] == ["web_search", "query"]

    def test_register_disabled_by_default(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        server = StubMCPServer("s1")
        basic_agent.register_mcp_server("search", server)
        assert basic_agent.mcp_servers["search"]["enabled"] is False

    def test_register_enabled_when_requested(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        server = StubMCPServer("s1")
        basic_agent.register_mcp_server("search", server, enabled=True)
        assert basic_agent.mcp_servers["search"]["enabled"] is True

    def test_register_multiple_servers(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("s1", StubMCPServer("s1"))
        basic_agent.register_mcp_server("s2", StubMCPServer("s2"))
        assert len(basic_agent.mcp_servers) == 2


class TestEnableDisableMCPServer:
    @pytest.mark.asyncio
    async def test_enable_known_server_returns_true(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("db"))
        result = await basic_agent.enable_mcp_server("db")
        assert result is True

    @pytest.mark.asyncio
    async def test_enable_sets_enabled_flag(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("db"))
        await basic_agent.enable_mcp_server("db")
        assert basic_agent.mcp_servers["db"]["enabled"] is True

    @pytest.mark.asyncio
    async def test_enable_unknown_server_returns_false(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await basic_agent.enable_mcp_server("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_disable_known_server_returns_true(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("db"), enabled=True)
        result = await basic_agent.disable_mcp_server("db")
        assert result is True

    @pytest.mark.asyncio
    async def test_disable_clears_enabled_flag(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("db"), enabled=True)
        await basic_agent.disable_mcp_server("db")
        assert basic_agent.mcp_servers["db"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_disable_unknown_server_returns_false(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        result = await basic_agent.disable_mcp_server("nonexistent")
        assert result is False


class TestGetActiveMCPServers:
    def test_no_active_servers_when_all_disabled(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("a", StubMCPServer("a"))
        basic_agent.register_mcp_server("b", StubMCPServer("b"))
        assert basic_agent.get_active_mcp_servers() == {}

    def test_only_enabled_servers_returned(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        s1 = StubMCPServer("s1")
        s2 = StubMCPServer("s2")
        basic_agent.register_mcp_server("s1", s1, enabled=True)
        basic_agent.register_mcp_server("s2", s2, enabled=False)
        active = basic_agent.get_active_mcp_servers()
        assert "s1" in active
        assert "s2" not in active

    def test_active_servers_returns_server_instances(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        s1 = StubMCPServer("s1")
        basic_agent.register_mcp_server("s1", s1, enabled=True)
        active = basic_agent.get_active_mcp_servers()
        assert active["s1"] is s1


class TestRouteMCPRequest:
    @pytest.mark.asyncio
    async def test_route_to_enabled_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        server = StubMCPServer("web")
        basic_agent.register_mcp_server("web", server, enabled=True)
        result = await basic_agent.route_mcp_request("web", "search", {"query": "test"})
        assert result["result"] == "ok"
        assert result["server"] == "web"

    @pytest.mark.asyncio
    async def test_route_passes_params_to_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        server = StubMCPServer("web")
        basic_agent.register_mcp_server("web", server, enabled=True)
        await basic_agent.route_mcp_request("web", "search", {"query": "AOS"})
        assert server.calls[0]["params"] == {"query": "AOS"}

    @pytest.mark.asyncio
    async def test_route_raises_for_unknown_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        with pytest.raises(ValueError, match="not registered"):
            await basic_agent.route_mcp_request("unknown", "tool", {})

    @pytest.mark.asyncio
    async def test_route_raises_for_disabled_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("db"), enabled=False)
        with pytest.raises(RuntimeError, match="disabled"):
            await basic_agent.route_mcp_request("db", "query", {})


class TestSelectMCPServersForEvent:
    @pytest.mark.asyncio
    async def test_no_tags_enables_all_servers(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("a", StubMCPServer("a"), tags=["x"])
        basic_agent.register_mcp_server("b", StubMCPServer("b"), tags=["y"])
        activated = await basic_agent.select_mcp_servers_for_event({"type": "ping"})
        assert set(activated) == {"a", "b"}

    @pytest.mark.asyncio
    async def test_matching_tag_enables_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("search", StubMCPServer("s"), tags=["web_search"])
        basic_agent.register_mcp_server("db", StubMCPServer("d"), tags=["database"])
        activated = await basic_agent.select_mcp_servers_for_event(
            {"type": "query", "tags": ["web_search"]}
        )
        assert "search" in activated
        assert "db" not in activated

    @pytest.mark.asyncio
    async def test_non_matching_tag_disables_server(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server("db", StubMCPServer("d"), tags=["database"], enabled=True)
        await basic_agent.select_mcp_servers_for_event(
            {"type": "search", "tags": ["web_search"]}
        )
        assert basic_agent.mcp_servers["db"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_event_type_matches_server_tag(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        basic_agent.register_mcp_server(
            "file_tool", StubMCPServer("f"), tags=["file_system"]
        )
        activated = await basic_agent.select_mcp_servers_for_event(
            {"type": "file_system", "tags": ["other"]}
        )
        assert "file_tool" in activated

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_servers(
        self, basic_agent: GenericPurposeDrivenAgent
    ) -> None:
        activated = await basic_agent.select_mcp_servers_for_event({"type": "test"})
        assert activated == []

    @pytest.mark.asyncio
    async def test_handle_event_invokes_dynamic_selection(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        """handle_event automatically activates matching MCP servers."""
        initialised_agent.register_mcp_server(
            "search", StubMCPServer("s"), tags=["web_search"]
        )
        initialised_agent.register_mcp_server(
            "db", StubMCPServer("d"), tags=["database"]
        )
        await initialised_agent.handle_event(
            {"type": "lookup", "tags": ["web_search"]}
        )
        assert initialised_agent.mcp_servers["search"]["enabled"] is True
        assert initialised_agent.mcp_servers["db"]["enabled"] is False


class TestGetStateMCPServers:
    @pytest.mark.asyncio
    async def test_state_contains_mcp_server_keys(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        state = await initialised_agent.get_state()
        assert "registered_mcp_servers" in state
        assert "active_mcp_servers" in state

    @pytest.mark.asyncio
    async def test_state_lists_registered_servers(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        initialised_agent.register_mcp_server("s1", StubMCPServer("s1"))
        state = await initialised_agent.get_state()
        assert "s1" in state["registered_mcp_servers"]

    @pytest.mark.asyncio
    async def test_state_lists_active_servers(
        self, initialised_agent: GenericPurposeDrivenAgent
    ) -> None:
        initialised_agent.register_mcp_server("s1", StubMCPServer("s1"), enabled=True)
        initialised_agent.register_mcp_server("s2", StubMCPServer("s2"), enabled=False)
        state = await initialised_agent.get_state()
        assert "s1" in state["active_mcp_servers"]
        assert "s2" not in state["active_mcp_servers"]
