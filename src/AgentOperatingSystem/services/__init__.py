"""
AOS Services - Service interfaces for clean dependency injection.
"""

from .interfaces import IStorageService, IMessagingService, IWorkflowService, IAuthService

# Import enhanced service interfaces from migration
try:
    from .service_interfaces import (
        IStorageService as EnhancedIStorageService,
        IMessagingService as EnhancedIMessagingService,
        IWorkflowService as EnhancedIWorkflowService,
        IAuthService as EnhancedIAuthService
    )
    HAS_ENHANCED = True
except ImportError:
    HAS_ENHANCED = False

base_exports = [
    'IStorageService',
    'IMessagingService',
    'IWorkflowService',
    'IAuthService'
]

if HAS_ENHANCED:
    base_exports.extend([
        'EnhancedIStorageService',
        'EnhancedIMessagingService',
        'EnhancedIWorkflowService',
        'EnhancedIAuthService'
    ])

__all__ = base_exports
