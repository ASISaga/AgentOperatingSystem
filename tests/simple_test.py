"""
Simple AOS Test Runner

Basic test to ensure AOS can be imported and initialized.
"""
import sys
import os
import asyncio

# Add the parent directory to Python path so we can import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

async def simple_test():
    """Simple test that doesn't rely on complex imports"""
    print("🚀 Simple AOS Test")
    print("=" * 30)
    
    try:
        # Test basic import
        print("📦 Testing imports...")
        
        # Test configuration
        from AgentOperatingSystem.config.aos import AOSConfig
        config = AOSConfig()
        print("✅ Configuration: SUCCESS")
        
        # Test base agent
        from AgentOperatingSystem.agents.base import BaseAgent, Agent
        agent = Agent(agent_id="test", name="Test Agent")
        print("✅ Base Agent: SUCCESS")
        
        # Test message types
        from AgentOperatingSystem.messaging.types import Message, MessageType
        print("✅ Message Types: SUCCESS")
        
        # Test storage config
        from AgentOperatingSystem.config.storage import StorageConfig
        storage_config = StorageConfig()
        print("✅ Storage Config: SUCCESS")
        
        print("=" * 30)
        print("✅ All basic tests PASSED!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())