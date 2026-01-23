"""
CMO Agent - Lean wrapper over PurposeDrivenAgent for marketing leadership.

This agent is a minimal wrapper that loads configuration from YAML.
All multi-purpose and adapter switching functionality is inherited from PurposeDrivenAgent.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts, agent persona)
- Core purposes are added to primary LLM context
- MCP provides context management and domain-specific tools
"""

from typing import Dict, Any, List, Optional
from .leadership_agent import LeadershipAgent


class CMOAgent(LeadershipAgent):
    """
    Chief Marketing Officer (CMO) agent - lean wrapper over LeadershipAgent.
    
    Provides:
    - Marketing strategy and execution
    - Brand management
    - Customer acquisition and retention
    - Market analysis
    - Leadership and decision-making (inherited)
    
    This agent is configured via YAML with dual purposes:
    1. Marketing purpose -> "marketing" LoRA adapter
    2. Leadership purpose -> "leadership" LoRA adapter
    
    All multi-purpose functionality (adapter switching, purpose management) is
    inherited from PurposeDrivenAgent. This class provides minimal CMO-specific logic.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str = None,
        role: str = None,
        **kwargs
    ):
        """
        Initialize CMO Agent.
        
        For YAML-based configuration, use CMOAgent.from_yaml() instead.
        This constructor is primarily for backward compatibility.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role (defaults to "CMO")
            **kwargs: Additional arguments passed to parent LeadershipAgent
        """
        # Initialize parent LeadershipAgent
        super().__init__(
            agent_id=agent_id,
            name=name or "CMO",
            role=role or "CMO",
            **kwargs
        )
