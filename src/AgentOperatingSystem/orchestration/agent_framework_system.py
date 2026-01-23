"""
AOS Agent Framework Multi-Agent System

Provides multi-agent orchestration capabilities using Microsoft Agent Framework.
Supports agent collaboration, workflow execution, and advanced orchestration patterns.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from agent_framework import ChatAgent, WorkflowBuilder
    AGENT_FRAMEWORK_AVAILABLE = True

    # Try to import logging setup if available (replaces deprecated setup_telemetry)
    try:
        from agent_framework import setup_logging
        LOGGING_AVAILABLE = True
    except ImportError:
        LOGGING_AVAILABLE = False
        def setup_logging(*args, **kwargs):
            """Fallback logging setup"""
            logging.info("Logging setup called (fallback implementation)")
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    TELEMETRY_AVAILABLE = False
    logging.warning("Agent Framework not available")

    # Mock classes for when Agent Framework is not available
    class ChatAgent:
        def __init__(self, *args, **kwargs):
            pass

    class WorkflowBuilder:
        def __init__(self, *args, **kwargs):
            pass

    def setup_logging(*args, **kwargs):
        """Fallback logging setup"""



class AgentFrameworkSystem:
    """
    Multi-agent system using Microsoft Agent Framework for AOS.
    Replaces Semantic Kernel-based orchestration with modern Agent Framework patterns.
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

            # Setup telemetry for tracing
            await self._setup_telemetry()

            # Initialize default agents
            await self._initialize_default_agents()

            self.is_initialized = True
            self.logger.info("Agent Framework System initialized successfully")

        except Exception as error:
            self.logger.error("Failed to initialize Agent Framework System: %s", str(error))
            raise

    async def _setup_telemetry(self):
        """
        Setup OpenTelemetry tracing for Agent Framework

        Note: In agent-framework >= 1.0.0b251218, setup_telemetry has been replaced with setup_logging.
        Custom OTLP endpoints are no longer configurable through this function.

        To configure a custom OTLP endpoint, use the OpenTelemetry SDK directly before calling this method:

        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
        # Configure tracer provider with the exporter...

        Or set environment variables:
        export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
        """
        try:
            # Use AI Toolkit's OTLP endpoint for tracing
            # Note: setup_telemetry has been replaced with setup_logging in agent-framework >= 1.0.0b251218
            setup_logging(
                level=logging.INFO,
                enable_sensitive_data=True  # Enable capturing prompts and completions
            )
            self.logger.info("Logging setup completed")
        except Exception as error:
            self.logger.warning("Could not setup logging: %s", str(error))

    async def _initialize_default_agents(self):
        """Initialize default agent roles using Agent Framework"""
        try:
            # Business Analyst Agent
            ba_agent = await self._create_chat_agent(
                "BusinessAnalyst",
                "You are a Business Analyst responsible for analyzing requirements and documenting business processes.",
                {"domain": "business_analysis", "capabilities": ["requirements_analysis", "process_documentation"]}
            )
            self.agents["BusinessAnalyst"] = ba_agent

            # Software Engineer Agent
            se_agent = await self._create_chat_agent(
                "SoftwareEngineer",
                "You are a Software Engineer responsible for implementing solutions and writing code.",
                {"domain": "software_engineering", "capabilities": ["coding", "architecture", "testing"]}
            )
            self.agents["SoftwareEngineer"] = se_agent

            # Product Owner Agent
            po_agent = await self._create_chat_agent(
                "ProductOwner",
                "You are a Product Owner responsible for defining requirements and ensuring quality.",
                {"domain": "product_management", "capabilities": ["requirements_definition", "quality_assurance"]}
            )
            self.agents["ProductOwner"] = po_agent

            self.logger.info("Initialized %s Agent Framework agents", len(self.agents))

        except Exception as error:
            self.logger.error("Failed to initialize default agents: %s", str(error))

    async def _create_chat_agent(self, name: str, instructions: str, metadata: Dict[str, Any]) -> ChatAgent:
        """Create a ChatAgent with the specified configuration"""
        try:
            # Create a mock chat client for testing - in production this would be a real client
            from unittest.mock import Mock
            mock_chat_client = Mock()

            # Create chat agent with Agent Framework
            agent = ChatAgent(
                chat_client=mock_chat_client,
                instructions=instructions,
                name=name,
                **metadata
            )
            return agent
        except Exception as error:
            self.logger.error("Failed to create chat agent %s: %s", name, str(error))
            raise

    async def run_multi_agent_conversation(self, input_message: str, agent_roles: List[str] = None) -> Dict[str, Any]:
        """
        Run a multi-agent conversation using Agent Framework workflows
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
                        self.logger.warning("Agent role '%s' not found", role)
            else:
                # Use all available agents if none specified
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

        except Exception as error:
            self.logger.error("Multi-agent conversation failed: %s", str(error))
            self.stats["failed_completions"] += 1
            return {
                "success": False,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat(),
                "input_message": input_message,
                "selected_agents": [agent.name for agent in selected_agents]
            }

    async def _create_conversation_workflow(self, agents: List[ChatAgent], input_message: str) -> Any:
        """Create a workflow for multi-agent conversation"""
        try:
            workflow_builder = WorkflowBuilder()

            # Add agents to workflow
            for agent in agents:
                workflow_builder.add_agent(agent)

            # Define conversation flow
            workflow = workflow_builder.build_sequential_workflow(
                initial_message=input_message,
                agents=agents
            )

            return workflow

        except Exception as error:
            self.logger.error("Failed to create conversation workflow: %s", str(error))
            raise

    async def _execute_workflow(self, workflow: Any) -> Dict[str, Any]:
        """Execute the Agent Framework workflow"""
        try:
            # Execute the workflow
            result = await workflow.execute()

            return {
                "success": True,
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
                "workflow_id": getattr(workflow, 'id', 'unknown')
            }

        except Exception as error:
            self.logger.error("Workflow execution failed: %s", str(error))
            return {
                "success": False,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def create_agent(self, name: str, instructions: str, capabilities: List[str] = None) -> ChatAgent:
        """Create a new agent with specified capabilities"""
        metadata = {
            "capabilities": capabilities or [],
            "created_at": datetime.utcnow().isoformat()
        }

        agent = await self._create_chat_agent(name, instructions, metadata)
        self.agents[name] = agent

        self.logger.info("Created new agent: %s", name)
        return agent

    async def remove_agent(self, name: str) -> bool:
        """Remove an agent from the system"""
        if name in self.agents:
            del self.agents[name]
            self.logger.info("Removed agent: %s", name)
            return True
        else:
            self.logger.warning("Agent %s not found for removal", name)
            return False

    def get_agent(self, name: str) -> Optional[ChatAgent]:
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
            "framework": "Microsoft Agent Framework"
        }

    async def shutdown(self):
        """Shutdown the Agent Framework system"""
        try:
            # Clean up resources
            self.agents.clear()
            self.workflows.clear()
            self.is_initialized = False

            self.logger.info("Agent Framework System shutdown completed")

        except Exception as error:
            self.logger.error("Error during shutdown: %s", str(error))
