"""
AOS Authentication Module

Authentication and authorization system for AOS.
"""

from .manager import AuthenticationError, AuthManager

__all__ = [
    "AuthManager",
    "AuthenticationError"
]
