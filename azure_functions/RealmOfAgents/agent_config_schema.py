"""
Agent Configuration Schema for GenesisAgents

Defines the structure for configuration-driven agent deployment.
Developers provide only configuration - purpose, domain knowledge, and tools.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgentType(str, Enum):
    """Types of agents supported by GenesisAgents"""
    PURPOSE_DRIVEN = "purpose_driven"
    PERPETUAL = "perpetual"
    LEADERSHIP = "leadership"


class DomainKnowledge(BaseModel):
    """Domain knowledge configuration for fine-tuning LoRA adapters"""
    domain: str = Field(..., description="Domain name (e.g., 'finance', 'marketing')")
    training_data_path: str = Field(..., description="Path to training data in Azure Blob")
    adapter_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "task_type": "causal_lm",
            "r": 16,
            "lora_alpha": 32,
            "target_modules": ["q_proj", "v_proj"]
        },
        description="LoRA adapter configuration"
    )


class MCPToolReference(BaseModel):
    """Reference to an MCP tool from the registry"""
    server_name: str = Field(..., description="Name of the MCP server (e.g., 'github', 'erpnext')")
    tool_name: str = Field(..., description="Name of the tool within the server")
    configuration: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Tool-specific configuration"
    )


class AgentConfiguration(BaseModel):
    """
    Complete configuration for a PurposeDrivenAgent.
    
    This is all that's needed to onboard a new agent - no code required!
    
    Example:
        {
            "agent_id": "cfo",
            "agent_type": "purpose_driven",
            "purpose": "Financial oversight and strategic planning",
            "purpose_scope": "Financial planning, budget approval, risk assessment",
            "success_criteria": [
                "Maintain healthy cash flow",
                "Optimize operational costs",
                "Ensure financial compliance"
            ],
            "domain_knowledge": {
                "domain": "finance",
                "training_data_path": "training-data/cfo/financial_scenarios.jsonl",
                "adapter_config": {
                    "task_type": "causal_lm",
                    "r": 16,
                    "lora_alpha": 32,
                    "target_modules": ["q_proj", "v_proj"]
                }
            },
            "mcp_tools": [
                {
                    "server_name": "erpnext",
                    "tool_name": "get_financial_reports"
                },
                {
                    "server_name": "excel",
                    "tool_name": "analyze_spreadsheet"
                }
            ],
            "system_message": "You are the Chief Financial Officer...",
            "enabled": true
        }
    """
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_type: AgentType = Field(
        default=AgentType.PURPOSE_DRIVEN,
        description="Type of agent to instantiate"
    )
    
    # Purpose-driven attributes
    purpose: str = Field(..., description="The long-term purpose this agent works toward")
    purpose_scope: Optional[str] = Field(
        default=None,
        description="Scope/boundaries of the purpose"
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="List of criteria that define success"
    )
    
    # Domain knowledge for LoRA fine-tuning
    domain_knowledge: DomainKnowledge = Field(
        ...,
        description="Domain knowledge for fine-tuning LoRA adapters"
    )
    
    # MCP tools from registry
    mcp_tools: List[MCPToolReference] = Field(
        default_factory=list,
        description="MCP tools from the registry that this agent can use"
    )
    
    # Optional customization
    system_message: Optional[str] = Field(
        default=None,
        description="Custom system message for the agent"
    )
    
    # Lifecycle
    enabled: bool = Field(
        default=True,
        description="Whether this agent is enabled and should be instantiated"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for tracking and management"
    )


class AgentRegistry(BaseModel):
    """Registry of all agent configurations"""
    agents: List[AgentConfiguration] = Field(
        default_factory=list,
        description="List of all agent configurations"
    )
    version: str = Field(
        default="1.0",
        description="Registry schema version"
    )
    
    def get_enabled_agents(self) -> List[AgentConfiguration]:
        """Get all enabled agents"""
        return [agent for agent in self.agents if agent.enabled]
    
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentConfiguration]:
        """Get agent configuration by ID"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
