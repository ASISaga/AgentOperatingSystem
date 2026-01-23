"""
Extensibility features for AgentOperatingSystem

Provides plugin framework, schema registry, and enhanced agent registry
for platform extensibility and evolution.
"""

from .enhanced_agent_registry import (
    AgentCapability,
    AgentDependency,
    AgentHealth,
    AgentHealthCheck,
    AgentUpgradeStatus,
    EnhancedAgentRegistry,
)
from .plugin_framework import (
    ConnectorPlugin,
    MessageTypePlugin,
    Plugin,
    PluginRegistry,
    PluginStatus,
    PluginType,
    PolicyPlugin,
)
from .schema_registry import (
    CompatibilityMode,
    SchemaMigration,
    SchemaRegistry,
    SchemaStatus,
    SchemaVersion,
)

__all__ = [
    # Plugin Framework
    "Plugin",
    "PolicyPlugin",
    "ConnectorPlugin",
    "MessageTypePlugin",
    "PluginRegistry",
    "PluginType",
    "PluginStatus",

    # Schema Registry
    "SchemaRegistry",
    "SchemaVersion",
    "SchemaMigration",
    "SchemaStatus",
    "CompatibilityMode",

    # Enhanced Agent Registry
    "EnhancedAgentRegistry",
    "AgentCapability",
    "AgentDependency",
    "AgentHealthCheck",
    "AgentHealth",
    "AgentUpgradeStatus",
]
