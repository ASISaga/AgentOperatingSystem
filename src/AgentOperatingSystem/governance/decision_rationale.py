"""
Decision rationale for AgentOperatingSystem

Structured memos captured alongside decisions for precedent and audit.
Queryable for historical context and decision patterns.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionOutcome(str, Enum):
    """Possible decision outcomes"""
    APPROVED = "approved"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class DecisionRationale(BaseModel):
    """
    Structured memo for a decision with full context and reasoning.
    """
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Decision context
    title: str
    description: str
    decision_type: str  # e.g., "budget", "strategic", "operational"
    requester: str
    approvers: List[str] = Field(default_factory=list)

    # Rationale
    problem_statement: str
    proposed_solution: str
    alternatives_considered: List[str] = Field(default_factory=list)
    counter_arguments: List[str] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)

    # Risk and impact
    risks_identified: List[str] = Field(default_factory=list)
    impact_assessment: Dict[str, Any] = Field(default_factory=dict)

    # Outcome
    outcome: Optional[DecisionOutcome] = None
    rationale_for_outcome: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)

    # Precedent and learning
    precedent_decisions: List[str] = Field(default_factory=list)  # Related past decisions
    lessons_learned: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DecisionRationaleStore:
    """
    Store for decision rationales with query capabilities.

    Enables precedent lookup and decision pattern analysis.
    """

    def __init__(self):
        """Initialize decision rationale store"""
        self._rationales: Dict[str, DecisionRationale] = {}

    def create_rationale(
        self,
        title: str,
        description: str,
        decision_type: str,
        requester: str,
        problem_statement: str,
        proposed_solution: str,
        approvers: Optional[List[str]] = None
    ) -> DecisionRationale:
        """
        Create a new decision rationale.

        Args:
            title: Decision title
            description: Detailed description
            decision_type: Type of decision
            requester: Who requested the decision
            problem_statement: Problem being addressed
            proposed_solution: Proposed solution
            approvers: List of approvers

        Returns:
            Created rationale
        """
        rationale = DecisionRationale(
            title=title,
            description=description,
            decision_type=decision_type,
            requester=requester,
            problem_statement=problem_statement,
            proposed_solution=proposed_solution,
            approvers=approvers or []
        )

        self._rationales[rationale.decision_id] = rationale
        return rationale

    def add_alternative(self, decision_id: str, alternative: str):
        """Add an alternative considered"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.alternatives_considered.append(alternative)

    def add_counter_argument(self, decision_id: str, argument: str):
        """Add a counter-argument"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.counter_arguments.append(argument)

    def add_evidence(self, decision_id: str, evidence: str):
        """Add supporting evidence"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.supporting_evidence.append(evidence)

    def add_risk(self, decision_id: str, risk: str):
        """Add identified risk"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.risks_identified.append(risk)

    def set_impact_assessment(self, decision_id: str, assessment: Dict[str, Any]):
        """Set impact assessment"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.impact_assessment = assessment

    def set_outcome(
        self,
        decision_id: str,
        outcome: DecisionOutcome,
        rationale_text: str,
        conditions: Optional[List[str]] = None
    ):
        """
        Set the decision outcome.

        Args:
            decision_id: Decision ID
            outcome: Outcome of the decision
            rationale_text: Rationale for the outcome
            conditions: Any conditions attached to the decision
        """
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.outcome = outcome
        rationale.rationale_for_outcome = rationale_text
        if conditions:
            rationale.conditions = conditions

    def link_precedent(self, decision_id: str, precedent_id: str):
        """Link to a precedent decision"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        if precedent_id not in rationale.precedent_decisions:
            rationale.precedent_decisions.append(precedent_id)

    def add_lessons_learned(self, decision_id: str, lessons: str):
        """Add lessons learned from this decision"""
        rationale = self._rationales.get(decision_id)
        if not rationale:
            raise ValueError(f"Decision {decision_id} not found")

        rationale.lessons_learned = lessons

    def query_rationales(
        self,
        decision_type: Optional[str] = None,
        requester: Optional[str] = None,
        outcome: Optional[DecisionOutcome] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DecisionRationale]:
        """
        Query decision rationales with filters.

        Args:
            decision_type: Filter by decision type
            requester: Filter by requester
            outcome: Filter by outcome
            category: Filter by category
            tags: Filter by tags (must match all)
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number to return

        Returns:
            List of matching rationales
        """
        results = []

        for rationale in self._rationales.values():
            if decision_type and rationale.decision_type != decision_type:
                continue
            if requester and rationale.requester != requester:
                continue
            if outcome and rationale.outcome != outcome:
                continue
            if category and rationale.category != category:
                continue
            if tags and not all(t in rationale.tags for t in tags):
                continue
            if start_time and rationale.timestamp < start_time:
                continue
            if end_time and rationale.timestamp > end_time:
                continue

            results.append(rationale)

            if len(results) >= limit:
                break

        return results

    def find_similar_decisions(
        self,
        decision_id: str,
        limit: int = 10
    ) -> List[DecisionRationale]:
        """
        Find similar decisions based on type, tags, and content.

        Args:
            decision_id: Decision to find similar ones for
            limit: Maximum number to return

        Returns:
            List of similar decisions
        """
        target = self._rationales.get(decision_id)
        if not target:
            raise ValueError(f"Decision {decision_id} not found")

        # Simple similarity based on type and tags
        candidates = []

        for rationale in self._rationales.values():
            if rationale.decision_id == decision_id:
                continue

            score = 0

            # Same type
            if rationale.decision_type == target.decision_type:
                score += 3

            # Common tags
            common_tags = set(rationale.tags) & set(target.tags)
            score += len(common_tags)

            # Same category
            if rationale.category == target.category and rationale.category:
                score += 2

            if score > 0:
                candidates.append((score, rationale))

        # Sort by score and return top results
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in candidates[:limit]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get decision rationale statistics"""
        total = len(self._rationales)

        by_type = {}
        by_outcome = {}

        for rationale in self._rationales.values():
            by_type[rationale.decision_type] = by_type.get(rationale.decision_type, 0) + 1
            if rationale.outcome:
                by_outcome[rationale.outcome.value] = by_outcome.get(rationale.outcome.value, 0) + 1

        return {
            "total_decisions": total,
            "by_type": by_type,
            "by_outcome": by_outcome
        }
