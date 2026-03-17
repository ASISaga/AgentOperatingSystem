"""
Failure Classification

Intelligent classification of deployment failures into logic vs environmental categories.
"""

import re
from enum import Enum
from typing import Dict, Any, Optional


class FailureType(Enum):
    """Types of deployment failures."""
    
    LOGIC = "logic"  # Code/template errors
    ENVIRONMENTAL = "environmental"  # Cloud/infrastructure issues
    UNKNOWN = "unknown"


class FailureClassifier:
    """
    Classifies deployment failures to determine appropriate response.
    
    Logic failures halt the process.
    Environmental failures trigger smart retry.
    """
    
    # Patterns indicating logic failures (halt immediately)
    LOGIC_FAILURE_PATTERNS = [
        r"lint.*error",
        r"bicep.*error",
        r"syntax.*error",
        r"validation.*failed",
        r"invalid.*parameter",
        r"invalid.*bicep",
        r"missing.*required.*parameter",
        r"template.*validation.*error",
        r"circular.*dependency",
        r"resource.*type.*not.*found",
        r"api.*version.*not.*supported",
        r"property.*not.*allowed",
        r"deployment.*template.*validation.*failed",
        r"parameter.*must be",
        r"error\s*bcp\d+",  # Bicep error codes
        r"InvalidResourceLocation",       # Resource already exists in different location
        r"InvalidResourceGroupLocation",  # Resource group already exists in different location
        r"already.*exists.*in.*location", # Generic "already exists in location X" messages
        r"resource.*already.*exists.*location",
        r"InvalidTemplateDeployment",     # ARM template deployment validation failure
        r"authorization.*failed.*template.*resource",  # RBAC write denied on template resource
        r"does not have permission to perform action.*Microsoft\.Authorization",  # SP lacks RBAC write
        r"NamespaceUnavailable",          # Service Bus namespace name is invalid or reserved
    ]
    
    # Patterns indicating environmental failures (retry possible)
    ENVIRONMENTAL_FAILURE_PATTERNS = [
        r"timeout",
        r"throttl(ed|ing)",
        r"rate.*limit",
        r"service.*unavailable",
        r"internal.*server.*error",
        r"network.*error",
        r"network.*timeout",
        r"connection.*refused",
        r"connection.*timeout",
        r"temporary.*failure",
        r"quota.*exceeded",
        r"capacity.*unavailable",
        r"region.*unavailable",
        r"sku.*not.*available",
        r"conflict.*another.*operation",
    ]
    
    def __init__(self):
        """Initialize classifier."""
        self.logic_patterns = [re.compile(p, re.IGNORECASE) for p in self.LOGIC_FAILURE_PATTERNS]
        self.env_patterns = [re.compile(p, re.IGNORECASE) for p in self.ENVIRONMENTAL_FAILURE_PATTERNS]
    
    def classify(self, error_message: str, exit_code: Optional[int] = None) -> FailureType:
        """
        Classify a failure based on error message and exit code.
        
        Args:
            error_message: The error message from the failed operation
            exit_code: Optional exit code from the command
            
        Returns:
            FailureType indicating the classification
        """
        if not error_message:
            return FailureType.UNKNOWN
        
        # Check for logic failures first (these take precedence)
        for pattern in self.logic_patterns:
            if pattern.search(error_message):
                return FailureType.LOGIC
        
        # Check for environmental failures
        for pattern in self.env_patterns:
            if pattern.search(error_message):
                return FailureType.ENVIRONMENTAL
        
        # Exit code analysis
        if exit_code is not None:
            # Exit code 1 often indicates logic error in Azure CLI
            if exit_code == 1 and any(term in error_message.lower() 
                                     for term in ["invalid", "error", "failed"]):
                return FailureType.LOGIC
            # Exit codes > 100 often indicate environmental issues
            elif exit_code > 100:
                return FailureType.ENVIRONMENTAL
        
        return FailureType.UNKNOWN
    
    def should_retry(self, failure_type: FailureType) -> bool:
        """
        Determine if a retry should be attempted.
        
        Args:
            failure_type: The classified failure type
            
        Returns:
            True if retry is appropriate, False otherwise
        """
        return failure_type == FailureType.ENVIRONMENTAL
    
    def get_retry_strategy(self, failure_type: FailureType, attempt: int) -> Dict[str, Any]:
        """
        Get retry strategy for a failure type.
        
        Args:
            failure_type: The classified failure type
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Dictionary with retry parameters
        """
        if not self.should_retry(failure_type):
            return {"should_retry": False, "delay": 0, "max_attempts": 0}
        
        # Exponential backoff with jitter
        base_delay = 5  # seconds
        max_delay = 300  # 5 minutes
        max_attempts = 5
        
        delay = min(base_delay * (2 ** attempt), max_delay)
        
        return {
            "should_retry": attempt < max_attempts,
            "delay": delay,
            "max_attempts": max_attempts,
            "attempt": attempt + 1
        }
