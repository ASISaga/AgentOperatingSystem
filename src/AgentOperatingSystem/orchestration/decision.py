from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Decision:
    """Represents a decision made by the boardroom"""
    decision_id: str
    topic: str
    decision_type: str
    participants: List[str]
    outcome: Dict[str, Any]
    confidence_score: float
    timestamp: datetime
    implementation_status: str = "pending"
    audit_trail: List[str] = field(default_factory=list)
