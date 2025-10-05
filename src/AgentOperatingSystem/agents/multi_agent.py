"""
AOS Multi-Agent System

Provides multi-agent orchestration capabilities using various frameworks.
Supports agent collaboration, workflow execution, and termination strategies.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
    from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
    from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import (
        KernelFunctionSelectionStrategy,
    )
    from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
    from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
    from semantic_kernel.contents.chat_message_content import ChatMessageContent
    from semantic_kernel.contents.utils.author_role import AuthorRole
    from semantic_kernel.kernel import Kernel
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    SEMANTIC_KERNEL_AVAILABLE = False
    logging.warning("Semantic Kernel not available")

from .base import BaseAgent

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
    
    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate based on approval token."""
        if not SEMANTIC_KERNEL_AVAILABLE:
            return False
        
        return any("%APPR%" in message.content for message in history)


class MultiAgentSystem:
    """
    Multi-agent system for AOS supporting various agent collaboration patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AOS.MultiAgentSystem")
        self.agents: Dict[str, BaseAgent] = {}
        self.kernel = None
        self.group_chat = None
        self.is_initialized = False
        
        # Statistics
        self.stats = {
            "total_conversations": 0,
            "successful_completions": 0,
            "failed_completions": 0,
            "average_conversation_length": 0
        }
    
    async def initialize(self):
        """Initialize the multi-agent system"""
        try:
            self.logger.info("Initializing Multi-Agent System...")
            
            if SEMANTIC_KERNEL_AVAILABLE:
                await self._initialize_semantic_kernel()
            
            # Initialize default agent roles
            await self._initialize_default_agents()
            
            self.is_initialized = True
            self.logger.info("Multi-Agent System initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Multi-Agent System: {e}")
            raise
    
    async def _initialize_semantic_kernel(self):
        """Initialize Semantic Kernel components"""
        try:
            service_id = "agent"
            self.kernel = Kernel()
            
            # Add Azure Chat Completion service if configured
            if os.getenv("AZURE_OPENAI_ENDPOINT"):
                self.kernel.add_service(AzureChatCompletion(service_id=service_id))
                settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
                settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
            
            self.logger.info("Semantic Kernel initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Semantic Kernel: {e}")
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
        Run a multi-agent conversation to solve a problem.
        
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
            
            # Select agents for this conversation
            if agent_roles is None:
                selected_agents = list(self.agents.values())
            else:
                selected_agents = [self.agents[role] for role in agent_roles if role in self.agents]
            
            if not selected_agents:
                raise ValueError("No valid agents selected for conversation")
            
            # Run conversation
            if SEMANTIC_KERNEL_AVAILABLE and self.kernel:
                result = await self._run_semantic_kernel_conversation(input_message, selected_agents)
            else:
                result = await self._run_basic_conversation(input_message, selected_agents)
            
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
                "conversation_id": conversation_id
            }
    
    async def _run_semantic_kernel_conversation(self, input_message: str, agents: List[BaseAgent]) -> Dict[str, Any]:
        """Run conversation using Semantic Kernel framework"""
        try:
            # Create Semantic Kernel agents
            sk_agents = []
            for agent in agents:
                if hasattr(agent, 'to_semantic_kernel_agent'):
                    sk_agent = agent.to_semantic_kernel_agent(self.kernel)
                    sk_agents.append(sk_agent)
            
            if not sk_agents:
                # Fallback to basic conversation
                return await self._run_basic_conversation(input_message, agents)
            
            # Create group chat with termination strategy
            termination_strategy = ApprovalTerminationStrategy()
            selection_strategy = KernelFunctionSelectionStrategy()
            
            group_chat = AgentGroupChat(
                agents=sk_agents,
                termination_strategy=termination_strategy,
                selection_strategy=selection_strategy
            )
            
            # Start conversation
            initial_message = ChatMessageContent(
                role=AuthorRole.USER,
                content=input_message
            )
            
            messages = []
            async for message in group_chat.invoke(initial_message):
                messages.append({
                    "role": message.role.value,
                    "content": message.content,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check if conversation was approved
            approved = any("%APPR%" in msg["content"] for msg in messages)
            
            return {
                "success": True,
                "approved": approved,
                "messages": messages,
                "agent_count": len(sk_agents),
                "framework": "semantic_kernel"
            }
            
        except Exception as e:
            self.logger.error(f"Semantic Kernel conversation failed: {e}")
            raise
    
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
            "semantic_kernel_available": SEMANTIC_KERNEL_AVAILABLE,
            "is_initialized": self.is_initialized
        }
    
    def list_agents(self) -> List[str]:
        """List all available agent roles"""
        return list(self.agents.keys())


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