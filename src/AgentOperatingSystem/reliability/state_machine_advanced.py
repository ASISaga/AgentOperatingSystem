"""
Advanced State Machine

Provides distributed state machine capabilities for workflow management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""


class DistributedStateMachine:
    """
    Distributed state machine with persistence and event sourcing.

    Features:
    - State persistence across nodes
    - Event sourcing for state changes
    - State transition validation
    - Rollback capabilities
    - State machine composition
    """

    def __init__(
        self,
        machine_id: str,
        initial_state: str,
        storage_manager=None
    ):
        self.machine_id = machine_id
        self.current_state = initial_state
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(f"AOS.StateMachine.{machine_id}")

        # State machine definition
        self.states = {initial_state}
        self.transitions = {}  # (from_state, event) -> to_state
        self.guards = {}  # (from_state, event) -> guard_function
        self.actions = {}  # (from_state, event) -> action_function

        # Event sourcing
        self.event_log = []
        self.snapshots = []

    def add_state(self, state: str):
        """Add a state to the machine"""
        self.states.add(state)
        self.logger.debug("Added state: %s", state)

    def add_transition(
        self,
        from_state: str,
        event: str,
        to_state: str,
        guard: Optional[Callable] = None,
        action: Optional[Callable] = None
    ):
        """
        Add a state transition.

        Args:
            from_state: Source state
            event: Triggering event
            to_state: Target state
            guard: Optional guard condition
            action: Optional action to execute
        """
        # Ensure states exist
        self.states.add(from_state)
        self.states.add(to_state)

        # Add transition
        transition_key = (from_state, event)
        self.transitions[transition_key] = to_state

        if guard:
            self.guards[transition_key] = guard

        if action:
            self.actions[transition_key] = action

        self.logger.debug(
            "Added transition: %s --[%s]--> %s", from_state, event, to_state
        )

    async def trigger(
        self,
        event: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Trigger an event to transition states.

        Args:
            event: Event to trigger
            context: Optional context data

        Returns:
            True if transition succeeded

        Raises:
            StateTransitionError: If transition is invalid
        """
        transition_key = (self.current_state, event)

        if transition_key not in self.transitions:
            raise StateTransitionError(
                f"No transition from {self.current_state} on event {event}"
            )

        # Check guard condition
        guard = self.guards.get(transition_key)
        if guard and not await self._execute_guard(guard, context):
            self.logger.info(
            "Guard prevented transition from %s on %s", self.current_state, event
        )
            return False

        # Get target state
        to_state = self.transitions[transition_key]

        # Execute action
        action = self.actions.get(transition_key)
        if action:
            await self._execute_action(action, context)

        # Record event
        event_record = {
            "event": event,
            "from_state": self.current_state,
            "to_state": to_state,
            "context": context,
            "timestamp": datetime.utcnow()
        }
        self.event_log.append(event_record)

        # Transition to new state
        old_state = self.current_state
        self.current_state = to_state

        self.logger.info(
            "Transitioned: %s --[%s]--> %s", old_state, event, to_state
        )

        # Persist state
        if self.storage_manager:
            await self._persist_state()

        return True

    async def _execute_guard(
        self,
        guard: Callable,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Execute guard condition"""
        try:
            if asyncio.iscoroutinefunction(guard):
                return await guard(self, context)
            else:
                return guard(self, context)
        except Exception as error:
            self.logger.error("Error in guard: %s", str(error))
            return False

    async def _execute_action(
        self,
        action: Callable,
        context: Optional[Dict[str, Any]]
    ):
        """Execute transition action"""
        try:
            if asyncio.iscoroutinefunction(action):
                await action(self, context)
            else:
                action(self, context)
        except Exception as error:
            self.logger.error("Error in action: %s", str(error))
            raise

    async def _persist_state(self):
        """Persist current state to storage"""
        if not self.storage_manager:
            return

        state_data = {
            "machine_id": self.machine_id,
            "current_state": self.current_state,
            "event_log": self.event_log,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.storage_manager.save(
            key=f"state_machine_{self.machine_id}",
            value=state_data,
            storage_type="blob"
        )

    async def restore_from_events(self):
        """Restore state machine from event log (event sourcing)"""
        self.logger.info("Restoring state from %s events", len(self.event_log))

        # Reset to initial state
        # Would restore from storage in real implementation

        # Replay events
        for event_record in self.event_log:
            event = event_record["event"]
            context = event_record.get("context")
            await self.trigger(event, context)

    def create_snapshot(self):
        """Create a snapshot of current state"""
        snapshot = {
            "machine_id": self.machine_id,
            "current_state": self.current_state,
            "event_count": len(self.event_log),
            "timestamp": datetime.utcnow()
        }

        self.snapshots.append(snapshot)
        self.logger.debug("Created snapshot at state %s", self.current_state)

        return snapshot

    async def rollback_to_snapshot(self, snapshot: Dict[str, Any]):
        """Rollback to a previous snapshot"""
        self.logger.info(
            f"Rolling back to snapshot at {snapshot['timestamp']}"
        )

        self.current_state = snapshot["current_state"]

        # Trim event log
        event_count = snapshot["event_count"]
        self.event_log = self.event_log[:event_count]

        if self.storage_manager:
            await self._persist_state()

    def get_available_events(self) -> List[str]:
        """Get list of events available from current state"""
        available = []

        for (from_state, event), to_state in self.transitions.items():
            if from_state == self.current_state:
                available.append(event)

        return available

    def to_dict(self) -> Dict[str, Any]:
        """Export state machine definition"""
        return {
            "machine_id": self.machine_id,
            "current_state": self.current_state,
            "states": list(self.states),
            "transitions": [
                {
                    "from": from_state,
                    "event": event,
                    "to": to_state
                }
                for (from_state, event), to_state in self.transitions.items()
            ],
            "event_count": len(self.event_log)
        }
