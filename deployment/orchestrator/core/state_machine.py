"""
Deployment State Machine

Manages the deployment lifecycle state transitions.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class DeploymentState(Enum):
    """Deployment lifecycle states."""
    
    INITIALIZED = "initialized"
    VALIDATING_PARAMETERS = "validating_parameters"
    LINTING = "linting"
    PLANNING = "planning"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    DEPLOYING = "deploying"
    VERIFYING_HEALTH = "verifying_health"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentStateMachine:
    """
    State machine for managing deployment lifecycle.
    
    Ensures valid state transitions and tracks deployment progress.
    """
    
    # Valid state transitions
    TRANSITIONS = {
        DeploymentState.INITIALIZED: [
            DeploymentState.VALIDATING_PARAMETERS,
            DeploymentState.FAILED
        ],
        DeploymentState.VALIDATING_PARAMETERS: [
            DeploymentState.LINTING,
            DeploymentState.FAILED
        ],
        DeploymentState.LINTING: [
            DeploymentState.PLANNING,
            DeploymentState.FAILED
        ],
        DeploymentState.PLANNING: [
            DeploymentState.AWAITING_CONFIRMATION,
            DeploymentState.DEPLOYING,
            DeploymentState.FAILED
        ],
        DeploymentState.AWAITING_CONFIRMATION: [
            DeploymentState.DEPLOYING,
            DeploymentState.FAILED
        ],
        DeploymentState.DEPLOYING: [
            DeploymentState.VERIFYING_HEALTH,
            DeploymentState.FAILED,
            DeploymentState.ROLLED_BACK
        ],
        DeploymentState.VERIFYING_HEALTH: [
            DeploymentState.COMPLETED,
            DeploymentState.FAILED
        ],
        DeploymentState.COMPLETED: [],
        DeploymentState.FAILED: [DeploymentState.ROLLED_BACK],
        DeploymentState.ROLLED_BACK: []
    }
    
    def __init__(self):
        """Initialize state machine."""
        self.current_state = DeploymentState.INITIALIZED
        self.state_history = [(DeploymentState.INITIALIZED, datetime.utcnow())]
        self.metadata: Dict[str, Any] = {}
    
    def transition_to(self, new_state: DeploymentState, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Transition to a new state.
        
        Args:
            new_state: The target state
            metadata: Optional metadata about the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        if new_state not in self.TRANSITIONS[self.current_state]:
            return False
        
        self.current_state = new_state
        self.state_history.append((new_state, datetime.utcnow()))
        
        if metadata:
            self.metadata[new_state.value] = metadata
        
        return True
    
    def get_state(self) -> DeploymentState:
        """Get current state."""
        return self.current_state
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal (completed or failed)."""
        return self.current_state in [
            DeploymentState.COMPLETED,
            DeploymentState.FAILED,
            DeploymentState.ROLLED_BACK
        ]
    
    def get_history(self) -> list:
        """Get state transition history."""
        return self.state_history.copy()
    
    def get_duration(self) -> float:
        """Get total duration in seconds."""
        if len(self.state_history) < 2:
            return 0.0
        
        start_time = self.state_history[0][1]
        end_time = self.state_history[-1][1]
        return (end_time - start_time).total_seconds()
