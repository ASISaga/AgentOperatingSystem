"""
PurposeDrivenAgent - The Fundamental Building Block of AgentOperatingSystem

PurposeDrivenAgent is a directly-instantiable, perpetual agent class. It is the
base class for all purpose-driven agents in AOS and can also be used on its own.

PurposeDrivenAgent works against a single, perpetual purpose rather than short-term
tasks. This is the fundamental building block that makes AOS an operating system of
Purpose-Driven, Perpetual Agents.

Architecture Components:
- LoRA Adapters: Provide domain-specific vocabulary, persona, and knowledge.
  Each class in the inheritance chain contributes exactly one adapter via _add_layer().
- Core Purpose: There is exactly one purpose per agent. It is added to the LLM
  context during initialization so that every decision is purpose-aligned.
- MCP: Provides context management, domain-specific tools, and access to contemporary
  software systems.

Layer Stacking:
  Each class in the inheritance chain (PurposeDrivenAgent, LeadershipAgent,
  CMOAgent, …) adds one entry to self._layers by calling self._add_layer().  Each
  layer specifies its LoRA adapter, a domain context dict, and a list of skill names.
  The full capability of an agent is the union of all layers.

  Example for CMOAgent:
      Layer 0 (LeadershipAgent): adapter="leadership", context={domain, capabilities…}
      Layer 1 (CMOAgent):        adapter="marketing",  context={domain, capabilities…}

  get_adapters()       → ["leadership", "marketing"]
  get_all_skills()     → all skills from all layers
  get_layer_contexts() → merged context dict from all layers

Deployment:
  PurposeDrivenAgent exposes a deploy() method that invokes the Python Azure
  deployment orchestrator (deployment/deploy.py).  Derived-agent GitHub workflows
  call this method to deploy their agent to Azure.

agent_framework.Agent (Microsoft Agent Framework >= 1.0.0rc1) is a MANDATORY runtime
dependency.  PurposeDrivenAgent directly inherits from it.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
import asyncio
import uuid
from agent_framework import Agent
from ..ml.pipeline_ops import trigger_lora_training, run_azure_ml_pipeline, aml_infer
from ..mcp.context_server import ContextMCPServer


class PurposeDrivenAgent(Agent):
    """
    Purpose-Driven Perpetual Agent — The fundamental building block of AOS.

    PurposeDrivenAgent is directly instantiable and can be used on its own or
    extended by more specialised agents (LeadershipAgent, CMOAgent, etc.).

    Core Design Principles:
    - **Single purpose**: There is exactly one purpose per agent. It is added to
      the LLM context during initialization so every decision is purpose-aligned.
    - **Layer stacking**: Each class in the inheritance chain calls _add_layer()
      once to contribute its LoRA adapter (vocabulary, persona, knowledge), a
      domain context dict, and a list of skill names.
    - **Perpetual**: Runs indefinitely, awakening on events.
    - **Stateful**: Maintains context across all interactions via MCP.
    - **Deployable**: Provides deploy() to push itself to Azure via the Python
      deployment orchestrator. Derived-agent GitHub workflows call this method.

    Layer Stacking:
      get_adapters()       → ordered list of all LoRA adapters
      get_all_skills()     → union of all skill names across layers
      get_layer_contexts() → merged context dict from all layers
      get_agent_type()     → alias for get_adapters()

    Example — direct use:
        >>> agent = PurposeDrivenAgent(
        ...     agent_id="assistant",
        ...     purpose="General assistance and task execution",
        ...     adapter_name="general"
        ... )
        >>> await agent.initialize()
        >>> await agent.start()

    Example — subclassing:
        >>> class MyAgent(PurposeDrivenAgent):
        ...     def __init__(self, agent_id):
        ...         super().__init__(agent_id=agent_id, purpose="My purpose", adapter_name=None)
        ...         self._add_layer("my-domain", {"domain": "custom"}, ["my_skill"])
    """

    def __init__(
        self,
        agent_id: str,
        purpose: str,
        name: Optional[str] = None,
        role: Optional[str] = None,
        agent_type: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        success_criteria: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None,
        adapter_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        aos: Optional[Any] = None
    ):
        """
        Initialize a Purpose-Driven Agent.

        Args:
            agent_id: Unique identifier for this agent
            purpose: The single, long-term purpose this agent works toward.
                     Added to the LLM context so every decision is purpose-aligned.
            name: Human-readable agent name
            role: Agent role/type
            agent_type: Type of agent (e.g., "perpetual", "purpose_driven")
            purpose_scope: Scope/boundaries of the purpose (optional)
            success_criteria: List of criteria that define success (optional)
            tools: Tools available to the agent (optional, via MCP)
            system_message: System message for the agent (optional)
            adapter_name: LoRA adapter for THIS base layer (e.g., 'general', 'ceo').
                Subclasses that manage their own layers should pass None here and
                call self._add_layer() explicitly after super().__init__().
            config: Optional configuration dictionary
            aos: Optional reference to AgentOperatingSystem instance for querying available personas

        Architecture:
            - The purpose is added to the primary LLM context to guide behavior.
            - Each class in the inheritance chain calls _add_layer() to register
              its LoRA adapter (vocabulary, persona, knowledge), domain context,
              and skill names.
            - MCP (via ContextMCPServer) provides context management and domain tools.
        """
        # Initialise agent_framework.Agent (mandatory runtime dependency).
        # client=None defers LLM client wiring to the AOS runtime layer.
        # instructions receives the combined system message + purpose statement
        # so the agent's purpose is visible to the LLM from the start.
        super().__init__(
            client=None,
            name=name or agent_id,
            instructions=system_message or purpose,
        )

        # BaseAgent attributes
        self.agent_id = agent_id
        self.name = name or agent_id
        self.role = role or "agent"
        self.agent_type = agent_type or "purpose_driven"
        self.config = config or {}
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        self.state = "initialized"

        # PurposeDrivenAgent attributes — perpetual operation
        self.tools = tools or []
        self.system_message = system_message or ""
        # adapter_name always reflects the LAST layer added (most specific).
        # Initialised to None; _add_layer() updates it on every call.
        self.adapter_name: Optional[str] = None

        # Perpetual operation state
        self.is_running = False
        self.sleep_mode = True
        self.event_subscriptions: Dict[str, List[Callable]] = {}
        self.wake_count = 0
        self.total_events_processed = 0

        # Context is preserved via ContextMCPServer (common infrastructure)
        # Each perpetual agent has a dedicated ContextMCPServer instance
        self.mcp_context_server: Optional[ContextMCPServer] = None

        # PurposeDrivenAgent attributes
        # The purpose will be added to primary LLM context during initialization
        self.purpose = purpose
        self.purpose_scope = purpose_scope or "General purpose operation"
        self.success_criteria = success_criteria or []

        # Purpose tracking
        self.purpose_metrics = {
            "purpose_aligned_actions": 0,
            "purpose_evaluations": 0,
            "decisions_made": 0,
            "goals_achieved": 0
        }

        # Goals and progress
        self.active_goals: List[Dict[str, Any]] = []
        self.completed_goals: List[Dict[str, Any]] = []

        # Reference to AgentOperatingSystem for querying available personas
        self.aos = aos

        # Layer registry: each class in the inheritance chain calls _add_layer()
        # once to contribute its LoRA adapter, domain context, and skill names.
        self._layers: List[Dict[str, Any]] = []

        self.logger = logging.getLogger(f"aos.purpose_driven.{self.agent_id}")

        # Register base layer when an adapter is supplied at this level.
        # Direct subclasses (LeadershipAgent, CMOAgent, …) pass adapter_name=None
        # and call _add_layer() themselves after super().__init__() returns.
        if adapter_name is not None:
            self._add_layer(
                adapter_name=adapter_name,
                context={
                    "purpose": self.purpose,
                    "purpose_scope": self.purpose_scope,
                },
                skills=[],
            )

        self.logger.info(
            f"PurposeDrivenAgent {self.agent_id} created with purpose: {self.purpose}, "
            f"adapters: {self.get_adapters()}"
        )

    # ------------------------------------------------------------------
    # Layer stacking API
    # ------------------------------------------------------------------

    def _add_layer(
        self,
        adapter_name: str,
        context: Dict[str, Any],
        skills: List[str],
    ) -> None:
        """
        Register a capability layer contributed by the calling class.

        Called once per class in the inheritance chain during __init__. Each call:
        - Appends an entry to self._layers with the adapter, context, and skills.
        - Updates self.adapter_name to the newly added adapter so that ML
          operations always target the most recently added (most specific) adapter.

        Args:
            adapter_name: Name of the LoRA adapter for this layer (e.g. "leadership").
            context:      Domain-specific key-value context entries for this layer.
                          Stored in MCP during initialize(); visible to the LLM.
            skills:       List of skill/capability names introduced by this layer.
        """
        self._layers.append({
            "adapter": adapter_name,
            "context": context,
            "skills": list(skills),
        })
        self.adapter_name = adapter_name
        self.logger.info(
            f"Agent {self.agent_id}: layer '{adapter_name}' registered "
            f"({len(skills)} skills, {len(context)} context keys)"
        )

    def get_adapters(self) -> List[str]:
        """
        Return all LoRA adapters accumulated across the inheritance chain.

        The list is ordered from most-base (first registered) to most-specific
        (last registered), matching the LoRAx superimposition order.

        Returns:
            Ordered list of LoRA adapter names, one per layer.
        """
        return [layer["adapter"] for layer in self._layers]

    def get_all_skills(self) -> List[str]:
        """
        Return all skill names accumulated across the inheritance chain.

        Returns:
            Flat list of skill names from all layers, in registration order.
        """
        return [skill for layer in self._layers for skill in layer["skills"]]

    def get_layer_contexts(self) -> Dict[str, Any]:
        """
        Return the merged context dict from all layers in the inheritance chain.

        Later layers override earlier layers on key collision.

        Returns:
            Merged dict of all layer context entries.
        """
        merged: Dict[str, Any] = {}
        for layer in self._layers:
            merged.update(layer["context"])
        return merged

    def get_agent_type(self) -> List[str]:
        """
        Return the ordered list of LoRA adapters (personas) for this agent.

        This is the direct result of the layer stacking performed during __init__.
        Subclasses should call _add_layer() instead of overriding this method.

        Returns:
            Ordered list of adapter/persona names from all layers.
        """
        return self.get_adapters()

    def get_available_personas(self) -> List[str]:
        """
        Query AgentOperatingSystem for available personas.
        
        Returns:
            List of available persona names, or empty list if AOS not available
        """
        if self.aos:
            return self.aos.get_available_personas()
        else:
            # Fallback if AOS not provided - return default personas
            self.logger.warning("AgentOperatingSystem not available, using default personas")
            return ["generic", "leadership", "marketing", "finance", "operations", 
                    "technology", "hr", "legal"]

    def validate_personas(self, personas: List[str]) -> bool:
        """
        Validate that requested personas are available in AgentOperatingSystem.
        
        Args:
            personas: List of persona names to validate
            
        Returns:
            True if all personas are available
        """
        if self.aos:
            return self.aos.validate_personas(personas)
        else:
            # If AOS not available, allow any personas
            return True

    async def initialize(self) -> bool:
        """
        Initialize agent resources and MCP context server.

        For perpetual agents, this sets up the dedicated MCP server for
        context preservation, event listeners, and recovery mechanisms.

        Then extends with purpose-specific setup:
        - Stores purpose in context (added to primary LLM context)
        - Stores all layer contexts (adapters, domain contexts, skills) in MCP
        - LoRA adapters (registered via _add_layer) provide domain knowledge & persona

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

            # Purpose-specific initialization
            try:
                # Load purpose-specific context
                await self._load_purpose_context()

                # Store purpose in MCP context server
                # This makes the purpose available to the primary LLM context
                if self.mcp_context_server:
                    await self.mcp_context_server.set_context("purpose", self.purpose)
                    await self.mcp_context_server.set_context("purpose_scope", self.purpose_scope)
                    await self.mcp_context_server.set_context("success_criteria", self.success_criteria)

                    # Store all accumulated layer contexts so every layer's domain
                    # knowledge is available to the LLM context
                    for key, value in self.get_layer_contexts().items():
                        await self.mcp_context_server.set_context(key, value)

                    # Store the full adapter and skill stacks for introspection
                    await self.mcp_context_server.set_context("adapters", self.get_adapters())
                    await self.mcp_context_server.set_context("skills", self.get_all_skills())

                self.logger.info(
                    f"PurposeDrivenAgent {self.agent_id} initialized - "
                    f"purpose added to LLM context, adapters {self.get_adapters()} provide domain expertise"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to initialize PurposeDrivenAgent: {e}")
                return False

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

        Saves purpose-specific state before stopping.

        Returns:
            True if stopped successfully
        """
        try:
            self.logger.info(f"Stopping perpetual agent {self.agent_id}")

            # Save purpose-specific state
            if self.mcp_context_server:
                await self.mcp_context_server.set_context("active_goals", self.active_goals)
                await self.mcp_context_server.set_context("completed_goals", self.completed_goals)
                await self.mcp_context_server.set_context("purpose_metrics", self.purpose_metrics)

            # Save context to MCP before shutdown
            await self._save_context_to_mcp()

            self.is_running = False

            self.logger.info(f"Perpetual agent {self.agent_id} stopped gracefully")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping perpetual agent {self.agent_id}: {e}")
            return False

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming message - redirects to handle_event for perpetual agents.

        Args:
            message: Message payload

        Returns:
            Response dictionary
        """
        return await self.handle_event(message)

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health status with state, metrics, issues
        """
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "healthy": self.state in ["initialized", "running"],
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "metadata": self.metadata
        }

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
        Handle an event with purpose-driven processing.

        This is the core of the perpetual model: the agent awakens,
        processes the event, updates context via MCP, then returns to sleep.

        Extends with purpose alignment evaluation.

        Args:
            event: Event payload

        Returns:
            Response dictionary
        """
        try:
            # First, check if event aligns with purpose
            alignment = await self.evaluate_purpose_alignment(event)

            if alignment["aligned"]:
                self.purpose_metrics["purpose_aligned_actions"] += 1

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

            # Add purpose-specific metadata to result
            result["purpose_alignment"] = alignment
            result["purpose"] = self.purpose

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
            Current state dictionary including MCP context status and layer stack.
        """
        return {
            "agent_id": self.agent_id,
            "adapter_name": self.adapter_name,
            "adapters": self.get_adapters(),
            "skills": self.get_all_skills(),
            "layers": len(self._layers),
            "is_running": self.is_running,
            "sleep_mode": self.sleep_mode,
            "wake_count": self.wake_count,
            "total_events_processed": self.total_events_processed,
            "subscriptions": list(self.event_subscriptions.keys()),
            "mcp_context_preserved": self.mcp_context_server is not None
        }

    async def evaluate_purpose_alignment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate whether an action aligns with the agent's purpose.

        Args:
            action: Action to evaluate

        Returns:
            Evaluation result with alignment score and reasoning
        """
        self.purpose_metrics["purpose_evaluations"] += 1

        # Placeholder for actual purpose alignment logic
        # In production, this would use LLM reasoning, rules engine, etc.
        evaluation = {
            "action": action.get("type", "unknown"),
            "aligned": True,  # Placeholder
            "alignment_score": 0.85,  # Placeholder (0-1)
            "reasoning": f"Action aligns with purpose: {self.purpose}",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.debug(
            f"Purpose alignment evaluation: {evaluation['aligned']} "
            f"(score: {evaluation['alignment_score']})"
        )

        return evaluation

    async def make_purpose_driven_decision(
        self,
        decision_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make a decision based on the agent's purpose.

        Args:
            decision_context: Context and options for the decision

        Returns:
            Decision result with reasoning
        """
        self.purpose_metrics["decisions_made"] += 1

        # Evaluate alignment of decision options with purpose
        options = decision_context.get("options", [])
        evaluated_options = []

        for option in options:
            evaluation = await self.evaluate_purpose_alignment(option)
            evaluated_options.append({
                "option": option,
                "evaluation": evaluation
            })

        # Select best aligned option (simplified logic)
        best_option = max(
            evaluated_options,
            key=lambda x: x["evaluation"]["alignment_score"],
            default=None
        )

        decision = {
            "decision_id": f"decision_{self.purpose_metrics['decisions_made']}",
            "context": decision_context,
            "selected_option": best_option["option"] if best_option else None,
            "reasoning": f"Selected option most aligned with purpose: {self.purpose}",
            "alignment_score": best_option["evaluation"]["alignment_score"] if best_option else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Store decision in context
        if self.mcp_context_server:
            await self.mcp_context_server.add_memory({
                "type": "decision",
                "decision": decision
            })

        self.logger.info(f"Made purpose-driven decision: {decision['decision_id']}")

        return decision

    async def add_goal(
        self,
        goal_description: str,
        success_criteria: List[str] = None,
        deadline: str = None
    ) -> str:
        """
        Add a goal aligned with the agent's purpose.

        Args:
            goal_description: Description of the goal
            success_criteria: Criteria for goal completion
            deadline: Optional deadline

        Returns:
            Goal ID
        """
        goal_id = f"goal_{len(self.active_goals) + len(self.completed_goals) + 1}"

        goal = {
            "goal_id": goal_id,
            "description": goal_description,
            "success_criteria": success_criteria or [],
            "deadline": deadline,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "progress": 0.0
        }

        self.active_goals.append(goal)

        # Store in context
        if self.mcp_context_server:
            await self.mcp_context_server.set_context(
                f"goal_{goal_id}",
                goal
            )

        self.logger.info(f"Added goal: {goal_id} - {goal_description}")

        return goal_id

    async def update_goal_progress(
        self,
        goal_id: str,
        progress: float,
        notes: str = None
    ) -> bool:
        """
        Update progress on a goal.

        Args:
            goal_id: Goal ID
            progress: Progress percentage (0.0 to 1.0)
            notes: Optional progress notes

        Returns:
            True if successful
        """
        for goal in self.active_goals:
            if goal["goal_id"] == goal_id:
                goal["progress"] = progress
                goal["last_updated"] = datetime.utcnow().isoformat()
                if notes:
                    goal.setdefault("notes", []).append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "note": notes
                    })

                # Check if complete
                if progress >= 1.0:
                    goal["status"] = "completed"
                    goal["completed_at"] = datetime.utcnow().isoformat()
                    self.active_goals.remove(goal)
                    self.completed_goals.append(goal)
                    self.purpose_metrics["goals_achieved"] += 1
                    self.logger.info(f"Goal completed: {goal_id}")

                # Update in context
                if self.mcp_context_server:
                    await self.mcp_context_server.set_context(
                        f"goal_{goal_id}",
                        goal
                    )

                return True

        return False

    async def get_purpose_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent's purpose-driven operation.

        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "purpose": self.purpose,
            "purpose_scope": self.purpose_scope,
            "success_criteria": self.success_criteria,
            "metrics": self.purpose_metrics,
            "active_goals": len(self.active_goals),
            "completed_goals": len(self.completed_goals),
            "is_running": self.is_running,
            "total_events_processed": self.total_events_processed
        }

    def deploy(
        self,
        environment: str = "dev",
        resource_group: Optional[str] = None,
        location: Optional[str] = None,
        template: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> int:
        """
        Deploy this agent to Azure using the Python deployment orchestrator.

        This method invokes ``deployment/deploy.py`` (the AOS Bicep orchestrator)
        as a subprocess.  It is the entry-point called by derived-agent GitHub
        workflows that need to deploy or update an agent on Azure.

        Args:
            environment:    Target Azure environment ('dev', 'staging', 'prod').
                            Defaults to 'dev'.
            resource_group: Azure resource-group name.  When omitted the
                            orchestrator derives a name from the environment.
            location:       Primary Azure region.  When omitted the orchestrator
                            auto-selects a region.
            template:       Path to the Bicep template file.  When omitted the
                            orchestrator uses the default modular template.
            extra_args:     Additional CLI arguments forwarded verbatim to
                            deploy.py (e.g. ['--skip-health-checks']).

        Returns:
            The subprocess return-code (0 = success).

        Raises:
            FileNotFoundError: If deploy.py cannot be located relative to the
                               package root.
        """
        deploy_script = Path(__file__).resolve().parents[3] / "deployment" / "deploy.py"
        if not deploy_script.exists():
            raise FileNotFoundError(
                f"Deployment script not found at {deploy_script}. "
                "Ensure the deployment/ directory is present in the repository root."
            )

        cmd = [sys.executable, str(deploy_script), "--environment", environment]

        if resource_group:
            cmd += ["--resource-group", resource_group]
        if location:
            cmd += ["--location", location]
        if template:
            cmd += ["--template", template]
        if extra_args:
            cmd += extra_args

        self.logger.info(
            f"Deploying agent '{self.agent_id}' to Azure "
            f"(environment={environment}, resource_group={resource_group or 'auto'})"
        )

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if result.stdout:
            self.logger.info(result.stdout.rstrip())
        if result.returncode == 0:
            self.logger.info(f"Agent '{self.agent_id}' deployed successfully.")
        else:
            if result.stderr:
                self.logger.error(result.stderr.rstrip())
            self.logger.error(
                f"Deployment of agent '{self.agent_id}' failed "
                f"(return-code {result.returncode})."
            )
        return result.returncode

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

        Note: self.config is always initialized in __init__ (line 114), so no
        defensive check is needed here.
        """
        try:
            self.mcp_context_server = ContextMCPServer(
                agent_id=self.agent_id,
                config=self.config.get("context_server", {})
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
            # Persist the accumulated layer stack for restart recovery
            await self.mcp_context_server.set_context("adapters", self.get_adapters())
            await self.mcp_context_server.set_context("skills", self.get_all_skills())
            self.logger.debug(f"Saved context to ContextMCPServer")

    async def _load_purpose_context(self) -> None:
        """
        Load purpose-specific context from MCP server.
        """
        if self.mcp_context_server:
            # Load active goals
            active_goals_data = await self.mcp_context_server.get_context("active_goals")
            if active_goals_data:
                self.active_goals = active_goals_data

            # Load completed goals
            completed_goals_data = await self.mcp_context_server.get_context("completed_goals")
            if completed_goals_data:
                self.completed_goals = completed_goals_data

            # Load metrics
            metrics_data = await self.mcp_context_server.get_context("purpose_metrics")
            if metrics_data:
                self.purpose_metrics.update(metrics_data)

        self.logger.debug(f"Loaded purpose context for {self.agent_id}")


# ---------------------------------------------------------------------------
# Backward-compatibility aliases
# ---------------------------------------------------------------------------
# GenericPurposeDrivenAgent has been merged into PurposeDrivenAgent.
# The alias ensures that existing code importing GenericPurposeDrivenAgent
# (or its older aliases BaseAgent / PerpetualAgent) continues to work.
GenericPurposeDrivenAgent = PurposeDrivenAgent

