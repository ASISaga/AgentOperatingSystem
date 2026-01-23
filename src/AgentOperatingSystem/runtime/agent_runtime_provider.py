"""
Agent Runtime Provider - Infrastructure Layer for Agent Execution

This module provides infrastructure-level runtime support for agents, enabling
them to run on Microsoft Foundry Agent Service with Llama 3.3 70B Instruct
and domain-specific LoRA adapters.

The runtime provider is completely transparent to PurposeDrivenAgent, which
remains pure Microsoft Agent Framework code. The infrastructure handles:
- Foundry Agent Service integration
- Llama 3.3 70B model with LoRA adapters
- Stateful thread management
- Tool integration
- Lifecycle management

Architecture:
- PurposeDrivenAgent: Pure Microsoft Agent Framework (no runtime awareness)
- AgentRuntimeProvider: Infrastructure layer providing Foundry runtime
- LoRAx Server: Manages multiple LoRA adapters for domain specialization
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    Agent,
    AgentThread,
    ThreadRun,
    FunctionTool,
    FunctionDefinition,
    ToolSet,
)
from azure.identity.aio import DefaultAzureCredential


logger = logging.getLogger("AOS.Runtime")


@dataclass
class RuntimeConfig:
    """Configuration for Agent Runtime Provider."""
    
    # Foundry Agent Service endpoint
    foundry_endpoint: str = ""
    
    # Base model (Llama 3.3 70B Instruct)
    base_model: str = "llama-3.3-70b-instruct"
    
    # LoRA adapter configuration
    enable_lora_adapters: bool = True
    lora_adapter_prefix: str = "llama-3.3-70b"  # Prefix for LoRA-adapted models
    
    # Runtime features
    enable_stateful_threads: bool = True
    enable_managed_lifecycle: bool = True
    
    # Performance settings
    timeout: int = 60
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'RuntimeConfig':
        """Create configuration from environment variables."""
        return cls(
            foundry_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", ""),
            base_model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "llama-3.3-70b-instruct"),
            enable_lora_adapters=os.getenv("ENABLE_LORA_ADAPTERS", "true").lower() == "true",
            enable_stateful_threads=os.getenv("ENABLE_STATEFUL_THREADS", "true").lower() == "true",
            enable_managed_lifecycle=os.getenv("ENABLE_MANAGED_LIFECYCLE", "true").lower() == "true",
            timeout=int(os.getenv("RUNTIME_TIMEOUT", "60")),
            max_retries=int(os.getenv("RUNTIME_MAX_RETRIES", "3")),
        )


class AgentRuntimeProvider:
    """
    Infrastructure-level runtime provider for agents.
    
    This provider enables PurposeDrivenAgent to run on Microsoft Foundry Agent
    Service with Llama 3.3 70B Instruct and domain-specific LoRA adapters,
    while keeping the agent implementation pure Microsoft Agent Framework.
    
    The runtime provider handles:
    - Agent deployment to Foundry Agent Service
    - LoRA adapter selection and deployment
    - Stateful thread management
    - Tool integration
    - Lifecycle management
    
    Example:
        # Infrastructure creates runtime provider
        runtime = AgentRuntimeProvider(config)
        await runtime.initialize()
        
        # Deploy agent to runtime (transparent to agent)
        runtime_agent = await runtime.deploy_agent(
            agent_id="ceo",
            purpose="Strategic oversight",
            adapter_name="ceo"  # Uses llama-3.3-70b-ceo LoRA adapter
        )
        
        # Process events through runtime
        response = await runtime.process_event(
            runtime_agent_id=runtime_agent.id,
            event_type="DecisionRequested",
            payload={...}
        )
    """
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        """
        Initialize the Agent Runtime Provider.
        
        Args:
            config: Runtime configuration. If None, loads from environment.
        """
        self.config = config or RuntimeConfig.from_env()
        self.logger = logging.getLogger("AOS.Runtime.Provider")
        
        # Foundry client
        self.foundry_client: Optional[AgentsClient] = None
        
        # Runtime agent registry (maps agent_id -> Foundry Agent)
        self.runtime_agents: Dict[str, Agent] = {}
        self.runtime_threads: Dict[str, AgentThread] = {}
        
        # Metrics
        self.metrics = {
            "total_agents_deployed": 0,
            "total_events_processed": 0,
            "successful_events": 0,
            "failed_events": 0,
            "average_latency_ms": 0.0
        }
        
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the runtime provider.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            # Validate configuration
            if not self.config.foundry_endpoint:
                self.logger.warning(
                    "AZURE_AI_PROJECT_ENDPOINT not configured. "
                    "Runtime will operate in simulation mode."
                )
                self._initialized = True
                return True
            
            # Initialize Foundry Agent Service client
            credential = DefaultAzureCredential()
            self.foundry_client = AgentsClient(
                endpoint=self.config.foundry_endpoint,
                credential=credential
            )
            
            self.logger.info(
                f"Agent Runtime Provider initialized with Foundry Agent Service\n"
                f"  - Endpoint: {self.config.foundry_endpoint}\n"
                f"  - Base Model: {self.config.base_model}\n"
                f"  - LoRA Adapters: {'Enabled' if self.config.enable_lora_adapters else 'Disabled'}\n"
                f"  - Stateful Threads: {'Enabled' if self.config.enable_stateful_threads else 'Disabled'}"
            )
            
            self._initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize runtime provider: {e}")
            return False
    
    async def deploy_agent(
        self,
        agent_id: str,
        purpose: str,
        adapter_name: Optional[str] = None,
        purpose_scope: Optional[str] = None,
        success_criteria: Optional[List[str]] = None,
        tools: Optional[List[Any]] = None,
        system_message: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Deploy an agent to the Foundry runtime.
        
        This creates the agent on Azure AI Agents runtime with Llama 3.3 70B
        fine-tuned using the specified LoRA adapter.
        
        Args:
            agent_id: Unique identifier for the agent
            purpose: The agent's long-term purpose
            adapter_name: Domain-specific LoRA adapter name (e.g., 'ceo', 'cfo')
            purpose_scope: Scope/boundaries of the purpose (optional)
            success_criteria: List of success criteria (optional)
            tools: Tools available to the agent (optional)
            system_message: System message for the agent (optional)
            
        Returns:
            Foundry Agent instance, or None if deployment failed
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Determine model deployment with LoRA adapter
            if self.config.enable_lora_adapters and adapter_name:
                model_deployment = f"{self.config.lora_adapter_prefix}-{adapter_name}"
                self.logger.info(f"Using LoRA-adapted model: {model_deployment}")
            else:
                model_deployment = self.config.base_model
                self.logger.info(f"Using base model: {model_deployment}")
            
            # Build agent instructions from purpose
            instructions = self._build_instructions(
                agent_id=agent_id,
                purpose=purpose,
                purpose_scope=purpose_scope,
                success_criteria=success_criteria,
                system_message=system_message,
                adapter_name=adapter_name
            )
            
            # Convert tools to Foundry ToolSet
            toolset = self._build_toolset(tools) if tools else None
            
            # Create agent on Foundry runtime
            if self.foundry_client:
                foundry_agent = await self.foundry_client.create_agent(
                    model=model_deployment,
                    name=agent_id,
                    description=purpose,
                    instructions=instructions,
                    toolset=toolset,
                    metadata={
                        "agent_type": "purpose_driven",
                        "purpose": purpose,
                        "lora_adapter": adapter_name or "none",
                        "aos_agent_id": agent_id,
                        "runtime_provider": "AOS",
                    }
                )
                
                # Store in registry
                self.runtime_agents[agent_id] = foundry_agent
                
                # Create stateful thread if enabled
                if self.config.enable_stateful_threads:
                    thread = await self.foundry_client.create_thread(
                        metadata={
                            "agent_id": agent_id,
                            "purpose": purpose
                        }
                    )
                    self.runtime_threads[agent_id] = thread
                
                self.metrics["total_agents_deployed"] += 1
                
                self.logger.info(
                    f"Agent {agent_id} deployed to Foundry runtime\n"
                    f"  - Foundry Agent ID: {foundry_agent.id}\n"
                    f"  - Model: {model_deployment}\n"
                    f"  - Thread ID: {thread.id if thread else 'N/A'}"
                )
                
                return foundry_agent
            else:
                # Simulation mode
                self.logger.info(
                    f"Agent {agent_id} deployed in simulation mode (no Foundry endpoint)"
                )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to deploy agent {agent_id} to runtime: {e}")
            return None
    
    async def process_event(
        self,
        agent_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an event for an agent through the runtime.
        
        Args:
            agent_id: Agent identifier
            event_type: Type of event
            payload: Event payload
            
        Returns:
            Processing result
        """
        if not self._initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            foundry_agent = self.runtime_agents.get(agent_id)
            if not foundry_agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found in runtime"
                }
            
            # Get or create thread
            thread = self.runtime_threads.get(agent_id)
            
            # Format event as message
            import json
            message_content = f"Event: {event_type}\nPayload: {json.dumps(payload, indent=2)}"
            
            # Process using Foundry runtime
            if self.foundry_client:
                run = await self.foundry_client.create_thread_and_process_run(
                    agent_id=foundry_agent.id,
                    thread=thread,
                    additional_messages=[{"role": "user", "content": message_content}]
                )
                
                # Extract response
                response_content = None
                if run.status == "completed":
                    messages = await self.foundry_client.list_messages(thread_id=thread.id)
                    for msg in messages:
                        if msg.role == "assistant":
                            response_content = msg.content
                            break
                
                # Update metrics
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                self._update_metrics(success=(run.status == "completed"), latency_ms=latency_ms)
                
                return {
                    "success": run.status == "completed",
                    "response": response_content,
                    "status": run.status,
                    "thread_id": thread.id,
                    "run_id": run.id,
                    "latency_ms": latency_ms
                }
            else:
                # Simulation mode
                return {
                    "success": True,
                    "response": f"[Simulation] Processed {event_type} for {agent_id}",
                    "status": "completed_simulation"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to process event for agent {agent_id}: {e}")
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(success=False, latency_ms=latency_ms)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def undeploy_agent(self, agent_id: str) -> bool:
        """
        Undeploy an agent from the runtime.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if successful
        """
        try:
            foundry_agent = self.runtime_agents.get(agent_id)
            if not foundry_agent:
                return False
            
            # Delete from Foundry (optional - can keep for history)
            # if self.foundry_client:
            #     await self.foundry_client.delete_agent(foundry_agent.id)
            
            # Remove from registries
            if agent_id in self.runtime_agents:
                del self.runtime_agents[agent_id]
            if agent_id in self.runtime_threads:
                del self.runtime_threads[agent_id]
            
            self.logger.info(f"Agent {agent_id} undeployed from runtime")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to undeploy agent {agent_id}: {e}")
            return False
    
    def _build_instructions(
        self,
        agent_id: str,
        purpose: str,
        purpose_scope: Optional[str],
        success_criteria: Optional[List[str]],
        system_message: Optional[str],
        adapter_name: Optional[str]
    ) -> str:
        """Build comprehensive instructions for the Foundry agent."""
        instructions = f"""You are {agent_id}, a purpose-driven AI agent.

PURPOSE: {purpose}

SCOPE: {purpose_scope or "General purpose operation"}
"""
        
        if success_criteria:
            instructions += "\nSUCCESS CRITERIA:\n"
            for criterion in success_criteria:
                instructions += f"- {criterion}\n"
        
        if system_message:
            instructions += f"\n{system_message}"
        
        instructions += f"""

You are powered by Llama 3.3 70B Instruct"""
        
        if adapter_name:
            instructions += f" with domain-specific LoRA adapter ('{adapter_name}')"""
        
        instructions += """
Work continuously toward your purpose. Make decisions aligned with your purpose and success criteria.
"""
        
        return instructions
    
    def _build_toolset(self, tools: List[Any]) -> Optional[ToolSet]:
        """Convert agent tools to Foundry ToolSet."""
        if not tools:
            return None
        
        toolset = ToolSet()
        
        for tool in tools:
            try:
                # Convert tool to FunctionTool
                function_def = FunctionDefinition(
                    name=tool.get('name', 'unknown_tool'),
                    description=tool.get('description', ''),
                    parameters=tool.get('parameters', {})
                )
                function_tool = FunctionTool(function=function_def)
                toolset.add_tool(function_tool)
            except Exception as e:
                self.logger.warning(f"Failed to convert tool to Foundry ToolSet: {e}")
        
        return toolset
    
    def _update_metrics(self, success: bool, latency_ms: float):
        """Update runtime metrics."""
        self.metrics["total_events_processed"] += 1
        
        if success:
            self.metrics["successful_events"] += 1
        else:
            self.metrics["failed_events"] += 1
        
        # Update average latency
        total = self.metrics["total_events_processed"]
        current_avg = self.metrics["average_latency_ms"]
        self.metrics["average_latency_ms"] = ((current_avg * (total - 1)) + latency_ms) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get runtime metrics."""
        return {
            **self.metrics,
            "active_agents": len(self.runtime_agents),
            "active_threads": len(self.runtime_threads)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get runtime status."""
        return {
            "initialized": self._initialized,
            "foundry_endpoint": self.config.foundry_endpoint,
            "base_model": self.config.base_model,
            "lora_adapters_enabled": self.config.enable_lora_adapters,
            "stateful_threads_enabled": self.config.enable_stateful_threads,
            "active_agents": len(self.runtime_agents),
            "active_threads": len(self.runtime_threads),
            "metrics": self.metrics
        }
