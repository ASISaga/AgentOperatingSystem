"""
State machine pattern for AgentOperatingSystem

Explicit lifecycle states for decisions, approvals, incidents, audits
with timeout and escalation rules.
"""

from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging


logger = logging.getLogger(__name__)


class State(BaseModel):
    """A state in the state machine"""
    name: str
    is_terminal: bool = False  # Terminal states cannot transition
    timeout_seconds: Optional[int] = None
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True


class Transition(BaseModel):
    """A transition between states"""
    from_state: str
    to_state: str
    event: str
    guard: Optional[Callable[[Dict[str, Any]], bool]] = None  # Condition to allow transition
    action: Optional[Callable[[Dict[str, Any]], None]] = None  # Action to perform during transition

    class Config:
        arbitrary_types_allowed = True


class StateMachineConfig(BaseModel):
    """Configuration for a state machine"""
    name: str
    states: List[State]
    transitions: List[Transition]
    initial_state: str

    class Config:
        arbitrary_types_allowed = True


class StateMachineInstance(BaseModel):
    """An instance of a state machine with current state"""
    instance_id: str
    machine_name: str
    current_state: str
    context: Dict[str, Any] = Field(default_factory=dict)
    state_entered_at: datetime = Field(default_factory=datetime.utcnow)
    transition_history: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StateMachine:
    """
    Generic state machine implementation.

    Supports:
    - Explicit states with enter/exit hooks
    - Guarded transitions
    - Timeout-based automatic transitions
    - Escalation rules
    """

    def __init__(self, config: StateMachineConfig):
        """
        Initialize state machine.

        Args:
            config: State machine configuration
        """
        self.config = config
        self._states = {s.name: s for s in config.states}
        self._transitions: Dict[str, List[Transition]] = {}

        # Index transitions by from_state for quick lookup
        for transition in config.transitions:
            if transition.from_state not in self._transitions:
                self._transitions[transition.from_state] = []
            self._transitions[transition.from_state].append(transition)

        # Validate initial state exists
        if config.initial_state not in self._states:
            raise ValueError(f"Initial state {config.initial_state} not found in states")

    def create_instance(self, instance_id: str, initial_context: Optional[Dict[str, Any]] = None) -> StateMachineInstance:
        """
        Create a new state machine instance.

        Args:
            instance_id: Unique identifier for this instance
            initial_context: Initial context data

        Returns:
            New state machine instance
        """
        instance = StateMachineInstance(
            instance_id=instance_id,
            machine_name=self.config.name,
            current_state=self.config.initial_state,
            context=initial_context or {}
        )

        # Call on_enter for initial state
        initial_state = self._states[self.config.initial_state]
        if initial_state.on_enter:
            initial_state.on_enter(instance.context)

        return instance

    def transition(
        self,
        instance: StateMachineInstance,
        event: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Attempt to transition the instance based on an event.

        Args:
            instance: State machine instance to transition
            event: Event triggering the transition
            event_data: Optional data associated with the event

        Returns:
            True if transition occurred, False otherwise
        """
        current_state = instance.current_state

        # Check if current state is terminal
        if self._states[current_state].is_terminal:
            logger.warning(
                f"Cannot transition from terminal state {current_state} "
                f"for instance {instance.instance_id}"
            )
            return False

        # Find matching transition
        transitions = self._transitions.get(current_state, [])
        for transition in transitions:
            if transition.event == event:
                # Check guard condition if present
                if transition.guard:
                    context = {**instance.context, **(event_data or {})}
                    if not transition.guard(context):
                        logger.debug(
                            f"Guard condition failed for transition {current_state} -> "
                            f"{transition.to_state} on event {event}"
                        )
                        continue

                # Execute transition
                return self._execute_transition(instance, transition, event_data)

        logger.warning(
            f"No valid transition found for instance {instance.instance_id} "
            f"from state {current_state} on event {event}"
        )
        return False

    def _execute_transition(
        self,
        instance: StateMachineInstance,
        transition: Transition,
        event_data: Optional[Dict[str, Any]]
    ) -> bool:
        """Execute a transition"""
        old_state = instance.current_state
        new_state = transition.to_state

        # Validate new state exists
        if new_state not in self._states:
            logger.error(f"Target state {new_state} not found")
            return False

        # Call on_exit for old state
        old_state_obj = self._states[old_state]
        if old_state_obj.on_exit:
            old_state_obj.on_exit(instance.context)

        # Execute transition action if present
        if transition.action:
            context = {**instance.context, **(event_data or {})}
            transition.action(context)

        # Update instance
        instance.current_state = new_state
        instance.state_entered_at = datetime.utcnow()

        # Update context with event data
        if event_data:
            instance.context.update(event_data)

        # Record transition in history
        instance.transition_history.append({
            "from_state": old_state,
            "to_state": new_state,
            "event": transition.event,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Call on_enter for new state
        new_state_obj = self._states[new_state]
        if new_state_obj.on_enter:
            new_state_obj.on_enter(instance.context)

        logger.info(
            f"Instance {instance.instance_id} transitioned from "
            f"{old_state} to {new_state} on event {transition.event}"
        )

        return True

    def check_timeout(self, instance: StateMachineInstance) -> Optional[str]:
        """
        Check if current state has timed out.

        Args:
            instance: State machine instance to check

        Returns:
            Timeout event name if timed out, None otherwise
        """
        current_state_obj = self._states[instance.current_state]

        if current_state_obj.timeout_seconds is None:
            return None

        elapsed = (datetime.utcnow() - instance.state_entered_at).total_seconds()

        if elapsed >= current_state_obj.timeout_seconds:
            logger.warning(
                f"State {instance.current_state} timed out for instance "
                f"{instance.instance_id} after {elapsed:.1f}s"
            )
            return f"{instance.current_state}_timeout"

        return None

    def get_available_events(self, instance: StateMachineInstance) -> List[str]:
        """
        Get list of events that can trigger transitions from current state.

        Args:
            instance: State machine instance

        Returns:
            List of event names
        """
        transitions = self._transitions.get(instance.current_state, [])
        return [t.event for t in transitions]

    def is_terminal(self, instance: StateMachineInstance) -> bool:
        """Check if instance is in a terminal state"""
        return self._states[instance.current_state].is_terminal


# Predefined state machines for common workflows

def create_decision_state_machine() -> StateMachine:
    """Create state machine for decision workflow"""
    config = StateMachineConfig(
        name="DecisionWorkflow",
        initial_state="pending",
        states=[
            State(name="pending", timeout_seconds=86400),  # 24 hours
            State(name="under_review", timeout_seconds=259200),  # 3 days
            State(name="approved", is_terminal=True),
            State(name="rejected", is_terminal=True),
            State(name="escalated", timeout_seconds=172800),  # 2 days
        ],
        transitions=[
            Transition(from_state="pending", to_state="under_review", event="start_review"),
            Transition(from_state="pending", to_state="escalated", event="pending_timeout"),
            Transition(from_state="under_review", to_state="approved", event="approve"),
            Transition(from_state="under_review", to_state="rejected", event="reject"),
            Transition(from_state="under_review", to_state="escalated", event="escalate"),
            Transition(from_state="escalated", to_state="approved", event="approve"),
            Transition(from_state="escalated", to_state="rejected", event="reject"),
        ]
    )
    return StateMachine(config)


def create_incident_state_machine() -> StateMachine:
    """Create state machine for incident workflow"""
    config = StateMachineConfig(
        name="IncidentWorkflow",
        initial_state="reported",
        states=[
            State(name="reported", timeout_seconds=3600),  # 1 hour
            State(name="acknowledged", timeout_seconds=14400),  # 4 hours
            State(name="investigating", timeout_seconds=28800),  # 8 hours
            State(name="resolved", timeout_seconds=86400),  # 24 hours for verification
            State(name="closed", is_terminal=True),
        ],
        transitions=[
            Transition(from_state="reported", to_state="acknowledged", event="acknowledge"),
            Transition(from_state="acknowledged", to_state="investigating", event="start_investigation"),
            Transition(from_state="investigating", to_state="resolved", event="resolve"),
            Transition(from_state="resolved", to_state="closed", event="verify"),
            Transition(from_state="resolved", to_state="investigating", event="reopen"),
        ]
    )
    return StateMachine(config)
