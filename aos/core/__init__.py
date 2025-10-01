"""
AOS Core Module

Core infrastructure components for the Agent Operating System.
"""

from .system import AgentOperatingSystem
from .config import AOSConfig, default_config

try:
    from .boardroom import AutonomousBoardroom, BoardroomMember, BoardroomRole, create_autonomous_boardroom
    BOARDROOM_AVAILABLE = True
except ImportError:
    BOARDROOM_AVAILABLE = False

__all__ = [
    "AgentOperatingSystem",
    "AOSConfig", 
    "default_config"
]

if BOARDROOM_AVAILABLE:
    __all__.extend([
        "AutonomousBoardroom", 
        "BoardroomMember",
        "BoardroomRole",
        "create_autonomous_boardroom"
    ])