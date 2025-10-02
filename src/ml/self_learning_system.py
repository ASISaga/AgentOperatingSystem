"""
AOS ML - Self-Learning System for Agent Optimization

Implements the self-learning loop mechanism that continuously improves 
agents through feedback collection, performance analysis, and model adaptation.
This is the OS-level machine learning infrastructure for agent optimization.

Key Features:
- Agent performance monitoring and analysis
- Feedback collection and processing
- Continuous learning and adaptation
- Model optimization and deployment
- Knowledge preservation and transfer
"""

import os
import json
import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import uuid

from aos.core.base import AOSComponent
from aos.monitoring.audit_trail import audit_log, AuditEventType, AuditSeverity
from aos.storage.manager import StorageManager

logger = logging.getLogger(__name__)


class LearningPhase(Enum):
    """Phases in the self-learning loop"""
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    FEEDBACK_COLLECTION = "feedback_collection"
    PATTERN_IDENTIFICATION = "pattern_identification"
    MODEL_ADAPTATION = "model_adaptation"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"


class LearningFocus(Enum):
    """Areas of focus for learning improvements"""
    AGENT_BEHAVIOR = "agent_behavior"
    COMMUNICATION = "communication"
    DECISION_MAKING = "decision_making"
    TASK_EXECUTION = "task_execution"
    RESOURCE_UTILIZATION = "resource_utilization"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class FeedbackType(Enum):
    """Types of feedback for learning"""
    PERFORMANCE_METRIC = "performance_metric"
    USER_RATING = "user_rating"
    SYSTEM_OBSERVATION = "system_observation"
    ERROR_ANALYSIS = "error_analysis"
    EFFICIENCY_MEASURE = "efficiency_measure"
    OUTCOME_EVALUATION = "outcome_evaluation"


@dataclass
class LearningEpisode:
    """Represents a learning episode with agent performance data"""
    episode_id: str
    agent_id: str
    task_id: Optional[str]
    scenario_type: str
    timestamp: datetime
    
    # Input context
    input_data: Dict[str, Any]
    environmental_context: Dict[str, Any]
    task_requirements: Dict[str, Any]
    
    # Agent behavior
    agent_actions: List[Dict[str, Any]]
    decision_process: Dict[str, Any]
    communication_patterns: List[Dict[str, Any]]
    resource_usage: Dict[str, float]
    
    # Outcomes
    task_results: Dict[str, Any]
    performance_metrics: Dict[str, float]
    success_indicators: Dict[str, bool]
    error_information: List[Dict[str, Any]] = field(default_factory=list)
    
    # Feedback
    feedback_scores: Dict[str, float] = field(default_factory=dict)
    feedback_comments: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    # Metadata
    duration_seconds: float = 0.0
    complexity_score: float = 0.0
    confidence_level: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class LearningPattern:
    """Identified pattern from learning analysis"""
    pattern_id: str
    pattern_type: str
    description: str
    agent_ids: List[str]
    scenarios: List[str]
    
    # Pattern characteristics
    frequency: int
    confidence: float
    impact_score: float
    
    # Associated data
    trigger_conditions: Dict[str, Any]
    behavioral_indicators: List[str]
    performance_correlations: Dict[str, float]
    
    # Improvement opportunities
    optimization_potential: float
    recommended_actions: List[str]
    expected_improvements: Dict[str, float]
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    last_observed: datetime = field(default_factory=datetime.now)
    validation_status: str = "pending"


@dataclass
class AdaptationPlan:
    """Plan for adapting agent behavior based on learning"""
    plan_id: str
    target_agent_id: str
    focus_areas: List[LearningFocus]
    
    # Planned changes
    behavioral_adjustments: Dict[str, Any]
    parameter_updates: Dict[str, float]
    model_modifications: List[str]
    
    # Implementation details
    deployment_strategy: str
    rollback_criteria: Dict[str, Any]
    success_metrics: List[str]
    
    # Schedule
    planned_start: datetime
    estimated_duration: timedelta
    validation_period: timedelta
    
    # Risk assessment
    risk_level: str
    potential_impacts: List[str]
    mitigation_strategies: List[str]
    
    # Status
    status: str = "planned"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SelfLearningSystem(AOSComponent):
    """
    Self-learning system for continuous agent improvement
    
    Monitors agent performance, identifies patterns, and implements
    adaptive improvements to optimize agent behavior and system performance.
    """
    
    def __init__(self, aos_instance=None):
        super().__init__("self_learning_system", aos_instance)
        
        # Core components
        self.storage_manager = StorageManager()
        
        # Learning state
        self.learning_episodes: Dict[str, LearningEpisode] = {}
        self.identified_patterns: Dict[str, LearningPattern] = {}
        self.adaptation_plans: Dict[str, AdaptationPlan] = {}
        
        # Configuration
        self.config = {
            "episode_retention_days": 30,
            "pattern_confidence_threshold": 0.7,
            "learning_batch_size": 100,
            "adaptation_approval_required": True,
            "continuous_learning_enabled": True,
            "feedback_aggregation_window": timedelta(hours=1)
        }
        
        # Metrics tracking
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        self.improvement_history: List[Dict[str, Any]] = []
        
        self.logger.info("Self-learning system initialized")
    
    async def initialize(self):
        """Initialize the self-learning system"""
        try:
            # Initialize storage
            await self.storage_manager.initialize()
            
            # Load existing learning data
            await self._load_learning_state()
            
            # Start background learning processes
            if self.config["continuous_learning_enabled"]:
                await self._start_learning_tasks()
            
            await audit_log(
                AuditEventType.COMPONENT_STARTED,
                "Self-learning system initialized",
                component="self_learning",
                severity=AuditSeverity.INFO
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize self-learning system: {e}")
            raise
    
    async def record_episode(self, episode: LearningEpisode) -> bool:
        """Record a learning episode for analysis"""
        try:
            # Validate episode data
            if not self._validate_episode(episode):
                return False
            
            # Store episode
            self.learning_episodes[episode.episode_id] = episode
            
            # Persist to storage
            await self.storage_manager.store(
                f"learning_episodes/{episode.episode_id}",
                episode.__dict__
            )
            
            # Trigger analysis if needed
            await self._analyze_recent_episodes()
            
            await audit_log(
                AuditEventType.DATA_ACCESS,
                f"Learning episode recorded: {episode.episode_id}",
                subject_id=episode.agent_id,
                subject_type="agent",
                component="self_learning",
                severity=AuditSeverity.DEBUG,
                metadata={
                    "episode_id": episode.episode_id,
                    "scenario_type": episode.scenario_type,
                    "performance_score": episode.performance_metrics.get("overall_score", 0.0)
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to record learning episode: {e}")
            return False
    
    async def collect_feedback(self, episode_id: str, feedback_type: FeedbackType,
                             feedback_data: Dict[str, Any]) -> bool:
        """Collect feedback for a learning episode"""
        try:
            episode = self.learning_episodes.get(episode_id)
            if not episode:
                self.logger.warning(f"Episode not found: {episode_id}")
                return False
            
            # Process feedback based on type
            if feedback_type == FeedbackType.PERFORMANCE_METRIC:
                episode.performance_metrics.update(feedback_data.get("metrics", {}))
            elif feedback_type == FeedbackType.USER_RATING:
                episode.feedback_scores.update(feedback_data.get("ratings", {}))
            elif feedback_type == FeedbackType.ERROR_ANALYSIS:
                episode.error_information.extend(feedback_data.get("errors", []))
            
            # Add general feedback
            if "comments" in feedback_data:
                episode.feedback_comments.extend(feedback_data["comments"])
            if "suggestions" in feedback_data:
                episode.improvement_suggestions.extend(feedback_data["suggestions"])
            
            # Update episode
            await self.storage_manager.store(
                f"learning_episodes/{episode_id}",
                episode.__dict__
            )
            
            await audit_log(
                AuditEventType.DATA_MODIFICATION,
                f"Feedback collected for episode: {episode_id}",
                component="self_learning",
                severity=AuditSeverity.DEBUG,
                metadata={
                    "episode_id": episode_id,
                    "feedback_type": feedback_type.value,
                    "agent_id": episode.agent_id
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to collect feedback: {e}")
            return False
    
    async def analyze_patterns(self, agent_id: Optional[str] = None) -> List[LearningPattern]:
        """Analyze learning episodes to identify patterns"""
        try:
            # Filter episodes if agent_id specified
            episodes = self.learning_episodes.values()
            if agent_id:
                episodes = [ep for ep in episodes if ep.agent_id == agent_id]
            
            patterns = []
            
            # Performance pattern analysis
            performance_patterns = await self._analyze_performance_patterns(episodes)
            patterns.extend(performance_patterns)
            
            # Error pattern analysis
            error_patterns = await self._analyze_error_patterns(episodes)
            patterns.extend(error_patterns)
            
            # Efficiency pattern analysis
            efficiency_patterns = await self._analyze_efficiency_patterns(episodes)
            patterns.extend(efficiency_patterns)
            
            # Store identified patterns
            for pattern in patterns:
                if pattern.confidence >= self.config["pattern_confidence_threshold"]:
                    self.identified_patterns[pattern.pattern_id] = pattern
                    await self.storage_manager.store(
                        f"learning_patterns/{pattern.pattern_id}",
                        pattern.__dict__
                    )
            
            self.logger.info(f"Identified {len(patterns)} learning patterns")
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze patterns: {e}")
            return []
    
    async def create_adaptation_plan(self, pattern: LearningPattern) -> Optional[AdaptationPlan]:
        """Create an adaptation plan based on identified pattern"""
        try:
            plan_id = str(uuid.uuid4())
            
            # Determine focus areas based on pattern
            focus_areas = self._determine_focus_areas(pattern)
            
            # Create adaptation plan
            plan = AdaptationPlan(
                plan_id=plan_id,
                target_agent_id=pattern.agent_ids[0] if len(pattern.agent_ids) == 1 else "multiple",
                focus_areas=focus_areas,
                behavioral_adjustments=self._generate_behavioral_adjustments(pattern),
                parameter_updates=self._generate_parameter_updates(pattern),
                model_modifications=pattern.recommended_actions,
                deployment_strategy="gradual_rollout",
                rollback_criteria={"performance_threshold": 0.8},
                success_metrics=["task_success_rate", "efficiency_score", "error_rate"],
                planned_start=datetime.now() + timedelta(days=1),
                estimated_duration=timedelta(days=7),
                validation_period=timedelta(days=3),
                risk_level=self._assess_risk_level(pattern),
                potential_impacts=self._identify_potential_impacts(pattern),
                mitigation_strategies=self._generate_mitigation_strategies(pattern)
            )
            
            self.adaptation_plans[plan_id] = plan
            
            await self.storage_manager.store(
                f"adaptation_plans/{plan_id}",
                plan.__dict__
            )
            
            await audit_log(
                AuditEventType.AGENT_DECISION,
                f"Adaptation plan created: {plan_id}",
                component="self_learning",
                severity=AuditSeverity.INFO,
                metadata={
                    "plan_id": plan_id,
                    "pattern_id": pattern.pattern_id,
                    "focus_areas": [area.value for area in focus_areas],
                    "risk_level": plan.risk_level
                }
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create adaptation plan: {e}")
            return None
    
    async def execute_adaptation_plan(self, plan_id: str) -> bool:
        """Execute an adaptation plan"""
        try:
            plan = self.adaptation_plans.get(plan_id)
            if not plan:
                self.logger.error(f"Adaptation plan not found: {plan_id}")
                return False
            
            # Check if approval is required
            if self.config["adaptation_approval_required"] and plan.status != "approved":
                self.logger.warning(f"Adaptation plan {plan_id} requires approval")
                return False
            
            plan.status = "executing"
            plan.updated_at = datetime.now()
            
            # Execute adaptations based on focus areas
            for focus_area in plan.focus_areas:
                await self._execute_focus_area_adaptation(plan, focus_area)
            
            plan.status = "completed"
            plan.updated_at = datetime.now()
            
            # Record improvement
            self.improvement_history.append({
                "plan_id": plan_id,
                "executed_at": datetime.now(),
                "focus_areas": [area.value for area in plan.focus_areas],
                "target_agent": plan.target_agent_id
            })
            
            await audit_log(
                AuditEventType.WORKFLOW_COMPLETED,
                f"Adaptation plan executed: {plan_id}",
                component="self_learning",
                severity=AuditSeverity.INFO,
                metadata={
                    "plan_id": plan_id,
                    "target_agent": plan.target_agent_id,
                    "focus_areas": [area.value for area in plan.focus_areas]
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute adaptation plan {plan_id}: {e}")
            return False
    
    async def get_learning_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get learning system metrics"""
        try:
            episodes = list(self.learning_episodes.values())
            if agent_id:
                episodes = [ep for ep in episodes if ep.agent_id == agent_id]
            
            if not episodes:
                return {"total_episodes": 0}
            
            # Calculate metrics
            total_episodes = len(episodes)
            avg_performance = np.mean([
                ep.performance_metrics.get("overall_score", 0.0) 
                for ep in episodes
            ])
            
            success_rate = np.mean([
                ep.success_indicators.get("task_completed", False)
                for ep in episodes
            ])
            
            patterns_identified = len(self.identified_patterns)
            active_adaptations = len([
                plan for plan in self.adaptation_plans.values()
                if plan.status in ["executing", "planned"]
            ])
            
            return {
                "total_episodes": total_episodes,
                "average_performance": avg_performance,
                "success_rate": success_rate,
                "patterns_identified": patterns_identified,
                "active_adaptations": active_adaptations,
                "improvements_deployed": len(self.improvement_history),
                "learning_efficiency": self._calculate_learning_efficiency()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get learning metrics: {e}")
            return {}
    
    def _validate_episode(self, episode: LearningEpisode) -> bool:
        """Validate learning episode data"""
        required_fields = ["episode_id", "agent_id", "scenario_type", "timestamp"]
        return all(hasattr(episode, field) and getattr(episode, field) for field in required_fields)
    
    async def _load_learning_state(self):
        """Load existing learning state from storage"""
        try:
            # Load episodes
            episodes_data = await self.storage_manager.load("learning_episodes")
            if episodes_data:
                # Convert back to LearningEpisode objects
                pass
            
            # Load patterns
            patterns_data = await self.storage_manager.load("learning_patterns")
            if patterns_data:
                # Convert back to LearningPattern objects
                pass
                
        except Exception as e:
            self.logger.warning(f"Could not load learning state: {e}")
    
    async def _start_learning_tasks(self):
        """Start background learning tasks"""
        asyncio.create_task(self._continuous_analysis_task())
        asyncio.create_task(self._adaptation_monitoring_task())
    
    async def _continuous_analysis_task(self):
        """Background task for continuous pattern analysis"""
        while True:
            try:
                await self.analyze_patterns()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                self.logger.error(f"Error in continuous analysis: {e}")
                await asyncio.sleep(3600)
    
    async def _adaptation_monitoring_task(self):
        """Background task for monitoring adaptation execution"""
        while True:
            try:
                # Check for plans ready to execute
                for plan in self.adaptation_plans.values():
                    if (plan.status == "approved" and 
                        plan.planned_start <= datetime.now()):
                        await self.execute_adaptation_plan(plan.plan_id)
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in adaptation monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_recent_episodes(self):
        """Analyze recent episodes for immediate insights"""
        # Implementation for real-time episode analysis
        pass
    
    async def _analyze_performance_patterns(self, episodes) -> List[LearningPattern]:
        """Analyze performance patterns in episodes"""
        # Implementation for performance pattern analysis
        return []
    
    async def _analyze_error_patterns(self, episodes) -> List[LearningPattern]:
        """Analyze error patterns in episodes"""
        # Implementation for error pattern analysis
        return []
    
    async def _analyze_efficiency_patterns(self, episodes) -> List[LearningPattern]:
        """Analyze efficiency patterns in episodes"""
        # Implementation for efficiency pattern analysis
        return []
    
    def _determine_focus_areas(self, pattern: LearningPattern) -> List[LearningFocus]:
        """Determine focus areas based on pattern analysis"""
        # Implementation for focus area determination
        return [LearningFocus.PERFORMANCE_OPTIMIZATION]
    
    def _generate_behavioral_adjustments(self, pattern: LearningPattern) -> Dict[str, Any]:
        """Generate behavioral adjustments based on pattern"""
        return {}
    
    def _generate_parameter_updates(self, pattern: LearningPattern) -> Dict[str, float]:
        """Generate parameter updates based on pattern"""
        return {}
    
    def _assess_risk_level(self, pattern: LearningPattern) -> str:
        """Assess risk level of implementing pattern-based changes"""
        return "low" if pattern.confidence > 0.9 else "medium"
    
    def _identify_potential_impacts(self, pattern: LearningPattern) -> List[str]:
        """Identify potential impacts of implementing changes"""
        return ["performance_improvement", "efficiency_gain"]
    
    def _generate_mitigation_strategies(self, pattern: LearningPattern) -> List[str]:
        """Generate mitigation strategies for potential risks"""
        return ["gradual_rollout", "performance_monitoring", "rollback_capability"]
    
    async def _execute_focus_area_adaptation(self, plan: AdaptationPlan, focus_area: LearningFocus):
        """Execute adaptation for a specific focus area"""
        # Implementation for focus area specific adaptations
        pass
    
    def _calculate_learning_efficiency(self) -> float:
        """Calculate overall learning efficiency metric"""
        if not self.improvement_history:
            return 0.0
        
        # Simple efficiency calculation based on improvements over time
        return len(self.improvement_history) / max(len(self.learning_episodes), 1)
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of self-learning system"""
        return {
            "episodes_recorded": len(self.learning_episodes),
            "patterns_identified": len(self.identified_patterns),
            "active_adaptations": len([
                p for p in self.adaptation_plans.values() 
                if p.status in ["executing", "planned"]
            ]),
            "learning_enabled": self.config["continuous_learning_enabled"],
            "status": "healthy"
        }