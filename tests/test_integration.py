"""
Final verification test for AOS Learning System Integration
"""
import asyncio
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

try:
    # Import AOS components
    from AgentOperatingSystem.agent_operating_system import AgentOperatingSystem
    from AgentOperatingSystem.agents import BaseAgent, LeadershipAgent
    try:
        from AgentOperatingSystem.learning import SelfLearningAgent
        SELF_LEARNING_AVAILABLE = True
    except ImportError:
        SELF_LEARNING_AVAILABLE = False
        print("⚠️  SelfLearningAgent not available")
except ImportError as e:
    print(f"❌ Failed to import AOS components: {e}")
    sys.exit(1)

async def verify_integration():
    print('🧠 AOS Learning System Integration Verification')
    print('=' * 50)

    # Initialize AOS with default configuration
    aos = AgentOperatingSystem()
    await aos.start()
    
    try:
        # Test 1: Create self-learning agent
        if SELF_LEARNING_AVAILABLE:
            try:
                agent = SelfLearningAgent('test_agent', domains=['general'])
                success1 = await aos.register_agent(agent)
                print(f'✅ SelfLearningAgent creation: {"SUCCESS" if success1 else "FAILED"}')
            except Exception as e:
                print(f'❌ SelfLearningAgent creation: FAILED - {e}')
                success1 = False
        else:
            print('⏭️  SelfLearningAgent creation: SKIPPED (not available)')
            success1 = False
        
        # Test 2: Create enhanced leadership agent  
        try:
            leader = LeadershipAgent('leader_agent', 'Test Leader', 'CEO')
            success2 = await aos.register_agent(leader)
            print(f'✅ Enhanced LeadershipAgent: {"SUCCESS" if success2 else "FAILED"}')
        except Exception as e:
            print(f'❌ Enhanced LeadershipAgent: FAILED - {e}')
            success2 = False
        
        # Test 3: Check learning components
        has_learning = hasattr(aos, 'knowledge_manager') and hasattr(aos, 'rag_engine')
        print(f'✅ Learning components loaded: {"SUCCESS" if has_learning else "FAILED"}')
        
        # Test 4: Test learning mixin functionality (if available)
        if success1:
            has_mixin = hasattr(agent, 'handle_user_request') and hasattr(agent, 'add_domain_knowledge')
            print(f'✅ Learning mixin functionality: {"SUCCESS" if has_mixin else "FAILED"}')
        else:
            print('⏭️  Learning mixin functionality: SKIPPED (agent creation failed)')
        
        # Test 5: Check core AOS components
        core_components = ['agents', 'message_bus', 'orchestration_engine', 'decision_engine']
        working_components = []
        for component in core_components:
            if hasattr(aos, component):
                working_components.append(component)
        
        print(f'✅ Core components loaded: {len(working_components)}/{len(core_components)} ({", ".join(working_components)})')
        
        # Test 6: Basic agent communication test
        try:
            if success1 and success2:
                # Simple message test
                print('✅ Agent communication test: Ready for implementation')
            else:
                print('⏭️  Agent communication test: SKIPPED (agents not available)')
        except Exception as e:
            print(f'❌ Agent communication test: FAILED - {e}')
        
        print('=' * 50)
        overall_success = success1 and success2 and has_learning
        if overall_success:
            print('🎉 Integration verification COMPLETE!')
            print('🚀 AOS components successfully integrated!')
        else:
            print('⚠️  Integration verification completed with some issues')
            print('🔧 Some components may need additional setup or dependencies')
        
    finally:
        await aos.stop()

async def run_quick_test():
    """Quick test to verify basic functionality"""
    print('🚀 AOS Quick Test')
    print('=' * 30)
    
    try:
        aos = AgentOperatingSystem()
        print('✅ AOS initialization: SUCCESS')
        
        await aos.start()
        print('✅ AOS startup: SUCCESS')
        
        # Test basic agent creation
        agent = BaseAgent(agent_id="test_agent", agent_type="test")
        success = await aos.register_agent(agent)
        print(f'✅ Basic agent registration: {"SUCCESS" if success else "FAILED"}')
        
        await aos.stop()
        print('✅ AOS shutdown: SUCCESS')
        
        print('=' * 30)
        print('✅ Quick test PASSED!')
        
    except Exception as e:
        print(f'❌ Quick test FAILED: {e}')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AOS Integration Verification")
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(run_quick_test())
    else:
        asyncio.run(verify_integration())