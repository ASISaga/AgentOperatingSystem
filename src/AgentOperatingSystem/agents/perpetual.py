"""
PerpetualAgent for AgentOperatingSystem (AOS)

The PerpetualAgent represents the core architecture of AOS: agents that run indefinitely
and respond to events, rather than temporary task executors.

Traditional AI frameworks use task-based sessions where agents start, execute, and terminate.
AOS uses perpetual agents that register once and run continuously, awakening on events
while preserving state across their lifetime through MCP context preservation.

PurposeDrivenAgent (from the PurposeDrivenAgent package) inherits from PerpetualAgent
and works against a perpetual, assigned purpose rather than short-term tasks.
PurposeDrivenAgent is the fundamental building block of AgentOperatingSystem.
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import logging
import asyncio
from ..ml.pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer
from ..mcp.context_server import ContextMCPServer
from .base_agent import BaseAgent


class PerpetualAgent(BaseAgent):
    """
    A perpetual agent that runs indefinitely and responds to events.
    
    Key characteristics:
    - Persistent: Remains registered and active indefinitely
    - Event-driven: Awakens in response to events
    - Stateful: Maintains context across all interactions via MCP
    - Resource-efficient: Sleeps when idle, awakens on events
    
    This is the foundational agent type for AOS. PurposeDrivenAgent extends
    this to work against a perpetual, assigned purpose.
    
    Example:
        >>> agent = PerpetualAgent(
        ...     agent_id="ceo",
        ...     adapter_name="ceo"
        ... )
        >>> await agent.subscribe_to_event("DecisionRequested", handler)
        >>> # Agent runs perpetually, responding to events
    """
    
    def __init__(self, agent_id=None, tools=None, system_message=None, adapter_name=None):
        super().__init__(
            agent_id=agent_id or f"perpetual_{adapter_name}" if adapter_name else "perpetual_agent",
            agent_type="perpetual"
        )
        self.tools = tools or []
        self.system_message = system_message or ""
        self.adapter_name = adapter_name  # e.g., 'ceo', 'cfo', 'coo', etc.
        
        # Perpetual operation state
        self.is_running = False
        self.sleep_mode = True
        self.event_subscriptions: Dict[str, List[Callable]] = {}
        self.wake_count = 0
        self.total_events_processed = 0
        
        # Context is preserved via ContextMCPServer (common infrastructure)
        # Each perpetual agent has a dedicated ContextMCPServer instance
        self.mcp_context_server: Optional[ContextMCPServer] = None
        
        self.logger = logging.getLogger(f"aos.perpetual.{self.agent_id}")
        self.logger.info(f"PerpetualAgent {self.agent_id} created - will run indefinitely")

    async def initialize(self) -> bool:
        """
        Initialize agent resources and MCP context server.
        
        For perpetual agents, this sets up the dedicated MCP server for
        context preservation, event listeners, and recovery mechanisms.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info(f"Initializing perpetual agent {self.agent_id}")
            
            # Initialize MCP context server for persistence
            await self._setup_mcp_context_server()
            
            # Load any previously saved context from MCP
            await self._load_context_from_mcp()
            
            # Set up event listeners
            await self._setup_event_listeners()
            
            self.logger.info(f"Perpetual agent {self.agent_id} initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize perpetual agent {self.agent_id}: {e}")
            return False

    async def start(self) -> bool:
        """
        Start perpetual operations - agent runs indefinitely.
        
        Unlike task-based agents that complete and terminate, perpetual agents
        enter an indefinite run loop that only exits on explicit shutdown.
        
        Returns:
            True when agent is running
        """
        try:
            self.logger.info(f"Starting perpetual agent {self.agent_id}")
            
            self.is_running = True
            
            # Enter perpetual loop
            asyncio.create_task(self._perpetual_loop())
            
            self.logger.info(f"Perpetual agent {self.agent_id} is now running indefinitely")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start perpetual agent {self.agent_id}: {e}")
            return False

    async def stop(self) -> bool:
        """
        Stop perpetual operations gracefully.
        
        This is rarely called - perpetual agents typically run for the
        lifetime of the system. When called, ensures clean shutdown and
        context preservation to MCP.
        
        Returns:
            True if stopped successfully
        """
        try:
            self.logger.info(f"Stopping perpetual agent {self.agent_id}")
            
            # Save context to MCP before shutdown
            await self._save_context_to_mcp()
            
            self.is_running = False
            
            self.logger.info(f"Perpetual agent {self.agent_id} stopped gracefully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping perpetual agent {self.agent_id}: {e}")
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

    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming event - awakens agent from sleep if needed.
        
        This is the core of the perpetual model: the agent awakens,
        processes the event, updates context via MCP, then returns to sleep.
        
        Args:
            event: Event payload
            
        Returns:
            Response dictionary
        """
        try:
            # Awaken from sleep
            await self._awaken()
            
            event_type = event.get("type")
            self.logger.info(f"Agent {self.agent_id} processing event: {event_type}")
            
            result = {"status": "success", "processed_by": self.agent_id}
            
            # Check if we have subscribed handlers for this event
            if event_type in self.event_subscriptions:
                handlers = self.event_subscriptions[event_type]
                handler_results = []
                
                for handler in handlers:
                    try:
                        handler_result = await handler(event.get("data", {}))
                        handler_results.append(handler_result)
                    except Exception as e:
                        self.logger.error(f"Handler error for {event_type}: {e}")
                        handler_results.append({"error": str(e)})
                
                result["handler_results"] = handler_results
            
            # Save context to MCP after processing
            await self._save_context_to_mcp()
            
            self.total_events_processed += 1
            
            # Return to sleep
            await self._sleep()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling event: {e}")
            return {"status": "error", "error": str(e)}

    async def act(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Perform an action. Supports ML pipeline operations.
        """
        # Always inject this agent's adapter_name if not explicitly set in params
        if self.adapter_name and action in ("trigger_lora_training", "aml_infer"):
            if action == "trigger_lora_training":
                for adapter in params.get("adapters", []):
                    if "adapter_name" not in adapter:
                        adapter["adapter_name"] = self.adapter_name
            elif action == "aml_infer":
                params.setdefault("agent_id", self.adapter_name)

        if action == "trigger_lora_training":
            return await trigger_lora_training(params["training_params"], params["adapters"])
        elif action == "run_azure_ml_pipeline":
            return await run_azure_ml_pipeline(
                params["subscription_id"],
                params["resource_group"],
                params["workspace_name"]
            )
        elif action == "aml_infer":
            return await aml_infer(params["agent_id"], params["prompt"])
        else:
            raise ValueError(f"Unknown action: {action}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with perpetual operation capabilities.
        """
        try:
            action = task.get("action")
            params = task.get("params", {})
            
            if action:
                result = await self.act(action, params)
                return {"status": "success", "result": result}
            else:
                return {"status": "error", "error": "No action specified"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_state(self) -> Dict[str, Any]:
        """
        Get current perpetual state.
        
        Returns:
            Current state dictionary including MCP context status
        """
        return {
            "agent_id": self.agent_id,
            "adapter_name": self.adapter_name,
            "is_running": self.is_running,
            "sleep_mode": self.sleep_mode,
            "wake_count": self.wake_count,
            "total_events_processed": self.total_events_processed,
            "subscriptions": list(self.event_subscriptions.keys()),
            "mcp_context_preserved": self.mcp_context_server is not None
        }

    async def _perpetual_loop(self) -> None:
        """
        Main perpetual loop - runs indefinitely.
        
        This loop keeps the agent alive and responsive to events.
        """
        self.logger.info(f"Agent {self.agent_id} entered perpetual loop")
        
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
                self.logger.error(f"Error in perpetual loop: {e}")
                # Don't exit on errors - perpetual agents are resilient
                await asyncio.sleep(5)
        
        self.logger.info(f"Agent {self.agent_id} exited perpetual loop")

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

    async def _setup_mcp_context_server(self) -> None:
        """
        Set up dedicated ContextMCPServer for context preservation.
        
        Each perpetual agent has its own ContextMCPServer instance that preserves
        context across all events and agent restarts. This is a key differentiator
        from task-based frameworks.
        """
        try:
            self.mcp_context_server = ContextMCPServer(
                agent_id=self.agent_id,
                config=self.config.get("context_server", {}) if hasattr(self, 'config') else {}
            )
            await self.mcp_context_server.initialize()
            self.logger.info(f"ContextMCPServer initialized for agent {self.agent_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ContextMCPServer: {e}")
            raise

    async def _setup_event_listeners(self) -> None:
        """Set up event listening infrastructure."""
        # This would integrate with the messaging/event bus in production
        self.logger.debug(f"Event listeners set up for agent {self.agent_id}")

    async def _load_context_from_mcp(self) -> None:
        """Load previously saved context from ContextMCPServer."""
        if self.mcp_context_server:
            # Context is automatically loaded during ContextMCPServer initialization
            context = await self.mcp_context_server.get_all_context()
            self.logger.debug(f"Loaded {len(context)} context items from ContextMCPServer")

    async def _save_context_to_mcp(self) -> None:
        """Save current context to ContextMCPServer."""
        if self.mcp_context_server:
            # Save current processing state
            await self.mcp_context_server.set_context("wake_count", self.wake_count)
            await self.mcp_context_server.set_context("total_events_processed", self.total_events_processed)
            await self.mcp_context_server.set_context("last_active", datetime.utcnow().isoformat())
            self.logger.debug(f"Saved context to ContextMCPServer")