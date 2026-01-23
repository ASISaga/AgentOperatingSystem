"""
CMO Agent - Chief Marketing Officer Agent with marketing and leadership capabilities.
Extends LeadershipAgent with marketing-specific functionality.
Maps both Marketing and Leadership purposes to respective LoRA adapters.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts, agent persona)
- Core purposes are added to primary LLM context
- MCP provides context management and domain-specific tools
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .leadership_agent import LeadershipAgent


class CMOAgent(LeadershipAgent):
    """
    Chief Marketing Officer (CMO) agent providing:
    - Marketing strategy and execution
    - Brand management
    - Customer acquisition and retention
    - Market analysis
    - Leadership and decision-making (inherited)

    This agent maps two purposes to LoRA adapters:
    1. Marketing purpose -> "marketing" LoRA adapter (provides marketing domain knowledge & persona)
    2. Leadership purpose -> "leadership" LoRA adapter (provides leadership domain knowledge & persona)

    The core purposes are added to the primary LLM context to guide behavior.
    MCP integration provides context management and domain-specific tools.
    """

    def __init__(
        self,
        agent_id: str,
        name: str = None,
        role: str = None,
        marketing_purpose: str = None,
        leadership_purpose: str = None,
        purpose_scope: str = None,
        success_criteria: List[str] = None,
        tools: List[Any] = None,
        system_message: str = None,
        marketing_adapter_name: str = None,
        leadership_adapter_name: str = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize CMO Agent with dual purposes mapped to LoRA adapters.

        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role (defaults to "CMO")
            marketing_purpose: Marketing-specific purpose (defaults to standard CMO marketing purpose)
            leadership_purpose: Leadership purpose (defaults to standard leadership purpose)
            purpose_scope: Scope/boundaries of the purposes
            success_criteria: List of criteria that define success
            tools: Tools available to the agent
            system_message: System message for the agent
            marketing_adapter_name: Name for marketing LoRA adapter (defaults to "marketing")
            leadership_adapter_name: Name for leadership LoRA adapter (defaults to "leadership")
            config: Optional configuration dictionary
        """
        # Default marketing purpose if not provided
        if marketing_purpose is None:
            marketing_purpose = "Marketing: Brand strategy, customer acquisition, market analysis, and growth initiatives"

        # Default leadership purpose if not provided
        if leadership_purpose is None:
            leadership_purpose = "Leadership: Strategic decision-making, team coordination, and organizational guidance"

        # Combine purposes for the agent's overall purpose
        combined_purpose = f"{marketing_purpose}; {leadership_purpose}"

        # Default adapter names
        if marketing_adapter_name is None:
            marketing_adapter_name = "marketing"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"

        # Default purpose scope
        if purpose_scope is None:
            purpose_scope = "Marketing and Leadership domains"

        # Initialize parent LeadershipAgent with combined purpose
        # The primary adapter will be marketing since that's the CMO's main focus
        super().__init__(
            agent_id=agent_id,
            name=name or "CMO",
            role=role or "CMO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=marketing_adapter_name,  # Primary adapter
            config=config
        )

        # Store individual purposes and their adapter mappings
        self.marketing_purpose = marketing_purpose
        self.leadership_purpose = leadership_purpose
        self.marketing_adapter_name = marketing_adapter_name
        self.leadership_adapter_name = leadership_adapter_name

        # Purpose-to-adapter mapping configuration
        self.purpose_adapter_mapping = {
            "marketing": self.marketing_adapter_name,
            "leadership": self.leadership_adapter_name
        }

        self.logger.info(
            f"CMOAgent {self.agent_id} created with dual purposes: "
            f"Marketing (adapter: {self.marketing_adapter_name}), "
            f"Leadership (adapter: {self.leadership_adapter_name})"
        )

    def get_agent_type(self) -> List[str]:
        """
        Get the agent's personas/skills.
        
        CMO combines both marketing and leadership personas.
        
        Returns:
            ["marketing", "leadership"] - identifies this agent's dual personas
        """
        return ["marketing", "leadership"]

    def get_adapter_for_purpose(self, purpose_type: str) -> str:
        """
        Get the LoRA adapter name for a specific purpose type.

        Args:
            purpose_type: Type of purpose ("marketing" or "leadership")

        Returns:
            LoRA adapter name for the specified purpose

        Raises:
            ValueError: If purpose_type is not recognized
        """
        adapter_name = self.purpose_adapter_mapping.get(purpose_type.lower())

        if adapter_name is None:
            valid_types = list(self.purpose_adapter_mapping.keys())
            raise ValueError(
                f"Unknown purpose type '{purpose_type}'. Valid types: {valid_types}"
            )

        return adapter_name

    async def execute_with_purpose(
        self,
        task: Dict[str, Any],
        purpose_type: str = "marketing"
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.

        Args:
            task: Task to execute
            purpose_type: Which purpose to use ("marketing" or "leadership")

        Returns:
            Task execution result

        Raises:
            ValueError: If purpose_type is not recognized
        """
        # This will raise ValueError if purpose_type is invalid
        adapter_name = self.get_adapter_for_purpose(purpose_type)

        self.logger.info(
            f"Executing task with {purpose_type} purpose using adapter: {adapter_name}"
        )

        # Store original adapter and ensure restoration in all cases
        original_adapter = self.adapter_name

        try:
            # Temporarily switch adapter for this task execution
            self.adapter_name = adapter_name

            # Execute task with the purpose-specific adapter
            result = await self.handle_event(task)
            result["purpose_type"] = purpose_type
            result["adapter_used"] = adapter_name
            return result
        except Exception as e:
            self.logger.error(f"Error executing task with {purpose_type} purpose: {e}")
            raise
        finally:
            # Always restore original adapter, even if exception occurred
            self.adapter_name = original_adapter

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the CMO agent including purpose-adapter mappings.

        Returns:
            Status dictionary with purpose and adapter information
        """
        base_status = await self.get_purpose_status()

        # Add CMO-specific information
        base_status.update({
            "agent_type": "CMOAgent",
            "purposes": {
                "marketing": {
                    "description": self.marketing_purpose,
                    "adapter": self.marketing_adapter_name
                },
                "leadership": {
                    "description": self.leadership_purpose,
                    "adapter": self.leadership_adapter_name
                }
            },
            "purpose_adapter_mapping": self.purpose_adapter_mapping,
            "primary_adapter": self.adapter_name
        })

        return base_status
