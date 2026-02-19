#!/usr/bin/env python3
"""
Tests for workflow failure classification logic.

This script validates the failure classification patterns used in the 
GitHub Actions workflow to distinguish between logic and environmental failures.
"""

import re
import sys
from typing import List, Tuple


class FailureType:
    """Failure type constants."""
    LOGIC = "logic"
    ENVIRONMENTAL = "environmental"
    UNKNOWN = "unknown"


class WorkflowFailureClassifier:
    """
    Replicates the failure classification logic from the GitHub workflow.
    
    This allows testing the patterns without running the full workflow.
    """
    
    # Logic failure patterns (from workflow)
    LOGIC_PATTERNS = [
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
        r"error\s*bcp\d+",
        r"invalidtemplatedeployment",
        r"template deployment.*is not valid",
    ]
    
    # Environmental failure patterns (from workflow)
    ENVIRONMENTAL_PATTERNS = [
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
        r"code:\s*conflict",
        r"another operation.*in progress",
    ]
    
    def classify(self, error_message: str) -> str:
        """
        Classify an error message.
        
        Args:
            error_message: The error message to classify
            
        Returns:
            FailureType constant
        """
        if not error_message:
            return FailureType.UNKNOWN
        
        # Check logic patterns
        for pattern in self.LOGIC_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                return FailureType.LOGIC
        
        # Check environmental patterns
        for pattern in self.ENVIRONMENTAL_PATTERNS:
            if re.search(pattern, error_message, re.IGNORECASE):
                return FailureType.ENVIRONMENTAL
        
        return FailureType.UNKNOWN


def test_logic_failures() -> List[Tuple[str, bool]]:
    """Test logic failure classification."""
    classifier = WorkflowFailureClassifier()
    
    test_cases = [
        ("Bicep lint error found in template", FailureType.LOGIC),
        ("Syntax error on line 42", FailureType.LOGIC),
        ("Template validation failed", FailureType.LOGIC),
        ("Invalid parameter: location", FailureType.LOGIC),
        ("Missing required parameter: resourceGroup", FailureType.LOGIC),
        ("Error BCP123: Property not allowed", FailureType.LOGIC),
        ("Circular dependency detected in module", FailureType.LOGIC),
        ("Resource type 'Microsoft.Foo/Bar' not found", FailureType.LOGIC),
        ("API version '2023-01-01' not supported", FailureType.LOGIC),
        ("Deployment template validation error", FailureType.LOGIC),
        ("Parameter must be a string", FailureType.LOGIC),
    ]
    
    results = []
    for message, expected in test_cases:
        actual = classifier.classify(message)
        success = actual == expected
        results.append((message, success))
        
        status = "✅" if success else "❌"
        print(f"{status} Logic: '{message}' -> {actual} (expected {expected})")
    
    return results


def test_environmental_failures() -> List[Tuple[str, bool]]:
    """Test environmental failure classification."""
    classifier = WorkflowFailureClassifier()
    
    test_cases = [
        ("Request timeout after 30 seconds", FailureType.ENVIRONMENTAL),
        ("Azure service throttled the request", FailureType.ENVIRONMENTAL),
        ("Rate limit exceeded", FailureType.ENVIRONMENTAL),
        ("Service unavailable, please retry", FailureType.ENVIRONMENTAL),
        ("Internal server error (500)", FailureType.ENVIRONMENTAL),
        ("Network error: connection failed", FailureType.ENVIRONMENTAL),
        ("Connection refused by remote host", FailureType.ENVIRONMENTAL),
        ("Temporary failure, retry later", FailureType.ENVIRONMENTAL),
        ("Quota exceeded for this subscription", FailureType.ENVIRONMENTAL),
        ("Capacity unavailable in region eastus", FailureType.ENVIRONMENTAL),
        ("Region unavailable", FailureType.ENVIRONMENTAL),
        ("SKU not available in this region", FailureType.ENVIRONMENTAL),
        ("Conflict with another operation in progress", FailureType.ENVIRONMENTAL),
        ("Connection timeout", FailureType.ENVIRONMENTAL),
        ("Throttling occurred", FailureType.ENVIRONMENTAL),
    ]
    
    results = []
    for message, expected in test_cases:
        actual = classifier.classify(message)
        success = actual == expected
        results.append((message, success))
        
        status = "✅" if success else "❌"
        print(f"{status} Environmental: '{message}' -> {actual} (expected {expected})")
    
    return results


def test_real_world_errors() -> List[Tuple[str, bool]]:
    """Test with real-world error messages."""
    classifier = WorkflowFailureClassifier()
    
    test_cases = [
        (
            "ERROR: (InvalidTemplateDeployment) The template deployment 'main' is not valid according to the validation procedure.",
            FailureType.LOGIC
        ),
        (
            "Code: Conflict\nMessage: Another operation on this or dependent resource is in progress.",
            FailureType.ENVIRONMENTAL
        ),
        (
            "ERROR: Error BCP029: The resource type is not valid. Specify a valid resource type of format '<types>@<apiVersion>'.",
            FailureType.LOGIC
        ),
        (
            "ERROR: The client 'xxx' with object id 'yyy' does not have authorization to perform action 'Microsoft.Resources/deployments/validate/action'",
            FailureType.UNKNOWN  # This is an auth error, not classified
        ),
        (
            "ServiceUnavailable: The service is temporarily unavailable. Please retry your request.",
            FailureType.ENVIRONMENTAL
        ),
        (
            "TooManyRequests: Rate limit is exceeded. Try again in 60 seconds.",
            FailureType.ENVIRONMENTAL
        ),
    ]
    
    results = []
    for message, expected in test_cases:
        actual = classifier.classify(message)
        success = actual == expected
        results.append((message, success))
        
        status = "✅" if success else "❌"
        print(f"{status} Real-world: {message[:60]}... -> {actual} (expected {expected})")
    
    return results


def test_edge_cases() -> List[Tuple[str, bool]]:
    """Test edge cases."""
    classifier = WorkflowFailureClassifier()
    
    test_cases = [
        ("", FailureType.UNKNOWN),
        ("Some random error message", FailureType.UNKNOWN),
        ("ERROR: Something went wrong", FailureType.UNKNOWN),
        ("warning: this is just a warning", FailureType.UNKNOWN),
    ]
    
    results = []
    for message, expected in test_cases:
        actual = classifier.classify(message)
        success = actual == expected
        results.append((message, success))
        
        status = "✅" if success else "❌"
        print(f"{status} Edge case: '{message}' -> {actual} (expected {expected})")
    
    return results


def main():
    """Run all tests."""
    print("=" * 80)
    print("Workflow Failure Classification Tests")
    print("=" * 80)
    print()
    
    print("Testing Logic Failures...")
    print("-" * 80)
    logic_results = test_logic_failures()
    print()
    
    print("Testing Environmental Failures...")
    print("-" * 80)
    env_results = test_environmental_failures()
    print()
    
    print("Testing Real-World Errors...")
    print("-" * 80)
    real_results = test_real_world_errors()
    print()
    
    print("Testing Edge Cases...")
    print("-" * 80)
    edge_results = test_edge_cases()
    print()
    
    # Summary
    all_results = logic_results + env_results + real_results + edge_results
    total = len(all_results)
    passed = sum(1 for _, success in all_results if success)
    failed = total - passed
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {passed/total*100:.1f}%")
    print()
    
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
