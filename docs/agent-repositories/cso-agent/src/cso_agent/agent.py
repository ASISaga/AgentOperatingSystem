"""
CSOAgent - Chief Security Officer Agent.

Extends LeadershipAgent with dual-purpose security and leadership capabilities.
Maps both Security and Leadership purposes to respective LoRA adapters.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts,
  and agent persona)
- Core purposes are added to the primary LLM context
- MCP provides context management and domain-specific tools

Two purposes → two LoRA adapters:
    1. Security purpose  → "security" LoRA adapter
    2. Leadership purpose → "leadership" LoRA adapter (inherited)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from leadership_agent import LeadershipAgent


class CSOAgent(LeadershipAgent):
    """
    Chief Security Officer (CSO) agent with dual-purpose design.

    Capabilities:
    - Cybersecurity strategy and risk management
    - Compliance and regulatory governance
    - Human Essence integrity protection
    - Leadership and decision-making (inherited from LeadershipAgent)

    This agent maps two purposes to LoRA adapters:

    1. **Security purpose** → ``"security"`` LoRA adapter (security domain
       knowledge and persona)
    2. **Leadership purpose** → ``"leadership"`` LoRA adapter (leadership
       domain knowledge and persona, inherited)

    Example::

        from cso_agent import CSOAgent

        cso = CSOAgent(agent_id="cso-001")
        await cso.initialize()

        # Execute a security task
        result = await cso.execute_with_purpose(
            {"type": "risk_assessment", "data": {"system": "payments-api"}},
            purpose_type="security",
        )

        # Execute a leadership decision
        result = await cso.execute_with_purpose(
            {"type": "compliance_review"},
            purpose_type="leadership",
        )

        # Full status with dual purpose details
        status = await cso.get_status()
        print(status["purposes"])
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        security_purpose: Optional[str] = None,
        leadership_purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        security_adapter_name: Optional[str] = None,
        leadership_adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialise a CSOAgent with dual purposes mapped to LoRA adapters.

        Args:
            agent_id: Unique identifier for this agent.
            name: Human-readable name (defaults to ``"CSO"``).
            role: Role label (defaults to ``"CSO"``).
            security_purpose: Security-specific purpose string.  Defaults to
                the standard CSO security purpose if not provided.
            leadership_purpose: Leadership purpose string.  Defaults to the
                standard leadership purpose if not provided.
            purpose_scope: Scope/boundaries of the combined purpose.
            tools: Tools available to the agent.
            system_message: System message for the agent.
            security_adapter_name: LoRA adapter for security (defaults to
                ``"security"``).
            leadership_adapter_name: LoRA adapter for leadership (defaults to
                ``"leadership"``).
            config: Optional configuration dictionary.
        """
        if security_purpose is None:
            security_purpose = (
                "Security Leadership: Cybersecurity strategy, risk management, "
                "compliance, and Human Essence integrity"
            )
        if leadership_purpose is None:
            leadership_purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organisational guidance"
            )
        if security_adapter_name is None:
            security_adapter_name = "security"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Security governance and risk management domain"

        combined_purpose = f"{security_purpose}; {leadership_purpose}"

        super().__init__(
            agent_id=agent_id,
            name=name or "CSO",
            role=role or "CSO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            tools=tools,
            system_message=system_message,
            adapter_name=security_adapter_name,
            config=config,
        )

        # Dual-purpose configuration
        self.security_purpose: str = security_purpose
        self.leadership_purpose: str = leadership_purpose
        self.security_adapter_name: str = security_adapter_name
        self.leadership_adapter_name: str = leadership_adapter_name

        self.purpose_adapter_mapping: Dict[str, str] = {
            "security": self.security_adapter_name,
            "leadership": self.leadership_adapter_name,
        }

        self.logger.info(
            "CSOAgent '%s' created | security adapter='%s' | leadership adapter='%s'",
            self.agent_id,
            self.security_adapter_name,
            self.leadership_adapter_name,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation
    # ------------------------------------------------------------------

    def get_agent_type(self) -> List[str]:
        """
        Return ``["security", "leadership"]``.

        Returns:
            ``["security", "leadership"]``
        """
        available = self.get_available_personas()
        personas: List[str] = []

        for persona in ("security", "leadership"):
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
            purpose_type: One of ``"security"`` or ``"leadership"``
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
        purpose_type: str = "security",
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.

        Args:
            task: Task event dict passed to :meth:`handle_event`.
            purpose_type: Which purpose to use (``"security"`` or
                ``"leadership"``).  Defaults to ``"security"``.

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
            Status dictionary extended with CSO-specific fields.
        """
        base_status = await self.get_purpose_status()
        base_status.update(
            {
                "agent_type": "CSOAgent",
                "purposes": {
                    "security": {
                        "description": self.security_purpose,
                        "adapter": self.security_adapter_name,
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
