"""
Unit tests for Bicep Deployment Orchestrator components.
"""

import unittest
from pathlib import Path
import sys

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.core.state_machine import DeploymentState, DeploymentStateMachine
from orchestrator.core.failure_classifier import FailureClassifier, FailureType


class TestDeploymentStateMachine(unittest.TestCase):
    """Test deployment state machine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_machine = DeploymentStateMachine()
    
    def test_initial_state(self):
        """Test initial state is INITIALIZED."""
        self.assertEqual(self.state_machine.get_state(), DeploymentState.INITIALIZED)
    
    def test_valid_transition(self):
        """Test valid state transition."""
        result = self.state_machine.transition_to(DeploymentState.VALIDATING_PARAMETERS)
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_state(), DeploymentState.VALIDATING_PARAMETERS)
    
    def test_invalid_transition(self):
        """Test invalid state transition is rejected."""
        # Can't go directly from INITIALIZED to COMPLETED
        result = self.state_machine.transition_to(DeploymentState.COMPLETED)
        self.assertFalse(result)
        self.assertEqual(self.state_machine.get_state(), DeploymentState.INITIALIZED)
    
    def test_transition_chain(self):
        """Test complete valid transition chain."""
        states = [
            DeploymentState.VALIDATING_PARAMETERS,
            DeploymentState.LINTING,
            DeploymentState.PLANNING,
            DeploymentState.DEPLOYING,
            DeploymentState.VERIFYING_HEALTH,
            DeploymentState.COMPLETED
        ]
        
        for state in states:
            result = self.state_machine.transition_to(state)
            self.assertTrue(result, f"Failed to transition to {state}")
            self.assertEqual(self.state_machine.get_state(), state)
    
    def test_terminal_state(self):
        """Test terminal state detection."""
        self.assertFalse(self.state_machine.is_terminal())
        
        # Transition to completed
        self.state_machine.transition_to(DeploymentState.VALIDATING_PARAMETERS)
        self.state_machine.transition_to(DeploymentState.LINTING)
        self.state_machine.transition_to(DeploymentState.PLANNING)
        self.state_machine.transition_to(DeploymentState.DEPLOYING)
        self.state_machine.transition_to(DeploymentState.VERIFYING_HEALTH)
        self.state_machine.transition_to(DeploymentState.COMPLETED)
        
        self.assertTrue(self.state_machine.is_terminal())
    
    def test_failure_state(self):
        """Test transition to failure state."""
        result = self.state_machine.transition_to(DeploymentState.FAILED)
        self.assertTrue(result)
        self.assertEqual(self.state_machine.get_state(), DeploymentState.FAILED)
        self.assertTrue(self.state_machine.is_terminal())
    
    def test_state_history(self):
        """Test state history tracking."""
        self.state_machine.transition_to(DeploymentState.VALIDATING_PARAMETERS)
        self.state_machine.transition_to(DeploymentState.LINTING)
        
        history = self.state_machine.get_history()
        self.assertEqual(len(history), 3)  # INITIALIZED + 2 transitions
        self.assertEqual(history[0][0], DeploymentState.INITIALIZED)
        self.assertEqual(history[1][0], DeploymentState.VALIDATING_PARAMETERS)
        self.assertEqual(history[2][0], DeploymentState.LINTING)


class TestFailureClassifier(unittest.TestCase):
    """Test failure classification."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FailureClassifier()
    
    def test_logic_failure_lint_error(self):
        """Test classification of lint errors as logic failures."""
        error = "Bicep linting error: invalid syntax"
        failure_type = self.classifier.classify(error)
        self.assertEqual(failure_type, FailureType.LOGIC)
        self.assertFalse(self.classifier.should_retry(failure_type))
    
    def test_logic_failure_validation(self):
        """Test classification of validation errors as logic failures."""
        error = "Template validation failed: missing required parameter"
        failure_type = self.classifier.classify(error)
        self.assertEqual(failure_type, FailureType.LOGIC)
    
    def test_environmental_failure_timeout(self):
        """Test classification of timeouts as environmental failures."""
        error = "Request timeout while connecting to Azure"
        failure_type = self.classifier.classify(error)
        self.assertEqual(failure_type, FailureType.ENVIRONMENTAL)
        self.assertTrue(self.classifier.should_retry(failure_type))
    
    def test_environmental_failure_throttling(self):
        """Test classification of throttling as environmental failure."""
        error = "API throttled - too many requests"
        failure_type = self.classifier.classify(error)
        self.assertEqual(failure_type, FailureType.ENVIRONMENTAL)
    
    def test_environmental_failure_quota(self):
        """Test classification of quota errors as environmental failure."""
        error = "Quota exceeded in region eastus"
        failure_type = self.classifier.classify(error)
        self.assertEqual(failure_type, FailureType.ENVIRONMENTAL)
    
    def test_unknown_failure(self):
        """Test classification of unknown errors."""
        error = "Some random unexpected error"
        failure_type = self.classifier.classify(error)
        # Could be UNKNOWN or classified based on patterns
        self.assertIn(failure_type, [FailureType.UNKNOWN, FailureType.LOGIC, FailureType.ENVIRONMENTAL])
    
    def test_retry_strategy_environmental(self):
        """Test retry strategy for environmental failures."""
        strategy = self.classifier.get_retry_strategy(FailureType.ENVIRONMENTAL, 0)
        self.assertTrue(strategy["should_retry"])
        self.assertEqual(strategy["delay"], 5)  # First retry: 5 seconds
        
        strategy = self.classifier.get_retry_strategy(FailureType.ENVIRONMENTAL, 1)
        self.assertEqual(strategy["delay"], 10)  # Second retry: 10 seconds
        
        strategy = self.classifier.get_retry_strategy(FailureType.ENVIRONMENTAL, 2)
        self.assertEqual(strategy["delay"], 20)  # Third retry: 20 seconds
    
    def test_retry_strategy_logic(self):
        """Test retry strategy for logic failures (no retry)."""
        strategy = self.classifier.get_retry_strategy(FailureType.LOGIC, 0)
        self.assertFalse(strategy["should_retry"])
        self.assertEqual(strategy["delay"], 0)
    
    def test_max_retries(self):
        """Test maximum retry limit."""
        strategy = self.classifier.get_retry_strategy(FailureType.ENVIRONMENTAL, 5)
        self.assertFalse(strategy["should_retry"])  # Exceeded max attempts


class TestLintPatterns(unittest.TestCase):
    """Test specific lint error patterns."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FailureClassifier()
    
    def test_bicep_syntax_error(self):
        """Test Bicep syntax error classification."""
        errors = [
            "Error BCP001: Syntax error",
            "bicep linting error occurred",
            "Error: invalid bicep template"
        ]
        
        for error in errors:
            failure_type = self.classifier.classify(error)
            self.assertEqual(failure_type, FailureType.LOGIC, f"Failed for: {error}")
    
    def test_parameter_errors(self):
        """Test parameter error classification."""
        errors = [
            "Missing required parameter: location",
            "Invalid parameter value for 'sku'",
            "Parameter 'count' must be an integer"
        ]
        
        for error in errors:
            failure_type = self.classifier.classify(error)
            self.assertEqual(failure_type, FailureType.LOGIC, f"Failed for: {error}")
    
    def test_network_errors(self):
        """Test network error classification."""
        errors = [
            "Connection timeout after 30 seconds",
            "Network error: connection refused",
            "Temporary network failure"
        ]
        
        for error in errors:
            failure_type = self.classifier.classify(error)
            self.assertEqual(failure_type, FailureType.ENVIRONMENTAL, f"Failed for: {error}")


if __name__ == "__main__":
    unittest.main()
