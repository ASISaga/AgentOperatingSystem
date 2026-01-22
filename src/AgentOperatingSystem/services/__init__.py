"""
AOS Services - Service interfaces for clean dependency injection.
"""

# v2.0.0 - Canonical service interfaces
from .service_interfaces import (
    IStorageService,
    IMessagingService,
    IWorkflowService,
    IAuthService
)

__all__ = [
    'IStorageService',
    'IMessagingService',
    'IWorkflowService',
    'IAuthService'
]
