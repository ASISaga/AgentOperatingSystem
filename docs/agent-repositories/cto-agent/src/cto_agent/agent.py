"""
CTOAgent - Chief Technology Officer Agent.

Extends LeadershipAgent with dual-purpose technology and leadership capabilities.
Maps both Technology and Leadership purposes to respective LoRA adapters.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts,
  and agent persona)
- Core purposes are added to the primary LLM context
- MCP provides context management and domain-specific tools

Two purposes → two LoRA adapters:
    1. Technology purpose → "technology" LoRA adapter
    2. Leadership purpose → "leadership" LoRA adapter (inherited)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from leadership_agent import LeadershipAgent


class CTOAgent(LeadershipAgent):
    """
    Chief Technology Officer (CTO) agent with dual-purpose design.

    Capabilities:
    - Technical infrastructure and architecture decisions
    - Innovation strategy and engineering excellence
    - Technology roadmap and platform governance
    - Leadership and decision-making (inherited from LeadershipAgent)

    This agent maps two purposes to LoRA adapters:

    1. **Technology purpose** → ``"technology"`` LoRA adapter (technology domain
       knowledge and persona)
    2. **Leadership purpose** → ``"leadership"`` LoRA adapter (leadership
       domain knowledge and persona, inherited)

    Example::

        from cto_agent import CTOAgent

        cto = CTOAgent(agent_id="cto-001")
        await cto.initialize()

        # Execute a technology task
        result = await cto.execute_with_purpose(
            {"type": "architecture_review", "data": {"service": "auth-api"}},
            purpose_type="technology",
        )

        # Execute a leadership decision
        result = await cto.execute_with_purpose(
            {"type": "team_restructure"},
            purpose_type="leadership",
        )

        # Full status with dual purpose details
        status = await cto.get_status()
        print(status["purposes"])
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        technology_purpose: Optional[str] = None,
        leadership_purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        technology_adapter_name: Optional[str] = None,
        leadership_adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialise a CTOAgent with dual purposes mapped to LoRA adapters.

        Args:
            agent_id: Unique identifier for this agent.
            name: Human-readable name (defaults to ``"CTO"``).
            role: Role label (defaults to ``"CTO"``).
            technology_purpose: Technology-specific purpose string.  Defaults to
                the standard CTO technology purpose if not provided.
            leadership_purpose: Leadership purpose string.  Defaults to the
                standard leadership purpose if not provided.
            purpose_scope: Scope/boundaries of the combined purpose.
            tools: Tools available to the agent.
            system_message: System message for the agent.
            technology_adapter_name: LoRA adapter for technology (defaults to
                ``"technology"``).
            leadership_adapter_name: LoRA adapter for leadership (defaults to
                ``"leadership"``).
            config: Optional configuration dictionary.
        """
        if technology_purpose is None:
            technology_purpose = (
                "Technology Leadership: Technical infrastructure, innovation "
                "strategy, architecture decisions, and engineering excellence"
            )
        if leadership_purpose is None:
            leadership_purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organisational guidance"
            )
        if technology_adapter_name is None:
            technology_adapter_name = "technology"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Technology strategy and engineering leadership domain"

        combined_purpose = f"{technology_purpose}; {leadership_purpose}"

        super().__init__(
            agent_id=agent_id,
            name=name or "CTO",
            role=role or "CTO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            tools=tools,
            system_message=system_message,
            adapter_name=technology_adapter_name,
            config=config,
        )

        # Dual-purpose configuration
        self.technology_purpose: str = technology_purpose
        self.leadership_purpose: str = leadership_purpose
        self.technology_adapter_name: str = technology_adapter_name
        self.leadership_adapter_name: str = leadership_adapter_name

        self.purpose_adapter_mapping: Dict[str, str] = {
            "technology": self.technology_adapter_name,
            "leadership": self.leadership_adapter_name,
        }

        self.logger.info(
            "CTOAgent '%s' created | technology adapter='%s' | leadership adapter='%s'",
            self.agent_id,
            self.technology_adapter_name,
            self.leadership_adapter_name,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation
    # ------------------------------------------------------------------

    def get_agent_type(self) -> List[str]:
        """
        Return ``["technology", "leadership"]``.

        Returns:
            ``["technology", "leadership"]``
        """
        available = self.get_available_personas()
        personas: List[str] = []

        for persona in ("technology", "leadership"):
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
            purpose_type: One of ``"technology"`` or ``"leadership"``
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
        purpose_type: str = "technology",
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.

        Args:
            task: Task event dict passed to :meth:`handle_event`.
            purpose_type: Which purpose to use (``"technology"`` or
                ``"leadership"``).  Defaults to ``"technology"``.

        Returns:
            Result from :meth:`handle_event` augmented with purpose metadata.

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
            Status dictionary extended with CTO-specific fields.
        """
        base_status = await self.get_purpose_status()
        base_status.update(
            {
                "agent_type": "CTOAgent",
                "purposes": {
                    "technology": {
                        "description": self.technology_purpose,
                        "adapter": self.technology_adapter_name,
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
