"""
Risk registry for AgentOperatingSystem

Tracks risks with likelihood, impact, owner, mitigation plans, and review cadence.
Linked to decisions and incidents.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    """Risk lifecycle status"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class RiskLikelihood(str, Enum):
    """Risk likelihood levels"""
    RARE = "rare"  # < 10%
    UNLIKELY = "unlikely"  # 10-30%
    POSSIBLE = "possible"  # 30-60%
    LIKELY = "likely"  # 60-90%
    ALMOST_CERTAIN = "almost_certain"  # > 90%


class RiskImpact(str, Enum):
    """Risk impact levels"""
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CATASTROPHIC = "catastrophic"


class MitigationPlan(BaseModel):
    """Mitigation plan for a risk"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    actions: List[str] = Field(default_factory=list)
    owner: str
    target_completion: datetime
    status: str = "pending"  # pending, in_progress, completed
    effectiveness: Optional[str] = None  # Assessment of mitigation effectiveness

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RiskEntry(BaseModel):
    """
    Individual risk entry in the registry.
    """
    risk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str

    # Risk assessment
    likelihood: RiskLikelihood
    impact: RiskImpact
    level: RiskLevel  # Calculated from likelihood and impact

    # Ownership and accountability
    owner: str
    identified_by: str
    identified_at: datetime = Field(default_factory=datetime.utcnow)

    # Mitigation
    mitigation_plans: List[MitigationPlan] = Field(default_factory=list)

    # Monitoring
    status: RiskStatus = RiskStatus.IDENTIFIED
    review_cadence_days: int = 30
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None

    # Linkages
    related_decisions: List[str] = Field(default_factory=list)
    related_incidents: List[str] = Field(default_factory=list)

    # Additional context
    category: Optional[str] = None  # e.g., "financial", "operational", "strategic"
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def calculate_level(self) -> RiskLevel:
        """Calculate risk level from likelihood and impact"""
        # Simple risk matrix
        score = 0

        # Likelihood score
        likelihood_scores = {
            RiskLikelihood.RARE: 1,
            RiskLikelihood.UNLIKELY: 2,
            RiskLikelihood.POSSIBLE: 3,
            RiskLikelihood.LIKELY: 4,
            RiskLikelihood.ALMOST_CERTAIN: 5
        }

        # Impact score
        impact_scores = {
            RiskImpact.NEGLIGIBLE: 1,
            RiskImpact.MINOR: 2,
            RiskImpact.MODERATE: 3,
            RiskImpact.MAJOR: 4,
            RiskImpact.CATASTROPHIC: 5
        }

        score = likelihood_scores[self.likelihood] * impact_scores[self.impact]

        # Map score to level
        if score <= 4:
            return RiskLevel.LOW
        elif score <= 9:
            return RiskLevel.MEDIUM
        elif score <= 16:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    def schedule_next_review(self):
        """Schedule next review based on cadence"""
        self.next_review = datetime.utcnow() + timedelta(days=self.review_cadence_days)


class RiskRegistry:
    """
    Registry for tracking and managing organizational risks.

    Provides risk identification, assessment, mitigation tracking,
    and review scheduling capabilities.
    """

    def __init__(self):
        """Initialize risk registry"""
        self._risks: Dict[str, RiskEntry] = {}

    def register_risk(
        self,
        title: str,
        description: str,
        likelihood: RiskLikelihood,
        impact: RiskImpact,
        owner: str,
        identified_by: str,
        category: Optional[str] = None,
        review_cadence_days: int = 30
    ) -> RiskEntry:
        """
        Register a new risk.

        Args:
            title: Risk title
            description: Detailed description
            likelihood: Likelihood of occurrence
            impact: Impact if it occurs
            owner: Person responsible for this risk
            identified_by: Who identified the risk
            category: Risk category
            review_cadence_days: Days between reviews

        Returns:
            Created risk entry
        """
        risk = RiskEntry(
            title=title,
            description=description,
            likelihood=likelihood,
            impact=impact,
            level=RiskLevel.LOW,  # Will be calculated
            owner=owner,
            identified_by=identified_by,
            category=category,
            review_cadence_days=review_cadence_days
        )

        # Calculate risk level
        risk.level = risk.calculate_level()

        # Schedule first review
        risk.schedule_next_review()

        self._risks[risk.risk_id] = risk
        return risk

    def update_risk_assessment(
        self,
        risk_id: str,
        likelihood: Optional[RiskLikelihood] = None,
        impact: Optional[RiskImpact] = None
    ) -> RiskEntry:
        """Update risk assessment"""
        risk = self._risks.get(risk_id)
        if not risk:
            raise ValueError(f"Risk {risk_id} not found")

        if likelihood:
            risk.likelihood = likelihood
        if impact:
            risk.impact = impact

        # Recalculate level
        risk.level = risk.calculate_level()
        risk.last_reviewed = datetime.utcnow()
        risk.schedule_next_review()

        return risk

    def add_mitigation_plan(
        self,
        risk_id: str,
        description: str,
        actions: List[str],
        owner: str,
        target_completion: datetime
    ) -> MitigationPlan:
        """Add a mitigation plan to a risk"""
        risk = self._risks.get(risk_id)
        if not risk:
            raise ValueError(f"Risk {risk_id} not found")

        plan = MitigationPlan(
            description=description,
            actions=actions,
            owner=owner,
            target_completion=target_completion
        )

        risk.mitigation_plans.append(plan)
        risk.status = RiskStatus.MITIGATING

        return plan

    def update_risk_status(self, risk_id: str, status: RiskStatus) -> RiskEntry:
        """Update risk status"""
        risk = self._risks.get(risk_id)
        if not risk:
            raise ValueError(f"Risk {risk_id} not found")

        risk.status = status
        risk.last_reviewed = datetime.utcnow()

        return risk

    def link_to_decision(self, risk_id: str, decision_id: str):
        """Link risk to a decision"""
        risk = self._risks.get(risk_id)
        if not risk:
            raise ValueError(f"Risk {risk_id} not found")

        if decision_id not in risk.related_decisions:
            risk.related_decisions.append(decision_id)

    def link_to_incident(self, risk_id: str, incident_id: str):
        """Link risk to an incident"""
        risk = self._risks.get(risk_id)
        if not risk:
            raise ValueError(f"Risk {risk_id} not found")

        if incident_id not in risk.related_incidents:
            risk.related_incidents.append(incident_id)

    def get_risks_due_for_review(self) -> List[RiskEntry]:
        """Get all risks that are due for review"""
        now = datetime.utcnow()
        return [
            risk for risk in self._risks.values()
            if risk.next_review and risk.next_review <= now
            and risk.status not in [RiskStatus.CLOSED, RiskStatus.ACCEPTED]
        ]

    def query_risks(
        self,
        level: Optional[RiskLevel] = None,
        status: Optional[RiskStatus] = None,
        owner: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[RiskEntry]:
        """
        Query risks with filters.

        Args:
            level: Filter by risk level
            status: Filter by status
            owner: Filter by owner
            category: Filter by category

        Returns:
            List of matching risks
        """
        results = []

        for risk in self._risks.values():
            if level and risk.level != level:
                continue
            if status and risk.status != status:
                continue
            if owner and risk.owner != owner:
                continue
            if category and risk.category != category:
                continue

            results.append(risk)

        return results

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk registry summary statistics"""
        total = len(self._risks)

        by_level = {}
        by_status = {}

        for risk in self._risks.values():
            by_level[risk.level.value] = by_level.get(risk.level.value, 0) + 1
            by_status[risk.status.value] = by_status.get(risk.status.value, 0) + 1

        due_for_review = len(self.get_risks_due_for_review())

        return {
            "total_risks": total,
            "by_level": by_level,
            "by_status": by_status,
            "due_for_review": due_for_review
        }
