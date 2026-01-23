"""
AOS Multi-Agent System

Provides multi-agent orchestration capabilities using Microsoft Agent Framework.
Supports agent collaboration, workflow execution, and advanced orchestration patterns.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime

try:
    from agent_framework import ChatAgent, WorkflowBuilder
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    logging.warning("Agent Framework not available")

if TYPE_CHECKING:
    from agent_framework import ChatAgent

from .agent_framework_system import AgentFrameworkSystem
from ..agents.purpose_driven import BaseAgent

# Agent role definitions
BA_AGENT_NAME = "BusinessAnalyst"
BA_AGENT_INSTRUCTIONS = """You are a Business Analyst which will take the requirements from the user (also known as a 'customer') and create a project plan for creating the requested app. The Business Analyst understands the user requirements and creates detailed documents with requirements and costing. The documents should be usable by the SoftwareEngineer as a reference for implementing the required features, and by the
Product Owner for reference to determine if the application delivered by the Software Engineer meets all of the user's requirements."""

SE_AGENT_NAME = "SoftwareEngineer"
SE_AGENT_INSTRUCTIONS = """You are a Software Engineer, and your goal is create a web app using HTML and JavaScript by taking into consideration all the requirements given by the Business Analyst.
The application should implement all the requested features. Deliver the code to the Product Owner for review when completed.
You can also ask questions of the BusinessAnalyst to clarify any requirements that are unclear."""

PO_AGENT_NAME = "ProductOwner"
PO_AGENT_INSTRUCTIONS = """You are the Product Owner which will review the software engineer's code to ensure all user requirements are completed. You are the guardian of quality, ensuring the final product meets all specifications and receives the green light for release. Once all client requirements are completed, you can approve the request by just responding "%APPR%". Do not ask any other agent
or the user for approval. If there are missing features, you will need to send a request back
to the SoftwareEngineer or BusinessAnalyst with details of the defect. To approve, respond with the token %APPR%."""


class ApprovalTerminationStrategy:
    """A strategy for determining when an agent should terminate based on approval token."""

    def __init__(self, token: str = "%APPR%"):
        self.token = token

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate based on approval token."""
        if not history:
            return False

        # Check last few messages for approval token
        recent_messages = history[-3:] if len(history) > 3 else history
        for message in recent_messages:
            content = getattr(message, 'content', str(message))
            if self.token in content:
                return True

        return False

    def should_terminate(self, messages: List[Any]) -> bool:
        """Check if the conversation should terminate based on approval token."""
        if not messages:
            return False

        last_message = messages[-1]
        content = getattr(last_message, 'content', str(last_message))
        return self.token in content


class MultiAgentSystem:
    """
    Multi-agent system for AOS supporting various agent collaboration patterns.
    Uses Microsoft Agent Framework for modern multi-agent orchestration.
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.MultiAgentSystem")
        self.agents: Dict[str, BaseAgent] = {}
        self.is_initialized = False

        # Statistics
        self.stats = {
            "total_conversations": 0,
            "successful_completions": 0,
            "failed_completions": 0,
            "average_conversation_length": 0
        }

        # Initialize Agent Framework system
        self.agent_framework_system = AgentFrameworkSystem()

    async def initialize(self):
        """Initialize the multi-agent system"""
        try:
            self.logger.info("Initializing Multi-Agent System...")

            # Initialize Agent Framework system
            await self.agent_framework_system.initialize()

            # Initialize default agent roles
            await self._initialize_default_agents()

            self.is_initialized = True
            self.logger.info("Multi-Agent System initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Multi-Agent System: {e}")
            raise

    async def _initialize_default_agents(self):
        """Initialize default agent roles"""
        try:
            # Business Analyst Agent
            ba_agent = BusinessAnalystAgent()
            await ba_agent.initialize()
            self.agents[BA_AGENT_NAME] = ba_agent

            # Software Engineer Agent
            se_agent = SoftwareEngineerAgent()
            await se_agent.initialize()
            self.agents[SE_AGENT_NAME] = se_agent

            # Product Owner Agent
            po_agent = ProductOwnerAgent()
            await po_agent.initialize()
            self.agents[PO_AGENT_NAME] = po_agent

            self.logger.info(f"Initialized {len(self.agents)} default agents")

        except Exception as e:
            self.logger.error(f"Failed to initialize default agents: {e}")

    async def run_multi_agent_conversation(self, input_message: str, agent_roles: List[str] = None) -> Dict[str, Any]:
        """
        Run a multi-agent conversation to solve a problem using Agent Framework.

        Args:
            input_message: The initial user input/problem statement
            agent_roles: List of agent roles to include (defaults to all)

        Returns:
            Conversation result with messages and outcome
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            conversation_id = f"conversation_{datetime.now().timestamp()}"
            self.logger.info(f"Starting multi-agent conversation: {conversation_id}")

            # Use Agent Framework system for conversation
            result = await self.agent_framework_system.run_multi_agent_conversation(
                input_message, agent_roles
            )

            # Update statistics
            self.stats["total_conversations"] += 1
            if result.get("success", False):
                self.stats["successful_completions"] += 1
            else:
                self.stats["failed_completions"] += 1

            # Add conversation ID to result
            result["conversation_id"] = conversation_id
            return result

        except Exception as e:
            self.logger.error(f"Multi-agent conversation failed: {e}")
            self.stats["failed_completions"] += 1
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation_id
            }

    async def create_agent(self, name: str, instructions: str, capabilities: List[str] = None) -> 'ChatAgent':
        """Create a new agent with specified capabilities"""
        return await self.agent_framework_system.create_agent(name, instructions, capabilities)

    async def _run_basic_conversation(self, input_message: str, agents: List[BaseAgent]) -> Dict[str, Any]:
        """Run basic conversation without Semantic Kernel"""
        try:
            messages = [{"role": "user", "content": input_message, "timestamp": datetime.now().isoformat()}]
            current_message = input_message
            max_iterations = 10  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                # Get next agent response
                for agent in agents:
                    response = await agent.process_message(current_message)

                    message = {
                        "role": agent.agent_id,
                        "content": response.get("content", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    messages.append(message)

                    current_message = message["content"]

                    # Check for approval
                    if "%APPR%" in current_message:
                        return {
                            "success": True,
                            "approved": True,
                            "messages": messages,
                            "agent_count": len(agents),
                            "framework": "basic",
                            "iterations": iteration + 1
                        }

                iteration += 1

            # Conversation completed without approval
            return {
                "success": True,
                "approved": False,
                "messages": messages,
                "agent_count": len(agents),
                "framework": "basic",
                "iterations": iteration,
                "reason": "max_iterations_reached"
            }

        except Exception as e:
            self.logger.error(f"Basic conversation failed: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get multi-agent system statistics"""
        return {
            **self.stats,
            "total_agents": len(self.agents),
            "agent_framework_available": AGENT_FRAMEWORK_AVAILABLE,
            "is_initialized": self.is_initialized,
            "framework_stats": self.agent_framework_system.get_statistics() if self.agent_framework_system else None
        }

    def list_agents(self) -> List[str]:
        """List all available agent roles"""
        framework_agents = self.agent_framework_system.list_agents() if self.agent_framework_system else []
        return list(self.agents.keys()) + framework_agents

    async def remove_agent(self, name: str) -> bool:
        """Remove an agent from the system"""
        # Remove from legacy agents
        removed_legacy = False
        if name in self.agents:
            del self.agents[name]
            removed_legacy = True

        # Remove from Agent Framework system
        removed_framework = False
        if self.agent_framework_system:
            removed_framework = await self.agent_framework_system.remove_agent(name)

        return removed_legacy or removed_framework

    def get_agent(self, name: str):
        """Get an agent by name"""
        # Check legacy agents first
        if name in self.agents:
            return self.agents[name]

        # Check Agent Framework agents
        if self.agent_framework_system:
            return self.agent_framework_system.get_agent(name)

        return None

    async def shutdown(self):
        """Shutdown the multi-agent system"""
        try:
            # Shutdown Agent Framework system
            if self.agent_framework_system:
                await self.agent_framework_system.shutdown()

            # Clear legacy agents
            self.agents.clear()
            self.is_initialized = False

            self.logger.info("Multi-Agent System shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


class BusinessAnalystAgent(BaseAgent):
    """Business Analyst agent implementation"""

    def __init__(self):
        super().__init__(agent_id=BA_AGENT_NAME, agent_type="business_analyst")
        self.instructions = BA_AGENT_INSTRUCTIONS

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process message as Business Analyst"""
        # Placeholder implementation
        return {
            "content": f"[{self.agent_id}] Analyzing requirements: {message[:100]}...",
            "analysis": "Requirements analyzed and documented"
        }


class SoftwareEngineerAgent(BaseAgent):
    """Software Engineer agent implementation"""

    def __init__(self):
        super().__init__(agent_id=SE_AGENT_NAME, agent_type="software_engineer")
        self.instructions = SE_AGENT_INSTRUCTIONS

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process message as Software Engineer"""
        # Placeholder implementation
        return {
            "content": f"[{self.agent_id}] Implementing solution based on: {message[:100]}...",
            "code": "// Implementation placeholder"
        }


class ProductOwnerAgent(BaseAgent):
    """Product Owner agent implementation"""

    def __init__(self):
        super().__init__(agent_id=PO_AGENT_NAME, agent_type="product_owner")
        self.instructions = PO_AGENT_INSTRUCTIONS

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process message as Product Owner"""
        # Placeholder implementation - would include actual review logic
        if "implementation complete" in message.lower():
            return {
                "content": f"[{self.agent_id}] Reviewing implementation... %APPR%",
                "approved": True
            }
        else:
            return {
                "content": f"[{self.agent_id}] Reviewing: {message[:100]}...",
                "approved": False
            }