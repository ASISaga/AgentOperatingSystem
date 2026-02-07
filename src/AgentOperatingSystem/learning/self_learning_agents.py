"""
Enhanced AOS Agent Classes with Self-Learning Capabilities

Enhanced versions of base agent classes that integrate self-learning capabilities.
These classes combine the original AOS agent functionality with learning features.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..agents.purpose_driven import GenericPurposeDrivenAgent as BaseAgent, PurposeDrivenAgent
from .self_learning_mixin import SelfLearningMixin

# Legacy Agent and StatefulAgent classes for backward compatibility
# These can be replaced with PurposeDrivenAgent in the future
Agent = PurposeDrivenAgent
StatefulAgent = PurposeDrivenAgent


class SelfLearningAgent(SelfLearningMixin, Agent):
    """
    Agent class with integrated self-learning capabilities.

    Combines the standard Agent functionality with:
    - Domain expertise and knowledge management
    - RAG-based context retrieval
    - Interaction learning and feedback processing
    - Multi-domain support
    - Continuous improvement
    """

    def __init__(self, agent_id: str, name: str = None, domains: List[str] = None,
                 config: Dict[str, Any] = None, learning_config: Dict[str, Any] = None):
        # Set learning properties before calling super().__init__
        self.domains = domains or ['general']
        self.default_domain = self.domains[0] if self.domains else 'general'
        self.learning_config = learning_config or {}

        # Initialize both base classes
        super().__init__(agent_id, name, config)

        # Register learning-specific message handlers
        self.register_message_handler("user_request", self._handle_user_request_message)
        self.register_message_handler("rate_interaction", self._handle_rate_interaction_message)
        self.register_message_handler("add_knowledge", self._handle_add_knowledge_message)
        self.register_message_handler("get_insights", self._handle_get_insights_message)

    async def start(self):
        """Start the self-learning agent"""
        await super().start()

        # Initialize learning components if AOS context is available
        if self.aos_context:
            await self._initialize_learning_components(self.aos_context)

        self.logger.info(f"Self-Learning Agent {self.agent_id} started with domains: {self.domains}")

    async def _handle_user_request_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user request messages with learning capabilities"""
        try:
            user_input = message.get("content", "")
            domain = message.get("domain", self.default_domain)
            conversation_id = message.get("conversation_id")

            result = await self.handle_user_request(user_input, domain, conversation_id)

            # Return just the response to avoid nested serialization
            return result

        except Exception as e:
            self.logger.error(f"Error handling user request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def _handle_rate_interaction_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle interaction rating messages"""
        try:
            conversation_id = message.get("conversation_id")
            rating = message.get("rating")
            feedback = message.get("feedback", "")

            result = await self.rate_interaction(conversation_id, rating, feedback)

            return {
                "status": "success",
                "result": result,
                "agent_id": self.agent_id
            }

        except Exception as e:
            self.logger.error(f"Error rating interaction: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def _handle_add_knowledge_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle add knowledge messages"""
        try:
            domain = message.get("domain", self.default_domain)
            knowledge_entry = message.get("knowledge_entry", {})

            success = await self.add_domain_knowledge(domain, knowledge_entry)

            return {
                "status": "success",
                "added": success,
                "domain": domain,
                "agent_id": self.agent_id
            }

        except Exception as e:
            self.logger.error(f"Error adding knowledge: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def _handle_get_insights_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get insights messages"""
        try:
            domain = message.get("domain")

            insights = await self.get_domain_insights(domain)

            return {
                "status": "success",
                "insights": insights,
                "agent_id": self.agent_id
            }

        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get enhanced agent status including learning capabilities"""
        status = await super().get_status()

        # Add learning status
        learning_status = await self.get_learning_status()
        status.update({
            "learning": learning_status,
            "domains": self.domains,
            "default_domain": self.default_domain
        })

        return status


class SelfLearningStatefulAgent(SelfLearningMixin, StatefulAgent):
    """
    Stateful agent class with integrated self-learning capabilities.

    Combines StatefulAgent functionality with learning capabilities,
    maintaining both agent state and learning state.
    """

    def __init__(self, agent_id: str, name: str = None, domains: List[str] = None,
                 config: Dict[str, Any] = None, learning_config: Dict[str, Any] = None):
        # Set learning properties before calling super().__init__
        self.domains = domains or ['general']
        self.default_domain = self.domains[0] if self.domains else 'general'
        self.learning_config = learning_config or {}

        # Initialize both base classes
        super().__init__(agent_id, name, config)

        # Add learning state tracking
        self.learning_state = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "knowledge_entries_learned": 0,
            "last_learning_update": None
        }

        # Register learning-specific message handlers
        self.register_message_handler("user_request", self._handle_user_request_message)
        self.register_message_handler("rate_interaction", self._handle_rate_interaction_message)
        self.register_message_handler("update_learning_state", self._handle_update_learning_state_message)

    async def start(self):
        """Start the self-learning stateful agent"""
        await super().start()

        # Initialize learning components if AOS context is available
        if self.aos_context:
            await self._initialize_learning_components(self.aos_context)

        self.logger.info(f"Self-Learning Stateful Agent {self.agent_id} started")

    async def handle_user_request(self, user_input: str, domain: str = None,
                                conversation_id: str = None, **kwargs) -> Dict[str, Any]:
        """Enhanced user request handler that updates learning state"""
        result = await super().handle_user_request(user_input, domain, conversation_id, **kwargs)

        # Update learning state
        self.learning_state["total_interactions"] += 1
        self.learning_state["last_learning_update"] = datetime.utcnow().isoformat()

        # Update agent state
        self.set_state({
            "last_interaction": datetime.utcnow().isoformat(),
            "last_domain": domain or self.default_domain,
            "learning_state": self.learning_state
        })

        return result

    async def rate_interaction(self, conversation_id: str, rating: float, feedback: str = "") -> Dict[str, Any]:
        """Enhanced interaction rating that updates learning state"""
        result = await super().rate_interaction(conversation_id, rating, feedback)

        # Update learning state for successful interactions
        if rating >= 4.0:
            self.learning_state["successful_interactions"] += 1
            self.set_state({"learning_state": self.learning_state})

        return result

    async def add_domain_knowledge(self, domain: str, knowledge_entry: Dict[str, Any]):
        """Enhanced knowledge addition that updates learning state"""
        success = await super().add_domain_knowledge(domain, knowledge_entry)

        if success:
            self.learning_state["knowledge_entries_learned"] += 1
            self.learning_state["last_learning_update"] = datetime.utcnow().isoformat()
            self.set_state({"learning_state": self.learning_state})

        return success

    async def _handle_user_request_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user request messages"""
        try:
            user_input = message.get("content", "")
            domain = message.get("domain", self.default_domain)
            conversation_id = message.get("conversation_id")

            result = await self.handle_user_request(user_input, domain, conversation_id)

            # Return just the result to avoid nested serialization
            return result

        except Exception as e:
            self.logger.error(f"Error handling user request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def _handle_rate_interaction_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle interaction rating messages"""
        try:
            conversation_id = message.get("conversation_id")
            rating = message.get("rating")
            feedback = message.get("feedback", "")

            result = await self.rate_interaction(conversation_id, rating, feedback)

            return {
                "status": "success",
                "result": result,
                "agent_id": self.agent_id,
                "updated_state": self.get_state()
            }

        except Exception as e:
            self.logger.error(f"Error rating interaction: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def _handle_update_learning_state_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle learning state update messages"""
        try:
            state_updates = message.get("state_updates", {})

            self.learning_state.update(state_updates)
            self.set_state({"learning_state": self.learning_state})

            return {
                "status": "success",
                "updated_learning_state": self.learning_state,
                "agent_id": self.agent_id
            }

        except Exception as e:
            self.logger.error(f"Error updating learning state: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get enhanced status including learning and state information"""
        status = await super().get_status()

        # Add learning status
        learning_status = await self.get_learning_status()
        status.update({
            "learning": learning_status,
            "learning_state": self.learning_state,
            "domains": self.domains,
            "default_domain": self.default_domain
        })

        return status

    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning-specific metrics"""
        total = self.learning_state["total_interactions"]
        successful = self.learning_state["successful_interactions"]

        return {
            "total_interactions": total,
            "successful_interactions": successful,
            "success_rate": successful / total if total > 0 else 0,
            "knowledge_entries_learned": self.learning_state["knowledge_entries_learned"],
            "last_learning_update": self.learning_state["last_learning_update"]
        }