"""
PurposeDrivenAgent - LLM-First Fundamental Agent of AgentOperatingSystem

PurposeDrivenAgent is an LLM-first agent that operates based on verbose, detailed 
purposes passed directly to the LLM as context. Unlike conventional logic-based agents, 
PurposeDrivenAgent relies on the LLM's reasoning capabilities guided by comprehensive 
purpose descriptions rather than hard-coded decision logic.

This is the fundamental building block that makes AOS an operating system of 
Purpose-Driven, Perpetual, LLM-First Agents.

LLM-First Architecture:
- Verbose Purposes: Detailed, comprehensive purpose descriptions (not brief summaries)
  are converted to LLM context and passed to LoRA adapters
- LoRA Adapters: Provide domain-specific knowledge, language, vocabulary, concepts, 
  and agent persona to the LLM
- LLM Reasoning: Decision-making and behavior guided by LLM reasoning over the purpose
  context, not hard-coded logic
- MCP Integration: Provides context management, domain-specific tools, and access to 
  contemporary software systems

Configuration:
- Agents are configured via YAML files containing verbose purpose descriptions
- No code-based initialization - configuration-driven only
- Purposes are converted to LLM context automatically
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import logging
import yaml
from pathlib import Path
from .perpetual import PerpetualAgent


class PurposeDrivenAgent(PerpetualAgent):
    """
    LLM-First Purpose-Driven Perpetual Agent - The fundamental agent of AOS.
    
    This agent operates based on verbose purpose descriptions that are converted to 
    LLM context and passed to LoRA adapters. The agent's behavior is guided by the 
    LLM's reasoning over this purpose context, not by hard-coded decision logic.
    
    LLM-First Architecture:
    - Verbose Purposes: Comprehensive purpose descriptions in YAML are converted to 
      LLM context (not brief summaries or hard-coded logic)
    - LoRA Adapters: Purpose-specific adapters provide domain knowledge and persona 
      to the LLM
    - LLM Reasoning: All decisions and behaviors emerge from LLM reasoning over the 
      purpose context
    - MCP Integration: ContextMCPServer provides state preservation and tool access
    
    Key Characteristics:
    - LLM-First: Relies on LLM reasoning, not conventional logic
    - Purpose-Driven: Works toward verbose, detailed purposes
    - Perpetual: Runs indefinitely (inherited from PerpetualAgent)
    - Configuration-Driven: Created from YAML, not code
    - Context-Aware: Uses ContextMCPServer for state preservation
    
    Example:
        >>> # Load agent from YAML with verbose purpose
        >>> agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
        >>> await agent.initialize()  # Purposes converted to LLM context
        >>> await agent.start()
        >>> # Agent now operates based on LLM reasoning over purpose context
    """
    
    def __init__(
        self,
        agent_id: str,
        purposes: List[Dict[str, Any]],
        mcp_tools: List[Dict[str, Any]] = None,
        capabilities: List[str] = None,
        metadata: Dict[str, Any] = None,
        tools: List[Any] = None,
        system_message: str = None
    ):
        """
        Initialize an LLM-First Purpose-Driven Agent.
        
        IMPORTANT: This constructor is for internal use. Create agents using 
        PurposeDrivenAgent.from_yaml() which loads verbose purposes from YAML.
        
        Args:
            agent_id: Unique identifier for this agent
            purposes: List of verbose purpose configurations (from YAML)
                Each purpose contains:
                - name: Purpose identifier
                - description: Verbose LLM context (multi-line, comprehensive)
                - adapter_name: LoRA adapter for this purpose
                - scope: Brief scope description
            mcp_tools: MCP tool configurations
            capabilities: List of agent capabilities
            metadata: Additional metadata
            tools: Tools available to the agent (via MCP)
            system_message: Brief system message (detail comes from verbose purposes)
        
        LLM-First Architecture:
            The verbose purpose descriptions are converted to LLM context and passed 
            to LoRA adapters. The LLM reasons over this context to guide all agent 
            behavior - no hard-coded decision logic.
        """
        # Validate that purposes are provided (required for LLM-first operation)
        if not purposes or len(purposes) == 0:
            raise ValueError(
                "PurposeDrivenAgent requires at least one purpose with verbose description. "
                "Create agents using PurposeDrivenAgent.from_yaml() to load purposes from YAML."
            )
        
        # Get primary purpose and adapter
        primary_purpose = purposes[0]
        adapter_name = primary_purpose.get("adapter_name")
        
        if not adapter_name:
            raise ValueError(
                "Purpose must specify 'adapter_name' to map to LoRA adapter. "
                "Check YAML configuration."
            )
        
        # Initialize parent PerpetualAgent
        super().__init__(
            agent_id=agent_id,
            tools=tools,
            system_message=system_message,
            adapter_name=adapter_name
        )
        
        # Store verbose purposes for LLM context conversion
        self.purposes_config = purposes
        
        # Extract verbose purpose description for primary purpose
        # This is the comprehensive, multi-line description that becomes LLM context
        self.purpose = primary_purpose.get("description", "")
        self.purpose_scope = primary_purpose.get("scope", "")
        
        # Build purpose-to-adapter mapping for multi-purpose agents
        self.purpose_adapter_mapping = {}
        for purpose_config in self.purposes_config:
            purpose_name = purpose_config.get("name", "").lower()
            adapter_name_for_purpose = purpose_config.get("adapter_name")
            if purpose_name and adapter_name_for_purpose:
                self.purpose_adapter_mapping[purpose_name] = adapter_name_for_purpose
        
        # Store MCP tools and capabilities configuration
        self.mcp_tools_config = mcp_tools or []
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        
        # Purpose tracking metrics
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
        Create an LLM-First PurposeDrivenAgent from YAML configuration.
        
        This is the primary way to create agents. The YAML file should contain 
        verbose purpose descriptions that will be converted to LLM context and 
        passed to LoRA adapters for LLM reasoning.
        
        Args:
            yaml_path: Path to the YAML configuration file containing verbose purposes
            
        Returns:
            LLM-First PurposeDrivenAgent with verbose purposes loaded
            
        Raises:
            FileNotFoundError: If the YAML file doesn't exist
            ValueError: If the YAML is invalid or missing required fields (agent_id, purposes)
            
        Example:
            >>> # YAML should contain verbose, multi-line purpose descriptions
            >>> agent = PurposeDrivenAgent.from_yaml("config/agents/ceo_agent.yaml")
            >>> await agent.initialize()  # Purposes converted to LLM context
            >>> await agent.start()  # Agent operates via LLM reasoning over purpose
        """
        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            raise FileNotFoundError(
                f"Agent configuration file not found: {yaml_path}\n"
                f"Create a YAML file with verbose purpose descriptions for LLM context."
            )
        
        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file {yaml_path}: {e}")
        
        # Validate required fields for LLM-first operation
        if not config.get("agent_id"):
            raise ValueError(f"Missing required field 'agent_id' in {yaml_path}")
        
        purposes = config.get("purposes", [])
        if not purposes or len(purposes) == 0:
            raise ValueError(
                f"Missing required 'purposes' in {yaml_path}\n"
                f"LLM-first agents require verbose purpose descriptions in YAML."
            )
        
        # Validate each purpose has required fields
        for i, purpose in enumerate(purposes):
            if not purpose.get("description"):
                raise ValueError(
                    f"Purpose {i} missing 'description' in {yaml_path}\n"
                    f"Each purpose must have a verbose description for LLM context."
                )
            if not purpose.get("adapter_name"):
                raise ValueError(
                    f"Purpose {i} missing 'adapter_name' in {yaml_path}\n"
                    f"Each purpose must specify a LoRA adapter."
                )
        
        # Create the LLM-first agent instance
        return cls(
            agent_id=config["agent_id"],
            purposes=purposes,
            mcp_tools=config.get("mcp_tools", []),
            capabilities=config.get("capabilities", []),
            metadata=config.get("metadata", {}),
            system_message=config.get("system_message")
        )
    
    async def initialize(self) -> bool:
        """
        Initialize the LLM-First Purpose-Driven Agent.
        
        This method converts verbose purposes from YAML to LLM context and passes 
        them to LoRA adapters. The LLM will reason over this context to guide all 
        agent behavior.
        
        LLM-First Initialization:
        - Converts verbose purpose descriptions to LLM context
        - Passes purpose context to LoRA adapters for domain specialization
        - Sets up MCP context server for state preservation and tool access
        - Makes purpose context available to primary LLM
        
        Returns:
            True if initialization successful (purposes converted to LLM context)
        """
        # Call parent initialization (sets up MCP context server, etc.)
        if not await super().initialize():
            return False
        
        try:
            # Load purpose-specific context
            await self._load_purpose_context()
            
            # Convert verbose purposes to LLM context via MCP context server
            # This is the core of LLM-first architecture: purposes become LLM reasoning context
            if self.mcp_context_server:
                # Store verbose primary purpose description as LLM context
                await self.mcp_context_server.set_context("purpose", self.purpose)
                await self.mcp_context_server.set_context("purpose_scope", self.purpose_scope)
                
                # Store all verbose purposes for multi-purpose agents
                # Each purpose's verbose description becomes LLM context for its adapter
                if self.purposes_config:
                    await self.mcp_context_server.set_context("purposes", self.purposes_config)
                    
                    # Log verbose purpose conversion for each purpose
                    for purpose_config in self.purposes_config:
                        purpose_name = purpose_config.get("name")
                        adapter = purpose_config.get("adapter_name")
                        desc_length = len(purpose_config.get("description", ""))
                        self.logger.debug(
                            f"Converted verbose purpose '{purpose_name}' ({desc_length} chars) "
                            f"to LLM context for adapter '{adapter}'"
                        )
                
                # Store MCP tools configuration for LLM access
                if self.mcp_tools_config:
                    await self.mcp_context_server.set_context("mcp_tools", self.mcp_tools_config)
                
                # Store capabilities as part of LLM context
                if self.capabilities:
                    await self.mcp_context_server.set_context("capabilities", self.capabilities)
            
            self.logger.info(
                f"LLM-First PurposeDrivenAgent {self.agent_id} initialized - "
                f"verbose purposes converted to LLM context via adapter '{self.adapter_name}'"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM-First PurposeDrivenAgent: {e}")
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
        status = {
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
        
        # Add multi-purpose information if available
        if self.purpose_adapter_mapping:
            status["purpose_adapter_mapping"] = self.purpose_adapter_mapping
            status["purposes"] = {}
            for purpose_config in self.purposes_config:
                purpose_name = purpose_config.get("name", "")
                if purpose_name:
                    status["purposes"][purpose_name] = {
                        "description": purpose_config.get("description", ""),
                        "adapter": purpose_config.get("adapter_name", ""),
                        "success_criteria": purpose_config.get("success_criteria", [])
                    }
        
        return status
    
    def get_adapter_for_purpose(self, purpose_type: str) -> str:
        """
        Get the LoRA adapter name for a specific purpose type.
        
        For multi-purpose agents, retrieves the adapter mapped to the specified purpose.
        
        Args:
            purpose_type: Type of purpose (e.g., "marketing", "leadership")
            
        Returns:
            LoRA adapter name for the specified purpose
            
        Raises:
            ValueError: If purpose_type is not recognized or agent is not multi-purpose
        """
        if not self.purpose_adapter_mapping:
            raise ValueError(
                f"Agent {self.agent_id} is not configured for multi-purpose operation. "
                f"No purpose-to-adapter mappings available."
            )
        
        adapter_name = self.purpose_adapter_mapping.get(purpose_type.lower())
        
        if adapter_name is None:
            valid_types = list(self.purpose_adapter_mapping.keys())
            raise ValueError(
                f"Unknown purpose type '{purpose_type}'. Valid types: {valid_types}"
            )
        
        return adapter_name
    
    async def execute_with_purpose(
        self, 
        task: Dict[str, Any], 
        purpose_type: str
    ) -> Dict[str, Any]:
        """
        Execute a task using the LoRA adapter for the specified purpose.
        
        For multi-purpose agents, this method switches to the appropriate adapter
        before executing the task, then restores the original adapter.
        
        Args:
            task: Task to execute
            purpose_type: Which purpose to use (e.g., "marketing", "leadership")
            
        Returns:
            Task execution result
            
        Raises:
            ValueError: If purpose_type is not recognized
        """
        # This will raise ValueError if purpose_type is invalid
        adapter_name = self.get_adapter_for_purpose(purpose_type)
        
        self.logger.info(
            f"Executing task with {purpose_type} purpose using adapter: {adapter_name}"
        )
        
        # Store original adapter and ensure restoration in all cases
        original_adapter = self.adapter_name
        
        try:
            # Temporarily switch adapter for this task execution
            self.adapter_name = adapter_name
            
            # Execute task with the purpose-specific adapter
            result = await self.handle_event(task)
            result["purpose_type"] = purpose_type
            result["adapter_used"] = adapter_name
            return result
        except Exception as e:
            self.logger.error(f"Error executing task with {purpose_type} purpose: {e}")
            raise
        finally:
            # Always restore original adapter, even if exception occurred
            self.adapter_name = original_adapter
    
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
