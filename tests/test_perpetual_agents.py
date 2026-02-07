"""
Tests for Perpetual Agent functionality

This test suite validates the core USP of Agent Operating System:
perpetual, event-driven, persistent agents vs traditional task-based sessions.
"""

import pytest
import asyncio
from datetime import datetime

from AgentOperatingSystem.agents import GenericPurposeDrivenAgent
from AgentOperatingSystem.orchestration import UnifiedAgentManager


class TestPerpetualAgent:
    """Test the perpetual agent implementation"""

    @pytest.mark.asyncio
    async def test_agent_persistence_across_events(self):
        """
        Test that agent state persists across multiple events.

        This demonstrates the key difference from task-based frameworks:
        the agent maintains context across all interactions.
        """
        agent = GenericPurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Executive oversight",
            adapter_name="executive",
        )

        assert await agent.initialize()
        assert await agent.start()

        assert agent.is_running

        event1 = {"type": "DecisionRequested", "data": {"decision": "hire_engineer"}}
        result1 = await agent.handle_message(event1)
        assert result1["status"] == "success"

        event2 = {"type": "DecisionRequested", "data": {"decision": "approve_budget"}}
        result2 = await agent.handle_message(event2)
        assert result2["status"] == "success"

        # Agent should still be running (not terminated)
        assert agent.is_running
        await agent.stop()

    @pytest.mark.asyncio
    async def test_event_driven_awakening(self):
        """
        Test that agent awakens in response to events.
        """
        agent = GenericPurposeDrivenAgent(
            agent_id="test_cfo",
            purpose="Financial management",
            adapter_name="finance",
        )

        await agent.initialize()
        await agent.start()

        assert agent.sleep_mode
        assert agent.wake_count == 0

        event = {"type": "BudgetRequest", "data": {"amount": 100000}}
        await agent.handle_message(event)

        assert agent.wake_count == 1
        assert agent.sleep_mode

        await agent.handle_message(event)
        assert agent.wake_count == 2

        await agent.stop()

    @pytest.mark.asyncio
    async def test_event_subscription(self):
        """
        Test that agents can subscribe to specific event types.
        """
        agent = GenericPurposeDrivenAgent(
            agent_id="test_coo",
            purpose="Operations management",
            adapter_name="operations",
        )

        handler_calls = []

        async def incident_handler(event_data):
            handler_calls.append(event_data)
            return {"handled": True}

        await agent.initialize()

        assert await agent.subscribe_to_event("IncidentRaised", incident_handler)

        await agent.start()

        incident_event = {
            "type": "IncidentRaised",
            "data": {"severity": "high", "system": "database"},
        }
        result = await agent.handle_message(incident_event)

        assert len(handler_calls) == 1
        assert handler_calls[0]["severity"] == "high"
        assert result["status"] == "success"

        await agent.stop()

    @pytest.mark.asyncio
    async def test_context_preservation(self):
        """
        Test that agent context is preserved across interactions.
        """
        agent = GenericPurposeDrivenAgent(
            agent_id="test_cto",
            purpose="Technology leadership",
            adapter_name="technology",
        )

        await agent.initialize()
        await agent.start()

        # Set context via MCP server
        await agent.mcp_context_server.set_context("current_sprint", "sprint-42")
        await agent.mcp_context_server.set_context("team_size", 10)

        await agent.handle_message({"type": "CodeReview", "data": {}})
        await agent.handle_message({"type": "DeploymentApproval", "data": {}})

        # Context should be preserved
        sprint = await agent.mcp_context_server.get_context("current_sprint")
        team_size = await agent.mcp_context_server.get_context("team_size")
        assert sprint == "sprint-42"
        assert team_size == 10

        await agent.stop()


class TestAlwaysOnVsTaskBased:
    """
    Comparative tests showing the difference between perpetual
    and task-based agent models.
    """

    @pytest.mark.asyncio
    async def test_perpetual_agent_lifecycle(self):
        """
        Demonstrate perpetual lifecycle: register once, run indefinitely.
        """
        manager = UnifiedAgentManager()

        agent = GenericPurposeDrivenAgent(
            agent_id="persistent_ceo",
            purpose="Executive leadership",
            adapter_name="executive",
        )

        assert await manager.register_agent(agent, perpetual=True)

        assert agent.is_running

        for i in range(5):
            event = {"type": "Decision", "data": {"id": i}}
            await agent.handle_message(event)

        assert agent.is_running

        state = await agent.get_state()
        assert state is not None

        stats = manager.get_agent_statistics()
        assert stats["perpetual_agents"] == 1
        assert stats["total_agents"] == 1

        await manager.deregister_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_multiple_perpetual_agents(self):
        """
        Test multiple perpetual agents running concurrently.
        """
        manager = UnifiedAgentManager()

        ceo = GenericPurposeDrivenAgent(
            agent_id="ceo", purpose="Strategy", adapter_name="executive"
        )
        cfo = GenericPurposeDrivenAgent(
            agent_id="cfo", purpose="Finance", adapter_name="finance"
        )
        cto = GenericPurposeDrivenAgent(
            agent_id="cto", purpose="Technology", adapter_name="technology"
        )

        await manager.register_agent(ceo, perpetual=True)
        await manager.register_agent(cfo, perpetual=True)
        await manager.register_agent(cto, perpetual=True)

        stats = manager.get_agent_statistics()
        assert stats["perpetual_agents"] == 3
        assert stats["perpetual_percentage"] == 100.0

        await ceo.handle_message({"type": "StrategyDecision", "data": {}})
        await cfo.handle_message({"type": "BudgetApproval", "data": {}})
        await cto.handle_message({"type": "TechReview", "data": {}})

        assert ceo.is_running
        assert cfo.is_running
        assert cto.is_running

        await manager.deregister_agent("ceo")
        await manager.deregister_agent("cfo")
        await manager.deregister_agent("cto")

    @pytest.mark.asyncio
    async def test_health_check_shows_operational_mode(self):
        """
        Test that health checks distinguish between operational modes.
        """
        manager = UnifiedAgentManager()

        perpetual = GenericPurposeDrivenAgent(
            agent_id="perpetual_agent",
            purpose="Always-on testing",
            adapter_name="test",
        )

        await manager.register_agent(perpetual, perpetual=True)

        health = await manager.health_check_all()

        assert "perpetual_agent" in health
        assert health["perpetual_agent"]["operational_mode"] == "perpetual"
        assert health["perpetual_agent"]["healthy"]

        await manager.deregister_agent("perpetual_agent")
