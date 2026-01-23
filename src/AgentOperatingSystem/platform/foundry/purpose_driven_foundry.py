"""
PurposeDrivenAgent with Microsoft Foundry Agent Service Runtime

This module extends PurposeDrivenAgent to use Microsoft Foundry Agent Service
(Azure AI Agents runtime) as the underlying execution engine. Each PurposeDrivenAgent
is deployed as an Azure AI Agent with fine-tuned Llama 3.3 70B model using LoRA adapters.

Architecture:
- PurposeDrivenAgent API remains unchanged (core architectural component)
- Foundry Agent Service provides the runtime execution
- Llama 3.3 70B fine-tuned with domain-specific LoRA adapters
- Stateful threads managed by Azure AI Agents
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import os
import json
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

from .purpose_driven import PurposeDrivenAgent


class PurposeDrivenAgentFoundry(PurposeDrivenAgent):
    """
    PurposeDrivenAgent with Microsoft Foundry Agent Service runtime.

    This class extends the core PurposeDrivenAgent to use Azure AI Agents
    (Foundry Agent Service) as the underlying runtime. Each agent is deployed
    as a Foundry Agent with Llama 3.3 70B fine-tuned using LoRA adapters.

    Key features:
    - Maintains PurposeDrivenAgent API and semantics
    - Uses Foundry Agent Service for execution
    - Supports Llama 3.3 70B with domain-specific LoRA adapters
    - Stateful threads managed by Azure AI Agents
    - Enterprise-grade scalability and reliability

    Example:
        >>> agent = PurposeDrivenAgentFoundry(
        ...     agent_id="ceo",
        ...     purpose="Strategic oversight and company growth",
        ...     purpose_scope="Strategic planning, major decisions",
        ...     adapter_name="ceo",  # LoRA adapter for CEO domain
        ...     foundry_endpoint=os.getenv('AZURE_AI_PROJECT_ENDPOINT')
        ... )
        >>> await agent.initialize()
        >>> await agent.start()
        >>> # Agent runs on Foundry runtime with Llama 3.3 70B + CEO LoRA
    """

    def __init__(
        self,
        agent_id: str,
        purpose: str,
        purpose_scope: str = None,
        success_criteria: List[str] = None,
        tools: List[Any] = None,
        system_message: str = None,
        adapter_name: str = None,
        foundry_endpoint: str = None,
        model_deployment: str = None
    ):
        """
        Initialize a Purpose-Driven Agent with Foundry runtime.

        Args:
            agent_id: Unique identifier for this agent
            purpose: The long-term purpose this agent works toward
            purpose_scope: Scope/boundaries of the purpose (optional)
            success_criteria: List of criteria that define success (optional)
            tools: Tools available to the agent (optional)
            system_message: System message for the agent (optional)
            adapter_name: Name for LoRA adapter (e.g., 'ceo', 'cfo')
            foundry_endpoint: Azure AI Project endpoint for Foundry runtime
            model_deployment: Model deployment name (Llama 3.3 70B with LoRA)
        """
        # Initialize parent PurposeDrivenAgent
        super().__init__(
            agent_id=agent_id,
            purpose=purpose,
            purpose_scope=purpose_scope,
            success_criteria=success_criteria,
            tools=tools,
            system_message=system_message,
            adapter_name=adapter_name
        )

        # Foundry-specific attributes
        self.foundry_endpoint = foundry_endpoint or os.getenv('AZURE_AI_PROJECT_ENDPOINT')
        self.model_deployment = model_deployment or os.getenv('AZURE_AI_MODEL_DEPLOYMENT', 'llama-3.3-70b')
        self.foundry_client: Optional[AgentsClient] = None
        self.foundry_agent: Optional[Agent] = None
        self.foundry_thread: Optional[AgentThread] = None

        # LoRA adapter configuration
        self.lora_adapter_name = adapter_name  # e.g., 'ceo', 'cfo', 'cto'

        self.logger = logging.getLogger(f"aos.purpose_driven_foundry.{self.agent_id}")
        self.logger.info(
            f"PurposeDrivenAgentFoundry {self.agent_id} created with Llama 3.3 70B + LoRA adapter '{self.lora_adapter_name}'"
        )

    async def initialize(self) -> bool:
        """
        Initialize the agent on Foundry Agent Service runtime.

        Creates the agent on Azure AI Agents runtime with Llama 3.3 70B
        fine-tuned using the domain-specific LoRA adapter.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize parent (sets up basic attributes)
            parent_success = await super().initialize()
            if not parent_success:
                return False

            # Initialize Foundry Agent Service client
            if not self.foundry_endpoint:
                raise ValueError("AZURE_AI_PROJECT_ENDPOINT not configured")

            credential = DefaultAzureCredential()
            self.foundry_client = AgentsClient(
                endpoint=self.foundry_endpoint,
                credential=credential
            )

            # Construct agent instructions from purpose
            instructions = self._build_agent_instructions()

            # Convert tools to Foundry ToolSet
            toolset = self._build_toolset()

            # Determine model deployment with LoRA adapter
            # Format: "llama-3.3-70b-{adapter_name}" for fine-tuned deployment
            model_with_lora = f"{self.model_deployment}-{self.lora_adapter_name}" if self.lora_adapter_name else self.model_deployment

            # Create agent on Foundry runtime
            self.foundry_agent = await self.foundry_client.create_agent(
                model=model_with_lora,
                name=self.agent_id,
                description=self.purpose,
                instructions=instructions,
                toolset=toolset if toolset else None,
                metadata={
                    "agent_type": "purpose_driven",
                    "purpose": self.purpose,
                    "lora_adapter": self.lora_adapter_name or "none",
                    "aos_agent_id": self.agent_id,
                }
            )

            # Create stateful thread for this agent
            self.foundry_thread = await self.foundry_client.create_thread(
                metadata={
                    "agent_id": self.agent_id,
                    "purpose": self.purpose
                }
            )

            self.logger.info(
                f"Agent {self.agent_id} initialized on Foundry runtime "
                f"(Agent ID: {self.foundry_agent.id}, Thread ID: {self.foundry_thread.id}, "
                f"Model: {model_with_lora})"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize on Foundry runtime: {e}")
            return False

    def _build_agent_instructions(self) -> str:
        """Build comprehensive instructions for the Foundry agent."""
        instructions = f"""You are {self.agent_id}, a purpose-driven AI agent running on Microsoft Foundry Agent Service.

PURPOSE: {self.purpose}

SCOPE: {self.purpose_scope}
"""

        if self.success_criteria:
            instructions += f"\nSUCCESS CRITERIA:\n"
            for criterion in self.success_criteria:
                instructions += f"- {criterion}\n"

        if self.system_message:
            instructions += f"\n{self.system_message}"

        instructions += f"""

You are powered by Llama 3.3 70B fine-tuned with a domain-specific LoRA adapter ('{self.lora_adapter_name}').
Work continuously toward your purpose. Make decisions aligned with your purpose and success criteria.
"""

        return instructions

    def _build_toolset(self) -> Optional[ToolSet]:
        """Convert agent tools to Foundry ToolSet."""
        if not self.tools:
            return None

        toolset = ToolSet()

        for tool in self.tools:
            try:
                # Convert tool to FunctionTool
                # Assuming tools have a compatible structure
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

    async def process_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an event using Foundry Agent Service runtime.

        Args:
            event_type: Type of event (e.g., 'DecisionRequested', 'TaskAssigned')
            payload: Event payload data

        Returns:
            Response from agent processing
        """
        try:
            if not self.foundry_client or not self.foundry_agent or not self.foundry_thread:
                raise RuntimeError("Agent not initialized on Foundry runtime")

            # Format event as message
            message_content = f"Event: {event_type}\nPayload: {json.dumps(payload, indent=2)}"

            # Process using Foundry runtime
            run = await self.foundry_client.create_thread_and_process_run(
                agent_id=self.foundry_agent.id,
                thread=self.foundry_thread,
                additional_messages=[{"role": "user", "content": message_content}]
            )

            # Extract response
            response_content = None
            if run.status == "completed":
                messages = await self.foundry_client.list_messages(thread_id=self.foundry_thread.id)
                for msg in messages:
                    if msg.role == "assistant":
                        response_content = msg.content
                        break

            # Update metrics
            self.purpose_metrics["purpose_evaluations"] += 1

            return {
                "success": run.status == "completed",
                "response": response_content,
                "status": run.status,
                "thread_id": self.foundry_thread.id,
                "run_id": run.id
            }

        except Exception as e:
            self.logger.error(f"Failed to process event on Foundry runtime: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def start(self):
        """
        Start the agent in perpetual operation mode.

        The agent is already running on Foundry runtime after initialization.
        This method sets the running flag for compatibility with parent class.
        """
        if not self.foundry_agent:
            raise RuntimeError("Agent must be initialized before starting")

        self.is_running = True
        self.logger.info(
            f"Agent {self.agent_id} running on Foundry runtime with Llama 3.3 70B + {self.lora_adapter_name} LoRA"
        )

    async def stop(self):
        """
        Stop the agent.

        Note: The Foundry agent itself continues to exist but won't process new events.
        """
        self.is_running = False
        self.logger.info(f"Agent {self.agent_id} stopped (Foundry agent still exists)")

    async def cleanup(self):
        """
        Clean up Foundry resources.

        Optionally delete the agent from Foundry runtime if needed.
        """
        try:
            if self.foundry_client and self.foundry_agent:
                # Optionally delete the Foundry agent
                # await self.foundry_client.delete_agent(self.foundry_agent.id)
                self.logger.info(f"Agent {self.agent_id} cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
