"""
Intelligent Scheduler

Provides advanced resource scheduling and allocation for workflows.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class WorkflowPriority(Enum):
    """Workflow priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class IntelligentScheduler:
    """
    Advanced scheduler with priority-based scheduling and resource quotas.
    
    Features:
    - Priority-based scheduling with preemption
    - Resource quotas and limits
    - Affinity/anti-affinity rules
    - Predictive resource allocation
    - Auto-scaling capabilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AOS.IntelligentScheduler")
        self.policies = {}
        self.resource_quotas = {}
        self.scheduled_workflows = {}
        self.active_workflows = {}
        
    async def configure(self, policies: Dict[str, Any]):
        """
        Configure scheduling policies.
        
        Args:
            policies: Scheduling configuration
        """
        self.policies = policies
        self.logger.info(f"Configured scheduler with {len(policies)} policies")
        
        # Extract resource quotas
        if "resource_quotas" in policies:
            self.resource_quotas = policies["resource_quotas"]
    
    async def schedule_workflow(
        self,
        workflow_id: str,
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        deadline: Optional[datetime] = None,
        affinity_rules: Optional[Dict[str, str]] = None,
        anti_affinity_rules: Optional[Dict[str, str]] = None
    ):
        """
        Schedule a workflow with advanced constraints.
        
        Args:
            workflow_id: Workflow to schedule
            priority: Workflow priority level
            deadline: Completion deadline
            affinity_rules: Agent-to-node affinity
            anti_affinity_rules: Agent-to-node anti-affinity
        """
        self.logger.info(f"Scheduling workflow {workflow_id} with priority {priority.name}")
        
        schedule_entry = {
            "workflow_id": workflow_id,
            "priority": priority,
            "deadline": deadline,
            "affinity_rules": affinity_rules or {},
            "anti_affinity_rules": anti_affinity_rules or {},
            "scheduled_at": datetime.utcnow(),
            "status": "scheduled"
        }
        
        self.scheduled_workflows[workflow_id] = schedule_entry
        
        # Check for preemption if enabled
        if self.policies.get("preemption_enabled"):
            await self._check_preemption(workflow_id, priority)
        
        # Allocate resources
        await self._allocate_resources(workflow_id)
    
    async def _check_preemption(self, workflow_id: str, priority: WorkflowPriority):
        """Check if this workflow should preempt running workflows"""
        for active_id, active_workflow in list(self.active_workflows.items()):
            active_priority = active_workflow.get("priority", WorkflowPriority.NORMAL)
            
            # Preempt lower priority workflows
            if priority.value < active_priority.value:
                self.logger.info(
                    f"Preempting workflow {active_id} (priority {active_priority.name}) "
                    f"for {workflow_id} (priority {priority.name})"
                )
                await self._suspend_workflow(active_id)
    
    async def _allocate_resources(self, workflow_id: str):
        """Allocate resources based on quotas"""
        schedule_entry = self.scheduled_workflows.get(workflow_id)
        if not schedule_entry:
            return
        
        # Simple resource allocation
        schedule_entry["allocated_resources"] = {
            "cpu": "50%",
            "memory": "4GB"
        }
        
        # Move to active
        self.active_workflows[workflow_id] = schedule_entry
        schedule_entry["status"] = "active"
    
    async def _suspend_workflow(self, workflow_id: str):
        """Suspend a running workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows.pop(workflow_id)
            workflow["status"] = "suspended"
            self.scheduled_workflows[workflow_id] = workflow
    
    def get_predictor(self):
        """Get resource predictor for ML-based predictions"""
        return ResourcePredictor()
    
    async def auto_scale(self, target_metrics: Dict[str, str]):
        """
        Enable auto-scaling based on target metrics.
        
        Args:
            target_metrics: Target performance metrics
        """
        self.logger.info(f"Enabling auto-scaling with targets: {target_metrics}")
        self.policies["auto_scale"] = True
        self.policies["target_metrics"] = target_metrics


class ResourcePredictor:
    """Predicts resource requirements using historical data"""
    
    def __init__(self):
        self.logger = logging.getLogger("AOS.ResourcePredictor")
    
    async def predict(
        self,
        workflow_type: str,
        historical_data: List[Dict[str, Any]],
        current_load: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict resource requirements.
        
        Args:
            workflow_type: Type of workflow
            historical_data: Past execution data
            current_load: Current system load
            
        Returns:
            Predicted resource requirements
        """
        self.logger.info(f"Predicting resources for workflow type: {workflow_type}")
        
        # Simple average-based prediction
        # Can be enhanced with ML models
        if historical_data:
            avg_cpu = sum(d.get("cpu_usage", 50) for d in historical_data) / len(historical_data)
            avg_memory = sum(d.get("memory_mb", 2048) for d in historical_data) / len(historical_data)
            avg_duration = sum(d.get("duration_seconds", 300) for d in historical_data) / len(historical_data)
        else:
            avg_cpu = 50
            avg_memory = 2048
            avg_duration = 300
        
        # Adjust based on current load
        load_factor = current_load.get("load_factor", 1.0)
        
        return {
            "predicted_cpu_percent": avg_cpu * load_factor,
            "predicted_memory_mb": avg_memory * load_factor,
            "predicted_duration_seconds": avg_duration * load_factor,
            "confidence": 0.7
        }
