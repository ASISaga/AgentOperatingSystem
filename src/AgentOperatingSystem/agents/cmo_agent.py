"""
CMO Agent - Chief Marketing Officer Agent with marketing and leadership capabilities.
Extends LeadershipAgent with a marketing layer.

Layer stacking architecture:
  Layer 0 (LeadershipAgent): adapter="leadership", context={domain, capabilities…}, skills=[…]
  Layer 1 (CMOAgent):        adapter="marketing",  context={domain, capabilities…}, skills=[…]

  get_adapters()   → ["leadership", "marketing"]
  get_all_skills() → leadership skills + marketing skills

The "marketing" LoRA adapter provides marketing-specific domain knowledge and persona.
The inherited "leadership" adapter provides leadership capabilities.
MCP provides context management and domain-specific tools.
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
    - Leadership and decision-making (inherited from LeadershipAgent)

    CMOAgent adds exactly one layer (adapter="marketing") on top of the
    LeadershipAgent layer stack:
      Layer 0: "leadership"  (from LeadershipAgent._add_layer)
      Layer 1: "marketing"   (from CMOAgent._add_layer)
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
        Initialize CMO Agent with marketing and leadership layers.

        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role (defaults to "CMO")
            marketing_purpose: Marketing-specific purpose statement
            leadership_purpose: Leadership purpose statement
            purpose_scope: Scope/boundaries of the purposes
            success_criteria: List of criteria that define success
            tools: Tools available to the agent
            system_message: System message for the agent
            marketing_adapter_name: LoRA adapter for the marketing layer (default "marketing")
            leadership_adapter_name: LoRA adapter for the leadership layer (default "leadership")
            config: Optional configuration dictionary
        """
        if marketing_purpose is None:
            marketing_purpose = (
                "Marketing: Brand strategy, customer acquisition, market analysis, "
                "and growth initiatives"
            )
        if leadership_purpose is None:
            leadership_purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organizational guidance"
            )
        if marketing_adapter_name is None:
            marketing_adapter_name = "marketing"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Marketing and Leadership domains"

        # Combined purpose statement used as the LLM instructions
        combined_purpose = f"{marketing_purpose}; {leadership_purpose}"

        # Initialise LeadershipAgent.  Pass leadership_adapter_name so the
        # leadership layer uses the caller-supplied (or default) adapter name.
        super().__init__(
            agent_id=agent_id,
            name=name or "CMO",
            role=role or "CMO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=leadership_adapter_name,  # used by LeadershipAgent._add_layer
            config=config
        )

        # Store individual purposes for introspection / status reporting
        self.marketing_purpose = marketing_purpose
        self.leadership_purpose = leadership_purpose
        self.marketing_adapter_name = marketing_adapter_name
        self.leadership_adapter_name = leadership_adapter_name

        # Purpose-to-adapter mapping (used by execute_with_purpose).
        # Ordered to match the layer hierarchy (leadership first, marketing second).
        self.purpose_adapter_mapping = {
            "leadership": self.leadership_adapter_name,
            "marketing": self.marketing_adapter_name,
        }

        # Register the marketing layer on top of the inherited leadership layer.
        self._add_layer(
            adapter_name=marketing_adapter_name,
            context={
                "domain": "marketing",
                "marketing_purpose": self.marketing_purpose,
                "capabilities": [
                    "brand_strategy",
                    "customer_acquisition",
                    "market_analysis",
                    "growth_initiatives",
                ],
            },
            skills=["analyze_market", "execute_with_purpose", "manage_brand"],
        )

        self.logger.info(
            f"CMOAgent {self.agent_id} created with layers: {self.get_adapters()}"
        )

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
            "adapters": self.get_adapters(),
            "primary_adapter": self.adapter_name
        })

        return base_status
