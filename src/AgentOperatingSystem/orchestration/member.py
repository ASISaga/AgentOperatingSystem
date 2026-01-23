from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .role import Role


@dataclass
class Member:
    """Represents a member of the autonomous boardroom"""
    agent_id: str
    role: Role
    expertise_domains: List[str]
    lora_adapters: List[str]
    status: str = "active"
    last_activity: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
