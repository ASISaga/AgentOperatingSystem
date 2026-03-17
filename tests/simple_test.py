"""
Simple AOS test to ensure core imports and initialization work.
"""
from AgentOperatingSystem.config.aos import AOSConfig
from AgentOperatingSystem.agents import GenericPurposeDrivenAgent
from AgentOperatingSystem.messaging.types import Message, MessageType
from AgentOperatingSystem.config.storage import StorageConfig


class TestBasicImports:
    """Verify that core AOS components can be imported and instantiated."""

    def test_configuration(self):
        config = AOSConfig()
        assert config is not None

    def test_generic_agent_creation(self):
        agent = GenericPurposeDrivenAgent(
            agent_id="test",
            purpose="Test purpose",
            adapter_name="test",
        )
        assert agent is not None
        assert agent.agent_id == "test"

    def test_message_types_importable(self):
        assert Message is not None
        assert MessageType is not None

    def test_storage_config(self):
        config = StorageConfig()
        assert config is not None