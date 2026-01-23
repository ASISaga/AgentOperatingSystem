"""
Tests for Perpetual Agent functionality

This test suite validates the core USP of Agent Operating System:
perpetual, event-driven, persistent agents vs traditional task-based sessions.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AgentOperatingSystem.agents import PerpetualAgent
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
        # Create perpetual agent
        agent = PerpetualAgent(
            agent_id="test_ceo",
            name="Test CEO",
            role="executive"
        )
        
        # Initialize and start
        assert await agent.initialize()
        assert await agent.start()
        
        # Agent should be running
        assert agent.is_running
        assert agent.state == "running"
        
        # Process first event
        event1 = {"type": "DecisionRequested", "data": {"decision": "hire_engineer"}}
        result1 = await agent.handle_message(event1)
        assert result1["status"] == "success"
        
        # Process second event
        event2 = {"type": "DecisionRequested", "data": {"decision": "approve_budget"}}
        result2 = await agent.handle_message(event2)
        assert result2["status"] == "success"
        
        # Check persistent state - should remember both events
        state = await agent.get_persistent_state()
        assert state["total_events_processed"] == 2
        assert len(state["memory"]) == 2
        
        # Agent should still be running (not terminated)
        assert agent.is_running
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_event_driven_awakening(self):
        """
        Test that agent awakens in response to events.
        
        Demonstrates event-driven nature: agent sleeps when idle,
        awakens to process events, then returns to sleep.
        """
        agent = PerpetualAgent(
            agent_id="test_cfo",
            name="Test CFO",
            role="finance"
        )
        
        await agent.initialize()
        await agent.start()
        
        # Agent should start in sleep mode
        assert agent.sleep_mode
        assert agent.wake_count == 0
        
        # Process event - agent should awaken
        event = {"type": "BudgetRequest", "data": {"amount": 100000}}
        await agent.handle_message(event)
        
        # Agent should have awakened and returned to sleep
        assert agent.wake_count == 1
        assert agent.sleep_mode  # Back to sleep after processing
        
        # Process another event
        await agent.handle_message(event)
        assert agent.wake_count == 2
        
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_event_subscription(self):
        """
        Test that agents can subscribe to specific event types.
        
        This enables selective awakening based on relevant events.
        """
        agent = PerpetualAgent(
            agent_id="test_coo",
            name="Test COO",
            role="operations"
        )
        
        # Track handler invocations
        handler_calls = []
        
        async def incident_handler(event_data):
            handler_calls.append(event_data)
            return {"handled": True}
        
        await agent.initialize()
        
        # Subscribe to specific event type
        assert await agent.subscribe_to_event("IncidentRaised", incident_handler)
        
        await agent.start()
        
        # Send subscribed event
        incident_event = {
            "type": "IncidentRaised",
            "data": {"severity": "high", "system": "database"}
        }
        result = await agent.handle_message(incident_event)
        
        # Handler should have been called
        assert len(handler_calls) == 1
        assert handler_calls[0]["severity"] == "high"
        assert result["status"] == "success"
        
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_context_preservation(self):
        """
        Test that agent context is preserved across interactions.
        
        This is crucial for continuous operations where agents
        build up knowledge over time.
        """
        agent = PerpetualAgent(
            agent_id="test_cto",
            name="Test CTO",
            role="technology"
        )
        
        await agent.initialize()
        await agent.start()
        
        # Update context
        await agent.update_context({
            "current_sprint": "sprint-42",
            "team_size": 10,
            "tech_debt_score": 7.5
        })
        
        # Process some events
        await agent.handle_message({"type": "CodeReview", "data": {}})
        await agent.handle_message({"type": "DeploymentApproval", "data": {}})
        
        # Context should still be intact
        state = await agent.get_persistent_state()
        assert state["context"]["current_sprint"] == "sprint-42"
        assert state["context"]["team_size"] == 10
        assert state["total_events_processed"] == 2
        
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
        
        agent = PerpetualAgent(
            agent_id="persistent_ceo",
            name="Persistent CEO",
            role="executive"
        )
        
        # Register as perpetual
        assert await manager.register_agent(agent, perpetual=True)
        
        # Agent should be running immediately
        assert agent.is_running
        
        # Process multiple events without restarting
        for i in range(5):
            event = {"type": "Decision", "data": {"id": i}}
            await agent.handle_message(event)
        
        # Agent should still be running
        assert agent.is_running
        state = await agent.get_persistent_state()
        assert state["total_events_processed"] == 5
        
        # Get statistics
        stats = manager.get_agent_statistics()
        assert stats["perpetual_agents"] == 1
        assert stats["total_agents"] == 1
        
        # Clean up
        await manager.deregister_agent(agent.agent_id)
    
    @pytest.mark.asyncio
    async def test_multiple_perpetual_agents(self):
        """
        Test multiple perpetual agents running concurrently.
        
        This demonstrates the "operating system" aspect: multiple
        persistent agents coexisting and responding to different events.
        """
        manager = UnifiedAgentManager()
        
        # Create multiple perpetual agents
        ceo = PerpetualAgent(agent_id="ceo", name="CEO", role="executive")
        cfo = PerpetualAgent(agent_id="cfo", name="CFO", role="finance")
        cto = PerpetualAgent(agent_id="cto", name="CTO", role="technology")
        
        # Register all as perpetual
        await manager.register_agent(ceo, perpetual=True)
        await manager.register_agent(cfo, perpetual=True)
        await manager.register_agent(cto, perpetual=True)
        
        # All should be running
        stats = manager.get_agent_statistics()
        assert stats["perpetual_agents"] == 3
        assert stats["perpetual_percentage"] == 100.0
        
        # Send events to different agents
        await ceo.handle_message({"type": "StrategyDecision", "data": {}})
        await cfo.handle_message({"type": "BudgetApproval", "data": {}})
        await cto.handle_message({"type": "TechReview", "data": {}})
        
        # All agents should have processed their events
        ceo_state = await ceo.get_persistent_state()
        cfo_state = await cfo.get_persistent_state()
        cto_state = await cto.get_persistent_state()
        
        assert ceo_state["total_events_processed"] == 1
        assert cfo_state["total_events_processed"] == 1
        assert cto_state["total_events_processed"] == 1
        
        # All should still be running
        assert ceo.is_running
        assert cfo.is_running
        assert cto.is_running
        
        # Clean up
        await manager.deregister_agent("ceo")
        await manager.deregister_agent("cfo")
        await manager.deregister_agent("cto")
    
    @pytest.mark.asyncio
    async def test_health_check_shows_operational_mode(self):
        """
        Test that health checks distinguish between operational modes.
        """
        manager = UnifiedAgentManager()
        
        # Create perpetual agent
        perpetual = PerpetualAgent(
            agent_id="perpetual_agent",
            name="Always On",
            role="test"
        )
        
        await manager.register_agent(perpetual, perpetual=True)
        
        # Get health status
        health = await manager.health_check_all()
        
        # Should indicate perpetual mode
        assert "perpetual_agent" in health
        assert health["perpetual_agent"]["operational_mode"] == "perpetual"
        assert health["perpetual_agent"]["healthy"]
        
        await manager.deregister_agent("perpetual_agent")


if __name__ == "__main__":
    # Run tests
    asyncio.run(pytest.main([__file__, "-v"]))
