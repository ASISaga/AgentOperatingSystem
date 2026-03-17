"""
App Configuration and Registry for AgentOperatingSystem

This module provides the infrastructure for registering and managing apps on AOS.
"""

from .app_config_schema import (
    AppType,
    AgentReference,
    AppConfiguration,
    AppRegistry
)

__all__ = [
    'AppType',
    'AgentReference',
    'AppConfiguration',
    'AppRegistry'
]
