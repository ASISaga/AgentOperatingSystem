"""
AOS Services - Service interfaces for clean dependency injection.
"""

from .interfaces import IStorageService, IMessagingService, IWorkflowService, IAuthService

__all__ = [
    'IStorageService',
    'IMessagingService',
    'IWorkflowService',
    'IAuthService'
]
