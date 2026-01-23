"""
Self-Learning Mixin for AOS Agents

Provides self-learning capabilities that can be mixed into any AOS agent.
Integrates knowledge management, RAG, and interaction learning.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .interaction_learner import InteractionLearner
from .knowledge_manager import KnowledgeManager
from .rag_engine import RAGEngine


class SelfLearningMixin:
    """
    Mixin class that adds self-learning capabilities to any AOS agent.

    This mixin provides:
    - Domain knowledge management
    - RAG-based context retrieval
    - Interaction learning and feedback processing
    - Multi-domain expertise
    - Continuous improvement capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Learning components (will be initialized by AOS)
        self.knowledge_manager: Optional[KnowledgeManager] = None
        self.rag_engine: Optional[RAGEngine] = None
        self.interaction_learner: Optional[InteractionLearner] = None

        # Learning-specific logger
        self.learning_logger = logging.getLogger(f"AOS.Learning.{self.__class__.__name__}")

        # Domain configuration
        self.domains = getattr(self, 'domains', ['general'])
        self.default_domain = getattr(self, 'default_domain', 'general')

        # Conversation tracking
        self.conversations = {}

        # Learning configuration
        self.learning_config = getattr(self, 'learning_config', {})
        self.enable_rag = self.learning_config.get('enable_rag', True)
        self.enable_interaction_learning = self.learning_config.get('enable_interaction_learning', True)
        self.min_similarity = self.learning_config.get('min_similarity', 0.7)
        self.top_k_snippets = self.learning_config.get('top_k_snippets', 5)

    async def _initialize_learning_components(self, aos_context):
        """Initialize learning components (called by AOS during agent setup)"""
        try:
            if hasattr(aos_context, 'knowledge_manager'):
                self.knowledge_manager = aos_context.knowledge_manager

            if hasattr(aos_context, 'rag_engine'):
                self.rag_engine = aos_context.rag_engine

            if hasattr(aos_context, 'interaction_learner'):
                self.interaction_learner = aos_context.interaction_learner

            self.learning_logger.info("Learning components initialized for agent")

        except Exception as error:
            self.learning_logger.error("Failed to initialize learning components: %s", str(error))

    async def handle_user_request(self, user_input: str, domain: str = None,
                                conversation_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Enhanced user request handler with self-learning capabilities.

        This method integrates knowledge retrieval, context building, and learning.
        """
        domain = domain or self.default_domain
        conversation_id = conversation_id or f"conv_{self.agent_id}_{datetime.utcnow().timestamp()}"

        try:
            # Track conversation
            self._track_conversation(conversation_id, "user", user_input, domain)

            # Get domain context and knowledge
            context = await self._build_learning_context(domain, user_input, conversation_id)

            # Generate response using learning-enhanced processing
            response = await self._generate_learning_enhanced_response(
                user_input, domain, context, conversation_id, **kwargs
            )

            # Track agent response
            self._track_conversation(conversation_id, "agent", response, domain)

            # Log interaction for learning
            if self.interaction_learner and self.enable_interaction_learning:
                await self.interaction_learner.log_interaction(
                    agent_id=self.agent_id,
                    user_input=user_input,
                    response=response,
                    domain=domain,
                    conversation_id=conversation_id,
                    context=context
                )

            return {
                "response": response,
                "domain": domain,
                "conversation_id": conversation_id,
                "context_snippets": len(context.get("rag_snippets", [])),
                "learning_enabled": True,
                "success": True
            }

        except Exception as error:
            self.learning_logger.error("Error in learning-enhanced request handling: %s", str(error))
            return {
                "error": str(error),
                "domain": domain,
                "conversation_id": conversation_id,
                "success": False
            }

    async def _build_learning_context(self, domain: str, query: str, conversation_id: str) -> Dict[str, Any]:
        """Build comprehensive context using learning components"""
        context = {
            "domain": domain,
            "query": query,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Get domain context from knowledge manager
        if self.knowledge_manager:
            try:
                domain_context = await self.knowledge_manager.get_domain_context(domain)
                context.update({
                    "purpose": domain_context.get("purpose", ""),
                    "key_metrics": domain_context.get("key_metrics", []),
                    "responsibilities": domain_context.get("responsibilities", [])
                })

                # Get agent directives
                directives = await self.knowledge_manager.get_agent_directives(domain)
                context["directives"] = directives

                # Get domain knowledge
                knowledge = await self.knowledge_manager.get_domain_knowledge(domain)
                context["domain_knowledge"] = knowledge

            except Exception as error:
                self.learning_logger.warning("Failed to get knowledge manager context: %s", str(error))

        # Get RAG snippets if available
        if self.rag_engine and self.enable_rag:
            try:
                rag_snippets = await self.rag_engine.query_knowledge(domain, query, self.top_k_snippets)
                context["rag_snippets"] = rag_snippets

                # Also get relevant past interactions
                similar_interactions = await self.rag_engine.get_similar_interactions(query, domain)
                context["similar_interactions"] = similar_interactions

            except Exception as error:
                self.learning_logger.warning("Failed to get RAG context: %s", str(error))
                context["rag_snippets"] = []
                context["similar_interactions"] = []

        # Get conversation history
        conversation_history = self.conversations.get(conversation_id, [])
        context["conversation_history"] = conversation_history[-5:]  # Last 5 exchanges

        return context

    async def _generate_learning_enhanced_response(self, user_input: str, domain: str,
                                                 context: Dict[str, Any], conversation_id: str,
                                                 **kwargs) -> str:
        """Generate response using learning-enhanced context"""

        # Generate learning-based response directly to avoid recursion
        return await self._generate_learning_based_response(user_input, domain, context)

    async def _enhance_response_with_learning(self, base_response: str, context: Dict[str, Any]) -> str:
        """Enhance a base response with learning context"""
        enhanced_parts = [base_response]

        # Add relevant RAG snippets if available and useful
        rag_snippets = context.get("rag_snippets", [])
        if rag_snippets and len(rag_snippets) > 0:
            high_relevance_snippets = [s for s in rag_snippets if s.get("similarity", 0) > 0.8]
            if high_relevance_snippets:
                enhanced_parts.append("\\nBased on relevant knowledge:")
                for snippet in high_relevance_snippets[:2]:  # Top 2 most relevant
                    enhanced_parts.append(f"- {snippet['content'][:200]}...")

        # Add domain-specific guidance if appropriate
        directives = context.get("directives", "")
        if directives and len(base_response) < 100:  # Only for short responses
            enhanced_parts.append(f"\\n\\nFollowing {context.get('domain', 'general')} best practices: {directives}")

        return "\\n".join(enhanced_parts)

    async def _generate_learning_based_response(self, user_input: str, domain: str, context: Dict[str, Any]) -> str:
        """Generate response purely from learning context (fallback)"""
        response_parts = []

        # Start with domain expertise
        purpose = context.get("purpose", "")
        if purpose:
            response_parts.append(f"As a {domain} expert, I understand you're asking about: {user_input}")
            response_parts.append(f"\\nIn the {domain} domain, my purpose is: {purpose}")
        else:
            response_parts.append(f"I'll help you with your {domain} related question: {user_input}")

        # Add RAG knowledge if available
        rag_snippets = context.get("rag_snippets", [])
        if rag_snippets:
            response_parts.append("\\nBased on relevant knowledge:")
            for snippet in rag_snippets[:3]:  # Top 3 snippets
                response_parts.append(f"- {snippet['content']}")

        # Add domain knowledge
        domain_knowledge = context.get("domain_knowledge", [])
        if domain_knowledge:
            response_parts.append("\\nRelevant domain information:")
            for knowledge in domain_knowledge[:2]:  # Top 2 entries
                if isinstance(knowledge, dict):
                    response_parts.append(f"- {knowledge.get('content', str(knowledge))}")
                else:
                    response_parts.append(f"- {str(knowledge)}")

        # Add directives
        directives = context.get("directives", "")
        if directives:
            response_parts.append(f"\\nFollowing {domain} best practices: {directives}")

        # Closing
        response_parts.append("\\nHow can I help you further with this topic?")

        return "\\n".join(response_parts)

    def _track_conversation(self, conversation_id: str, role: str, content: str, domain: str):
        """Track conversation for context building"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep only last 20 exchanges per conversation
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]

    async def rate_interaction(self, conversation_id: str, rating: float, feedback: str = "") -> Dict[str, Any]:
        """Rate an interaction for learning purposes"""
        try:
            if self.interaction_learner:
                success = await self.interaction_learner.add_feedback(conversation_id, rating, feedback)

                if success and self.rag_engine:
                    # Add the interaction to RAG if it was highly rated
                    conversation = self.conversations.get(conversation_id, [])
                    if conversation and rating >= 4.0:
                        last_user_msg = None
                        last_agent_msg = None

                        for msg in reversed(conversation):
                            if msg["role"] == "agent" and not last_agent_msg:
                                last_agent_msg = msg
                            elif msg["role"] == "user" and not last_user_msg:
                                last_user_msg = msg

                            if last_user_msg and last_agent_msg:
                                break

                        if last_user_msg and last_agent_msg:
                            await self.rag_engine.add_interaction_learning(
                                user_input=last_user_msg["content"],
                                response=last_agent_msg["content"],
                                domain=last_user_msg["domain"],
                                rating=rating,
                                context={"conversation_id": conversation_id}
                            )

                return {
                    "conversation_id": conversation_id,
                    "rating": rating,
                    "feedback": feedback,
                    "success": success
                }
            else:
                return {"error": "Interaction learning not available", "success": False}

        except Exception as error:
            self.learning_logger.error("Error rating interaction: %s", str(error))
            return {"error": str(error), "success": False}

    async def get_learning_status(self) -> Dict[str, Any]:
        """Get the learning status of this agent"""
        status = {
            "agent_id": self.agent_id,
            "learning_enabled": True,
            "domains": self.domains,
            "default_domain": self.default_domain,
            "active_conversations": len(self.conversations),
            "components": {
                "knowledge_manager": self.knowledge_manager is not None,
                "rag_engine": self.rag_engine is not None,
                "interaction_learner": self.interaction_learner is not None
            },
            "configuration": {
                "enable_rag": self.enable_rag,
                "enable_interaction_learning": self.enable_interaction_learning,
                "min_similarity": self.min_similarity,
                "top_k_snippets": self.top_k_snippets
            }
        }

        # Add component-specific status
        if self.rag_engine:
            try:
                rag_stats = await self.rag_engine.get_system_statistics()
                status["rag_statistics"] = rag_stats
            except Exception as error:
                self.learning_logger.warning("Failed to get RAG statistics: %s", str(error))

        if self.interaction_learner:
            try:
                learning_summary = await self.interaction_learner.get_learning_summary()
                status["learning_summary"] = learning_summary
            except Exception as error:
                self.learning_logger.warning("Failed to get learning summary: %s", str(error))

        return status

    async def add_domain_knowledge(self, domain: str, knowledge_entry: Dict[str, Any]):
        """Add knowledge to a specific domain"""
        if self.knowledge_manager:
            await self.knowledge_manager.add_knowledge_entry(domain, knowledge_entry)

            # Also add to RAG if available
            if self.rag_engine and isinstance(knowledge_entry, dict):
                content = knowledge_entry.get("content", str(knowledge_entry))
                entry_id = knowledge_entry.get("id", f"entry_{datetime.utcnow().timestamp()}")
                metadata = {k: v for k, v in knowledge_entry.items() if k not in ["content", "id"]}

                await self.rag_engine.add_knowledge_entry(domain, entry_id, content, metadata)

            self.learning_logger.info("Added knowledge entry to domain: %s", domain)
            return True

        return False

    async def get_domain_insights(self, domain: str = None) -> Dict[str, Any]:
        """Get learning insights for a domain"""
        domain = domain or self.default_domain

        insights = {
            "domain": domain,
            "agent_id": self.agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        if self.interaction_learner:
            try:
                learning_insights = await self.interaction_learner.get_domain_insights(domain)
                insights.update(learning_insights)
            except Exception as error:
                self.learning_logger.warning("Failed to get interaction insights: %s", str(error))

        if self.rag_engine:
            try:
                rag_stats = await self.rag_engine.get_domain_statistics(domain)
                insights["rag_statistics"] = rag_stats
            except Exception as error:
                self.learning_logger.warning("Failed to get RAG domain statistics: %s", str(error))

        return insights
