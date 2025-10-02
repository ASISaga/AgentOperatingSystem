"""
LeadershipOrchestrator - Manages and coordinates LeadershipAgent instances in AOS.

This orchestrator provides centralized management for all leadership agents,
including registration, coordination, and delegation of leadership tasks.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

from .LeadershipAgent import LeadershipAgent


class LeadershipOrchestrator:
    """
    Orchestrates multiple LeadershipAgent instances within the Agent Operating System.
    
    Responsibilities:
    - Register and manage leadership agents
    - Coordinate multi-agent leadership decisions
    - Delegate tasks to appropriate leadership agents
    - Monitor leadership performance across the system
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.leadership_agents: Dict[str, LeadershipAgent] = {}
        self.delegation_rules = {}
        self.coordination_history = []
        
        self.logger = logging.getLogger("LeadershipOrchestrator")
        self.logger.info("LeadershipOrchestrator initialized")
    
    def register_leadership_agent(self, role: str, agent: LeadershipAgent) -> bool:
        """
        Register a leadership agent with the orchestrator.
        
        Args:
            role: The leadership role (e.g., "CEO", "CFO", "CTO")
            agent: LeadershipAgent instance
            
        Returns:
            bool: Success status
        """
        try:
            if role in self.leadership_agents:
                self.logger.warning(f"Leadership agent {role} already registered, replacing")
            
            self.leadership_agents[role] = agent
            self.logger.info(f"Registered leadership agent: {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register leadership agent {role}: {e}")
            return False
    
    def unregister_leadership_agent(self, role: str) -> bool:
        """
        Unregister a leadership agent.
        
        Args:
            role: The leadership role to remove
            
        Returns:
            bool: Success status
        """
        try:
            if role in self.leadership_agents:
                del self.leadership_agents[role]
                self.logger.info(f"Unregistered leadership agent: {role}")
                return True
            else:
                self.logger.warning(f"Leadership agent {role} not found for unregistration")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister leadership agent {role}: {e}")
            return False
    
    def get_leadership_agent(self, role: str) -> Optional[LeadershipAgent]:
        """
        Get a specific leadership agent by role.
        
        Args:
            role: The leadership role
            
        Returns:
            LeadershipAgent instance or None
        """
        return self.leadership_agents.get(role)
    
    def list_leadership_agents(self) -> List[str]:
        """
        Get list of registered leadership agent roles.
        
        Returns:
            List of role names
        """
        return list(self.leadership_agents.keys())
    
    async def orchestrate_leadership_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a leadership decision across multiple agents if needed.
        
        Args:
            decision_context: Context for the leadership decision
            
        Returns:
            Dict containing orchestrated decision results
        """
        try:
            # Determine which leadership agents should be involved
            involved_roles = self._determine_involved_roles(decision_context)
            
            if not involved_roles:
                return {
                    "error": "No appropriate leadership agents found for decision context",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Collect decisions from involved agents
            agent_decisions = {}
            for role in involved_roles:
                agent = self.leadership_agents.get(role)
                if agent:
                    decision = await agent.make_decision(decision_context)
                    agent_decisions[role] = decision
            
            # Synthesize the final decision
            final_decision = await self._synthesize_decisions(agent_decisions, decision_context)
            
            # Record coordination
            coordination_record = {
                "coordination_id": f"coord_{len(self.coordination_history)}",
                "context": decision_context,
                "involved_roles": involved_roles,
                "agent_decisions": agent_decisions,
                "final_decision": final_decision,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.coordination_history.append(coordination_record)
            
            self.logger.info(f"Orchestrated leadership decision involving {len(involved_roles)} agents")
            return coordination_record
            
        except Exception as e:
            self.logger.error(f"Leadership decision orchestration failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def delegate_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a task to the appropriate leadership agent(s).
        
        Args:
            task_context: Context for the task to delegate
            
        Returns:
            Dict containing delegation results
        """
        try:
            # Determine best agent for the task
            target_role = self._determine_delegation_target(task_context)
            
            if not target_role or target_role not in self.leadership_agents:
                return {
                    "error": f"No suitable leadership agent found for task: {task_context.get('type', 'unknown')}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Delegate to the appropriate agent
            agent = self.leadership_agents[target_role]
            
            # Convert task context to coordination request
            coordination_request = {
                "type": task_context.get("type", "general_task"),
                "participants": task_context.get("participants", []),
                "objectives": task_context.get("objectives", []),
                "timeline": task_context.get("timeline", "standard"),
                "resources": task_context.get("resources", [])
            }
            
            result = await agent.coordinate_team(coordination_request)
            
            self.logger.info(f"Delegated task to {target_role}: {task_context.get('type', 'unknown')}")
            return {
                "delegated_to": target_role,
                "task_context": task_context,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Task delegation failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def monitor_leadership_performance(self) -> Dict[str, Any]:
        """
        Monitor performance across all leadership agents.
        
        Returns:
            Dict containing aggregated performance metrics
        """
        performance_data = {
            "total_agents": len(self.leadership_agents),
            "agent_performance": {},
            "coordination_stats": {
                "total_coordinations": len(self.coordination_history),
                "recent_coordinations": len([c for c in self.coordination_history[-10:]]),
            },
            "system_health": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Collect individual agent performance
        for role, agent in self.leadership_agents.items():
            try:
                agent_perf = await agent.monitor_performance()
                performance_data["agent_performance"][role] = agent_perf
            except Exception as e:
                self.logger.error(f"Failed to get performance for {role}: {e}")
                performance_data["agent_performance"][role] = {"error": str(e)}
        
        # Assess overall system health
        performance_data["system_health"] = self._assess_system_health(performance_data)
        
        return performance_data
    
    def set_delegation_rule(self, task_type: str, target_role: str) -> bool:
        """
        Set a delegation rule for specific task types.
        
        Args:
            task_type: Type of task
            target_role: Role to delegate to
            
        Returns:
            bool: Success status
        """
        try:
            self.delegation_rules[task_type] = target_role
            self.logger.info(f"Set delegation rule: {task_type} -> {target_role}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set delegation rule: {e}")
            return False
    
    # Private helper methods
    def _determine_involved_roles(self, decision_context: Dict[str, Any]) -> List[str]:
        """Determine which leadership roles should be involved in a decision."""
        decision_type = decision_context.get("type", "general")
        impact_level = decision_context.get("impact", "medium")
        
        # Default involvement rules
        involvement_rules = {
            "strategic": ["CEO", "CFO", "COO"],
            "financial": ["CFO", "CEO"],
            "operational": ["COO", "CTO"],
            "marketing": ["CMO", "CEO"],
            "technology": ["CTO", "CIO"],
            "human_resources": ["CHRO", "CEO"],
            "general": ["CEO"]
        }
        
        # High-impact decisions involve more roles
        if impact_level == "high":
            base_roles = involvement_rules.get(decision_type, ["CEO"])
            if "CEO" not in base_roles:
                base_roles.append("CEO")
            return base_roles
        
        return involvement_rules.get(decision_type, ["CEO"])
    
    async def _synthesize_decisions(self, agent_decisions: Dict[str, Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple agent decisions into a final decision."""
        if not agent_decisions:
            return {"error": "No agent decisions to synthesize"}
        
        # Simple synthesis - in practice, this would be more sophisticated
        decisions = [d.get("decision", {}) for d in agent_decisions.values()]
        actions = [d.get("action", "no_action") for d in decisions]
        confidences = [d.get("confidence", 0.5) for d in decisions]
        
        # Most common action
        most_common_action = max(set(actions), key=actions.count) if actions else "no_action"
        
        # Average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        return {
            "action": most_common_action,
            "confidence": avg_confidence,
            "synthesis_method": "majority_vote",
            "contributing_agents": list(agent_decisions.keys()),
            "reasoning": f"Synthesized from {len(agent_decisions)} agent decisions"
        }
    
    def _determine_delegation_target(self, task_context: Dict[str, Any]) -> Optional[str]:
        """Determine the best leadership agent to delegate a task to."""
        task_type = task_context.get("type", "general")
        
        # Check delegation rules first
        if task_type in self.delegation_rules:
            rule_target = self.delegation_rules[task_type]
            if rule_target in self.leadership_agents:
                return rule_target
        
        # Default delegation logic
        delegation_map = {
            "financial": "CFO",
            "operational": "COO", 
            "technical": "CTO",
            "marketing": "CMO",
            "strategic": "CEO",
            "human_resources": "CHRO",
            "general": "CEO"
        }
        
        return delegation_map.get(task_type, "CEO")
    
    def _assess_system_health(self, performance_data: Dict[str, Any]) -> str:
        """Assess overall leadership system health."""
        agent_count = performance_data["total_agents"]
        
        if agent_count == 0:
            return "critical"
        elif agent_count < 3:
            return "degraded"
        else:
            # Check for errors in agent performance
            errors = sum(1 for perf in performance_data["agent_performance"].values() 
                        if "error" in perf)
            
            if errors > agent_count / 2:
                return "degraded"
            else:
                return "healthy"
