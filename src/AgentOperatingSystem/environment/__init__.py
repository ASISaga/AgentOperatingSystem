"""
AOS Environment Module

Environment variable and configuration management for AOS.
"""

from .manager import EnvironmentManager, EnvironmentError, env_manager

__all__ = [
    "EnvironmentManager",
    "EnvironmentError",
    "env_manager"
]