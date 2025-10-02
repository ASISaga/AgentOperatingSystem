"""
Simple test script to verify basic AOS Learning System integration
"""

import asyncio
import logging
from aos import (
    AgentOperatingSystem, 
    SelfLearningAgent, 
    AOSConfig
)

# Configure logging to show less verbose output
logging.basicConfig(level=logging.ERROR)

async def test_basic_integration():
    """Test basic integration without complex features"""
    print("🚀 Testing Basic AOS Learning System...")
    
    # Create simple AOS configuration
    config = AOSConfig()
    # Disable features that might cause issues
    config.learning_config.enable_rag = False
    config.learning_config.enable_interaction_learning = True
    config.learning_config.enable_learning_pipeline = False
    
    aos = AgentOperatingSystem(config)
    
    try:
        print("📍 Starting AOS...")
        await aos.start()
        print("✅ AOS started successfully")
        
        print("🤖 Creating simple learning agent...")
        agent = SelfLearningAgent(
            agent_id="simple_agent",
            name="Simple Learning Agent",
            domains=["general"],
            learning_config={
                "enable_rag": False,
                "enable_interaction_learning": False
            }
        )
        
        print("📝 Registering agent...")
        success = await aos.register_agent(agent)
        if success:
            print("✅ Agent registered successfully")
        else:
            print("❌ Agent registration failed")
            return
        
        print("🚀 Starting agent...")
        await agent.start()
        print("✅ Agent started successfully")
        
        print("💬 Testing direct response generation...")
        # Test the learning-based response generation directly
        response = await agent._generate_learning_based_response(
            user_input="Hello, how can you help me?",
            domain="general",
            context={
                "purpose": "Provide general assistance",
                "directives": "Be helpful and professional"
            }
        )
        
        print("📊 Response generated:")
        print(f"Length: {len(response)} characters")
        print(f"Preview: {response[:200]}...")
        
        print("📈 Checking agent status...")
        status = await agent.get_status()
        print(f"Agent ID: {status.get('agent_id')}")
        print(f"Type: {status.get('type')}")
        print(f"Running: {status.get('is_running')}")
        
        print("✅ Basic integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("🧹 Cleaning up...")
        await aos.stop()
        print("✅ Cleanup completed")

if __name__ == "__main__":
    print("=" * 50)
    print("🧠 BASIC AOS LEARNING INTEGRATION TEST")
    print("=" * 50)
    
    asyncio.run(test_basic_integration())
    
    print("=" * 50)
    print("🎉 Test completed!")
    print("=" * 50)