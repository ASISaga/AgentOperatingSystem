"""
App Configuration Schema for AgentOperatingSystem

Defines the structure for registering and configuring apps that run on AOS.
Similar to how BusinessInfinity is installed on AOS, this enables plug-and-play
app deployment with configuration-driven agent orchestration.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AppType(str, Enum):
    """Types of apps that can be deployed on AOS"""
    AGENT_ORCHESTRATION = "agent_orchestration"  # Like RealmOfAgents
    MCP_SERVER = "mcp_server"  # Like MCPServers
    BUSINESS_APPLICATION = "business_application"  # Like BusinessInfinity
    CUSTOM = "custom"


class AgentReference(BaseModel):
    """Reference to an agent to be orchestrated by the app"""
    agent_id: str = Field(..., description="ID of the agent to orchestrate")
    role: str = Field(..., description="Role of the agent in this app's context")
    configuration: Optional[Dict[str, Any]] = Field(
        default=None,
        description="App-specific configuration for this agent"
    )


class AppConfiguration(BaseModel):
    """
    Complete configuration for an app running on AgentOperatingSystem.

    This enables plug-and-play app deployment similar to BusinessInfinity.
    The app developer provides the purpose and selects agents to orchestrate.

    Example:
        {
            "app_id": "business_infinity",
            "app_name": "BusinessInfinity",
            "app_type": "business_application",
            "purpose": "Autonomous business operations and strategic decision-making",
            "description": "Enterprise business application for autonomous operations",
            "agents_to_orchestrate": [
                {
                    "agent_id": "ceo",
                    "role": "Strategic Leadership",
                    "configuration": {
                        "decision_authority_level": "executive"
                    }
                },
                {
                    "agent_id": "cfo",
                    "role": "Financial Management"
                }
            ],
            "mcp_servers_required": ["erpnext", "linkedin"],
            "azure_resources": {
                "storage_account": true,
                "service_bus": true,
                "key_vault": true
            },
            "enabled": true
        }
    """
    app_id: str = Field(..., description="Unique identifier for the app")
    app_name: str = Field(..., description="Human-readable name of the app")
    app_type: AppType = Field(..., description="Type of app")

    # App purpose and description
    purpose: str = Field(
        ...,
        description="The primary purpose of this app on AOS"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the app"
    )

    # Agent orchestration
    agents_to_orchestrate: List[AgentReference] = Field(
        default_factory=list,
        description="Agents that this app orchestrates"
    )

    # MCP server dependencies
    mcp_servers_required: List[str] = Field(
        default_factory=list,
        description="IDs of MCP servers this app requires"
    )

    # Azure resources configuration
    azure_resources: Dict[str, Any] = Field(
        default_factory=dict,
        description="Azure resources required by this app"
    )

    # Repository and deployment
    repository_url: Optional[str] = Field(
        default=None,
        description="Git repository URL for this app (if in dedicated repo)"
    )
    deployment_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Deployment-specific configuration"
    )

    # Lifecycle
    enabled: bool = Field(
        default=True,
        description="Whether this app is enabled"
    )
    version: str = Field(
        default="1.0.0",
        description="App version"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for tracking and management"
    )


class AppRegistry(BaseModel):
    """Registry of all apps deployed on AgentOperatingSystem"""
    apps: List[AppConfiguration] = Field(
        default_factory=list,
        description="List of all app configurations"
    )
    version: str = Field(
        default="1.0",
        description="Registry schema version"
    )

    def get_enabled_apps(self) -> List[AppConfiguration]:
        """Get all enabled apps"""
        return [app for app in self.apps if app.enabled]

    def get_app_by_id(self, app_id: str) -> Optional[AppConfiguration]:
        """Get app configuration by ID"""
        for app in self.apps:
            if app.app_id == app_id:
                return app
        return None

    def get_apps_by_type(self, app_type: AppType) -> List[AppConfiguration]:
        """Get all apps of a specific type"""
        return [app for app in self.apps if app.app_type == app_type]

    def get_apps_using_agent(self, agent_id: str) -> List[AppConfiguration]:
        """Get all apps that orchestrate a specific agent"""
        result = []
        for app in self.apps:
            if any(ref.agent_id == agent_id for ref in app.agents_to_orchestrate):
                result.append(app)
        return result
