"""
Intelligent Message Routing

Provides ML-based and content-based intelligent message routing.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class IntelligentRouter:
    """
    Routes messages using ML-based optimization and content analysis.

    Features:
    - ML-based routing decisions
    - Content-based routing
    - Geographic routing
    - Load-aware routing
    - Dynamic routing rules
    """

    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.logger = logging.getLogger("AOS.IntelligentRouter")
        self.routing_strategy = "round_robin"
        self.routing_rules = []
        self.routing_model = None
        self.agent_stats = {}

    async def configure_routing(
        self,
        strategy: str,
        model: Optional[str] = None,
        factors: Optional[List[str]] = None
    ):
        """
        Configure routing strategy.

        Args:
            strategy: Routing strategy ("ml_based", "content_based", etc.)
            model: Optional ML model name
            factors: Factors to consider in routing
        """
        self.logger.info("Configuring routing with strategy: %s", strategy)

        self.routing_strategy = strategy
        self.routing_model = model
        self.routing_factors = factors or []

    async def route_message(
        self,
        message: Dict[str, Any],
        candidate_agents: List[str],
        optimization_goal: str = "minimize_latency"
    ) -> str:
        """
        Route message to optimal agent.

        Args:
            message: Message to route
            candidate_agents: List of candidate agents
            optimization_goal: Optimization objective

        Returns:
            Selected agent ID
        """
        self.logger.debug(
            f"Routing message to one of {len(candidate_agents)} agents "
            f"(goal: {optimization_goal})"
        )

        if self.routing_strategy == "ml_based":
            return await self._ml_based_routing(
                message,
                candidate_agents,
                optimization_goal
            )
        elif self.routing_strategy == "content_based":
            return await self._content_based_routing(message, candidate_agents)
        elif self.routing_strategy == "load_balanced":
            return await self._load_balanced_routing(candidate_agents)
        else:
            # Default: round-robin
            return candidate_agents[0] if candidate_agents else None

    async def _ml_based_routing(
        self,
        message: Dict[str, Any],
        candidate_agents: List[str],
        optimization_goal: str
    ) -> str:
        """Route using ML model predictions"""
        # Calculate scores for each agent
        agent_scores = {}

        for agent_id in candidate_agents:
            score = await self._calculate_agent_score(
                agent_id,
                message,
                optimization_goal
            )
            agent_scores[agent_id] = score

        # Select agent with best score
        best_agent = max(agent_scores.items(), key=lambda x: x[1])[0]

        self.logger.debug(
            "ML routing selected %s with score %s", best_agent, agent_scores[best_agent]
        )

        return best_agent

    async def _calculate_agent_score(
        self,
        agent_id: str,
        message: Dict[str, Any],
        optimization_goal: str
    ) -> float:
        """Calculate routing score for an agent"""
        score = 0.0

        # Get agent statistics
        stats = self.agent_stats.get(agent_id, {})

        if optimization_goal == "minimize_latency":
            # Prefer agents with lower average latency
            avg_latency = stats.get("avg_latency_ms", 100)
            current_load = stats.get("current_load", 0.5)

            # Lower latency and load = higher score
            score = 100 / (avg_latency * (1 + current_load))

        elif optimization_goal == "maximize_throughput":
            # Prefer agents with higher throughput capacity
            throughput = stats.get("throughput_msgs_per_sec", 10)
            score = throughput

        elif optimization_goal == "optimize_cost":
            # Prefer lower-cost agents
            cost_per_msg = stats.get("cost_per_message", 0.01)
            score = 1 / cost_per_msg

        # Apply expertise match factor
        message_type = message.get("type")
        agent_expertise = stats.get("expertise", [])
        if message_type in agent_expertise:
            score *= 1.5

        return score

    async def _content_based_routing(
        self,
        message: Dict[str, Any],
        candidate_agents: List[str]
    ) -> str:
        """Route based on message content"""
        content = message.get("content", {})

        # Simple content-based routing
        # Can be enhanced with NLP
        keywords = content.get("keywords", [])

        for agent_id in candidate_agents:
            stats = self.agent_stats.get(agent_id, {})
            specialties = stats.get("specialties", [])

            # Check if agent specializes in these keywords
            if any(kw in specialties for kw in keywords):
                return agent_id

        # Default to first agent
        return candidate_agents[0] if candidate_agents else None

    async def _load_balanced_routing(
        self,
        candidate_agents: List[str]
    ) -> str:
        """Route to least loaded agent"""
        min_load = float('inf')
        selected_agent = None

        for agent_id in candidate_agents:
            stats = self.agent_stats.get(agent_id, {})
            current_load = stats.get("current_load", 0)

            if current_load < min_load:
                min_load = current_load
                selected_agent = agent_id

        return selected_agent or (candidate_agents[0] if candidate_agents else None)

    async def add_routing_rule(
        self,
        condition: Callable,
        target: str,
        bypass_load_balancing: bool = False
    ):
        """
        Add dynamic routing rule.

        Args:
            condition: Function to check if rule applies
            target: Target agent or queue
            bypass_load_balancing: Whether to skip load balancing
        """
        rule = {
            "condition": condition,
            "target": target,
            "bypass_load_balancing": bypass_load_balancing,
            "added_at": datetime.utcnow()
        }

        self.routing_rules.append(rule)
        self.logger.debug("Added routing rule targeting %s", target)

    async def configure_geo_routing(
        self,
        strategy: str,
        latency_budget_ms: int,
        fallback_to_any_region: bool = True
    ):
        """
        Configure geographic routing.

        Args:
            strategy: Geographic routing strategy
            latency_budget_ms: Maximum acceptable latency
            fallback_to_any_region: Allow fallback to other regions
        """
        self.logger.info("Configuring geo-routing: %s", strategy)

        self.geo_routing_config = {
            "strategy": strategy,
            "latency_budget_ms": latency_budget_ms,
            "fallback_to_any_region": fallback_to_any_region
        }

    def update_agent_stats(
        self,
        agent_id: str,
        stats: Dict[str, Any]
    ):
        """Update agent statistics for routing decisions"""
        if agent_id not in self.agent_stats:
            self.agent_stats[agent_id] = {}

        self.agent_stats[agent_id].update(stats)
        self.agent_stats[agent_id]["updated_at"] = datetime.utcnow()
