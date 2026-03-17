"""
Integration tests for AOS Learning System.
"""
import pytest

from AgentOperatingSystem.agent_operating_system import AgentOperatingSystem
from AgentOperatingSystem.agents import LeadershipAgent

try:
    from AgentOperatingSystem.learning import SelfLearningAgent
    SELF_LEARNING_AVAILABLE = True
except ImportError:
    SELF_LEARNING_AVAILABLE = False


class TestAOSIntegration:
    """Integration tests for core AOS components."""

    @pytest.fixture
    async def aos(self):
        """Create and start an AOS instance."""
        aos = AgentOperatingSystem()
        await aos.start()
        yield aos
        await aos.stop()

    async def test_aos_initialization(self):
        """Test that AOS can be initialized."""
        aos = AgentOperatingSystem()
        assert aos is not None

    async def test_aos_startup_shutdown(self):
        """Test AOS start/stop lifecycle."""
        aos = AgentOperatingSystem()
        await aos.start()
        await aos.stop()

    async def test_core_components_loaded(self, aos):
        """Test that core AOS components are loaded."""
        core_components = ['agents', 'message_bus', 'orchestration_engine', 'decision_engine']
        for component in core_components:
            assert hasattr(aos, component), f"Missing core component: {component}"

    async def test_leadership_agent_registration(self, aos):
        """Test creating and registering a LeadershipAgent."""
        leader = LeadershipAgent('leader_agent', 'Test Leader', 'CEO')
        success = await aos.register_agent(leader)
        assert success, "LeadershipAgent registration failed"

    async def test_learning_components_loaded(self, aos):
        """Test that learning components are available."""
        assert hasattr(aos, 'knowledge_manager'), "Missing knowledge_manager"
        assert hasattr(aos, 'rag_engine'), "Missing rag_engine"

    @pytest.mark.skipif(not SELF_LEARNING_AVAILABLE, reason="SelfLearningAgent not available")
    async def test_self_learning_agent(self, aos):
        """Test SelfLearningAgent creation and registration."""
        agent = SelfLearningAgent('test_agent', domains=['general'])
        success = await aos.register_agent(agent)
        assert success, "SelfLearningAgent registration failed"
        assert hasattr(agent, 'handle_user_request')
        assert hasattr(agent, 'add_domain_knowledge')