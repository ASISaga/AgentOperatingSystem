"""
AOS Authentication Module

Authentication and authorization system for AOS.
"""

from .manager import AuthManager, AuthenticationError

__all__ = [
    "AuthManager",
    "AuthenticationError"
]
