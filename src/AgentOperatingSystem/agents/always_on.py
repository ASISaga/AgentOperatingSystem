"""
AlwaysOn Agent - Event-driven, persistent agent model

The AlwaysOnAgent represents the core USP of Agent Operating System:
Unlike traditional AI frameworks that run task-based sessions, AOS agents
are ALWAYS-ON, persistent entities that remain active and respond to events.

Traditional Framework (Task-Based):
    1. Start agent for a specific task
    2. Agent processes the task
    3. Agent completes and terminates
    4. State is lost unless explicitly saved

Agent Operating System (Always-On):
    1. Agent is registered once and stays alive indefinitely
    2. Agent sleeps when idle, conserving resources
    3. Agent awakens automatically when relevant events occur
    4. Agent maintains persistent state across all interactions
    5. Agent can be woken by multiple event types
    6. Agent never terminates unless explicitly deregistered

This model enables:
- Continuous operations without manual intervention
- Context preservation across interactions
- Event-driven reactive behavior
- True "operating system" for agents
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
import asyncio
from .base_agent import BaseAgent


class AlwaysOnAgent(BaseAgent):
    """
    Always-On Agent - The foundational agent type for AOS.
    
    This agent represents the core difference between AOS and traditional
    AI frameworks: it is a permanent, event-driven entity rather than
    a temporary task executor.
    
    Key Features:
    - Persistent: Remains registered and active indefinitely
    - Event-driven: Awakens in response to subscribed events
    - Stateful: Maintains context across all interactions
    - Resource-efficient: Sleeps when idle, awakens on events
    
    Example:
        >>> agent = AlwaysOnAgent(
        ...     agent_id="ceo",
        ...     name="CEO Agent",
        ...     role="executive"
        ... )
        >>> await agent.initialize()
        >>> await agent.subscribe_to_event("DecisionRequested", handler)
        >>> await agent.start()  # Agent now runs indefinitely
        >>> # Agent automatically awakens when DecisionRequested events occur
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        config: Dict[str, Any] = None
    ):
        """
        Initialize an always-on agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable agent name
            role: Agent role/type
            config: Optional configuration dictionary
        """
        super().__init__(agent_id, name, role, config)
        
        # Always-on state tracking
        self.is_running = False
        self.sleep_mode = True
        self.event_subscriptions: Dict[str, List[Callable]] = {}
        self.state_history: List[Dict[str, Any]] = []
        self.wake_count = 0
        self.total_events_processed = 0
        
        # Persistent state - preserved across all events
        self.persistent_state: Dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat(),
            "context": {},
            "memory": [],
            "preferences": {}
        }
        
        self.logger.info(f"AlwaysOnAgent {agent_id} created - will run indefinitely once started")
    
    async def initialize(self) -> bool:
        """
        Initialize agent resources.
        
        For always-on agents, this sets up persistent storage connections,
        event listeners, and recovery mechanisms.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info(f"Initializing always-on agent {self.agent_id}")
            
            # Load any previously saved state
            await self._load_persistent_state()
            
            # Set up event listeners
            await self._setup_event_listeners()
            
            self.state = "initialized"
            self.logger.info(f"Always-on agent {self.agent_id} initialized - ready to start")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize always-on agent {self.agent_id}: {e}")
            return False
    
    async def start(self) -> bool:
        """
        Start agent operations - agent runs indefinitely.
        
        Unlike task-based agents that complete and terminate, always-on agents
        enter a persistent run loop that only exits on explicit shutdown.
        
        Returns:
            True when agent is running
        """
        try:
            self.logger.info(f"Starting always-on agent {self.agent_id} - will run indefinitely")
            
            self.is_running = True
            self.state = "running"
            
            # Enter always-on loop
            asyncio.create_task(self._always_on_loop())
            
            self.logger.info(f"Always-on agent {self.agent_id} is now running and listening for events")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start always-on agent {self.agent_id}: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop agent operations gracefully.
        
        This is rarely called - always-on agents typically run for the
        lifetime of the system. When called, ensures clean shutdown.
        
        Returns:
            True if stopped successfully
        """
        try:
            self.logger.info(f"Stopping always-on agent {self.agent_id}")
            
            # Save persistent state before shutdown
            await self._save_persistent_state()
            
            self.is_running = False
            self.state = "stopped"
            
            self.logger.info(f"Always-on agent {self.agent_id} stopped gracefully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping always-on agent {self.agent_id}: {e}")
            return False
    
    async def subscribe_to_event(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], Any]
    ) -> bool:
        """
        Subscribe to an event type.
        
        When the specified event occurs, the agent will awaken from sleep
        and execute the handler.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event occurs
            
        Returns:
            True if subscription successful
            
        Example:
            >>> async def handle_decision(event):
            ...     return await self.make_decision(event)
            >>> await agent.subscribe_to_event("DecisionRequested", handle_decision)
        """
        try:
            if event_type not in self.event_subscriptions:
                self.event_subscriptions[event_type] = []
            
            self.event_subscriptions[event_type].append(handler)
            
            self.logger.info(
                f"Agent {self.agent_id} subscribed to event: {event_type} "
                f"(total subscriptions: {len(self.event_subscriptions[event_type])})"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe to event {event_type}: {e}")
            return False
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message - awakens agent from sleep if needed.
        
        This is the core of the always-on model: the agent awakens,
        processes the message, updates its persistent state, then
        returns to sleep mode.
        
        Args:
            message: Message payload
            
        Returns:
            Response dictionary
        """
        try:
            # Awaken from sleep
            await self._awaken()
            
            self.logger.info(f"Agent {self.agent_id} processing message: {message.get('type', 'unknown')}")
            
            # Process based on message type
            message_type = message.get("type")
            event_data = message.get("data", {})
            
            result = {"status": "success", "processed_by": self.agent_id}
            
            # Check if we have subscribed handlers for this event
            if message_type in self.event_subscriptions:
                handlers = self.event_subscriptions[message_type]
                handler_results = []
                
                for handler in handlers:
                    try:
                        handler_result = await handler(event_data)
                        handler_results.append(handler_result)
                    except Exception as e:
                        self.logger.error(f"Handler error for {message_type}: {e}")
                        handler_results.append({"error": str(e)})
                
                result["handler_results"] = handler_results
            
            # Update persistent state
            await self._update_persistent_state(message, result)
            
            self.total_events_processed += 1
            
            # Return to sleep
            await self._sleep()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_persistent_state(self) -> Dict[str, Any]:
        """
        Get current persistent state.
        
        Returns:
            Current persistent state dictionary
        """
        return {
            **self.persistent_state,
            "wake_count": self.wake_count,
            "total_events_processed": self.total_events_processed,
            "is_running": self.is_running,
            "sleep_mode": self.sleep_mode,
            "subscriptions": list(self.event_subscriptions.keys())
        }
    
    async def update_context(self, context_update: Dict[str, Any]) -> None:
        """
        Update persistent context.
        
        Context is preserved across all events and agent awakenings.
        
        Args:
            context_update: Dictionary of context updates to merge
        """
        self.persistent_state["context"].update(context_update)
        await self._save_persistent_state()
    
    async def _always_on_loop(self) -> None:
        """
        Main always-on loop - runs indefinitely.
        
        This loop keeps the agent alive and responsive to events.
        It represents the core difference from task-based frameworks.
        """
        self.logger.info(f"Agent {self.agent_id} entered always-on loop")
        
        while self.is_running:
            try:
                # Health check
                if self.wake_count % 100 == 0:  # Periodic logging
                    self.logger.debug(
                        f"Agent {self.agent_id} heartbeat - "
                        f"processed {self.total_events_processed} events, "
                        f"awoken {self.wake_count} times"
                    )
                
                # Sleep briefly to avoid busy-waiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in always-on loop: {e}")
                # Don't exit on errors - always-on agents are resilient
                await asyncio.sleep(5)
        
        self.logger.info(f"Agent {self.agent_id} exited always-on loop")
    
    async def _awaken(self) -> None:
        """Awaken agent from sleep mode."""
        if self.sleep_mode:
            self.sleep_mode = False
            self.wake_count += 1
            self.logger.debug(f"Agent {self.agent_id} awakened (count: {self.wake_count})")
    
    async def _sleep(self) -> None:
        """Put agent into sleep mode."""
        if not self.sleep_mode:
            self.sleep_mode = True
            self.logger.debug(f"Agent {self.agent_id} sleeping")
    
    async def _setup_event_listeners(self) -> None:
        """Set up event listening infrastructure."""
        # This would integrate with the messaging/event bus in production
        self.logger.debug(f"Event listeners set up for agent {self.agent_id}")
    
    async def _load_persistent_state(self) -> None:
        """Load previously saved state."""
        # In production, this would load from storage
        self.logger.debug(f"Loaded persistent state for agent {self.agent_id}")
    
    async def _save_persistent_state(self) -> None:
        """Save persistent state to storage."""
        # In production, this would save to storage
        self.logger.debug(f"Saved persistent state for agent {self.agent_id}")
    
    async def _update_persistent_state(
        self,
        message: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Update persistent state with event processing results."""
        # Add to memory
        self.persistent_state["memory"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "message_type": message.get("type"),
            "result": result
        })
        
        # Keep only recent memory (e.g., last 1000 events)
        if len(self.persistent_state["memory"]) > 1000:
            self.persistent_state["memory"] = self.persistent_state["memory"][-1000:]
        
        # Save to storage
        await self._save_persistent_state()
