"""
Domain Expert for AOS Learning System

Provides specialized domain expertise and knowledge management for agents.
Handles domain-specific reasoning, context, and best practices.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .knowledge_manager import KnowledgeManager
from .rag_engine import RAGEngine


class DomainExpert:
    """
    Provides domain-specific expertise and reasoning capabilities.
    Acts as a specialized knowledge processor for different business domains.
    """

    def __init__(self, domain: str, knowledge_manager: KnowledgeManager,
                 rag_engine: RAGEngine = None, config: Dict[str, Any] = None):
        self.domain = domain
        self.knowledge_manager = knowledge_manager
        self.rag_engine = rag_engine
        self.config = config or {}
        self.logger = logging.getLogger(f"AOS.Learning.DomainExpert.{domain}")

        # Domain-specific configuration
        self.expertise_level = self.config.get("expertise_level", "intermediate")
        self.response_style = self.config.get("response_style", "professional")
        self.max_context_snippets = self.config.get("max_context_snippets", 5)

        # Domain capabilities cache
        self._capabilities_cache = None
        self._context_cache = None
        self._last_cache_update = None

    async def initialize(self):
        """Initialize the domain expert"""
        try:
            await self._load_domain_capabilities()
            await self._load_domain_context()

            self.logger.info(f"Domain Expert initialized for {self.domain}")

        except Exception as e:
            self.logger.error(f"Failed to initialize Domain Expert for {self.domain}: {e}")
            raise

    async def _load_domain_capabilities(self):
        """Load domain-specific capabilities and knowledge"""
        self._capabilities_cache = await self.knowledge_manager.get_domain_knowledge(self.domain)
        self._last_cache_update = datetime.utcnow()

        self.logger.debug(f"Loaded {len(self._capabilities_cache)} capabilities for {self.domain}")

    async def _load_domain_context(self):
        """Load domain context and directives"""
        self._context_cache = await self.knowledge_manager.get_domain_context(self.domain)

        self.logger.debug(f"Loaded context for {self.domain}")

    async def process_domain_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query specific to this domain"""
        try:
            # Build comprehensive domain context
            domain_context = await self._build_domain_context(query, context)

            # Generate domain-specific response
            response = await self._generate_domain_response(query, domain_context)

            # Add domain insights
            insights = await self._extract_domain_insights(query, response, domain_context)

            return {
                "domain": self.domain,
                "query": query,
                "response": response,
                "context": domain_context,
                "insights": insights,
                "confidence": self._calculate_confidence(domain_context),
                "timestamp": datetime.utcnow().isoformat(),
                "success": True
            }

        except Exception as e:
            self.logger.error(f"Error processing domain query: {e}")
            return {
                "domain": self.domain,
                "query": query,
                "error": str(e),
                "success": False
            }

    async def _build_domain_context(self, query: str, additional_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build comprehensive context for domain processing"""
        context = {
            "domain": self.domain,
            "query": query,
            "expertise_level": self.expertise_level,
            "response_style": self.response_style
        }

        # Add cached domain context
        if self._context_cache:
            context.update(self._context_cache)

        # Add domain directives
        directives = await self.knowledge_manager.get_agent_directives(self.domain)
        context["directives"] = directives

        # Get RAG-based context if available
        if self.rag_engine:
            try:
                rag_results = await self.rag_engine.query_knowledge(
                    self.domain, query, self.max_context_snippets
                )
                context["knowledge_snippets"] = rag_results

                # Get similar past interactions
                similar_interactions = await self.rag_engine.get_similar_interactions(query, self.domain)
                context["similar_interactions"] = similar_interactions

            except Exception as e:
                self.logger.warning(f"Failed to get RAG context: {e}")
                context["knowledge_snippets"] = []
                context["similar_interactions"] = []

        # Add any additional context
        if additional_context:
            context.update(additional_context)

        return context

    async def _generate_domain_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a domain-specific response"""
        response_parts = []

        # Start with domain expertise
        purpose = context.get("purpose", "")
        if purpose:
            response_parts.append(f"As a {self.domain} expert, I'll address your question: {query}")

        # Add relevant knowledge snippets
        knowledge_snippets = context.get("knowledge_snippets", [])
        if knowledge_snippets:
            high_relevance = [s for s in knowledge_snippets if s.get("similarity", 0) > 0.8]
            if high_relevance:
                response_parts.append("\\nBased on relevant domain knowledge:")
                for snippet in high_relevance[:3]:
                    response_parts.append(f"• {snippet['content']}")

        # Add domain-specific guidance
        key_metrics = context.get("key_metrics", [])
        responsibilities = context.get("responsibilities", [])

        if responsibilities:
            relevant_responsibilities = [r for r in responsibilities if any(word in query.lower() for word in r.split('_'))]
            if relevant_responsibilities:
                response_parts.append(f"\\nIn the {self.domain} domain, this relates to: {', '.join(relevant_responsibilities)}")

        # Add best practices
        directives = context.get("directives", "")
        if directives:
            response_parts.append(f"\\nBest practices: {directives}")

        # Add similar interaction insights
        similar_interactions = context.get("similar_interactions", [])
        if similar_interactions:
            successful_interactions = [i for i in similar_interactions if i.get("metadata", {}).get("rating", 0) >= 4.0]
            if successful_interactions:
                response_parts.append("\\nBased on successful similar interactions:")
                response_parts.append(f"• {successful_interactions[0]['content'][:200]}...")

        # Closing based on response style
        if self.response_style == "professional":
            response_parts.append("\\nPlease let me know if you need any clarification or have additional questions.")
        elif self.response_style == "friendly":
            response_parts.append("\\nHope this helps! Feel free to ask if you need more details.")
        else:
            response_parts.append("\\nHow else can I assist you with this topic?")

        return "\\n".join(response_parts)

    async def _extract_domain_insights(self, query: str, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from the domain processing"""
        insights = {
            "query_type": self._classify_query_type(query),
            "knowledge_sources_used": len(context.get("knowledge_snippets", [])),
            "similar_interactions_found": len(context.get("similar_interactions", [])),
            "domain_coverage": self._assess_domain_coverage(query, context)
        }

        # Add confidence factors
        confidence_factors = []
        if context.get("knowledge_snippets"):
            confidence_factors.append("relevant_knowledge_available")
        if context.get("similar_interactions"):
            confidence_factors.append("similar_interactions_found")
        if context.get("directives"):
            confidence_factors.append("domain_directives_applied")

        insights["confidence_factors"] = confidence_factors

        return insights

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of domain query"""
        query_lower = query.lower()

        # Domain-specific classifications
        if self.domain == "sales":
            if any(word in query_lower for word in ["lead", "prospect", "customer"]):
                return "customer_management"
            elif any(word in query_lower for word in ["revenue", "target", "quota"]):
                return "revenue_planning"
            elif any(word in query_lower for word in ["proposal", "pitch", "presentation"]):
                return "sales_process"

        elif self.domain == "leadership":
            if any(word in query_lower for word in ["team", "staff", "employee"]):
                return "team_management"
            elif any(word in query_lower for word in ["strategy", "vision", "goal"]):
                return "strategic_planning"
            elif any(word in query_lower for word in ["decision", "choice", "option"]):
                return "decision_making"

        elif self.domain == "erp":
            if any(word in query_lower for word in ["process", "workflow", "procedure"]):
                return "process_management"
            elif any(word in query_lower for word in ["data", "report", "analytics"]):
                return "data_management"
            elif any(word in query_lower for word in ["integration", "system", "module"]):
                return "system_integration"

        elif self.domain == "crm":
            if any(word in query_lower for word in ["customer", "client", "account"]):
                return "customer_management"
            elif any(word in query_lower for word in ["support", "service", "ticket"]):
                return "customer_support"
            elif any(word in query_lower for word in ["relationship", "retention", "satisfaction"]):
                return "relationship_management"

        # General classifications
        if any(word in query_lower for word in ["what", "how", "why", "when", "where"]):
            return "information_request"
        elif any(word in query_lower for word in ["help", "assist", "support"]):
            return "assistance_request"
        else:
            return "general_inquiry"

    def _assess_domain_coverage(self, query: str, context: Dict[str, Any]) -> str:
        """Assess how well the domain can cover this query"""
        query_lower = query.lower()

        # Check if query aligns with domain responsibilities
        responsibilities = context.get("responsibilities", [])
        if responsibilities:
            relevant_count = sum(1 for resp in responsibilities
                               if any(word in query_lower for word in resp.split('_')))
            if relevant_count > 0:
                return "high"

        # Check knowledge availability
        knowledge_snippets = context.get("knowledge_snippets", [])
        if knowledge_snippets:
            high_relevance_count = sum(1 for snippet in knowledge_snippets
                                     if snippet.get("similarity", 0) > 0.8)
            if high_relevance_count >= 2:
                return "high"
            elif high_relevance_count >= 1:
                return "medium"

        return "low"

    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for domain response"""
        confidence = 0.5  # Base confidence

        # Boost confidence based on available context
        if context.get("knowledge_snippets"):
            high_relevance = [s for s in context["knowledge_snippets"] if s.get("similarity", 0) > 0.8]
            confidence += min(0.3, len(high_relevance) * 0.1)

        if context.get("similar_interactions"):
            successful = [i for i in context["similar_interactions"]
                         if i.get("metadata", {}).get("rating", 0) >= 4.0]
            confidence += min(0.2, len(successful) * 0.1)

        if context.get("directives"):
            confidence += 0.1

        if context.get("responsibilities"):
            confidence += 0.1

        return min(1.0, confidence)

    async def add_domain_knowledge(self, knowledge_entry: Dict[str, Any]):
        """Add knowledge specific to this domain"""
        await self.knowledge_manager.add_knowledge_entry(self.domain, knowledge_entry)

        # Update RAG if available
        if self.rag_engine:
            content = knowledge_entry.get("content", str(knowledge_entry))
            entry_id = knowledge_entry.get("id", f"entry_{datetime.utcnow().timestamp()}")
            metadata = {k: v for k, v in knowledge_entry.items() if k not in ["content", "id"]}
            metadata["expertise_level"] = self.expertise_level

            await self.rag_engine.add_knowledge_entry(self.domain, entry_id, content, metadata)

        # Refresh capabilities cache
        await self._load_domain_capabilities()

        self.logger.info(f"Added knowledge entry to {self.domain} domain")

    async def update_domain_context(self, context_updates: Dict[str, Any]):
        """Update domain context and directives"""
        current_context = await self.knowledge_manager.get_domain_context(self.domain)
        current_context.update(context_updates)

        # This would typically involve updating the knowledge manager's storage
        # For now, we'll update the cache
        self._context_cache = current_context

        self.logger.info(f"Updated context for {self.domain} domain")

    async def get_domain_status(self) -> Dict[str, Any]:
        """Get status information for this domain expert"""
        status = {
            "domain": self.domain,
            "expertise_level": self.expertise_level,
            "response_style": self.response_style,
            "knowledge_entries": len(self._capabilities_cache or []),
            "last_cache_update": self._last_cache_update.isoformat() if self._last_cache_update else None,
            "rag_available": self.rag_engine is not None
        }

        if self.rag_engine:
            try:
                rag_stats = await self.rag_engine.get_domain_statistics(self.domain)
                status["rag_statistics"] = rag_stats
            except Exception as e:
                self.logger.warning(f"Failed to get RAG statistics: {e}")

        return status