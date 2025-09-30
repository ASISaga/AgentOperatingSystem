"""
AOS Core Module

Core infrastructure components for the Agent Operating System.
"""

from .system import AgentOperatingSystem
from .config import AOSConfig, default_config

__all__ = [
    "AgentOperatingSystem",
    "AOSConfig", 
    "default_config"
]