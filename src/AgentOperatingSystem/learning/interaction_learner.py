"""
Interaction Learner for AOS Learning System

Learns from agent interactions, tracks patterns, and improves responses over time.
Provides feedback processing and continuous learning capabilities.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from ..storage.manager import StorageManager


class InteractionLearner:
    """
    Learns from agent interactions to improve future responses and behavior.
    Tracks conversation patterns, success metrics, and user satisfaction.
    """

    def __init__(self, storage_manager: StorageManager, config: Dict[str, Any] = None):
        self.storage = storage_manager
        self.config = config or {}
        self.logger = logging.getLogger("AOS.Learning.InteractionLearner")

        # Learning data
        self.interaction_history = []
        self.conversation_patterns = defaultdict(list)
        self.success_metrics = defaultdict(list)
        self.user_feedback = defaultdict(list)

        # Configuration
        self.learning_window_days = self.config.get("learning_window_days", 30)
        self.min_interactions_for_pattern = self.config.get("min_interactions_for_pattern", 10)
        self.feedback_weight = self.config.get("feedback_weight", 0.7)

        # Storage paths
        self.interactions_path = "learning/interactions.json"
        self.patterns_path = "learning/patterns.json"
        self.metrics_path = "learning/metrics.json"

    async def initialize(self):
        """Initialize the interaction learner"""
        try:
            await self._load_interaction_history()
            await self._load_patterns()
            await self._load_metrics()

            self.logger.info("Interaction Learner initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Interaction Learner: {e}")
            raise

    async def _load_interaction_history(self):
        """Load interaction history from storage"""
        try:
            if await self.storage.exists(self.interactions_path):
                data = await self.storage.read_json(self.interactions_path)
                self.interaction_history = data.get("interactions", [])
                self.logger.info(f"Loaded {len(self.interaction_history)} interactions")
            else:
                self.interaction_history = []
                await self._save_interaction_history()

        except Exception as e:
            self.logger.error(f"Failed to load interaction history: {e}")

    async def _load_patterns(self):
        """Load conversation patterns from storage"""
        try:
            if await self.storage.exists(self.patterns_path):
                data = await self.storage.read_json(self.patterns_path)
                # Convert defaultdict back from regular dict
                for key, value in data.items():
                    self.conversation_patterns[key] = value
                self.logger.info(f"Loaded patterns for {len(self.conversation_patterns)} categories")
            else:
                await self._save_patterns()

        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")

    async def _load_metrics(self):
        """Load success metrics from storage"""
        try:
            if await self.storage.exists(self.metrics_path):
                data = await self.storage.read_json(self.metrics_path)
                # Convert defaultdict back from regular dict
                for key, value in data.items():
                    self.success_metrics[key] = value
                self.logger.info(f"Loaded metrics for {len(self.success_metrics)} categories")
            else:
                await self._save_metrics()

        except Exception as e:
            self.logger.error(f"Failed to load metrics: {e}")

    async def _save_interaction_history(self):
        """Save interaction history to storage"""
        data = {
            "interactions": self.interaction_history,
            "last_updated": datetime.utcnow().isoformat()
        }
        await self.storage.write_json(self.interactions_path, data)

    async def _save_patterns(self):
        """Save conversation patterns to storage"""
        # Convert defaultdict to regular dict for JSON serialization
        data = dict(self.conversation_patterns)
        await self.storage.write_json(self.patterns_path, data)

    async def _save_metrics(self):
        """Save success metrics to storage"""
        # Convert defaultdict to regular dict for JSON serialization
        data = dict(self.success_metrics)
        await self.storage.write_json(self.metrics_path, data)

    async def log_interaction(self, agent_id: str, user_input: str, response: str,
                            domain: str, conversation_id: str, context: Dict[str, Any] = None):
        """Log a new interaction for learning"""
        interaction = {
            "id": f"{agent_id}_{conversation_id}_{datetime.utcnow().timestamp()}",
            "agent_id": agent_id,
            "user_input": user_input,
            "response": response,
            "domain": domain,
            "conversation_id": conversation_id,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "rating": None,
            "feedback": None
        }

        self.interaction_history.append(interaction)

        # Analyze interaction for patterns
        await self._analyze_interaction(interaction)

        # Cleanup old interactions
        await self._cleanup_old_interactions()

        # Save to storage
        await self._save_interaction_history()

        self.logger.debug(f"Logged interaction for agent {agent_id} in domain {domain}")

    async def add_feedback(self, conversation_id: str, rating: float, feedback: str = None):
        """Add user feedback to an interaction"""
        for interaction in self.interaction_history:
            if interaction["conversation_id"] == conversation_id:
                interaction["rating"] = rating
                interaction["feedback"] = feedback
                interaction["feedback_timestamp"] = datetime.utcnow().isoformat()

                # Update success metrics
                await self._update_success_metrics(interaction)

                # Save changes
                await self._save_interaction_history()
                await self._save_metrics()

                self.logger.info(f"Added feedback (rating: {rating}) to conversation {conversation_id}")
                return True

        self.logger.warning(f"Conversation {conversation_id} not found for feedback")
        return False

    async def _analyze_interaction(self, interaction: Dict[str, Any]):
        """Analyze an interaction for patterns"""
        domain = interaction["domain"]
        user_input = interaction["user_input"]

        # Extract patterns
        pattern_key = f"{domain}_user_patterns"

        # Simple pattern extraction (could be enhanced with NLP)
        input_length = len(user_input.split())
        input_type = self._classify_input_type(user_input)

        pattern = {
            "input_length": input_length,
            "input_type": input_type,
            "timestamp": interaction["timestamp"],
            "context_size": len(interaction.get("context", {}))
        }

        self.conversation_patterns[pattern_key].append(pattern)

        # Keep only recent patterns
        cutoff_date = datetime.utcnow() - timedelta(days=self.learning_window_days)
        self.conversation_patterns[pattern_key] = [
            p for p in self.conversation_patterns[pattern_key]
            if datetime.fromisoformat(p["timestamp"]) > cutoff_date
        ]

        await self._save_patterns()

    def _classify_input_type(self, user_input: str) -> str:
        """Classify the type of user input"""
        input_lower = user_input.lower()

        if any(q in input_lower for q in ["what", "how", "why", "when", "where", "who"]):
            return "question"
        elif any(r in input_lower for r in ["please", "can you", "could you", "help"]):
            return "request"
        elif any(c in input_lower for c in ["hello", "hi", "good morning", "good afternoon"]):
            return "greeting"
        elif any(p in input_lower for p in ["thanks", "thank you", "appreciate"]):
            return "appreciation"
        else:
            return "statement"

    async def _update_success_metrics(self, interaction: Dict[str, Any]):
        """Update success metrics based on feedback"""
        domain = interaction["domain"]
        rating = interaction.get("rating")

        if rating is not None:
            metric_key = f"{domain}_ratings"
            self.success_metrics[metric_key].append({
                "rating": rating,
                "timestamp": interaction["feedback_timestamp"],
                "input_type": self._classify_input_type(interaction["user_input"])
            })

            # Keep only recent metrics
            cutoff_date = datetime.utcnow() - timedelta(days=self.learning_window_days)
            self.success_metrics[metric_key] = [
                m for m in self.success_metrics[metric_key]
                if datetime.fromisoformat(m["timestamp"]) > cutoff_date
            ]

    async def _cleanup_old_interactions(self):
        """Remove interactions older than the learning window"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.learning_window_days)

        original_count = len(self.interaction_history)
        self.interaction_history = [
            interaction for interaction in self.interaction_history
            if datetime.fromisoformat(interaction["timestamp"]) > cutoff_date
        ]

        removed_count = original_count - len(self.interaction_history)
        if removed_count > 0:
            self.logger.debug(f"Cleaned up {removed_count} old interactions")

    async def get_domain_insights(self, domain: str) -> Dict[str, Any]:
        """Get learning insights for a specific domain"""
        insights = {
            "domain": domain,
            "total_interactions": len([i for i in self.interaction_history if i["domain"] == domain]),
            "avg_rating": None,
            "common_patterns": [],
            "success_rate": None,
            "recommendations": []
        }

        # Calculate average rating
        metric_key = f"{domain}_ratings"
        if metric_key in self.success_metrics and self.success_metrics[metric_key]:
            ratings = [m["rating"] for m in self.success_metrics[metric_key]]
            insights["avg_rating"] = statistics.mean(ratings)
            insights["success_rate"] = len([r for r in ratings if r >= 4.0]) / len(ratings)

        # Analyze patterns
        pattern_key = f"{domain}_user_patterns"
        if pattern_key in self.conversation_patterns and self.conversation_patterns[pattern_key]:
            patterns = self.conversation_patterns[pattern_key]

            # Most common input types
            input_types = [p["input_type"] for p in patterns]
            type_counts = {}
            for input_type in input_types:
                type_counts[input_type] = type_counts.get(input_type, 0) + 1

            insights["common_patterns"] = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        # Generate recommendations
        insights["recommendations"] = await self._generate_recommendations(domain, insights)

        return insights

    async def _generate_recommendations(self, domain: str, insights: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on insights"""
        recommendations = []

        avg_rating = insights.get("avg_rating")
        if avg_rating is not None:
            if avg_rating < 3.5:
                recommendations.append(f"Focus on improving response quality in {domain} domain (current rating: {avg_rating:.2f})")
            elif avg_rating > 4.5:
                recommendations.append(f"Excellent performance in {domain} domain - consider sharing best practices")

        success_rate = insights.get("success_rate")
        if success_rate is not None and success_rate < 0.7:
            recommendations.append(f"Success rate in {domain} domain is {success_rate:.1%} - analyze failed interactions")

        common_patterns = insights.get("common_patterns", [])
        if common_patterns:
            most_common = common_patterns[0][0]
            recommendations.append(f"Most common interaction type is '{most_common}' - optimize responses for this pattern")

        return recommendations

    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get overall learning summary"""
        summary = {
            "total_interactions": len(self.interaction_history),
            "domains_active": len(set(i["domain"] for i in self.interaction_history)),
            "avg_rating_overall": None,
            "learning_window_days": self.learning_window_days,
            "last_updated": datetime.utcnow().isoformat()
        }

        # Calculate overall average rating
        all_ratings = []
        for metric_list in self.success_metrics.values():
            all_ratings.extend([m["rating"] for m in metric_list if "rating" in m])

        if all_ratings:
            summary["avg_rating_overall"] = statistics.mean(all_ratings)

        # Domain-specific insights
        domains = set(i["domain"] for i in self.interaction_history)
        domain_insights = {}
        for domain in domains:
            domain_insights[domain] = await self.get_domain_insights(domain)

        summary["domain_insights"] = domain_insights

        return summary

    async def get_interaction_by_id(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific interaction by ID"""
        for interaction in self.interaction_history:
            if interaction["id"] == interaction_id:
                return interaction
        return None

    async def get_recent_interactions(self, agent_id: str = None, domain: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent interactions with optional filtering"""
        interactions = self.interaction_history

        # Apply filters
        if agent_id:
            interactions = [i for i in interactions if i["agent_id"] == agent_id]
        if domain:
            interactions = [i for i in interactions if i["domain"] == domain]

        # Sort by timestamp (most recent first) and limit
        interactions.sort(key=lambda x: x["timestamp"], reverse=True)
        return interactions[:limit]
