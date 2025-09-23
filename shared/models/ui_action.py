"""
UI Action data model - represents user interface actions in the system
"""
from pydantic import BaseModel
from typing import Any, Dict, Optional, Literal

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
