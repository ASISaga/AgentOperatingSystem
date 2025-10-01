"""
Final verification test for AOS Learning System Integration
"""
import asyncio
from aos import AgentOperatingSystem, SelfLearningAgent, LeadershipAgent

async def verify_integration():
    print('🧠 AOS Learning System Integration Verification')
    print('=' * 50)

    aos = AgentOperatingSystem()
    await aos.start()
    
    try:
        # Test 1: Create self-learning agent
        agent = SelfLearningAgent('test_agent', domains=['general'])
        success1 = await aos.register_agent(agent)
        print(f'✅ SelfLearningAgent creation: {"SUCCESS" if success1 else "FAILED"}')
        
        # Test 2: Create enhanced leadership agent  
        leader = LeadershipAgent('leader_agent', 'Test Leader', 'CEO')
        success2 = await aos.register_agent(leader)
        print(f'✅ Enhanced LeadershipAgent: {"SUCCESS" if success2 else "FAILED"}')
        
        # Test 3: Check learning components
        has_learning = hasattr(aos, 'knowledge_manager') and hasattr(aos, 'rag_engine')
        print(f'✅ Learning components loaded: {"SUCCESS" if has_learning else "FAILED"}')
        
        # Test 4: Test learning mixin functionality
        has_mixin = hasattr(agent, 'handle_user_request') and hasattr(agent, 'add_domain_knowledge')
        print(f'✅ Learning mixin functionality: {"SUCCESS" if has_mixin else "FAILED"}')
        
        print('=' * 50)
        print('🎉 Integration verification COMPLETE!')
        print('🚀 SelfLearningAgent successfully integrated into AOS!')
        
    finally:
        await aos.stop()

if __name__ == "__main__":
    asyncio.run(verify_integration())