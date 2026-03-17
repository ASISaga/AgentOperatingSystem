"""
Tests for the Extensibility Features

Tests the plugin framework, schema registry, and enhanced agent registry.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import asyncio
from datetime import datetime

from AgentOperatingSystem.extensibility import (
    Plugin,
    PolicyPlugin,
    PluginRegistry,
    PluginType,
    PluginStatus,
    SchemaRegistry,
    SchemaStatus,
    CompatibilityMode,
    EnhancedAgentRegistry,
    AgentCapability,
    AgentHealth,
    AgentUpgradeStatus
)


# Sample plugin implementations for testing
class TestPolicyPlugin(PolicyPlugin):
    """Test policy plugin"""
    
    async def initialize(self) -> bool:
        return True
    
    async def shutdown(self) -> bool:
        return True
    
    def get_capabilities(self) -> list:
        return ["test_policy_evaluation"]
    
    async def evaluate_policy(self, context: dict) -> dict:
        return {"allowed": True, "rationale": "Test policy"}


class TestPluginRegistry:
    """Test the PluginRegistry"""
    
    def test_register_plugin(self):
        """Test plugin registration"""
        registry = PluginRegistry()
        
        plugin = TestPolicyPlugin(
            plugin_id="test_policy_1",
            name="Test Policy",
            version="1.0.0"
        )
        
        success = registry.register_plugin(
            plugin=plugin,
            plugin_type=PluginType.POLICY,
            metadata={"author": "test"}
        )
        
        assert success
        assert plugin.plugin_id in registry.plugins
        assert plugin.status == PluginStatus.REGISTERED
    
    @pytest.mark.asyncio
    async def test_load_and_activate_plugin(self):
        """Test plugin loading and activation"""
        registry = PluginRegistry()
        
        plugin = TestPolicyPlugin(
            plugin_id="test_policy_2",
            name="Test Policy 2",
            version="1.0.0"
        )
        
        registry.register_plugin(plugin, PluginType.POLICY)
        
        # Load plugin
        load_success = await registry.load_plugin("test_policy_2")
        assert load_success
        assert plugin.status == PluginStatus.LOADED
        
        # Activate plugin
        activate_success = await registry.activate_plugin("test_policy_2")
        assert activate_success
        assert plugin.status == PluginStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_get_plugins_by_type(self):
        """Test getting plugins by type"""
        registry = PluginRegistry()
        
        policy_plugin = TestPolicyPlugin(
            plugin_id="policy_1",
            name="Policy Plugin",
            version="1.0.0"
        )
        
        registry.register_plugin(policy_plugin, PluginType.POLICY)
        
        policy_plugins = registry.get_plugins_by_type(PluginType.POLICY)
        assert len(policy_plugins) == 1
        assert policy_plugins[0].plugin_id == "policy_1"


class TestSchemaRegistry:
    """Test the SchemaRegistry"""
    
    def test_register_and_get_schema(self):
        """Test schema registration and retrieval"""
        registry = SchemaRegistry()
        
        schema_def = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"}
            },
            "required": ["field1"]
        }
        
        success = registry.register_schema(
            schema_id="TestSchema",
            version_str="1.0.0",
            schema_definition=schema_def,
            compatibility_mode=CompatibilityMode.BACKWARD
        )
        
        assert success
        
        schema = registry.get_schema("TestSchema", "1.0.0")
        assert schema is not None
        assert schema.version_str == "1.0.0"
        assert schema.status == SchemaStatus.DRAFT
    
    def test_activate_and_deprecate_schema(self):
        """Test schema lifecycle"""
        registry = SchemaRegistry()
        
        schema_def = {"type": "object"}
        registry.register_schema("TestSchema", "1.0.0", schema_def)
        
        # Activate
        activate_success = registry.activate_schema("TestSchema", "1.0.0")
        assert activate_success
        
        schema = registry.get_schema("TestSchema", "1.0.0")
        assert schema.status == SchemaStatus.ACTIVE
        
        # Deprecate
        deprecate_success = registry.deprecate_schema("TestSchema", "1.0.0")
        assert deprecate_success
        
        schema = registry.get_schema("TestSchema", "1.0.0")
        assert schema.status == SchemaStatus.DEPRECATED
    
    def test_check_compatibility(self):
        """Test schema compatibility checking"""
        registry = SchemaRegistry()
        
        # Version 1.0.0
        schema_v1 = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"}
            },
            "required": ["field1"]
        }
        
        # Version 2.0.0 - backward compatible
        schema_v2 = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "string"}
            },
            "required": ["field1"]
        }
        
        registry.register_schema("TestSchema", "1.0.0", schema_v1)
        registry.register_schema("TestSchema", "2.0.0", schema_v2)
        
        compatibility = registry.check_compatibility("TestSchema", "1.0.0", "2.0.0")
        
        assert compatibility["compatible"] is True
        assert compatibility["compatibility_mode"] == CompatibilityMode.BACKWARD.value
    
    def test_add_migration(self):
        """Test adding migration path"""
        registry = SchemaRegistry()
        
        schema_v1 = {"type": "object"}
        schema_v2 = {"type": "object"}
        
        registry.register_schema("TestSchema", "1.0.0", schema_v1)
        registry.register_schema("TestSchema", "2.0.0", schema_v2)
        
        success = registry.add_migration(
            schema_id="TestSchema",
            from_version="1.0.0",
            to_version="2.0.0",
            guidance="Migrate by adding optional field2"
        )
        
        assert success
        
        migration_path = registry.get_migration_path("TestSchema", "1.0.0", "2.0.0")
        assert migration_path is not None
        assert len(migration_path) == 1


class TestEnhancedAgentRegistry:
    """Test the EnhancedAgentRegistry"""
    
    @pytest.mark.asyncio
    async def test_register_and_discover_capability(self):
        """Test capability registration and discovery"""
        registry = EnhancedAgentRegistry()
        
        capability = AgentCapability(
            capability_id="cap_1",
            name="decision_making",
            description="Makes decisions",
            version="1.0.0"
        )
        
        success = await registry.register_capability("agent_1", capability)
        assert success
        
        # Discover agents with this capability
        agents = await registry.discover_capabilities("decision_making")
        assert len(agents) == 1
        assert agents[0]["agent_id"] == "agent_1"
    
    @pytest.mark.asyncio
    async def test_dependency_management(self):
        """Test dependency tracking"""
        registry = EnhancedAgentRegistry()
        
        # Add dependency
        success = await registry.add_dependency(
            dependent_agent_id="agent_1",
            dependency_agent_id="agent_2",
            dependency_type="runtime",
            required=True
        )
        assert success
        
        # Get dependencies
        deps = await registry.get_dependencies("agent_1")
        assert len(deps) == 1
        assert deps[0]["dependency_agent_id"] == "agent_2"
        
        # Get dependents
        dependents = await registry.get_dependents("agent_2")
        assert len(dependents) == 1
        assert dependents[0] == "agent_1"
    
    @pytest.mark.asyncio
    async def test_dependency_tree(self):
        """Test dependency tree generation"""
        registry = EnhancedAgentRegistry()
        
        # Create a dependency chain: agent_1 -> agent_2 -> agent_3
        await registry.add_dependency("agent_1", "agent_2")
        await registry.add_dependency("agent_2", "agent_3")
        
        tree = await registry.get_dependency_tree("agent_1")
        
        assert tree["agent_id"] == "agent_1"
        assert len(tree["dependencies"]) == 1
        assert tree["dependencies"][0]["tree"]["agent_id"] == "agent_2"
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test health status tracking"""
        registry = EnhancedAgentRegistry()
        
        # Record health check
        success = await registry.record_health_check(
            agent_id="agent_1",
            status=AgentHealth.HEALTHY,
            checks_passed=5,
            checks_failed=0
        )
        assert success
        
        # Get health status
        health = await registry.get_health_status("agent_1")
        assert health is not None
        assert health["status"] == AgentHealth.HEALTHY.value
        assert health["checks_passed"] == 5
        
        # Record unhealthy status
        await registry.record_health_check(
            agent_id="agent_2",
            status=AgentHealth.UNHEALTHY,
            checks_passed=2,
            checks_failed=3
        )
        
        # Get unhealthy agents
        unhealthy = await registry.get_unhealthy_agents()
        assert len(unhealthy) == 1
        assert unhealthy[0]["agent_id"] == "agent_2"
    
    @pytest.mark.asyncio
    async def test_upgrade_orchestration(self):
        """Test upgrade status and orchestration"""
        registry = EnhancedAgentRegistry()
        
        # Set upgrade status
        await registry.set_upgrade_status(
            agent_id="agent_1",
            status=AgentUpgradeStatus.UPDATE_AVAILABLE,
            available_versions=["2.0.0", "2.1.0"]
        )
        
        # Get agents needing upgrade
        agents = await registry.get_agents_needing_upgrade()
        assert len(agents) == 1
        assert agents[0]["agent_id"] == "agent_1"
        
        # Orchestrate upgrade
        result = await registry.orchestrate_upgrade("agent_1", "2.0.0")
        assert result["status"] == "completed"
        
        # Verify status changed
        status = await registry.get_upgrade_status("agent_1")
        assert status == AgentUpgradeStatus.CURRENT.value
    
    def test_registry_summary(self):
        """Test registry summary generation"""
        registry = EnhancedAgentRegistry()
        
        summary = registry.get_registry_summary()
        
        assert "total_agents" in summary
        assert "total_capabilities" in summary
        assert "total_dependencies" in summary
        assert "health_summary" in summary
        assert "upgrade_summary" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
