"""
LeadershipAgent - Standalone leadership and decision-making agent.

Extends PurposeDrivenAgent with leadership-specific functionality:
- Decision-making with provenance tracking
- Stakeholder coordination (requires message bus integration)
- Consensus building
- Delegation patterns

The Leadership purpose is mapped to the "leadership" LoRA adapter, which
provides leadership-specific domain knowledge and agent persona. The core
purpose is added to the primary LLM context to guide agent behaviour.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from purpose_driven_agent import PurposeDrivenAgent


class LeadershipAgent(PurposeDrivenAgent):
    """
    Leadership agent providing decision-making and coordination capabilities.

    Capabilities:
    - Decision-making with confidence scoring and rationale
    - Stakeholder coordination (requires message bus integration)
    - Consensus building
    - Delegation patterns
    - Decision provenance tracking

    The Leadership purpose is mapped to the ``"leadership"`` LoRA adapter
    which provides leadership-specific domain knowledge and agent persona.
    The core purpose is incorporated into the primary LLM context.

    Example::

        from leadership_agent import LeadershipAgent

        agent = LeadershipAgent(agent_id="ceo-001")
        await agent.initialize()

        decision = await agent.make_decision(
            context={"proposal": "Expand to EU market", "budget": 2_000_000},
            mode="autonomous",
        )
        print(decision["decision"])
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a LeadershipAgent.

        Args:
            agent_id: Unique identifier for this agent.
            name: Human-readable agent name.
            role: Agent role (defaults to ``"leader"``).
            purpose: Leadership purpose (defaults to standard leadership
                purpose if not provided).
            purpose_scope: Scope/boundaries of the purpose.
            tools: Tools available to the agent.
            system_message: System message for the agent.
            adapter_name: LoRA adapter name (defaults to ``"leadership"``).
            config: Optional configuration dictionary.
            **kwargs: Additional keyword arguments forwarded to
                :class:`~purpose_driven_agent.PurposeDrivenAgent`.
        """
        if purpose is None:
            purpose = (
                "Leadership: Strategic decision-making, team coordination, "
                "and organisational guidance"
            )
        if adapter_name is None:
            adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Leadership and decision-making domain"

        super().__init__(
            agent_id=agent_id,
            purpose=purpose,
            purpose_scope=purpose_scope,
            tools=tools,
            system_message=system_message,
            adapter_name=adapter_name,
            name=name,
            role=role or "leader",
            config=config,
            **kwargs,
        )

        self.decisions_made: List[Dict[str, Any]] = []
        self.stakeholders: List[str] = []

    # ------------------------------------------------------------------
    # Abstract method implementation
    # ------------------------------------------------------------------

    def get_agent_type(self) -> List[str]:
        """
        Return ``["leadership"]``, selecting the leadership LoRA adapter persona.

        Queries the AOS registry and falls back to ``["leadership"]`` if the
        persona is unavailable.

        Returns:
            ``["leadership"]``
        """
        available = self.get_available_personas()
        if "leadership" not in available:
            self.logger.warning(
                "'leadership' persona not in AOS registry, using default"
            )
        return ["leadership"]

    # ------------------------------------------------------------------
    # Leadership capabilities
    # ------------------------------------------------------------------

    async def make_decision(
        self,
        context: Dict[str, Any],
        stakeholders: Optional[List[str]] = None,
        mode: str = "autonomous",
    ) -> Dict[str, Any]:
        """
        Make a decision based on the provided context.

        Records the decision with a unique ID, timestamp, and metadata in
        :attr:`decisions_made` for provenance tracking.

        Args:
            context: Decision context and relevant inputs.
            stakeholders: Optional list of stakeholder agent IDs to involve
                (used only in ``"consensus"`` mode).
            mode: Decision mode.  One of:

                - ``"autonomous"`` (default) — agent decides independently.
                - ``"consensus"`` — consult stakeholders before deciding.
                - ``"delegated"`` — delegate the decision.

        Returns:
            Decision dictionary with keys:

            - ``"id"`` — unique decision UUID.
            - ``"agent_id"`` — this agent's ID.
            - ``"context"`` — the provided context dict.
            - ``"mode"`` — decision mode used.
            - ``"stakeholders"`` — list of consulted stakeholders.
            - ``"timestamp"`` — ISO-8601 timestamp.
            - ``"decision"`` — outcome from :meth:`_evaluate_decision`.
            - ``"confidence"`` — confidence score (0.0–1.0).
            - ``"rationale"`` — rationale string.
        """
        decision: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "agent_id": self.agent_id,
            "context": context,
            "mode": mode,
            "stakeholders": stakeholders or [],
            "timestamp": datetime.utcnow().isoformat(),
            "decision": await self._evaluate_decision(context),
            "confidence": 0.0,
            "rationale": "",
        }
        self.decisions_made.append(decision)
        self.purpose_metrics["decisions_made"] += 1
        self.logger.info(
            "Decision made by '%s' (mode=%s): id=%s",
            self.agent_id,
            mode,
            decision["id"],
        )
        return decision

    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate and produce a decision outcome.

        Override in subclasses to implement domain-specific decision logic.

        Args:
            context: Decision context.

        Returns:
            Decision outcome dict.  Default returns ``{"decision": "pending",
            "reason": "not_implemented"}``.
        """
        return {"decision": "pending", "reason": "not_implemented"}

    async def consult_stakeholders(
        self,
        stakeholders: List[str],
        topic: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Consult stakeholder agents on a topic.

        This method requires message bus integration (e.g. Azure Service Bus)
        to send queries to other agents and collect responses.

        Args:
            stakeholders: List of agent IDs to consult.
            topic: Topic of the consultation.
            context: Context for the consultation.

        Raises:
            NotImplementedError: Always — wire up a message bus implementation
                in a subclass or via dependency injection.
        """
        raise NotImplementedError(
            "Stakeholder consultation requires message bus integration. "
            "Override consult_stakeholders() and integrate with a message bus."
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_decision_history(
        self, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Return recent decisions made by this agent.

        Args:
            limit: Maximum number of decisions to return (newest last).

        Returns:
            List of decision dicts.
        """
        return self.decisions_made[-limit:]
