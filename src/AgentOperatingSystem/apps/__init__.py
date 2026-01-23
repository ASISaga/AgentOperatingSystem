"""
App Configuration and Registry for AgentOperatingSystem

This module provides the infrastructure for registering and managing apps on AOS.
"""

from .app_config_schema import AgentReference, AppConfiguration, AppRegistry, AppType

__all__ = [
    'AppType',
    'AgentReference',
    'AppConfiguration',
    'AppRegistry'
]
