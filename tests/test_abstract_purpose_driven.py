"""
Test that PurposeDrivenAgent is properly abstract and cannot be directly instantiated.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_purpose_driven_agent_is_abstract():
    """Test that PurposeDrivenAgent cannot be directly instantiated."""
    from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
    from abc import ABC
    
    # Verify PurposeDrivenAgent is a subclass of ABC
    assert issubclass(PurposeDrivenAgent, ABC), "PurposeDrivenAgent should be a subclass of ABC"
    
    # Attempt to instantiate should raise TypeError
    try:
        agent = PurposeDrivenAgent(
            agent_id="test",
            purpose="test purpose",
            adapter_name="test"
        )
        # If we get here, the test failed
        raise AssertionError("PurposeDrivenAgent should not be instantiable!")
    except TypeError as e:
        # This is expected
        assert "abstract class" in str(e).lower() or "instantiate" in str(e).lower()
        pass


def test_generic_purpose_driven_agent_is_concrete():
    """Test that GenericPurposeDrivenAgent can be instantiated."""
    from AgentOperatingSystem.agents.purpose_driven import GenericPurposeDrivenAgent, PurposeDrivenAgent
    
    # Verify GenericPurposeDrivenAgent is a subclass of PurposeDrivenAgent
    assert issubclass(GenericPurposeDrivenAgent, PurposeDrivenAgent), \
        "GenericPurposeDrivenAgent should be a subclass of PurposeDrivenAgent"
    
    # Should be able to instantiate without error
    agent = GenericPurposeDrivenAgent(
        agent_id="test",
        purpose="test purpose",
        adapter_name="test"
    )
    
    assert agent.agent_id == "test"
    assert agent.purpose == "test purpose"
    assert agent.adapter_name == "test"


def test_leadership_agent_is_concrete():
    """Test that LeadershipAgent (subclass) can be instantiated."""
    from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
    from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
    
    # Verify LeadershipAgent is a subclass of PurposeDrivenAgent
    assert issubclass(LeadershipAgent, PurposeDrivenAgent), \
        "LeadershipAgent should be a subclass of PurposeDrivenAgent"
    
    # Should be able to instantiate without error
    agent = LeadershipAgent(
        agent_id="test_leader",
        purpose="Leadership and decision-making",
        adapter_name="leadership"
    )
    
    assert agent.agent_id == "test_leader"
    assert "Leadership" in agent.purpose


def test_backward_compatibility_aliases():
    """Test that backward compatibility aliases point to concrete implementations."""
    from AgentOperatingSystem.agents import BaseAgent, PerpetualAgent, GenericPurposeDrivenAgent
    
    # BaseAgent and PerpetualAgent should be aliases to GenericPurposeDrivenAgent
    assert BaseAgent is GenericPurposeDrivenAgent, \
        "BaseAgent should be an alias for GenericPurposeDrivenAgent"
    assert PerpetualAgent is GenericPurposeDrivenAgent, \
        "PerpetualAgent should be an alias for GenericPurposeDrivenAgent"
    
    # Should be able to use the aliases
    agent1 = BaseAgent(agent_id="test1", purpose="test", adapter_name="test")
    agent2 = PerpetualAgent(agent_id="test2", purpose="test", adapter_name="test")
    
    assert agent1.agent_id == "test1"
    assert agent2.agent_id == "test2"


if __name__ == "__main__":
    # Run tests manually for quick validation
    print("Testing that PurposeDrivenAgent is abstract...")
    test_purpose_driven_agent_is_abstract()
    print("✅ PurposeDrivenAgent is properly abstract")
    
    print("\nTesting that GenericPurposeDrivenAgent is concrete...")
    test_generic_purpose_driven_agent_is_concrete()
    print("✅ GenericPurposeDrivenAgent can be instantiated")
    
    print("\nTesting that LeadershipAgent is concrete...")
    test_leadership_agent_is_concrete()
    print("✅ LeadershipAgent can be instantiated")
    
    print("\nTesting backward compatibility aliases...")
    test_backward_compatibility_aliases()
    print("✅ Backward compatibility aliases work correctly")
    
    print("\n🎉 All tests passed!")
