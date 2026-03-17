"""
AOS Agent Framework Multi-Agent System

Provides multi-agent orchestration capabilities using Microsoft Agent Framework 1.0.0rc1.
Supports agent collaboration, workflow execution via SequentialBuilder, and advanced
orchestration patterns via agent-framework-orchestrations.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from agent_framework import Agent, WorkflowBuilder, Runner
    from agent_framework.observability import enable_instrumentation
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    logging.warning("Agent Framework not available")

    class Agent:
        def __init__(self, *args, **kwargs):
            pass

    class WorkflowBuilder:
        def __init__(self, *args, **kwargs):
            pass

try:
    from agent_framework_orchestrations import (
        SequentialBuilder,
        GroupChatBuilder,
        ConcurrentBuilder,
        HandoffBuilder,
    )
    ORCHESTRATIONS_AVAILABLE = True
except ImportError:
    ORCHESTRATIONS_AVAILABLE = False
    logging.warning("Agent Framework Orchestrations not available")

from ..agents.purpose_driven import GenericPurposeDrivenAgent as BaseAgent


class AgentFrameworkSystem:
    """
    Multi-agent system using Microsoft Agent Framework 1.0.0rc1 for AOS.

    Uses agent-framework-orchestrations builders (SequentialBuilder,
    GroupChatBuilder, ConcurrentBuilder) for multi-agent workflows.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, Any] = {}
        self.workflows: Dict[str, Any] = {}
        self.is_initialized = False
        self.stats = {
            "total_conversations": 0,
            "successful_completions": 0,
            "failed_completions": 0,
            "active_workflows": 0
        }

    async def initialize(self):
        """Initialize the Agent Framework system"""
        try:
            self.logger.info("Initializing Agent Framework System...")

            if not AGENT_FRAMEWORK_AVAILABLE:
                raise ImportError("Agent Framework not available")

            # Setup observability instrumentation
            await self._setup_observability()

            # Initialize default agents
            await self._initialize_default_agents()

            self.is_initialized = True
            self.logger.info("Agent Framework System initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Agent Framework System: {e}")
            raise

    async def _setup_observability(self):
        """
        Setup OpenTelemetry observability for Agent Framework.

        In agent-framework >= 1.0.0rc1, use enable_instrumentation() from
        agent_framework.observability. Custom OTLP endpoints are configured
        via the OpenTelemetry SDK or environment variables:

            export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
        """
        try:
            enable_instrumentation(enable_sensitive_data=True)
            self.logger.info("Observability instrumentation enabled")
        except Exception as e:
            self.logger.warning(f"Could not setup observability: {e}")

    async def _initialize_default_agents(self):
        """Initialize default agent roles using Agent Framework"""
        try:
            # Business Analyst Agent
            ba_agent = await self._create_agent(
                "BusinessAnalyst",
                "You are a Business Analyst responsible for analyzing requirements and documenting business processes.",
            )
            self.agents["BusinessAnalyst"] = ba_agent

            # Software Engineer Agent
            se_agent = await self._create_agent(
                "SoftwareEngineer",
                "You are a Software Engineer responsible for implementing solutions and writing code.",
            )
            self.agents["SoftwareEngineer"] = se_agent

            # Product Owner Agent
            po_agent = await self._create_agent(
                "ProductOwner",
                "You are a Product Owner responsible for defining requirements and ensuring quality.",
            )
            self.agents["ProductOwner"] = po_agent

            self.logger.info(f"Initialized {len(self.agents)} Agent Framework agents")

        except Exception as e:
            self.logger.error(f"Failed to initialize default agents: {e}")

    async def _create_agent(self, name: str, instructions: str, **kwargs) -> Agent:
        """Create an Agent with the specified configuration"""
        try:
            from unittest.mock import Mock
            mock_client = Mock()

            agent = Agent(
                client=mock_client,
                instructions=instructions,
                name=name,
            )
            return agent
        except Exception as e:
            self.logger.error(f"Failed to create agent {name}: {e}")
            raise

    async def run_multi_agent_conversation(self, input_message: str, agent_roles: List[str] = None) -> Dict[str, Any]:
        """
        Run a multi-agent conversation using Agent Framework orchestrations.
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Select agents for conversation
            selected_agents = []
            if agent_roles:
                for role in agent_roles:
                    if role in self.agents:
                        selected_agents.append(self.agents[role])
                    else:
                        self.logger.warning(f"Agent role '{role}' not found")
            else:
                selected_agents = list(self.agents.values())

            if not selected_agents:
                raise ValueError("No valid agents selected for conversation")

            # Create workflow for multi-agent conversation
            workflow = await self._create_conversation_workflow(selected_agents, input_message)

            # Execute workflow
            result = await self._execute_workflow(workflow)

            # Update statistics
            self.stats["total_conversations"] += 1
            if result.get("success", False):
                self.stats["successful_completions"] += 1
            else:
                self.stats["failed_completions"] += 1

            return result

        except Exception as e:
            self.logger.error(f"Multi-agent conversation failed: {e}")
            self.stats["failed_completions"] += 1
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "input_message": input_message,
                "selected_agents": [getattr(a, 'name', str(a)) for a in selected_agents]
            }

    async def _create_conversation_workflow(self, agents: List[Agent], input_message: str) -> Any:
        """Create a workflow for multi-agent conversation using SequentialBuilder"""
        try:
            if ORCHESTRATIONS_AVAILABLE:
                builder = SequentialBuilder(participants=agents)
                workflow = builder.build()
            else:
                # Fallback: use WorkflowBuilder with add_chain
                workflow = WorkflowBuilder(
                    start_executor=agents[0],
                ).add_chain(agents).build()

            return workflow

        except Exception as e:
            self.logger.error(f"Failed to create conversation workflow: {e}")
            raise

    async def _execute_workflow(self, workflow: Any) -> Dict[str, Any]:
        """Execute the Agent Framework workflow"""
        try:
            result = await workflow.execute()

            return {
                "success": True,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": getattr(workflow, 'id', 'unknown')
            }

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def create_agent(self, name: str, instructions: str, capabilities: List[str] = None) -> Agent:
        """Create a new agent with specified capabilities"""
        agent = await self._create_agent(name, instructions)
        self.agents[name] = agent

        self.logger.info(f"Created new agent: {name}")
        return agent

    async def remove_agent(self, name: str) -> bool:
        """Remove an agent from the system"""
        if name in self.agents:
            del self.agents[name]
            self.logger.info(f"Removed agent: {name}")
            return True
        else:
            self.logger.warning(f"Agent {name} not found for removal")
            return False

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        """List all available agent names"""
        return list(self.agents.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            **self.stats,
            "total_agents": len(self.agents),
            "is_initialized": self.is_initialized,
            "framework": "Microsoft Agent Framework 1.0.0rc1"
        }

    async def shutdown(self):
        """Shutdown the Agent Framework system"""
        try:
            self.agents.clear()
            self.workflows.clear()
            self.is_initialized = False

            self.logger.info("Agent Framework System shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")