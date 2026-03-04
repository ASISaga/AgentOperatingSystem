"""
CEOAgent - Chief Executive Officer Agent.

Extends LeadershipAgent with dual-purpose executive and leadership capabilities.
Maps both Executive and Leadership purposes to respective LoRA adapters.
Provides boardroom orchestration for routing tasks to specialist C-suite agents.

Architecture:
- LoRA adapters provide domain knowledge (language, vocabulary, concepts,
  and agent persona)
- Core purposes are added to the primary LLM context
- MCP provides context management and domain-specific tools

Two purposes → two LoRA adapters:
    1. Executive purpose  → "executive" LoRA adapter
    2. Leadership purpose → "leadership" LoRA adapter (inherited)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from leadership_agent import LeadershipAgent
from purpose_driven_agent import A2AAgentTool, PurposeDrivenAgent

_BOARDROOM_INSTRUCTIONS = (
    "You are the CEO and Chairperson of the boardroom. You have access to a "
    "board of specialist directors. For technical infrastructure decisions, "
    "call the CTO tool. For security, privacy, or 'Human Essence' integrity "
    "concerns, call the CSO tool. For financial analysis, budget audits, or "
    "fiscal governance, call the CFO tool. For market strategy, brand "
    "management, or customer insights, call the CMO tool. When a specialist's "
    "response suggests cross-functional impact (e.g., the CTO reports a "
    "high-cost infrastructure change), proactively consult the relevant "
    "specialist (e.g., trigger the CFO tool for a budget audit). Always "
    "synthesise specialist inputs into a cohesive executive decision."
)


class CEOAgent(LeadershipAgent):
    """
    Chief Executive Officer (CEO) agent with dual-purpose design.

    Capabilities:
    - Strategic vision and cross-functional orchestration
    - Organisational direction and executive decision-making
    - Boardroom orchestration — routing tasks to specialist C-suite agents
    - Leadership and decision-making (inherited from LeadershipAgent)

    This agent maps two purposes to LoRA adapters:

    1. **Executive purpose** → ``"executive"`` LoRA adapter (executive domain
       knowledge and persona)
    2. **Leadership purpose** → ``"leadership"`` LoRA adapter (leadership
       domain knowledge and persona, inherited)

    The CEO additionally provides boardroom methods for enrolling and
    querying specialist agent tools (CTO, CFO, CSO, CMO).

    Example::

        from ceo_agent import CEOAgent

        ceo = CEOAgent(agent_id="ceo-001")
        await ceo.initialize()

        # Execute an executive task
        result = await ceo.execute_with_purpose(
            {"type": "strategic_review", "data": {"initiative": "Q3 expansion"}},
            purpose_type="executive",
        )

        # Execute a leadership decision
        result = await ceo.execute_with_purpose(
            {"type": "org_alignment"},
            purpose_type="leadership",
        )

        # Full status with dual purpose details
        status = await ceo.get_status()
        print(status["purposes"])
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        executive_purpose: Optional[str] = None,
        leadership_purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        executive_adapter_name: Optional[str] = None,
        leadership_adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialise a CEOAgent with dual purposes mapped to LoRA adapters.

        Args:
            agent_id: Unique identifier for this agent.
            name: Human-readable name (defaults to ``"CEO"``).
            role: Role label (defaults to ``"CEO"``).
            executive_purpose: Executive-specific purpose string.  Defaults to
                the standard CEO executive purpose if not provided.
            leadership_purpose: Leadership purpose string.  Defaults to the
                standard leadership purpose if not provided.
            purpose_scope: Scope/boundaries of the combined purpose.
            tools: Tools available to the agent.
            system_message: System message for the agent.
            executive_adapter_name: LoRA adapter for executive (defaults to
                ``"executive"``).
            leadership_adapter_name: LoRA adapter for leadership (defaults to
                ``"leadership"``).
            config: Optional configuration dictionary.
        """
        if executive_purpose is None:
            executive_purpose = (
                "Executive Leadership: Strategic vision, cross-functional "
                "orchestration, and organisational direction"
            )
        if leadership_purpose is None:
            leadership_purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organisational guidance"
            )
        if executive_adapter_name is None:
            executive_adapter_name = "executive"
        if leadership_adapter_name is None:
            leadership_adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Executive Leadership and strategic direction domain"

        combined_purpose = f"{executive_purpose}; {leadership_purpose}"

        super().__init__(
            agent_id=agent_id,
            name=name or "CEO",
            role=role or "CEO",
            purpose=combined_purpose,
            purpose_scope=purpose_scope,
            tools=tools,
            system_message=system_message,
            adapter_name=executive_adapter_name,
            config=config,
        )

        # Dual-purpose configuration
        self.executive_purpose: str = executive_purpose
        self.leadership_purpose: str = leadership_purpose
        self.executive_adapter_name: str = executive_adapter_name
        self.leadership_adapter_name: str = leadership_adapter_name

        self.purpose_adapter_mapping: Dict[str, str] = {
            "executive": self.executive_adapter_name,
            "leadership": self.leadership_adapter_name,
        }

        # Boardroom orchestration
        self.boardroom_tools: List[A2AAgentTool] = []

        self.logger.info(
            "CEOAgent '%s' created | executive adapter='%s' | leadership adapter='%s'",
            self.agent_id,
            self.executive_adapter_name,
            self.leadership_adapter_name,
        )

    # ------------------------------------------------------------------
    # Abstract method implementation
    # ------------------------------------------------------------------

    def get_agent_type(self) -> List[str]:
        """
        Return ``["executive", "leadership"]``.

        Returns:
            ``["executive", "leadership"]``
        """
        available = self.get_available_personas()
        personas: List[str] = []

        for persona in ("executive", "leadership"):
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
            purpose_type: One of ``"executive"`` or ``"leadership"``
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
        purpose_type: str = "executive",
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.

        Args:
            task: Task event dict passed to :meth:`handle_event`.
            purpose_type: Which purpose to use (``"executive"`` or
                ``"leadership"``).  Defaults to ``"executive"``.

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
    # Boardroom orchestration
    # ------------------------------------------------------------------

    def get_boardroom_instructions(self) -> str:
        """
        Return system instructions for LLM routing across the boardroom.

        These instructions guide the LLM on when and how to invoke
        specialist C-suite agent tools.

        Returns:
            System instruction string for boardroom orchestration.
        """
        return _BOARDROOM_INSTRUCTIONS

    def enroll_boardroom_tools(
        self,
        specialists: List[PurposeDrivenAgent],
        thread_id: Optional[str] = None,
    ) -> List[A2AAgentTool]:
        """
        Enroll specialist agents as boardroom tools.

        Calls :meth:`as_tool` on each specialist and stores the resulting
        tools in :attr:`boardroom_tools`.

        Args:
            specialists: List of specialist agents to enroll.
            thread_id: Optional thread identifier for tool context.

        Returns:
            List of enrolled :class:`A2AAgentTool` instances.
        """
        self.boardroom_tools = [
            specialist.as_tool(thread_id=thread_id)
            for specialist in specialists
        ]
        self.logger.info(
            "Enrolled %d specialist(s) in boardroom", len(self.boardroom_tools)
        )
        return self.boardroom_tools

    def get_boardroom_tools(self) -> List[A2AAgentTool]:
        """
        Return the currently enrolled boardroom tools.

        Returns:
            List of :class:`A2AAgentTool` instances.
        """
        return self.boardroom_tools

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_status(self) -> Dict[str, Any]:
        """
        Return full status including dual purpose-adapter mappings.

        Returns:
            Status dictionary extended with CEO-specific fields.
        """
        base_status = await self.get_purpose_status()
        base_status.update(
            {
                "agent_type": "CEOAgent",
                "purposes": {
                    "executive": {
                        "description": self.executive_purpose,
                        "adapter": self.executive_adapter_name,
                    },
                    "leadership": {
                        "description": self.leadership_purpose,
                        "adapter": self.leadership_adapter_name,
                    },
                },
                "purpose_adapter_mapping": self.purpose_adapter_mapping,
                "primary_adapter": self.adapter_name,
                "boardroom_tools_count": len(self.boardroom_tools),
            }
        )
        return base_status
