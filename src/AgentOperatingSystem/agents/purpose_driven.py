"""
PurposeDrivenAgent - Fundamental Building Block of AgentOperatingSystem

PurposeDrivenAgent inherits from PerpetualAgent and works against a perpetual,
assigned purpose rather than short-term tasks. This is the fundamental building
block that makes AOS an operating system of Purpose-Driven, Perpetual Agents.

Architecture Components:
- LoRA Adapters: Provide domain-specific knowledge (language, vocabulary, concepts,
  and agent persona) to PurposeDrivenAgents
- Core Purposes: Added to the primary LLM context to guide agent behavior
- MCP: Provides context management, domain-specific tools, and access to contemporary
  software systems

PurposeDrivenAgent will eventually be moved to a dedicated repository.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import logging
import yaml
from pathlib import Path
from .perpetual import PerpetualAgent


class PurposeDrivenAgent(PerpetualAgent):
    """
    Purpose-Driven Perpetual Agent - The fundamental building block of AOS.
    
    Unlike task-based agents that execute and terminate, PurposeDrivenAgent
    works continuously against an assigned, long-term purpose. It inherits
    all perpetual operation capabilities from PerpetualAgent and adds
    purpose-oriented behavior.
    
    Architecture:
    - LoRA Adapters: Provide domain-specific knowledge (language, vocabulary, 
      concepts, and importantly agent persona) to specialize the agent
    - Core Purposes: Incorporated into the primary LLM context to guide all
      agent decisions and behaviors
    - MCP Integration: ContextMCPServer provides context management, domain-specific
      tools, and access to external software systems
    
    Key characteristics:
    - Perpetual: Runs indefinitely (inherited from PerpetualAgent)
    - Purpose-driven: Works toward a defined, long-term purpose
    - Context-aware: Uses ContextMCPServer for state preservation
    - Event-responsive: Awakens on events relevant to its purpose
    - Autonomous: Makes decisions aligned with its purpose
    - Adapter-mapped: Purpose mapped to LoRA adapter for domain expertise
    
    Example:
        >>> agent = PurposeDrivenAgent(
        ...     agent_id="ceo",
        ...     purpose="Strategic oversight and decision-making for company growth",
        ...     purpose_scope="Strategic planning, major decisions, alignment",
        ...     adapter_name="ceo"  # Maps to LoRA adapter providing CEO domain knowledge & persona
        ... )
        >>> await agent.initialize()  # Sets up MCP context server
        >>> await agent.start()
        >>> # Agent now runs perpetually, working toward its purpose
    """
    
    def __init__(
        self,
        agent_id: str,
        purpose: str = None,
        purpose_scope: str = None,
        success_criteria: List[str] = None,
        tools: List[Any] = None,
        system_message: str = None,
        adapter_name: str = None,
        purposes: List[Dict[str, Any]] = None,
        mcp_tools: List[Dict[str, Any]] = None,
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a Purpose-Driven Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            purpose: The long-term purpose this agent works toward (added to LLM context)
            purpose_scope: Scope/boundaries of the purpose (optional)
            success_criteria: List of criteria that define success (optional)
            tools: Tools available to the agent (optional, via MCP)
            system_message: System message for the agent (optional)
            adapter_name: Name for LoRA adapter providing domain knowledge & persona (e.g., 'ceo', 'cfo')
            purposes: List of purpose configurations for multi-purpose agents (optional)
            mcp_tools: List of MCP tool configurations (optional)
            capabilities: List of agent capabilities (optional)
            metadata: Additional metadata (optional)
        
        Architecture:
            - The purpose is added to the primary LLM context to guide behavior
            - The adapter_name maps to a LoRA adapter that provides domain-specific
              knowledge, vocabulary, concepts, and agent persona
            - MCP (via ContextMCPServer) provides context management and domain tools
        """
        # Initialize parent PerpetualAgent
        # - Sets up adapter_name for LoRA adapter (provides domain knowledge & persona)
        # - Initializes tools (via MCP for domain-specific access)
        super().__init__(
            agent_id=agent_id,
            tools=tools,
            system_message=system_message,
            adapter_name=adapter_name  # Maps to LoRA adapter for domain expertise
        )
        
        # Support both single purpose (backward compatible) and multi-purpose configurations
        self.purposes_config = purposes or []
        
        # If traditional single purpose is provided, use it
        if purpose:
            self.purpose = purpose
            self.purpose_scope = purpose_scope or "General purpose operation"
            self.success_criteria = success_criteria or []
        # If multi-purpose config is provided, use the first one as primary
        elif self.purposes_config:
            primary_purpose = self.purposes_config[0]
            self.purpose = primary_purpose.get("description", "")
            self.purpose_scope = primary_purpose.get("scope", "General purpose operation")
            self.success_criteria = primary_purpose.get("success_criteria", [])
        else:
            # Default values if nothing provided
            self.purpose = "General purpose agent"
            self.purpose_scope = "General purpose operation"
            self.success_criteria = []
        
        # Store MCP tools and capabilities configuration
        self.mcp_tools_config = mcp_tools or []
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        
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
        
        self.logger = logging.getLogger(f"aos.purpose_driven.{self.agent_id}")
        self.logger.info(
            f"PurposeDrivenAgent {self.agent_id} created with purpose: {self.purpose}, "
            f"adapter: {self.adapter_name}"
        )
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "PurposeDrivenAgent":
        """
        Create a PurposeDrivenAgent from a YAML configuration file.
        
        Args:
            yaml_path: Path to the YAML configuration file
            
        Returns:
            Initialized PurposeDrivenAgent instance
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            ValueError: If the YAML file is invalid or missing required fields
            
        Example:
            >>> agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
            >>> await agent.initialize()
            >>> await agent.start()
        """
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            raise FileNotFoundError(f"Agent configuration file not found: {yaml_path}")
        
        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file {yaml_path}: {e}")
        
        # Validate required fields
        if not config.get("agent_id"):
            raise ValueError(f"Missing required field 'agent_id' in {yaml_path}")
        
        # Extract purposes configuration
        purposes = config.get("purposes", [])
        
        # Determine adapter_name:
        # - If single purpose, use its adapter_name
        # - If multiple purposes, use the first one as primary
        # - Otherwise, use agent_id as fallback
        adapter_name = None
        if purposes:
            adapter_name = purposes[0].get("adapter_name")
        
        # Build combined purpose description from all purposes
        if purposes:
            purpose_descriptions = [p.get("description", "") for p in purposes]
            combined_purpose = "; ".join(purpose_descriptions)
        else:
            combined_purpose = config.get("purpose", "General purpose agent")
        
        # Create the agent instance
        return cls(
            agent_id=config["agent_id"],
            purpose=combined_purpose,
            purpose_scope=config.get("scope"),
            success_criteria=config.get("success_criteria"),
            system_message=config.get("system_message"),
            adapter_name=adapter_name or config.get("adapter_name"),
            purposes=purposes,
            mcp_tools=config.get("mcp_tools", []),
            capabilities=config.get("capabilities", []),
            metadata=config.get("metadata", {})
        )
    
    async def initialize(self) -> bool:
        """
        Initialize the Purpose-Driven Agent.
        
        Extends PerpetualAgent initialization with purpose-specific setup:
        - Sets up MCP context server for context management and domain tools
        - Stores purpose in context (added to primary LLM context)
        - LoRA adapter (specified by adapter_name) provides domain knowledge & persona
        
        Returns:
            True if initialization successful
        """
        # Call parent initialization (sets up MCP context server, etc.)
        if not await super().initialize():
            return False
        
        try:
            # Load purpose-specific context
            await self._load_purpose_context()
            
            # Store purpose in MCP context server
            # This makes the purpose available to the primary LLM context
            if self.mcp_context_server:
                await self.mcp_context_server.set_context("purpose", self.purpose)
                await self.mcp_context_server.set_context("purpose_scope", self.purpose_scope)
                await self.mcp_context_server.set_context("success_criteria", self.success_criteria)
                
                # Store multi-purpose configuration if available
                if self.purposes_config:
                    await self.mcp_context_server.set_context("purposes", self.purposes_config)
                
                # Store MCP tools configuration
                if self.mcp_tools_config:
                    await self.mcp_context_server.set_context("mcp_tools", self.mcp_tools_config)
                
                # Store capabilities
                if self.capabilities:
                    await self.mcp_context_server.set_context("capabilities", self.capabilities)
            
            self.logger.info(
                f"PurposeDrivenAgent {self.agent_id} initialized - "
                f"purpose added to LLM context, adapter '{self.adapter_name}' provides domain expertise"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PurposeDrivenAgent: {e}")
            return False
    
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
    
    async def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an event with purpose-driven processing.
        
        Extends parent event handling with purpose alignment evaluation.
        
        Args:
            event: Event payload
            
        Returns:
            Response dictionary
        """
        # First, check if event aligns with purpose
        alignment = await self.evaluate_purpose_alignment(event)
        
        if alignment["aligned"]:
            self.purpose_metrics["purpose_aligned_actions"] += 1
        
        # Call parent event handler
        result = await super().handle_event(event)
        
        # Add purpose-specific metadata to result
        result["purpose_alignment"] = alignment
        result["purpose"] = self.purpose
        
        return result
    
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
    
    async def stop(self) -> bool:
        """
        Stop the Purpose-Driven Agent gracefully.
        
        Saves purpose-specific state before stopping.
        
        Returns:
            True if stopped successfully
        """
        try:
            # Save purpose-specific state
            if self.mcp_context_server:
                await self.mcp_context_server.set_context("active_goals", self.active_goals)
                await self.mcp_context_server.set_context("completed_goals", self.completed_goals)
                await self.mcp_context_server.set_context("purpose_metrics", self.purpose_metrics)
            
            # Call parent stop
            return await super().stop()
            
        except Exception as e:
            self.logger.error(f"Error stopping PurposeDrivenAgent: {e}")
            return False
