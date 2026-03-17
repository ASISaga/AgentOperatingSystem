"""
Test PurposeDrivenAgent and ContextMCPServer integration.
"""
import pytest

from AgentOperatingSystem.agents.purpose_driven import GenericPurposeDrivenAgent
from AgentOperatingSystem.mcp.context_server import ContextMCPServer


class TestContextMCPServer:
    """Test ContextMCPServer functionality."""

    async def test_context_get_set(self):
        server = ContextMCPServer(agent_id="test_agent")
        await server.initialize()
        await server.set_context("test_key", "test_value")
        value = await server.get_context("test_key")
        assert value == "test_value"
        await server.shutdown()

    async def test_event_storage(self):
        server = ContextMCPServer(agent_id="test_agent")
        await server.initialize()
        await server.store_event({"type": "test_event", "data": "test"})
        history = await server.get_event_history()
        assert len(history) == 1
        await server.shutdown()

    async def test_memory_storage(self):
        server = ContextMCPServer(agent_id="test_agent")
        await server.initialize()
        await server.add_memory({"type": "test_memory", "content": "test"})
        memory = await server.get_memory()
        assert len(memory) == 1
        await server.shutdown()


class TestPurposeDrivenAgentIntegration:
    """Test PurposeDrivenAgent with ContextMCPServer integration."""

    async def test_agent_initialization(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Strategic oversight",
            adapter_name="ceo",
        )
        success = await agent.initialize()
        assert success
        assert agent.mcp_context_server is not None
        await agent.stop()

    async def test_purpose_alignment(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Strategic oversight",
            adapter_name="ceo",
        )
        await agent.initialize()
        action = {"type": "decision", "description": "Expand to new market"}
        alignment = await agent.evaluate_purpose_alignment(action)
        assert alignment["aligned"] is not None
        await agent.stop()

    async def test_goal_management(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Strategic oversight",
            adapter_name="ceo",
        )
        await agent.initialize()
        goal_id = await agent.add_goal(
            goal_description="Increase revenue by 50%",
            success_criteria=["Monthly revenue > $X"],
            deadline="Q4 2025",
        )
        assert goal_id is not None
        await agent.update_goal_progress(goal_id, 0.3, "Good progress")
        status = await agent.get_purpose_status()
        assert status["active_goals"] >= 1
        await agent.stop()

    async def test_multiple_agents_separate_context(self):
        ceo = GenericPurposeDrivenAgent(
            agent_id="ceo", purpose="Growth", adapter_name="ceo"
        )
        cfo = GenericPurposeDrivenAgent(
            agent_id="cfo", purpose="Stability", adapter_name="cfo"
        )
        await ceo.initialize()
        await cfo.initialize()
        assert ceo.mcp_context_server != cfo.mcp_context_server
        await ceo.mcp_context_server.set_context("focus", "growth")
        await cfo.mcp_context_server.set_context("focus", "stability")
        assert await ceo.mcp_context_server.get_context("focus") == "growth"
        assert await cfo.mcp_context_server.get_context("focus") == "stability"
        await ceo.stop()
        await cfo.stop()
