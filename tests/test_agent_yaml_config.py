"""
Tests for Agent YAML Configuration

This test suite validates the YAML configuration loading functionality
for PurposeDrivenAgent, LeadershipAgent, and CMOAgent.
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Direct imports to avoid package initialization issues
from AgentOperatingSystem.agents.purpose_driven import PurposeDrivenAgent
from AgentOperatingSystem.agents.leadership_agent import LeadershipAgent
from AgentOperatingSystem.agents.cmo_agent import CMOAgent


class TestAgentYAMLConfiguration:
    """Test agent YAML configuration loading"""
    
    @pytest.mark.asyncio
    async def test_load_ceo_agent_from_yaml(self):
        """
        Test loading a single-purpose CEO agent from YAML configuration.
        """
        yaml_path = "config/agents/ceo_agent.yaml"
        
        # Check if file exists
        if not Path(yaml_path).exists():
            pytest.skip(f"Configuration file {yaml_path} not found")
        
        # Load agent from YAML
        agent = PurposeDrivenAgent.from_yaml(yaml_path)
        
        # Verify agent was created correctly
        assert agent.agent_id == "ceo"
        assert agent.purpose is not None
        assert "Strategic oversight" in agent.purpose
        assert agent.adapter_name is not None
        
        # Verify YAML-specific attributes
        assert hasattr(agent, 'capabilities')
        assert hasattr(agent, 'mcp_tools_config')
        
        # Initialize and verify
        assert await agent.initialize()
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_load_leadership_agent_from_yaml(self):
        """
        Test loading a LeadershipAgent from YAML configuration.
        """
        yaml_path = "config/agents/leadership_agent.yaml"
        
        if not Path(yaml_path).exists():
            pytest.skip(f"Configuration file {yaml_path} not found")
        
        # Load agent from YAML
        agent = LeadershipAgent.from_yaml(yaml_path)
        
        # Verify agent was created correctly
        assert agent.agent_id == "leader"
        assert "Leadership" in agent.purpose
        assert agent.adapter_name == "leadership"
        
        # Initialize and verify
        assert await agent.initialize()
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_load_cmo_agent_from_yaml(self):
        """
        Test loading a multi-purpose CMO agent from YAML configuration.
        """
        yaml_path = "config/agents/cmo_agent.yaml"
        
        if not Path(yaml_path).exists():
            pytest.skip(f"Configuration file {yaml_path} not found")
        
        # Load agent from YAML
        agent = CMOAgent.from_yaml(yaml_path)
        
        # Verify agent was created correctly
        assert agent.agent_id == "cmo"
        assert agent.marketing_purpose is not None
        assert agent.leadership_purpose is not None
        
        # Verify purpose-to-adapter mappings
        assert agent.purpose_adapter_mapping["marketing"] == "marketing"
        assert agent.purpose_adapter_mapping["leadership"] == "leadership"
        
        # Verify adapter retrieval
        assert agent.get_adapter_for_purpose("marketing") == "marketing"
        assert agent.get_adapter_for_purpose("leadership") == "leadership"
        
        # Initialize and verify
        assert await agent.initialize()
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_yaml_validation_missing_file(self):
        """
        Test that loading from a non-existent YAML file raises appropriate error.
        """
        with pytest.raises(FileNotFoundError):
            PurposeDrivenAgent.from_yaml("config/agents/nonexistent.yaml")
    
    @pytest.mark.asyncio
    async def test_yaml_validation_invalid_yaml(self, tmp_path):
        """
        Test that loading from an invalid YAML file raises appropriate error.
        """
        # Create invalid YAML file
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [unclosed")
        
        with pytest.raises(ValueError):
            PurposeDrivenAgent.from_yaml(str(invalid_yaml))
    
    @pytest.mark.asyncio
    async def test_yaml_validation_missing_agent_id(self, tmp_path):
        """
        Test that loading YAML without agent_id raises appropriate error.
        """
        # Create YAML without agent_id
        incomplete_yaml = tmp_path / "incomplete.yaml"
        incomplete_yaml.write_text("""
name: Test Agent
purposes:
  - name: test
    description: Test purpose
""")
        
        with pytest.raises(ValueError, match="agent_id"):
            PurposeDrivenAgent.from_yaml(str(incomplete_yaml))
    
    @pytest.mark.asyncio
    async def test_backward_compatibility_code_based_creation(self):
        """
        Test that agents can still be created using code-based approach.
        This ensures backward compatibility.
        """
        # Create agent the traditional way
        agent = PurposeDrivenAgent(
            agent_id="test_ceo",
            purpose="Strategic oversight and company growth",
            purpose_scope="Strategic planning, major decisions",
            adapter_name="ceo"
        )
        
        # Verify agent works
        assert agent.agent_id == "test_ceo"
        assert agent.purpose == "Strategic oversight and company growth"
        assert agent.adapter_name == "ceo"
        
        # Initialize and verify
        assert await agent.initialize()
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_multi_purpose_agent_adapter_switching(self):
        """
        Test that multi-purpose agents can switch between adapters.
        """
        yaml_path = "config/agents/cmo_agent.yaml"
        
        if not Path(yaml_path).exists():
            pytest.skip(f"Configuration file {yaml_path} not found")
        
        agent = CMOAgent.from_yaml(yaml_path)
        await agent.initialize()
        
        # Test adapter retrieval for different purposes
        marketing_adapter = agent.get_adapter_for_purpose("marketing")
        leadership_adapter = agent.get_adapter_for_purpose("leadership")
        
        assert marketing_adapter == "marketing"
        assert leadership_adapter == "leadership"
        
        # Test invalid purpose type
        with pytest.raises(ValueError):
            agent.get_adapter_for_purpose("invalid_purpose")
        
        # Clean up
        await agent.stop()
    
    @pytest.mark.asyncio
    async def test_yaml_loaded_agent_status(self):
        """
        Test that YAML-loaded agents report complete status.
        """
        yaml_path = "config/agents/cmo_agent.yaml"
        
        if not Path(yaml_path).exists():
            pytest.skip(f"Configuration file {yaml_path} not found")
        
        agent = CMOAgent.from_yaml(yaml_path)
        await agent.initialize()
        
        # Get agent status
        status = await agent.get_status()
        
        # Verify status contains expected fields
        assert "agent_id" in status
        assert "agent_type" in status
        assert "purposes" in status
        assert "purpose_adapter_mapping" in status
        
        # Verify purpose mappings in status
        assert "marketing" in status["purposes"]
        assert "leadership" in status["purposes"]
        
        # Clean up
        await agent.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
