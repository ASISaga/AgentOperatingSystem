"""
LeadershipAgent - Leadership and decision-making capabilities.
Extends PurposeDrivenAgent with a leadership layer.

Layer stacking architecture:
  - PurposeDrivenAgent.__init__(adapter_name=None) sets up the base layer
    (no adapter at this level since leadership owns its layer).
  - LeadershipAgent.__init__() calls self._add_layer("leadership", context, skills)
    to register the leadership LoRA adapter, domain context, and skill names.

The "leadership" LoRA adapter provides leadership-specific domain knowledge and
agent persona.  The purpose is added to the primary LLM context to guide behavior.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from .purpose_driven import PurposeDrivenAgent


class LeadershipAgent(PurposeDrivenAgent):
    """
    Leadership agent providing:
    - Decision-making capabilities
    - Stakeholder coordination
    - Consensus building
    - Delegation patterns
    - Decision provenance

    LeadershipAgent adds exactly one layer (adapter="leadership") to the
    inherited PurposeDrivenAgent layer stack.  Subclasses (e.g., CMOAgent)
    build on top by calling _add_layer() in their own __init__.
    """

    def __init__(
        self,
        agent_id: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        purpose: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        success_criteria: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        if purpose is None:
            purpose = "Leadership: Strategic decision-making, team coordination, and organizational guidance"
        if purpose_scope is None:
            purpose_scope = "Leadership and decision-making domain"

        # Initialise PurposeDrivenAgent without passing adapter_name so the
        # base layer has no adapter entry.  LeadershipAgent owns its adapter.
        super().__init__(
            agent_id=agent_id,
            purpose=purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=None,   # leadership layer is registered below
            name=name,
            role=role or "leader",
            config=config
        )

        self.decisions_made = []
        self.stakeholders = []

        # Register this class's layer: the "leadership" LoRA adapter together
        # with domain context and the skills introduced at this level.
        leadership_adapter = adapter_name or "leadership"
        self._add_layer(
            adapter_name=leadership_adapter,
            context={
                "domain": "leadership",
                "purpose": self.purpose,
                "capabilities": [
                    "decision_making",
                    "stakeholder_coordination",
                    "consensus_building",
                    "delegation",
                ],
            },
            skills=["make_decision", "consult_stakeholders"],
        )

    async def make_decision(
        self,
        context: Dict[str, Any],
        stakeholders: List[str] = None,
        mode: str = "autonomous"
    ) -> Dict[str, Any]:
        """
        Make a decision based on context.

        Args:
            context: Decision context and inputs
            stakeholders: Optional list of stakeholder agent IDs to consult
            mode: Decision mode ("autonomous", "consensus", "delegated")

        Returns:
            Decision with rationale, confidence, metadata
        """
        decision = {
            "id": str(uuid.uuid4()),
            "agent_id": self.agent_id,
            "context": context,
            "mode": mode,
            "stakeholders": stakeholders or [],
            "timestamp": datetime.utcnow().isoformat(),
            "decision": await self._evaluate_decision(context),
            "confidence": 0.0,
            "rationale": ""
        }

        self.decisions_made.append(decision)
        return decision

    async def _evaluate_decision(self, context: Dict[str, Any]) -> Any:
        """
        Evaluate and make decision. Override in subclasses.

        Args:
            context: Decision context

        Returns:
            Decision outcome
        """
        # Base implementation - override in subclasses
        return {"decision": "pending", "reason": "not_implemented"}

    async def consult_stakeholders(
        self,
        stakeholders: List[str],
        topic: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Consult stakeholder agents on a topic.

        Args:
            stakeholders: List of agent IDs to consult
            topic: Consultation topic
            context: Context for consultation

        Returns:
            List of stakeholder responses
        """
        # TODO: Implement with message bus integration
        raise NotImplementedError("Stakeholder consultation requires message bus integration")
