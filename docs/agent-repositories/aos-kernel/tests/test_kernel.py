"""Tests for AgentOperatingSystem kernel class."""

import pytest

from AgentOperatingSystem import AgentOperatingSystem, __version__
from AgentOperatingSystem.config import KernelConfig


class TestKernelVersion:
    """Version tests."""

    def test_version(self):
        assert __version__ == "5.0.0"


class TestAgentOperatingSystem:
    """AgentOperatingSystem kernel integration tests."""

    @pytest.mark.asyncio
    async def test_initialize(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        health = await kernel.health_check()
        assert health["status"] == "healthy"
        assert health["foundry_connected"] is False  # no project client

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.initialize()  # should not error
        health = await kernel.health_check()
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_shutdown(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.shutdown()
        health = await kernel.health_check()
        assert health["status"] == "not_initialized"

    @pytest.mark.asyncio
    async def test_custom_config(self):
        config = KernelConfig(
            environment="staging",
            default_model="gpt-4o-mini",
        )
        kernel = AgentOperatingSystem(config=config)
        assert kernel.config.environment == "staging"
        assert kernel.config.default_model == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_register_agent(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        record = await kernel.register_agent(
            agent_id="ceo",
            purpose="Strategic leadership",
            name="CEO Agent",
            adapter_name="leadership",
        )
        assert record["agent_id"] == "ceo"
        assert record["managed_by"] == "foundry_agent_service"
        health = await kernel.health_check()
        assert health["agents_registered"] == 1

    @pytest.mark.asyncio
    async def test_unregister_agent(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")
        await kernel.unregister_agent("ceo")
        health = await kernel.health_check()
        assert health["agents_registered"] == 0

    @pytest.mark.asyncio
    async def test_create_orchestration(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")
        await kernel.register_agent("cfo", "Finance")

        orch = await kernel.create_orchestration(
            agent_ids=["ceo", "cfo"],
            purpose="Quarterly review",
            workflow="collaborative",
        )
        assert orch["orchestration_id"]
        assert orch["status"] == "active"
        assert orch["managed_by"] == "foundry_agent_service"
        health = await kernel.health_check()
        assert health["active_orchestrations"] == 1

    @pytest.mark.asyncio
    async def test_run_agent_turn(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")
        orch = await kernel.create_orchestration(["ceo"], "Review")
        turn = await kernel.run_agent_turn(
            orch["orchestration_id"],
            "ceo",
            "What is the strategy?",
        )
        assert turn["agent_id"] == "ceo"

    @pytest.mark.asyncio
    async def test_get_orchestration_status(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        orch = await kernel.create_orchestration(["ceo"], "Review")
        status = await kernel.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "active"

    @pytest.mark.asyncio
    async def test_stop_orchestration(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        orch = await kernel.create_orchestration(["ceo"], "Review")
        await kernel.stop_orchestration(orch["orchestration_id"])
        status = await kernel.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "stopped"

    @pytest.mark.asyncio
    async def test_cancel_orchestration(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        orch = await kernel.create_orchestration(["ceo"], "Review")
        await kernel.cancel_orchestration(orch["orchestration_id"])
        status = await kernel.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_send_message_to_agent(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        result = await kernel.send_message_to_agent("ceo", "Hello")
        assert result["direction"] == "foundry_to_agent"
        health = await kernel.health_check()
        assert health["messages_bridged"] == 1

    @pytest.mark.asyncio
    async def test_send_message_to_foundry(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        result = await kernel.send_message_to_foundry("ceo", "Response")
        assert result["direction"] == "agent_to_foundry"

    @pytest.mark.asyncio
    async def test_broadcast_purpose_alignment(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        orch = await kernel.create_orchestration(["ceo", "cfo"], "Initial")
        results = await kernel.broadcast_purpose_alignment(
            orchestration_id=orch["orchestration_id"],
            purpose="New direction",
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_full_orchestration_lifecycle(self):
        """End-to-end: register agents, create orchestration, run turns, stop."""
        kernel = AgentOperatingSystem()
        await kernel.initialize()

        # Register agents
        await kernel.register_agent("ceo", "Strategic leadership", adapter_name="leadership")
        await kernel.register_agent("cfo", "Financial oversight", adapter_name="finance")
        await kernel.register_agent("cmo", "Market analysis", adapter_name="marketing")

        # Create orchestration
        orch = await kernel.create_orchestration(
            agent_ids=["ceo", "cfo", "cmo"],
            purpose="Annual strategic planning",
            purpose_scope="C-suite coordination",
            workflow="collaborative",
        )

        # Run turns
        t1 = await kernel.run_agent_turn(orch["orchestration_id"], "ceo", "Set the agenda")
        t2 = await kernel.run_agent_turn(orch["orchestration_id"], "cfo", "Budget update")
        t3 = await kernel.run_agent_turn(orch["orchestration_id"], "cmo", "Market report")

        # Check status
        status = await kernel.get_orchestration_status(orch["orchestration_id"])
        assert len(status["turns"]) == 3
        assert status["status"] == "active"

        # Broadcast purpose alignment
        await kernel.broadcast_purpose_alignment(
            orch["orchestration_id"],
            "Pivot to cost reduction",
            "Across all departments",
        )

        # Stop orchestration
        await kernel.stop_orchestration(orch["orchestration_id"])
        status = await kernel.get_orchestration_status(orch["orchestration_id"])
        assert status["status"] == "stopped"

        # Health check
        health = await kernel.health_check()
        assert health["agents_registered"] == 3
        assert health["active_orchestrations"] == 1

        await kernel.shutdown()


class TestA2ABoardroomEnrollment:
    """Tests for A2A agent tool enrollment."""

    @pytest.mark.asyncio
    async def test_enroll_agent_tools(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Strategic leadership")
        await kernel.register_agent("cfo", "Financial oversight")
        await kernel.register_agent("cto", "Technology strategy")

        tools = kernel.enroll_agent_tools(
            chairperson_id="ceo",
            specialist_ids=["cfo", "cto"],
        )
        assert len(tools) == 2
        assert tools[0]["type"] == "agent"
        assert tools[0]["agent"]["agent_id"] == "cfo"
        assert tools[1]["agent"]["agent_id"] == "cto"

    @pytest.mark.asyncio
    async def test_enroll_agent_tools_with_thread_id(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")
        await kernel.register_agent("cso", "Security governance")

        tools = kernel.enroll_agent_tools(
            chairperson_id="ceo",
            specialist_ids=["cso"],
            thread_id="thread-abc-123",
        )
        assert len(tools) == 1
        assert tools[0]["agent"]["thread_id"] == "thread-abc-123"

    @pytest.mark.asyncio
    async def test_enroll_agent_tools_chairperson_not_registered(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("cfo", "Finance")

        with pytest.raises(KeyError):
            kernel.enroll_agent_tools("ceo", ["cfo"])

    @pytest.mark.asyncio
    async def test_enroll_agent_tools_specialist_not_registered(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")

        with pytest.raises(KeyError):
            kernel.enroll_agent_tools("ceo", ["unknown"])

    @pytest.mark.asyncio
    async def test_enroll_agent_tools_includes_purpose(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Strategic vision")
        await kernel.register_agent("cmo", "Market strategy and growth")

        tools = kernel.enroll_agent_tools("ceo", ["cmo"])
        assert tools[0]["agent"]["description"] == "Market strategy and growth"

    @pytest.mark.asyncio
    async def test_enroll_agent_tools_includes_connection_id(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("ceo", "Lead")
        await kernel.register_agent("cfo", "Finance")

        tools = kernel.enroll_agent_tools("ceo", ["cfo"])
        assert tools[0]["agent"]["connection_id"] == "a2a-connection-cfo"

    @pytest.mark.asyncio
    async def test_get_a2a_tool_definitions(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("cfo", "Finance")
        await kernel.register_agent("cto", "Technology")

        definitions = kernel.get_a2a_tool_definitions(["cfo", "cto"])
        assert len(definitions) == 2
        assert definitions[0]["agent"]["agent_id"] == "cfo"
        assert definitions[1]["agent"]["agent_id"] == "cto"

    @pytest.mark.asyncio
    async def test_get_a2a_tool_definitions_with_thread_id(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("cso", "Security")

        definitions = kernel.get_a2a_tool_definitions(["cso"], thread_id="t-42")
        assert definitions[0]["agent"]["thread_id"] == "t-42"

    @pytest.mark.asyncio
    async def test_get_a2a_tool_definitions_skips_unregistered(self):
        kernel = AgentOperatingSystem()
        await kernel.initialize()
        await kernel.register_agent("cfo", "Finance")

        definitions = kernel.get_a2a_tool_definitions(["cfo", "unknown"])
        assert len(definitions) == 1
        assert definitions[0]["agent"]["agent_id"] == "cfo"

    @pytest.mark.asyncio
    async def test_full_boardroom_enrollment_lifecycle(self):
        """End-to-end: register C-suite, enroll as tools, verify definitions."""
        kernel = AgentOperatingSystem()
        await kernel.initialize()

        # Register full C-suite
        await kernel.register_agent("ceo", "Strategic vision and executive direction")
        await kernel.register_agent("cfo", "Fiscal governance and budget oversight")
        await kernel.register_agent("cto", "Technical infrastructure and innovation")
        await kernel.register_agent("cso", "Security governance and compliance")
        await kernel.register_agent("cmo", "Market strategy and brand management")

        # Enroll specialists for CEO
        tools = kernel.enroll_agent_tools(
            chairperson_id="ceo",
            specialist_ids=["cfo", "cto", "cso", "cmo"],
            thread_id="boardroom-thread-001",
        )
        assert len(tools) == 4
        names = {t["agent"]["agent_id"] for t in tools}
        assert names == {"cfo", "cto", "cso", "cmo"}
        for tool in tools:
            assert tool["agent"]["thread_id"] == "boardroom-thread-001"
            assert tool["type"] == "agent"
