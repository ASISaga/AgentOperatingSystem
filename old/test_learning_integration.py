"""
Test script to verify AOS Learning System integration
"""

import asyncio
import logging
from aos import (
    AgentOperatingSystem, 
    SelfLearningAgent, 
    SelfLearningStatefulAgent,
    AOSConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_learning_system():
    """Test the integrated learning system"""
    print("🚀 Testing AOS Learning System Integration...")
    
    # Create AOS instance with learning enabled
    config = AOSConfig()
    config.learning_config.enable_rag = False  # Disable RAG for simple test
    
    aos = AgentOperatingSystem(config)
    
    try:
        # Start AOS
        print("\\n📍 Starting AOS...")
        await aos.start()
        
        # Create a self-learning agent
        print("\\n🤖 Creating Self-Learning Agent...")
        agent = SelfLearningAgent(
            agent_id="test_agent_001",
            name="Test Learning Agent",
            domains=["sales", "general"],
            config={"test_mode": True},
            learning_config={"enable_rag": False, "enable_interaction_learning": True}
        )
        
        # Register agent
        print("\\n📝 Registering agent with AOS...")
        success = await aos.register_agent(agent)
        print(f"Agent registration: {'✅ Success' if success else '❌ Failed'}")
        
        # Start agent
        await agent.start()
        
        # Test learning capabilities
        print("\\n🧠 Testing learning capabilities...")
        
        # Test user request handling
        response = await agent.handle_user_request(
            user_input="How can I improve my sales conversion rate?",
            domain="sales",
            conversation_id="test_conv_001"
        )
        
        print("\\n📊 User Request Response:")
        print(f"Success: {response.get('success')}")
        print(f"Domain: {response.get('domain')}")
        print(f"Response: {response.get('response', '')[:200]}...")
        
        # Test interaction rating
        rating_result = await agent.rate_interaction(
            conversation_id="test_conv_001",
            rating=4.5,
            feedback="Very helpful response about sales conversion"
        )
        
        print("\\n⭐ Interaction Rating:")
        print(f"Success: {rating_result.get('success')}")
        print(f"Rating: {rating_result.get('rating')}")
        
        # Test agent status
        status = await agent.get_status()
        print("\\n📈 Agent Status:")
        print(f"Agent ID: {status.get('agent_id')}")
        print(f"Learning Enabled: {status.get('learning', {}).get('learning_enabled')}")
        print(f"Domains: {status.get('learning', {}).get('domains')}")
        print(f"Active Conversations: {status.get('learning', {}).get('active_conversations')}")
        
        # Test domain knowledge addition
        knowledge_success = await agent.add_domain_knowledge(
            domain="sales",
            knowledge_entry={
                "content": "Follow-up within 24 hours significantly improves conversion rates",
                "type": "best_practice",
                "source": "test_data"
            }
        )
        print(f"\\n📚 Knowledge Addition: {'✅ Success' if knowledge_success else '❌ Failed'}")
        
        # Test domain insights
        insights = await agent.get_domain_insights("sales")
        print("\\n🔍 Domain Insights:")
        print(f"Domain: {insights.get('domain')}")
        print(f"Agent ID: {insights.get('agent_id')}")
        
        print("\\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        logger.exception("Test execution failed")
        
    finally:
        # Cleanup
        print("\\n🧹 Cleaning up...")
        await aos.stop()
        print("AOS stopped successfully")

async def test_stateful_learning_agent():
    """Test the stateful learning agent"""
    print("\\n🚀 Testing Stateful Learning Agent...")
    
    config = AOSConfig()
    config.learning_config.enable_rag = False  # Disable RAG for simple test
    
    aos = AgentOperatingSystem(config)
    
    try:
        await aos.start()
        
        # Create stateful learning agent
        stateful_agent = SelfLearningStatefulAgent(
            agent_id="stateful_agent_001",
            name="Test Stateful Learning Agent",
            domains=["leadership"],
            config={"test_mode": True}
        )
        
        await aos.register_agent(stateful_agent)
        await stateful_agent.start()
        
        # Test interaction
        response = await stateful_agent.handle_user_request(
            "What are the key principles of effective leadership?",
            domain="leadership",
            conversation_id="stateful_conv_001"
        )
        
        print("\\n📊 Stateful Agent Response:")
        print(f"Success: {response.get('success')}")
        print(f"Response: {response.get('response', '')[:200]}...")
        
        # Check state
        state = stateful_agent.get_state()
        print("\\n📈 Agent State:")
        print(f"Last Interaction: {state.get('last_interaction')}")
        print(f"Learning State: {state.get('learning_state', {})}")
        
        # Test learning metrics
        metrics = stateful_agent.get_learning_metrics()
        print("\\n📊 Learning Metrics:")
        print(f"Total Interactions: {metrics.get('total_interactions')}")
        print(f"Success Rate: {metrics.get('success_rate'):.2%}")
        
        print("\\n✅ Stateful agent test completed!")
        
    except Exception as e:
        print(f"\\n❌ Stateful agent test failed: {e}")
        logger.exception("Stateful agent test failed")
        
    finally:
        await aos.stop()

if __name__ == "__main__":
    print("=" * 60)
    print("🧠 AOS LEARNING SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    # Run basic learning system test
    asyncio.run(test_learning_system())
    
    print("\\n" + "=" * 60)
    
    # Run stateful learning agent test
    asyncio.run(test_stateful_learning_agent())
    
    print("\\n" + "=" * 60)
    print("🎉 Integration testing completed!")
    print("=" * 60)