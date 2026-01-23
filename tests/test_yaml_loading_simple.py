#!/usr/bin/env python3
"""
Simple standalone test for YAML agent configuration loading.
This script tests the core functionality without pytest dependencies.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_yaml_loading():
    """Test YAML configuration loading for agents"""
    print("Testing YAML configuration loading...\n")
    
    # Test 1: Load PurposeDrivenAgent from YAML
    print("Test 1: Loading CEO agent from YAML...")
    try:
        from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
        
        yaml_path = "config/agents/ceo_agent.yaml"
        if Path(yaml_path).exists():
            agent = PurposeDrivenAgent.from_yaml(yaml_path)
            print(f"✓ Successfully loaded CEO agent")
            print(f"  - Agent ID: {agent.agent_id}")
            print(f"  - Purpose: {agent.purpose[:80]}...")
            print(f"  - Adapter: {agent.adapter_name}")
            print(f"  - Capabilities: {len(agent.capabilities)} capabilities")
        else:
            print(f"⚠ Configuration file not found: {yaml_path}")
    except Exception as e:
        print(f"✗ Failed to load CEO agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Load LeadershipAgent from YAML
    print("\nTest 2: Loading Leadership agent from YAML...")
    try:
        from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
        
        yaml_path = "config/agents/leadership_agent.yaml"
        if Path(yaml_path).exists():
            agent = LeadershipAgent.from_yaml(yaml_path)
            print(f"✓ Successfully loaded Leadership agent")
            print(f"  - Agent ID: {agent.agent_id}")
            print(f"  - Purpose: {agent.purpose[:80]}...")
            print(f"  - Adapter: {agent.adapter_name}")
        else:
            print(f"⚠ Configuration file not found: {yaml_path}")
    except Exception as e:
        print(f"✗ Failed to load Leadership agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Load CMOAgent from YAML
    print("\nTest 3: Loading CMO agent from YAML...")
    try:
        from AgentOperatingSystem.agents.cmo_agent import CMOAgent
        
        yaml_path = "config/agents/cmo_agent.yaml"
        if Path(yaml_path).exists():
            agent = CMOAgent.from_yaml(yaml_path)
            print(f"✓ Successfully loaded CMO agent")
            print(f"  - Agent ID: {agent.agent_id}")
            print(f"  - Marketing Purpose: {agent.marketing_purpose[:60]}...")
            print(f"  - Leadership Purpose: {agent.leadership_purpose[:60]}...")
            print(f"  - Marketing Adapter: {agent.marketing_adapter_name}")
            print(f"  - Leadership Adapter: {agent.leadership_adapter_name}")
            
            # Test adapter retrieval
            marketing_adapter = agent.get_adapter_for_purpose("marketing")
            leadership_adapter = agent.get_adapter_for_purpose("leadership")
            print(f"  - Adapter for 'marketing': {marketing_adapter}")
            print(f"  - Adapter for 'leadership': {leadership_adapter}")
        else:
            print(f"⚠ Configuration file not found: {yaml_path}")
    except Exception as e:
        print(f"✗ Failed to load CMO agent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Backward compatibility - code-based creation
    print("\nTest 4: Backward compatibility test...")
    try:
        from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
        
        agent = PurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Strategic oversight and company growth",
            purpose_scope="Strategic planning, major decisions",
            adapter_name="ceo"
        )
        print(f"✓ Successfully created agent using code-based approach")
        print(f"  - Agent ID: {agent.agent_id}")
        print(f"  - Purpose: {agent.purpose}")
        print(f"  - Adapter: {agent.adapter_name}")
    except Exception as e:
        print(f"✗ Failed to create agent using code: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Validation tests
    print("\nTest 5: Validation tests...")
    try:
        from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
        
        # Test missing file
        try:
            agent = PurposeDrivenAgent.from_yaml("nonexistent.yaml")
            print(f"✗ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print(f"✓ Correctly raised FileNotFoundError for missing file")
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_yaml_loading()
    sys.exit(0 if success else 1)
