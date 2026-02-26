"""
CMOAgent - Chief Marketing Officer Agent.

Extends LeadershipAgent with dual-purpose marketing and leadership capabilities.
Maps both Marketing and Leadership purposes to respective LoRA adapters.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts,
  and agent persona)
- Core purposes are added to the primary LLM context
- MCP provides context management and domain-specific tools

Two purposes → two LoRA adapters:
    1. Marketing purpose  → "marketing" LoRA adapter
    2. Leadership purpose → "leadership" LoRA adapter (inherited)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from leadership_agent import LeadershipAgent


class CMOAgent(LeadershipAgent):
    """
    Chief Marketing Officer (CMO) agent with dual-purpose design.

    Capabilities:
    - Marketing strategy and execution
    - Brand management
    - Customer acquisition and retention
    - Market analysis
    - Leadership and decision-making (inherited from LeadershipAgent)

    This agent maps two purposes to LoRA adapters:

    1. **Marketing purpose** → ``"marketing"`` LoRA adapter (marketing domain
       knowledge and persona)
    2. **Leadership purpose** → ``"leadership"`` LoRA adapter (leadership
       domain knowledge and persona, inherited)

    The core purposes are added to the primary LLM context to guide behaviour.
    MCP integration provides context management and domain-specific tools.

    Example::

        from cmo_agent import CMOAgent

        cmo = CMOAgent(agent_id="cmo-001")
        await cmo.initialize()

        # Execute a marketing task
        result = await cmo.execute_with_purpose(
            {"type": "brand_analysis", "data": {"brand": "AcmeCorp"}},
            purpose_type="marketing",
        )

        # Execute a leadership decision
        result = await cmo.execute_with_purpose(
            {"type": "budget_review"},
            purpose_type="leadership",
        )

        # Full status with dual purpose details
        status = await cmo.get_status()
        print(status["purposes"])
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        marketing_purpose: Optional[str] = None,
        leadership_purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        success_criteria: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        marketing_adapter_name: Optional[str] = None,
        leadership_adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialise a CMOAgent with dual purposes mapped to LoRA adapters.

        Args:
            agent_id: Unique identifier for this agent.
            name: Human-readable name (defaults to ``"CMO"``).
            role: Role label (defaults to ``"CMO"``).
            marketing_purpose: Marketing-specific purpose string.  Defaults to
                the standard CMO marketing purpose if not provided.
            leadership_purpose: Leadership purpose string.  Defaults to the
                standard leadership purpose if not provided.
            purpose_scope: Scope/boundaries of the combined purpose.
            success_criteria: List of criteria that define success.
            tools: Tools available to the agent.
            system_message: System message for the agent.
            marketing_adapter_name: LoRA adapter for marketing (defaults to
                ``"marketing"``).
            leadership_adapter_name: LoRA adapter for leadership (defaults to
                ``"leadership"``).
            config: Optional configuration dictionary.
        """
        if marketing_purpose is None:
            marketing_purpose = (
                "Marketing: Brand strategy, customer acquisition, "
                "market analysis, and growth initiatives"
            )
        if leadership_purpose is None:
            leadership_purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organisational guidance"
            )
        if marketing_adapter_name is None:
            marketing_adapter_name = "marketing"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Marketing and Leadership domains"

        combined_purpose = f"{marketing_purpose}; {leadership_purpose}"

        # Primary adapter is "marketing" (CMO's primary domain)
        super().__init__(
            agent_id=agent_id,
            name=name or "CMO",
            role=role or "CMO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=marketing_adapter_name,
            config=config,
        )

        # Dual-purpose configuration
        self.marketing_purpose: str = marketing_purpose
        self.leadership_purpose: str = leadership_purpose
        self.marketing_adapter_name: str = marketing_adapter_name
        self.leadership_adapter_name: str = leadership_adapter_name

        self.purpose_adapter_mapping: Dict[str, str] = {
            "marketing": self.marketing_adapter_name,
            "leadership": self.leadership_adapter_name,
        }

        self.logger.info(
            "CMOAgent '%s' created | marketing adapter='%s' | leadership adapter='%s'",
            self.agent_id,
            self.marketing_adapter_name,
            self.leadership_adapter_name,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation
    # ------------------------------------------------------------------

    def get_agent_type(self) -> List[str]:
        """
        Return ``["marketing", "leadership"]``.

        Queries the AOS registry for both personas and falls back to defaults
        if either is unavailable.

        Returns:
            ``["marketing", "leadership"]``
        """
        available = self.get_available_personas()
        personas: List[str] = []

        for persona in ("marketing", "leadership"):
            if persona not in available:
                self.logger.warning(
                    "'%s' persona not in AOS registry, using default", persona
                )
            personas.append(persona)

        return personas

    # ------------------------------------------------------------------
    # Dual-purpose operations
    # ------------------------------------------------------------------

    def get_adapter_for_purpose(self, purpose_type: str) -> str:
        """
        Return the LoRA adapter name for the specified purpose type.

        Args:
            purpose_type: One of ``"marketing"`` or ``"leadership"``
                (case-insensitive).

        Returns:
            LoRA adapter name string.

        Raises:
            ValueError: If *purpose_type* is not a recognised purpose.
        """
        adapter_name = self.purpose_adapter_mapping.get(purpose_type.lower())
        if adapter_name is None:
            valid = list(self.purpose_adapter_mapping.keys())
            raise ValueError(
                f"Unknown purpose type '{purpose_type}'. Valid types: {valid}"
            )
        return adapter_name

    async def execute_with_purpose(
        self,
        task: Dict[str, Any],
        purpose_type: str = "marketing",
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.

        Temporarily switches :attr:`adapter_name` to the purpose-specific
        adapter, delegates to :meth:`handle_event`, then restores the
        original adapter — even if an exception occurs.

        Args:
            task: Task event dict passed to :meth:`handle_event`.
            purpose_type: Which purpose to use (``"marketing"`` or
                ``"leadership"``).  Defaults to ``"marketing"``.

        Returns:
            Result from :meth:`handle_event` augmented with:

            - ``"purpose_type"`` — the purpose type used.
            - ``"adapter_used"`` — the LoRA adapter that was active.

        Raises:
            ValueError: If *purpose_type* is not recognised.
        """
        adapter_name = self.get_adapter_for_purpose(purpose_type)
        self.logger.info(
            "Executing task with '%s' purpose using adapter '%s'",
            purpose_type,
            adapter_name,
        )

        original_adapter = self.adapter_name
        try:
            self.adapter_name = adapter_name
            result = await self.handle_event(task)
            result["purpose_type"] = purpose_type
            result["adapter_used"] = adapter_name
            return result
        except Exception:
            self.logger.error(
                "Error executing task with '%s' purpose", purpose_type
            )
            raise
        finally:
            self.adapter_name = original_adapter

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_status(self) -> Dict[str, Any]:
        """
        Return full status including dual purpose-adapter mappings.

        Returns:
            Status dictionary from :meth:`get_purpose_status` extended with:

            - ``"agent_type"`` — ``"CMOAgent"``.
            - ``"purposes"`` — per-purpose description and adapter info.
            - ``"purpose_adapter_mapping"`` — mapping dict.
            - ``"primary_adapter"`` — current active adapter name.
        """
        base_status = await self.get_purpose_status()
        base_status.update(
            {
                "agent_type": "CMOAgent",
                "purposes": {
                    "marketing": {
                        "description": self.marketing_purpose,
                        "adapter": self.marketing_adapter_name,
                    },
                    "leadership": {
                        "description": self.leadership_purpose,
                        "adapter": self.leadership_adapter_name,
                    },
                },
                "purpose_adapter_mapping": self.purpose_adapter_mapping,
                "primary_adapter": self.adapter_name,
            }
        )
        return base_status
