"""
Test that get_agent_type() returns list of personas/skills.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Temporarily disable package __init__ to avoid import errors
init_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'AgentOperatingSystem', '__init__.py')
init_backup = init_file + '.test_backup'

try:
    import shutil
    if os.path.exists(init_file):
        shutil.copy(init_file, init_backup)
        with open(init_file, 'w') as f:
            f.write('# Temporarily disabled for testing\n')
    
    # Mock dependencies
    import types
    from typing import List
    
    # Mock ml module
    ml_module = types.ModuleType('ml')
    pipeline_ops_module = types.ModuleType('pipeline_ops')
    
    async def mock_func(*args, **kwargs):
        return {}
    
    pipeline_ops_module.trigger_lora_training = mock_func
    pipeline_ops_module.run_azure_ml_pipeline = mock_func
    pipeline_ops_module.aml_infer = mock_func
    ml_module.pipeline_ops = pipeline_ops_module
    
    # Mock mcp module
    mcp_module = types.ModuleType('mcp')
    
    class MockContextMCPServer:
        def __init__(self, agent_id, config=None):
            pass
        async def initialize(self):
            pass
        async def get_context(self, key):
            return None
        async def set_context(self, key, value):
            pass
        async def get_all_context(self):
            return {}
        async def add_memory(self, memory):
            pass
    
    context_server_module = types.ModuleType('context_server')
    context_server_module.ContextMCPServer = MockContextMCPServer
    mcp_module.context_server = context_server_module
    
    # Add to sys.modules
    sys.modules['AgentOperatingSystem'] = types.ModuleType('AgentOperatingSystem')
    sys.modules['AgentOperatingSystem.ml'] = ml_module
    sys.modules['AgentOperatingSystem.ml.pipeline_ops'] = pipeline_ops_module
    sys.modules['AgentOperatingSystem.mcp'] = mcp_module
    sys.modules['AgentOperatingSystem.mcp.context_server'] = context_server_module
    
    # Now import
    from AgentOperatingSystem.agents.purpose_driven import GenericPurposeDrivenAgent
    from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
    from AgentOperatingSystem.agents.cmo_agent import CMOAgent
    
    print("=" * 60)
    print("Testing Agent Personas/Skills")
    print("=" * 60)
    
    # Test GenericPurposeDrivenAgent
    print("\n1. GenericPurposeDrivenAgent:")
    agent1 = GenericPurposeDrivenAgent(
        agent_id="test1",
        purpose="General tasks",
        adapter_name="general"
    )
    types1 = agent1.get_agent_type()
    print(f"   Personas: {types1}")
    assert isinstance(types1, list), "Should return a list"
    assert types1 == ["generic"], f"Expected ['generic'], got {types1}"
    print("   ✅ Returns ['generic']")
    
    # Test LeadershipAgent
    print("\n2. LeadershipAgent:")
    agent2 = LeadershipAgent(
        agent_id="test2",
        purpose="Leadership tasks",
        adapter_name="leadership"
    )
    types2 = agent2.get_agent_type()
    print(f"   Personas: {types2}")
    assert isinstance(types2, list), "Should return a list"
    assert types2 == ["leadership"], f"Expected ['leadership'], got {types2}"
    print("   ✅ Returns ['leadership']")
    
    # Test CMOAgent
    print("\n3. CMOAgent (Marketing + Leadership):")
    agent3 = CMOAgent(
        agent_id="test3",
        marketing_adapter_name="marketing",
        leadership_adapter_name="leadership"
    )
    types3 = agent3.get_agent_type()
    print(f"   Personas: {types3}")
    assert isinstance(types3, list), "Should return a list"
    assert types3 == ["marketing", "leadership"], f"Expected ['marketing', 'leadership'], got {types3}"
    print("   ✅ Returns ['marketing', 'leadership']")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\nKey Changes:")
    print("  • get_agent_type() now returns List[str] instead of str")
    print("  • CMO properly returns both personas: ['marketing', 'leadership']")
    print("  • Each agent can have multiple personas/skills")

finally:
    # Restore original __init__.py
    if os.path.exists(init_backup):
        shutil.move(init_backup, init_file)
