# App Configuration and Registry System

## Overview

The AgentOperatingSystem (AOS) provides a **plug-and-play app registration system** that enables configuration-driven deployment of applications. This system is analogous to installing apps like BusinessInfinity on AOS.

## Purpose

The app configuration system allows developers to:
- **Define the purpose** of their app on AOS
- **Select agents to orchestrate** via configuration
- **Specify MCP server dependencies**
- **Configure Azure resources** required by the app
- **Deploy apps from dedicated repositories**

## Architecture Decision: Dedicated Repositories

### Recommended Approach: Dedicated Repositories

Based on the AOS architecture principles and the need for modularity, we recommend **dedicated repositories** for each app:

```
ASISaga/
├── AgentOperatingSystem/     # Core AOS infrastructure
├── RealmOfAgents/            # Agent orchestration app (dedicated repo)
├── MCPServers/               # MCP server infrastructure (dedicated repo)
├── BusinessInfinity/         # Business application (dedicated repo)
└── [YourApp]/                # Your custom app (dedicated repo)
```

### Benefits of Dedicated Repositories

1. **Independent Versioning**
   - Each app can have its own release cycle
   - Version conflicts are eliminated
   - Easier to track changes specific to each app

2. **Clear Ownership**
   - Teams can own specific apps
   - Permissions can be managed independently
   - Clear responsibility boundaries

3. **Modularity**
   - Apps can be developed and tested independently
   - Easier to remove or replace apps
   - Reduced coupling between components

4. **Deployment Flexibility**
   - Apps can be deployed independently
   - Different deployment schedules for different apps
   - Rollback is simpler and safer

5. **Documentation**
   - Each app has its own comprehensive docs
   - Easier to maintain app-specific documentation
   - Clearer onboarding for new contributors

6. **Size Management**
   - Keeps repositories focused and smaller
   - Faster clone times
   - Easier to navigate

### Decision Criteria: When to Use Dedicated Repositories

**Use a dedicated repository when:**
- ✅ The app has its own deployment lifecycle
- ✅ The app will be maintained by a different team
- ✅ The app has significant complexity (>1000 LOC)
- ✅ The app is intended for reuse by others
- ✅ The app has its own Azure resources
- ✅ The app represents a distinct business domain
- ✅ The app will evolve independently of AOS

**Use the main AOS repository when:**
- ❌ It's a core AOS component (e.g., messaging, storage)
- ❌ It's tightly coupled to the AOS kernel
- ❌ It's a shared utility used by multiple components
- ❌ It's experimental and not ready for independent deployment

### Examples

| App | Repository Strategy | Rationale |
|-----|---------------------|-----------|
| **RealmOfAgents** | Dedicated Repo | Independent deployment, agent orchestration focus, will evolve separately |
| **MCPServers** | Dedicated Repo | MCP infrastructure, different lifecycle, can be reused by other projects |
| **BusinessInfinity** | Dedicated Repo | Business application, large codebase, independent team, business domain focus |
| **Storage Manager** | AOS Main Repo | Core infrastructure, tightly coupled to kernel, shared by all apps |
| **Message Bus** | AOS Main Repo | Core infrastructure, fundamental to AOS architecture |

## App Configuration Schema

### Basic Configuration

```json
{
  "app_id": "my_app",
  "app_name": "MyApp",
  "app_type": "business_application",
  "purpose": "Purpose of this app on AOS",
  "description": "Detailed description",
  "agents_to_orchestrate": [
    {
      "agent_id": "ceo",
      "role": "Strategic Leadership",
      "configuration": {
        "custom_setting": "value"
      }
    }
  ],
  "mcp_servers_required": ["github", "erpnext"],
  "azure_resources": {
    "storage_account": true,
    "service_bus": true
  },
  "repository_url": "https://github.com/ASISaga/MyApp",
  "enabled": true
}
```

### App Types

```python
class AppType(str, Enum):
    AGENT_ORCHESTRATION = "agent_orchestration"  # Like RealmOfAgents
    MCP_SERVER = "mcp_server"                    # Like MCPServers
    BUSINESS_APPLICATION = "business_application" # Like BusinessInfinity
    CUSTOM = "custom"
```

## Usage

### 1. Create App Configuration

Create a configuration file for your app (e.g., `my_app_config.json`):

```json
{
  "app_id": "sales_automation",
  "app_name": "SalesAutomation",
  "app_type": "business_application",
  "purpose": "Automate sales processes and customer engagement",
  "description": "Sales automation app using AI agents",
  "agents_to_orchestrate": [
    {
      "agent_id": "sales_manager",
      "role": "Sales Management"
    },
    {
      "agent_id": "customer_service",
      "role": "Customer Support"
    }
  ],
  "mcp_servers_required": ["salesforce", "hubspot"],
  "azure_resources": {
    "storage_account": true,
    "service_bus": true,
    "cosmos_db": true
  },
  "repository_url": "https://github.com/YourOrg/SalesAutomation",
  "enabled": true,
  "version": "1.0.0"
}
```

### 2. Add to App Registry

Add your app to the app registry (`config/app_registry.json`):

```json
{
  "version": "1.0",
  "apps": [
    {
      "app_id": "sales_automation",
      ...
    }
  ]
}
```

### 3. Load and Validate

```python
from AgentOperatingSystem.apps import AppRegistry, AppConfiguration
import json

# Load registry
with open('config/app_registry.json') as f:
    registry_data = json.load(f)

registry = AppRegistry(**registry_data)

# Get your app
app = registry.get_app_by_id('sales_automation')

# Validate agents and dependencies
print(f"App: {app.app_name}")
print(f"Purpose: {app.purpose}")
print(f"Agents: {[ref.agent_id for ref in app.agents_to_orchestrate]}")
print(f"MCP Servers: {app.mcp_servers_required}")
```

### 4. Query Registry

```python
# Get all business applications
business_apps = registry.get_apps_by_type(AppType.BUSINESS_APPLICATION)

# Get all apps using the CEO agent
apps_with_ceo = registry.get_apps_using_agent('ceo')

# Get all enabled apps
enabled_apps = registry.get_enabled_apps()
```

## Integration with AOS

### For App Developers

When creating an app on AOS:

1. **Define Your Purpose**
   ```json
   "purpose": "What your app does on AOS"
   ```

2. **Select Agents to Orchestrate**
   ```json
   "agents_to_orchestrate": [
     {
       "agent_id": "ceo",
       "role": "Strategic Leadership",
       "configuration": {
         "app_specific_setting": "value"
       }
     }
   ]
   ```

3. **Specify MCP Server Dependencies**
   ```json
   "mcp_servers_required": ["github", "erpnext", "linkedin"]
   ```

4. **Configure Azure Resources**
   ```json
   "azure_resources": {
     "storage_account": true,
     "service_bus": true,
     "key_vault": true,
     "cosmos_db": false
   }
   ```

5. **Set Repository URL** (if in dedicated repo)
   ```json
   "repository_url": "https://github.com/YourOrg/YourApp"
   ```

### For AOS Administrators

Managing apps on AOS:

```python
from AgentOperatingSystem.apps import AppRegistry

# Load registry
registry = AppRegistry.load_from_blob_storage()

# Check which apps use specific agents
ceo_apps = registry.get_apps_using_agent('ceo')
print(f"Apps using CEO agent: {[app.app_name for app in ceo_apps]}")

# Check required MCP servers across all apps
all_mcp_servers = set()
for app in registry.get_enabled_apps():
    all_mcp_servers.update(app.mcp_servers_required)
print(f"Required MCP servers: {all_mcp_servers}")

# Validate app dependencies
for app in registry.apps:
    print(f"App: {app.app_name}")
    print(f"  Agents: {len(app.agents_to_orchestrate)}")
    print(f"  MCP Servers: {len(app.mcp_servers_required)}")
```

## Migration from azure_functions to Dedicated Repositories

### Current Structure (Monorepo)

```
AgentOperatingSystem/
└── azure_functions/
    ├── RealmOfAgents/
    └── MCPServers/
```

### Recommended Structure (Dedicated Repos)

```
ASISaga/
├── AgentOperatingSystem/     # Core infrastructure only
├── RealmOfAgents/            # Moved to dedicated repo
└── MCPServers/               # Moved to dedicated repo
```

### Migration Steps

1. **Create Dedicated Repositories**
   ```bash
   # Create new repos on GitHub
   gh repo create ASISaga/RealmOfAgents --public
   gh repo create ASISaga/MCPServers --public
   ```

2. **Move Code**
   ```bash
   # Copy RealmOfAgents
   git clone https://github.com/ASISaga/RealmOfAgents
   cp -r AgentOperatingSystem/azure_functions/RealmOfAgents/* RealmOfAgents/
   
   # Copy MCPServers
   git clone https://github.com/ASISaga/MCPServers
   cp -r AgentOperatingSystem/azure_functions/MCPServers/* MCPServers/
   ```

3. **Update App Registry**
   ```json
   {
     "app_id": "realm_of_agents",
     "repository_url": "https://github.com/ASISaga/RealmOfAgents",
     ...
   }
   ```

4. **Update Documentation**
   - Update main README to reference dedicated repos
   - Add migration guide
   - Update deployment instructions

## Best Practices

1. **Purpose Definition**
   - Be clear and specific about your app's purpose
   - Explain what problem it solves
   - Define success criteria

2. **Agent Selection**
   - Only orchestrate agents you actually need
   - Provide app-specific configuration for agents
   - Document why each agent is required

3. **MCP Server Dependencies**
   - Declare all MCP server dependencies
   - Specify which tools from each server you use
   - Document integration points

4. **Azure Resources**
   - Request only resources you need
   - Use shared resources when possible
   - Document resource usage patterns

5. **Versioning**
   - Use semantic versioning (major.minor.patch)
   - Update version when making changes
   - Maintain a CHANGELOG

## Examples

See `config/example_app_registry.json` for complete examples:
- **RealmOfAgents**: Agent orchestration app
- **MCPServers**: MCP server infrastructure
- **BusinessInfinity**: Business application

## Support

For questions about app configuration:
- Review this documentation
- Check example configurations
- Consult the AOS team
