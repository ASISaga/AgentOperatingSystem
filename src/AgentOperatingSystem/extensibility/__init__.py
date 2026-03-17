"""
Extensibility features for AgentOperatingSystem

Provides plugin framework, schema registry, and enhanced agent registry
for platform extensibility and evolution.
"""

from .plugin_framework import (
    Plugin,
    PolicyPlugin,
    ConnectorPlugin,
    MessageTypePlugin,
    PluginRegistry,
    PluginType,
    PluginStatus
)
from .schema_registry import (
    SchemaRegistry,
    SchemaVersion,
    SchemaMigration,
    SchemaStatus,
    CompatibilityMode
)
from .enhanced_agent_registry import (
    EnhancedAgentRegistry,
    AgentCapability,
    AgentDependency,
    AgentHealthCheck,
    AgentHealth,
    AgentUpgradeStatus
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
