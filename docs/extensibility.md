# Extensibility Features Documentation

The AgentOperatingSystem provides comprehensive extensibility features that enable the platform to evolve and adapt to changing requirements without breaking existing functionality.

## Overview

The extensibility features are located in `src/AgentOperatingSystem/extensibility/` and provide three main capabilities:

1. **Plugin Framework** - Hot-swappable plugins for policies, connectors, and message types
2. **Schema Registry** - Central governance for schema versions and migrations
3. **Enhanced Agent Registry** - Advanced agent management with capabilities, dependencies, health monitoring, and upgrades

## Plugin Framework

The plugin framework enables registration and management of custom plugins that can be loaded, activated, and swapped at runtime.

### Plugin Types

```python
from AgentOperatingSystem.extensibility import PluginType

# Available plugin types:
# - POLICY: Policy evaluation and enforcement
# - CONNECTOR: External system integration
# - MESSAGE_TYPE: Custom message types
# - ADAPTER: Custom adapters
# - HANDLER: Custom handlers
# - VALIDATOR: Custom validators
```

### Creating a Policy Plugin

```python
from AgentOperatingSystem.extensibility import PolicyPlugin

class CustomPolicyPlugin(PolicyPlugin):
    """Custom policy for budget approval"""
    
    def __init__(self):
        super().__init__(
            plugin_id="budget_policy_v1",
            name="Budget Approval Policy",
            version="1.0.0"
        )
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        # Load policy rules, connect to data sources, etc.
        self.max_budget = 100000
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the plugin gracefully"""
        # Cleanup resources
        return True
    
    def get_capabilities(self) -> list:
        """Return list of capabilities"""
        return ["budget_evaluation", "threshold_checking"]
    
    async def evaluate_policy(self, context: dict) -> dict:
        """Evaluate policy against context"""
        budget_amount = context.get("amount", 0)
        
        if budget_amount <= self.max_budget:
            return {
                "allowed": True,
                "rationale": f"Budget ${budget_amount} is within limit"
            }
        else:
            return {
                "allowed": False,
                "rationale": f"Budget ${budget_amount} exceeds limit of ${self.max_budget}"
            }
```

### Creating a Connector Plugin

```python
from AgentOperatingSystem.extensibility import ConnectorPlugin

class ERPConnectorPlugin(ConnectorPlugin):
    """Connector for ERP system integration"""
    
    def __init__(self):
        super().__init__(
            plugin_id="erp_connector_v1",
            name="ERP Connector",
            version="1.0.0"
        )
        self.connection = None
    
    async def initialize(self) -> bool:
        """Initialize the connector"""
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the connector"""
        if self.connection:
            await self.disconnect()
        return True
    
    def get_capabilities(self) -> list:
        return ["erp_read", "erp_write"]
    
    async def connect(self, config: dict) -> bool:
        """Establish connection to ERP system"""
        # Connect to ERP system with config
        self.connection = {"host": config.get("host"), "connected": True}
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from ERP system"""
        self.connection = None
        return True
    
    async def send(self, data: dict) -> dict:
        """Send data to ERP system"""
        # Send data and return response
        return {"status": "sent", "record_id": "rec_123"}
    
    async def receive(self) -> dict:
        """Receive data from ERP system"""
        # Receive and return data
        return {"status": "received", "data": {}}
```

### Using the Plugin Registry

```python
from AgentOperatingSystem.extensibility import PluginRegistry, PluginType

# Create registry
registry = PluginRegistry()

# Create and register plugin
policy_plugin = CustomPolicyPlugin()

success = registry.register_plugin(
    plugin=policy_plugin,
    plugin_type=PluginType.POLICY,
    metadata={"author": "dev_team", "category": "finance"}
)

# Load the plugin
await registry.load_plugin("budget_policy_v1")

# Activate the plugin
await registry.activate_plugin("budget_policy_v1")

# Use the plugin
plugin = registry.get_plugin("budget_policy_v1")
result = await plugin.evaluate_policy({"amount": 50000})
print(f"Allowed: {result['allowed']}")

# Deactivate when needed
await registry.deactivate_plugin("budget_policy_v1")

# Hot reload the plugin
await registry.reload_plugin("budget_policy_v1")
```

### Listing and Filtering Plugins

```python
# Get all plugins of a specific type
policy_plugins = registry.get_plugins_by_type(PluginType.POLICY)

# Get all active plugins
active_plugins = registry.get_active_plugins()

# List all plugins with their info
all_plugins = registry.list_plugins()
for plugin_info in all_plugins:
    print(f"{plugin_info['name']} - {plugin_info['status']}")
```

## Schema Registry

The schema registry provides central governance for all message and model schemas with version management and migration support.

### Registering Schemas

```python
from AgentOperatingSystem.extensibility import SchemaRegistry, CompatibilityMode

registry = SchemaRegistry()

# Register version 1.0.0
schema_v1 = {
    "type": "object",
    "properties": {
        "decision_id": {"type": "string"},
        "amount": {"type": "number"},
        "status": {"type": "string"}
    },
    "required": ["decision_id", "amount", "status"]
}

registry.register_schema(
    schema_id="BudgetDecision",
    version_str="1.0.0",
    schema_definition=schema_v1,
    metadata={"created_by": "dev_team"},
    compatibility_mode=CompatibilityMode.BACKWARD
)

# Activate the schema
registry.activate_schema("BudgetDecision", "1.0.0")
```

### Schema Evolution

```python
# Register version 2.0.0 with backward-compatible changes
schema_v2 = {
    "type": "object",
    "properties": {
        "decision_id": {"type": "string"},
        "amount": {"type": "number"},
        "status": {"type": "string"},
        "priority": {"type": "string"},  # New optional field
        "notes": {"type": "string"}      # New optional field
    },
    "required": ["decision_id", "amount", "status"]  # Same required fields
}

registry.register_schema("BudgetDecision", "2.0.0", schema_v2)

# Check compatibility
compatibility = registry.check_compatibility(
    "BudgetDecision", "1.0.0", "2.0.0"
)

if compatibility["compatible"]:
    print("Schema versions are compatible")
    registry.activate_schema("BudgetDecision", "2.0.0")
else:
    print(f"Compatibility issues: {compatibility['issues']}")
```

### Migration Management

```python
# Define migration path
registry.add_migration(
    schema_id="BudgetDecision",
    from_version="1.0.0",
    to_version="2.0.0",
    migration_script="Add default priority='normal' and notes=''",
    guidance="""
    To migrate from v1.0.0 to v2.0.0:
    1. Add priority field with default value 'normal'
    2. Add notes field with empty string
    3. Existing required fields remain unchanged
    """
)

# Get migration path
migration_path = registry.get_migration_path(
    "BudgetDecision", "1.0.0", "2.0.0"
)

if migration_path:
    for migration in migration_path:
        print(f"From: {migration.from_version} To: {migration.to_version}")
        print(f"Guidance: {migration.guidance}")
```

### Schema Lifecycle

```python
# Get latest active version
latest = registry.get_latest_version("BudgetDecision", status=SchemaStatus.ACTIVE)
print(f"Latest version: {latest.version_str}")

# List all versions
versions = registry.list_versions("BudgetDecision")
for version in versions:
    print(f"v{version.version_str} - {version.status.value}")

# Deprecate old version
registry.deprecate_schema("BudgetDecision", "1.0.0")

# Eventually retire it
registry.retire_schema("BudgetDecision", "1.0.0")

# Export schema
schema_json = registry.export_schema("BudgetDecision", "2.0.0")
print(schema_json)
```

## Enhanced Agent Registry

The enhanced agent registry provides advanced capabilities for managing agents including capability discovery, dependency tracking, health monitoring, and upgrade orchestration.

### Capability Discovery

```python
from AgentOperatingSystem.extensibility import (
    EnhancedAgentRegistry,
    AgentCapability
)

registry = EnhancedAgentRegistry()

# Register agent capabilities
capability = AgentCapability(
    capability_id="cap_decision_making",
    name="decision_making",
    description="Makes complex decisions with risk assessment",
    version="2.0.0",
    metadata={"domain": "finance"}
)

await registry.register_capability("cfo_agent", capability)

# Discover agents with specific capability
agents = await registry.discover_capabilities("decision_making")
for agent_info in agents:
    print(f"Agent: {agent_info['agent_id']}")
    print(f"Capability version: {agent_info['capability']['version']}")

# Get all capabilities for an agent
caps = await registry.get_agent_capabilities("cfo_agent")
for cap in caps:
    print(f"{cap['name']} v{cap['version']}")
```

### Dependency Management

```python
# Add dependencies between agents
await registry.add_dependency(
    dependent_agent_id="ceo_agent",
    dependency_agent_id="cfo_agent",
    dependency_type="runtime",
    required=True
)

await registry.add_dependency(
    dependent_agent_id="ceo_agent",
    dependency_agent_id="analytics_agent",
    dependency_type="runtime",
    required=False
)

# Get agent dependencies
deps = await registry.get_dependencies("ceo_agent", include_optional=True)
for dep in deps:
    print(f"Depends on: {dep['dependency_agent_id']}")
    print(f"Required: {dep['required']}")

# Get agents that depend on this agent
dependents = await registry.get_dependents("cfo_agent")
print(f"Dependents: {dependents}")

# Get full dependency tree
tree = await registry.get_dependency_tree("ceo_agent", max_depth=5)
print(f"Dependency tree: {tree}")
```

### Health Monitoring

```python
from AgentOperatingSystem.extensibility import AgentHealth

# Record health check
await registry.record_health_check(
    agent_id="cfo_agent",
    status=AgentHealth.HEALTHY,
    details={"response_time_ms": 150, "memory_mb": 256},
    checks_passed=5,
    checks_failed=0
)

# Get current health status
health = await registry.get_health_status("cfo_agent")
print(f"Status: {health['status']}")
print(f"Checks passed: {health['checks_passed']}")

# Record unhealthy status
await registry.record_health_check(
    agent_id="analytics_agent",
    status=AgentHealth.DEGRADED,
    details={"error": "High latency", "response_time_ms": 2500},
    checks_passed=3,
    checks_failed=2
)

# Get all unhealthy agents
unhealthy = await registry.get_unhealthy_agents()
for agent in unhealthy:
    print(f"Agent {agent['agent_id']} is {agent['health_check']['status']}")
```

### Upgrade Orchestration

```python
from AgentOperatingSystem.extensibility import AgentUpgradeStatus

# Set upgrade status
await registry.set_upgrade_status(
    agent_id="cfo_agent",
    status=AgentUpgradeStatus.UPDATE_AVAILABLE,
    available_versions=["2.1.0", "2.2.0"]
)

# Get agents needing upgrade
agents_to_upgrade = await registry.get_agents_needing_upgrade()
for agent in agents_to_upgrade:
    print(f"Agent {agent['agent_id']} can upgrade to: {agent['available_versions']}")

# Orchestrate upgrade
result = await registry.orchestrate_upgrade(
    agent_id="cfo_agent",
    target_version="2.1.0"
)

if result["status"] == "completed":
    print(f"Upgrade completed successfully")
    print(f"Dependencies checked: {result['dependencies_checked']}")
    print(f"Dependents notified: {result['dependents_notified']}")
else:
    print(f"Upgrade failed: {result.get('error')}")
```

### Registry Summary

```python
# Get comprehensive registry summary
summary = registry.get_registry_summary()

print(f"Total agents: {summary['total_agents']}")
print(f"Total capabilities: {summary['total_capabilities']}")
print(f"Total dependencies: {summary['total_dependencies']}")

print("\nHealth summary:")
for status, count in summary['health_summary'].items():
    print(f"  {status}: {count}")

print("\nUpgrade summary:")
for status, count in summary['upgrade_summary'].items():
    print(f"  {status}: {count}")
```

## Best Practices

### Plugin Development

1. **Version your plugins** - Use semantic versioning for plugin versions
2. **Handle initialization errors** - Return False from initialize() on failure
3. **Implement graceful shutdown** - Clean up resources in shutdown()
4. **Document capabilities** - Clearly list what your plugin can do
5. **Test hot-reloading** - Ensure your plugin can be reloaded without issues

### Schema Management

1. **Plan migrations** - Design schema evolution paths before making changes
2. **Maintain compatibility** - Use backward-compatible changes when possible
3. **Document breaking changes** - Provide clear migration guidance
4. **Version strategically** - Use semantic versioning for schemas
5. **Test compatibility** - Always check compatibility before activating new versions

### Agent Management

1. **Register capabilities** - Make agent capabilities discoverable
2. **Track dependencies** - Document all agent dependencies
3. **Monitor health** - Regularly check agent health
4. **Plan upgrades** - Check dependency tree before upgrading
5. **Coordinate upgrades** - Upgrade dependencies first, then dependents

## Integration Example

Complete example integrating all extensibility features:

```python
from AgentOperatingSystem.extensibility import (
    PluginRegistry, PluginType,
    SchemaRegistry, CompatibilityMode,
    EnhancedAgentRegistry, AgentCapability, AgentHealth
)

async def setup_extensible_system():
    # Setup plugin registry
    plugin_registry = PluginRegistry()
    policy = CustomPolicyPlugin()
    plugin_registry.register_plugin(policy, PluginType.POLICY)
    await plugin_registry.load_plugin("budget_policy_v1")
    await plugin_registry.activate_plugin("budget_policy_v1")
    
    # Setup schema registry
    schema_registry = SchemaRegistry()
    schema_registry.register_schema(
        "BudgetDecision", "1.0.0", schema_v1,
        compatibility_mode=CompatibilityMode.BACKWARD
    )
    schema_registry.activate_schema("BudgetDecision", "1.0.0")
    
    # Setup agent registry
    agent_registry = EnhancedAgentRegistry()
    capability = AgentCapability(
        capability_id="cap_1",
        name="budget_approval",
        description="Approves budgets",
        version="1.0.0"
    )
    await agent_registry.register_capability("cfo_agent", capability)
    await agent_registry.record_health_check(
        "cfo_agent", AgentHealth.HEALTHY,
        checks_passed=10, checks_failed=0
    )
    
    return plugin_registry, schema_registry, agent_registry

# Run the setup
plugin_reg, schema_reg, agent_reg = await setup_extensible_system()
```
