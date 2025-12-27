"""
Test PurposeDrivenAgent and ContextMCPServer integration

Validates that:
1. ContextMCPServer can be instantiated and used
2. PurposeDrivenAgent can be created and uses ContextMCPServer
3. Purpose-driven behavior works as expected
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
from AgentOperatingSystem.mcp.context_server import ContextMCPServer


async def test_context_server():
    """Test ContextMCPServer functionality"""
    print("=" * 80)
    print("Testing ContextMCPServer")
    print("=" * 80)
    
    # Create and initialize server
    server = ContextMCPServer(agent_id="test_agent")
    await server.initialize()
    
    # Test context operations
    await server.set_context("test_key", "test_value")
    value = await server.get_context("test_key")
    assert value == "test_value", "Context get/set failed"
    print("✅ Context get/set works")
    
    # Test event storage
    await server.store_event({"type": "test_event", "data": "test"})
    history = await server.get_event_history()
    assert len(history) == 1, "Event storage failed"
    print("✅ Event storage works")
    
    # Test memory
    await server.add_memory({"type": "test_memory", "content": "test"})
    memory = await server.get_memory()
    assert len(memory) == 1, "Memory storage failed"
    print("✅ Memory storage works")
    
    # Test statistics
    stats = await server.get_statistics()
    print(f"✅ Statistics: {stats}")
    
    await server.shutdown()
    print("✅ ContextMCPServer test passed")
    print()


async def test_purpose_driven_agent():
    """Test PurposeDrivenAgent functionality"""
    print("=" * 80)
    print("Testing PurposeDrivenAgent")
    print("=" * 80)
    
    # Create agent
    agent = PurposeDrivenAgent(
        agent_id="test_ceo",
        purpose="Strategic oversight and company growth",
        purpose_scope="Strategic planning, major decisions",
        success_criteria=["Revenue growth", "Team expansion", "Market share"],
        adapter_name="ceo"
    )
    
    # Initialize agent
    success = await agent.initialize()
    assert success, "Agent initialization failed"
    print("✅ PurposeDrivenAgent initialized")
    
    # Check that ContextMCPServer was created
    assert agent.mcp_context_server is not None, "ContextMCPServer not created"
    print("✅ ContextMCPServer automatically created")
    
    # Test purpose alignment
    test_action = {"type": "decision", "description": "Expand to new market"}
    alignment = await agent.evaluate_purpose_alignment(test_action)
    assert alignment["aligned"] is not None, "Purpose alignment failed"
    print(f"✅ Purpose alignment: {alignment['aligned']} (score: {alignment['alignment_score']})")
    
    # Test decision making
    decision_context = {
        "question": "Should we expand to Europe?",
        "options": [
            {"action": "expand", "description": "Expand to Europe"},
            {"action": "wait", "description": "Wait and analyze"}
        ]
    }
    decision = await agent.make_purpose_driven_decision(decision_context)
    assert decision["selected_option"] is not None, "Decision making failed"
    print(f"✅ Made decision: {decision['selected_option']['action']}")
    
    # Test goal management
    goal_id = await agent.add_goal(
        goal_description="Increase revenue by 50%",
        success_criteria=["Monthly revenue > $X", "Customer count > Y"],
        deadline="Q4 2025"
    )
    print(f"✅ Added goal: {goal_id}")
    
    # Update goal progress
    await agent.update_goal_progress(goal_id, 0.3, "Good progress on customer acquisition")
    print(f"✅ Updated goal progress: 30%")
    
    # Get status
    status = await agent.get_purpose_status()
    print(f"✅ Agent status: {status['active_goals']} active goals, "
          f"{status['metrics']['decisions_made']} decisions made")
    
    # Test event handling with purpose alignment
    event = {
        "type": "DecisionRequested",
        "data": {"decision": "hire_engineer"}
    }
    result = await agent.handle_event(event)
    assert "purpose_alignment" in result, "Event handling missing purpose alignment"
    print(f"✅ Event handled with purpose alignment")
    
    # Stop agent
    await agent.stop()
    print("✅ PurposeDrivenAgent test passed")
    print()


async def test_integration():
    """Test full integration"""
    print("=" * 80)
    print("Testing Full Integration")
    print("=" * 80)
    
    # Create multiple purpose-driven agents
    ceo = PurposeDrivenAgent(
        agent_id="ceo",
        purpose="Strategic oversight and company growth",
        adapter_name="ceo"
    )
    
    cfo = PurposeDrivenAgent(
        agent_id="cfo",
        purpose="Financial management and fiscal responsibility",
        adapter_name="cfo"
    )
    
    # Initialize both
    await ceo.initialize()
    await cfo.initialize()
    print("✅ Multiple agents initialized")
    
    # Verify each has its own ContextMCPServer
    assert ceo.mcp_context_server != cfo.mcp_context_server, "Agents sharing context server!"
    print("✅ Each agent has dedicated ContextMCPServer")
    
    # Set different context for each
    await ceo.mcp_context_server.set_context("focus", "growth")
    await cfo.mcp_context_server.set_context("focus", "stability")
    
    ceo_focus = await ceo.mcp_context_server.get_context("focus")
    cfo_focus = await cfo.mcp_context_server.get_context("focus")
    
    assert ceo_focus == "growth", "CEO context not preserved"
    assert cfo_focus == "stability", "CFO context not preserved"
    print(f"✅ Context preserved separately: CEO={ceo_focus}, CFO={cfo_focus}")
    
    # Clean up
    await ceo.stop()
    await cfo.stop()
    print("✅ Integration test passed")
    print()


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ContextMCPServer & PurposeDrivenAgent Tests".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    try:
        await test_context_server()
        await test_purpose_driven_agent()
        await test_integration()
        
        print("=" * 80)
        print("ALL TESTS PASSED ✅")
        print("=" * 80)
        print()
        print("Summary:")
        print("✅ ContextMCPServer infrastructure working")
        print("✅ PurposeDrivenAgent implementation complete")
        print("✅ Agents use dedicated ContextMCPServer instances")
        print("✅ Purpose-driven behavior functioning")
        print("✅ Ready for use as AOS native agents")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
