"""
Learning Pipeline for AOS Learning System

Orchestrates the learning process across all components.
Manages continuous learning, knowledge updates, and system improvement.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .knowledge_manager import KnowledgeManager
from .rag_engine import RAGEngine
from .interaction_learner import InteractionLearner
from .domain_expert import DomainExpert


class LearningPipeline:
    """
    Orchestrates the learning process across all learning components.

    Manages:
    - Continuous learning from interactions
    - Knowledge base updates and optimization
    - Performance monitoring and improvement
    - Cross-domain knowledge sharing
    """

    def __init__(self, knowledge_manager: KnowledgeManager, rag_engine: RAGEngine,
                 interaction_learner: InteractionLearner, config: Dict[str, Any] = None):
        self.knowledge_manager = knowledge_manager
        self.rag_engine = rag_engine
        self.interaction_learner = interaction_learner
        self.config = config or {}
        self.logger = logging.getLogger("AOS.Learning.Pipeline")

        # Domain experts registry
        self.domain_experts = {}

        # Pipeline configuration
        self.learning_cycle_hours = self.config.get("learning_cycle_hours", 24)
        self.knowledge_update_threshold = self.config.get("knowledge_update_threshold", 0.8)
        self.cross_domain_sharing_enabled = self.config.get("cross_domain_sharing", True)
        self.auto_optimization_enabled = self.config.get("auto_optimization", True)

        # Pipeline state
        self.is_running = False
        self.last_learning_cycle = None
        self.learning_stats = {
            "cycles_completed": 0,
            "knowledge_entries_added": 0,
            "patterns_learned": 0,
            "optimizations_applied": 0
        }

        # Async tasks
        self._learning_task = None

    async def initialize(self):
        """Initialize the learning pipeline"""
        try:
            # Initialize domain experts for known domains
            await self._initialize_domain_experts()

            # Start continuous learning if enabled
            if self.config.get("auto_start", True):
                await self.start()

            self.logger.info("Learning Pipeline initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Learning Pipeline: {e}")
            raise

    async def _initialize_domain_experts(self):
        """Initialize domain experts for available domains"""
        try:
            # Get available domains from knowledge manager
            summary = await self.knowledge_manager.get_knowledge_summary()
            domains = summary.get("domains", ["general"])

            for domain in domains:
                if domain not in self.domain_experts:
                    expert = DomainExpert(
                        domain=domain,
                        knowledge_manager=self.knowledge_manager,
                        rag_engine=self.rag_engine,
                        config=self.config.get(f"domain_{domain}", {})
                    )
                    await expert.initialize()
                    self.domain_experts[domain] = expert

                    self.logger.info(f"Initialized domain expert for: {domain}")

        except Exception as e:
            self.logger.error(f"Failed to initialize domain experts: {e}")

    async def start(self):
        """Start the learning pipeline"""
        if self.is_running:
            self.logger.warning("Learning pipeline is already running")
            return

        self.is_running = True
        self._learning_task = asyncio.create_task(self._run_learning_cycle())

        self.logger.info("Learning Pipeline started")

    async def stop(self):
        """Stop the learning pipeline"""
        if not self.is_running:
            return

        self.is_running = False

        if self._learning_task:
            self._learning_task.cancel()
            try:
                await self._learning_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Learning Pipeline stopped")

    async def _run_learning_cycle(self):
        """Run the continuous learning cycle"""
        while self.is_running:
            try:
                cycle_start = datetime.utcnow()

                # Run learning cycle
                await self._execute_learning_cycle()

                # Update statistics
                self.learning_stats["cycles_completed"] += 1
                self.last_learning_cycle = cycle_start

                # Wait for next cycle
                cycle_duration = datetime.utcnow() - cycle_start
                wait_time = max(3600, self.learning_cycle_hours * 3600 - cycle_duration.total_seconds())

                self.logger.info(f"Learning cycle completed in {cycle_duration.total_seconds():.1f}s, next cycle in {wait_time/3600:.1f}h")

                await asyncio.sleep(wait_time)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in learning cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _execute_learning_cycle(self):
        """Execute a complete learning cycle"""
        self.logger.info("Starting learning cycle")

        # Phase 1: Analyze recent interactions
        await self._analyze_recent_interactions()

        # Phase 2: Update knowledge base
        await self._update_knowledge_base()

        # Phase 3: Optimize RAG performance
        if self.rag_engine:
            await self._optimize_rag_performance()

        # Phase 4: Cross-domain learning
        if self.cross_domain_sharing_enabled:
            await self._cross_domain_learning()

        # Phase 5: System optimization
        if self.auto_optimization_enabled:
            await self._optimize_system_performance()

        self.logger.info("Learning cycle completed")

    async def _analyze_recent_interactions(self):
        """Analyze recent interactions for learning opportunities"""
        try:
            # Get learning summary
            summary = await self.interaction_learner.get_learning_summary()

            # Analyze domain-specific insights
            domain_insights = summary.get("domain_insights", {})

            for domain, insights in domain_insights.items():
                avg_rating = insights.get("avg_rating")
                success_rate = insights.get("success_rate")

                # Identify improvement opportunities
                if avg_rating and avg_rating < 3.5:
                    await self._handle_low_performance_domain(domain, insights)

                if success_rate and success_rate < 0.7:
                    await self._handle_low_success_rate(domain, insights)

                # Extract successful patterns
                if avg_rating and avg_rating > 4.0:
                    await self._extract_successful_patterns(domain, insights)

            self.logger.debug("Completed interaction analysis")

        except Exception as e:
            self.logger.error(f"Error analyzing interactions: {e}")

    async def _update_knowledge_base(self):
        """Update knowledge base with learned insights"""
        try:
            # Get high-rated interactions for knowledge extraction
            recent_interactions = await self.interaction_learner.get_recent_interactions(limit=100)

            high_rated = [i for i in recent_interactions
                         if i.get("rating") and i["rating"] >= 4.5]

            for interaction in high_rated:
                # Extract knowledge from successful interactions
                knowledge_entry = {
                    "content": f"Q: {interaction['user_input']} A: {interaction['response']}",
                    "type": "successful_interaction",
                    "rating": interaction["rating"],
                    "domain": interaction["domain"],
                    "source": "interaction_learning",
                    "metadata": {
                        "interaction_id": interaction["id"],
                        "timestamp": interaction["timestamp"]
                    }
                }

                await self.knowledge_manager.add_knowledge_entry(
                    interaction["domain"], knowledge_entry
                )

                self.learning_stats["knowledge_entries_added"] += 1

            self.logger.debug(f"Added {len(high_rated)} knowledge entries from successful interactions")

        except Exception as e:
            self.logger.error(f"Error updating knowledge base: {e}")

    async def _optimize_rag_performance(self):
        """Optimize RAG engine performance"""
        try:
            if not self.rag_engine:
                return

            # Get RAG statistics
            stats = await self.rag_engine.get_system_statistics()

            # Analyze performance per domain
            domain_stats = stats.get("domain_statistics", {})

            for domain, domain_stat in domain_stats.items():
                total_entries = domain_stat.get("total_entries", 0)

                # If domain has too few entries, try to populate from knowledge base
                if total_entries < 10:
                    await self._populate_rag_from_knowledge_base(domain)

            self.learning_stats["optimizations_applied"] += 1
            self.logger.debug("Completed RAG optimization")

        except Exception as e:
            self.logger.error(f"Error optimizing RAG: {e}")

    async def _populate_rag_from_knowledge_base(self, domain: str):
        """Populate RAG with entries from knowledge base"""
        try:
            knowledge_entries = await self.knowledge_manager.get_domain_knowledge(domain)

            for i, entry in enumerate(knowledge_entries):
                if isinstance(entry, dict):
                    content = entry.get("content", str(entry))
                    entry_id = entry.get("id", f"kb_{i}")
                    metadata = {k: v for k, v in entry.items() if k not in ["content", "id"]}

                    await self.rag_engine.add_knowledge_entry(domain, entry_id, content, metadata)

            self.logger.info(f"Populated RAG for {domain} with {len(knowledge_entries)} entries")

        except Exception as e:
            self.logger.error(f"Error populating RAG for {domain}: {e}")

    async def _cross_domain_learning(self):
        """Share successful patterns across domains"""
        try:
            # Get successful patterns from each domain
            successful_patterns = {}

            for domain in self.domain_experts.keys():
                insights = await self.interaction_learner.get_domain_insights(domain)
                avg_rating = insights.get("avg_rating")

                if avg_rating and avg_rating > 4.0:
                    successful_patterns[domain] = insights

            # Share successful patterns across domains
            for source_domain, patterns in successful_patterns.items():
                for target_domain in self.domain_experts.keys():
                    if source_domain != target_domain:
                        await self._share_patterns_between_domains(
                            source_domain, target_domain, patterns
                        )

            self.logger.debug("Completed cross-domain learning")

        except Exception as e:
            self.logger.error(f"Error in cross-domain learning: {e}")

    async def _share_patterns_between_domains(self, source_domain: str, target_domain: str, patterns: Dict[str, Any]):
        """Share patterns between two domains"""
        try:
            # Extract generalizable insights
            common_patterns = patterns.get("common_patterns", [])
            recommendations = patterns.get("recommendations", [])

            # Create cross-domain knowledge entry
            if common_patterns or recommendations:
                knowledge_entry = {
                    "content": f"Successful patterns from {source_domain}: {', '.join([p[0] for p in common_patterns[:3]])}",
                    "type": "cross_domain_pattern",
                    "source_domain": source_domain,
                    "target_domain": target_domain,
                    "patterns": common_patterns,
                    "recommendations": recommendations,
                    "confidence": patterns.get("avg_rating", 0) / 5.0
                }

                await self.knowledge_manager.add_knowledge_entry(target_domain, knowledge_entry)

                self.learning_stats["patterns_learned"] += 1

        except Exception as e:
            self.logger.error(f"Error sharing patterns from {source_domain} to {target_domain}: {e}")

    async def _optimize_system_performance(self):
        """Optimize overall system performance"""
        try:
            # Clean up old data
            await self._cleanup_old_data()

            # Optimize domain expert performance
            for domain, expert in self.domain_experts.items():
                await self._optimize_domain_expert(expert)

            self.learning_stats["optimizations_applied"] += 1
            self.logger.debug("Completed system optimization")

        except Exception as e:
            self.logger.error(f"Error in system optimization: {e}")

    async def _cleanup_old_data(self):
        """Clean up old data to maintain performance"""
        try:
            # This would typically involve:
            # - Removing low-quality knowledge entries
            # - Archiving old interactions
            # - Optimizing vector database indices

            self.logger.debug("Completed data cleanup")

        except Exception as e:
            self.logger.error(f"Error in data cleanup: {e}")

    async def _optimize_domain_expert(self, expert: DomainExpert):
        """Optimize a specific domain expert"""
        try:
            # Update domain expert's knowledge cache
            await expert._load_domain_capabilities()
            await expert._load_domain_context()

        except Exception as e:
            self.logger.error(f"Error optimizing domain expert {expert.domain}: {e}")

    async def _handle_low_performance_domain(self, domain: str, insights: Dict[str, Any]):
        """Handle domains with low performance ratings"""
        self.logger.warning(f"Low performance detected in {domain} domain: {insights.get('avg_rating')}")

        # Add improvement recommendations to knowledge base
        improvement_entry = {
            "content": f"Performance improvement needed for {domain} domain",
            "type": "improvement_recommendation",
            "current_rating": insights.get("avg_rating"),
            "recommendations": insights.get("recommendations", []),
            "priority": "high"
        }

        await self.knowledge_manager.add_knowledge_entry(domain, improvement_entry)

    async def _handle_low_success_rate(self, domain: str, insights: Dict[str, Any]):
        """Handle domains with low success rates"""
        self.logger.warning(f"Low success rate detected in {domain} domain: {insights.get('success_rate')}")

        # Analyze common failure patterns
        # This would involve more sophisticated analysis of failed interactions

    async def _extract_successful_patterns(self, domain: str, insights: Dict[str, Any]):
        """Extract and preserve successful patterns"""
        patterns = insights.get("common_patterns", [])
        if patterns:
            pattern_entry = {
                "content": f"Successful interaction patterns for {domain}",
                "type": "successful_pattern",
                "patterns": patterns,
                "avg_rating": insights.get("avg_rating"),
                "success_rate": insights.get("success_rate")
            }

            await self.knowledge_manager.add_knowledge_entry(domain, pattern_entry)

    async def trigger_learning_cycle(self):
        """Manually trigger a learning cycle"""
        if not self.is_running:
            self.logger.warning("Cannot trigger learning cycle - pipeline not running")
            return False

        try:
            await self._execute_learning_cycle()
            return True
        except Exception as e:
            self.logger.error(f"Error in manual learning cycle: {e}")
            return False

    async def add_domain_expert(self, domain: str, config: Dict[str, Any] = None):
        """Add a new domain expert to the pipeline"""
        if domain in self.domain_experts:
            self.logger.warning(f"Domain expert for {domain} already exists")
            return

        try:
            expert = DomainExpert(
                domain=domain,
                knowledge_manager=self.knowledge_manager,
                rag_engine=self.rag_engine,
                config=config or {}
            )
            await expert.initialize()
            self.domain_experts[domain] = expert

            self.logger.info(f"Added domain expert for: {domain}")

        except Exception as e:
            self.logger.error(f"Failed to add domain expert for {domain}: {e}")

    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get learning pipeline status"""
        status = {
            "is_running": self.is_running,
            "last_learning_cycle": self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
            "learning_cycle_hours": self.learning_cycle_hours,
            "domain_experts": list(self.domain_experts.keys()),
            "statistics": self.learning_stats.copy(),
            "configuration": {
                "knowledge_update_threshold": self.knowledge_update_threshold,
                "cross_domain_sharing_enabled": self.cross_domain_sharing_enabled,
                "auto_optimization_enabled": self.auto_optimization_enabled
            }
        }

        # Add component status
        if self.knowledge_manager:
            status["knowledge_summary"] = await self.knowledge_manager.get_knowledge_summary()

        if self.rag_engine:
            status["rag_statistics"] = await self.rag_engine.get_system_statistics()

        if self.interaction_learner:
            status["learning_summary"] = await self.interaction_learner.get_learning_summary()

        return status

    async def cleanup(self):
        """Cleanup pipeline resources"""
        await self.stop()

        # Cleanup domain experts
        for expert in self.domain_experts.values():
            # Domain experts don't have explicit cleanup methods
            pass

        self.logger.info("Learning Pipeline cleaned up")