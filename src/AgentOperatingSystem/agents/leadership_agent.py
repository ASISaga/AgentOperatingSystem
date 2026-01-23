"""
LeadershipAgent - Leadership and decision-making capabilities.
Extends PurposeDrivenAgent with leadership-specific functionality.

The Leadership purpose is mapped to the "leadership" LoRA adapter, which provides
leadership-specific domain knowledge and agent persona. The core purpose is added
to the primary LLM context to guide agent behavior.
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

    The Leadership purpose is mapped to the "leadership" LoRA adapter, which provides
    leadership-specific domain knowledge and agent persona. The core purpose is added
    to the primary LLM context to guide agent behavior.
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
        # Default leadership purpose and adapter if not provided
        if purpose is None:
            purpose = "Leadership: Strategic decision-making, team coordination, and organizational guidance"
        if adapter_name is None:
            adapter_name = "leadership"
        if purpose_scope is None:
            purpose_scope = "Leadership and decision-making domain"

        # Pass all parameters to parent, including legacy compatibility attributes
        super().__init__(
            agent_id=agent_id,
            purpose=purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=adapter_name,
            name=name,
            role=role or "leader",
            config=config
        )

        self.decisions_made = []
        self.stakeholders = []

    def get_agent_type(self) -> str:
        """
        Get the agent type.
        
        Returns:
            "leadership" - identifies this as a leadership agent
        """
        return "leadership"

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
