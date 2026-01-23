"""
UI Action data model - represents user interface actions in the system
"""
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class UiAction(BaseModel):
    """
    Represents a user interface action for agent interactions
    """
    boardroomId: str
    conversationId: str
    agentId: str
    action: str
    args: Dict[str, Any]
    scope: Literal["local", "network"] = "local"
    correlationId: Optional[str] = None
