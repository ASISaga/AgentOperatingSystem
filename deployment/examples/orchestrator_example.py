#!/usr/bin/env python3
"""
Example: Using the Bicep Deployment Orchestrator

This example demonstrates how to use the orchestrator components.
"""

import sys
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.core.state_machine import DeploymentStateMachine, DeploymentState
from orchestrator.core.failure_classifier import FailureClassifier

def example_state_machine():
    """Example: Track deployment state transitions."""
    print("=" * 60)
    print("State Machine Example")
    print("=" * 60)
    
    state_machine = DeploymentStateMachine()
    
    # Simulate deployment lifecycle
    states = [
        DeploymentState.VALIDATING_PARAMETERS,
        DeploymentState.LINTING,
        DeploymentState.PLANNING,
        DeploymentState.DEPLOYING,
        DeploymentState.VERIFYING_HEALTH,
        DeploymentState.COMPLETED
    ]
    
    print("\nSimulating deployment states:\n")
    
    for state in states:
        success = state_machine.transition_to(state)
        if success:
            print(f"✅ Transitioned to: {state.value}")
        else:
            print(f"❌ Failed to transition to: {state.value}")
    
    # Get history
    history = state_machine.get_history()
    print(f"\nTotal transitions: {len(history)}")
    print(f"Duration: {state_machine.get_duration():.2f} seconds")
    print(f"Terminal state: {state_machine.is_terminal()}")


def example_failure_classification():
    """Example: Classify different failure types."""
    print("\n" + "=" * 60)
    print("Failure Classification Example")
    print("=" * 60)
    
    classifier = FailureClassifier()
    
    test_errors = [
        ("Bicep linting error: invalid syntax", "Logic error"),
        ("Template validation failed: missing parameter", "Logic error"),
        ("Request timeout while connecting to Azure", "Environmental error"),
        ("API throttled - too many requests", "Environmental error"),
        ("Quota exceeded in region eastus", "Environmental error"),
    ]
    
    print("\nClassifying errors:\n")
    
    for error, expected_type in test_errors:
        failure_type = classifier.classify(error)
        should_retry = classifier.should_retry(failure_type)
        
        print(f"Error: {error}")
        print(f"Type: {failure_type.value} ({expected_type})")
        print(f"Should retry: {'Yes' if should_retry else 'No'}")
        
        if should_retry:
            strategy = classifier.get_retry_strategy(failure_type, 0)
            print(f"First retry in: {strategy['delay']} seconds")
        
        print()


if __name__ == "__main__":
    example_state_machine()
    example_failure_classification()
    
    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)
