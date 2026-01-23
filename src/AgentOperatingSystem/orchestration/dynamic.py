"""
Dynamic Workflow Composer

Provides runtime workflow generation and adaptive orchestration capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .workflow import Workflow
from .workflow_step import WorkflowStep


class DynamicWorkflowComposer:
    """
    Generates workflows dynamically based on goals, constraints, and context.

    Enables intent-based orchestration where workflows are automatically
    composed from high-level objectives.
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.DynamicWorkflowComposer")
        self.workflow_templates = {}
        self.agent_capabilities = {}

    async def generate_workflow(
        self,
        goal: str,
        constraints: Dict[str, Any],
        available_agents: List[str],
        context: Dict[str, Any]
    ) -> Workflow:
        """
        Generate a workflow based on goal and constraints.

        Args:
            goal: High-level objective to achieve
            constraints: Budget, timeline, resource limits
            available_agents: List of agent IDs that can participate
            context: Additional context for workflow generation

        Returns:
            Generated workflow instance
        """
        self.logger.info("Generating workflow for goal: %s", goal)

        # Analyze goal and break down into steps
        steps = await self._decompose_goal(goal, constraints, context)

        # Match steps to available agents
        assigned_steps = await self._assign_agents(steps, available_agents)

        # Optimize workflow structure
        optimized_workflow = await self._optimize_workflow(
            assigned_steps, constraints
        )

        workflow = Workflow.from_steps(
            workflow_id=f"dynamic_{datetime.utcnow().timestamp()}",
            steps=optimized_workflow
        )
        workflow.metadata = {
            "goal": goal,
            "constraints": constraints,
            "generated_at": datetime.utcnow().isoformat()
        }

        self.logger.info("Generated workflow with %s steps", len(optimized_workflow))
        return workflow

    async def from_intent(self, intent: Dict[str, Any]) -> Workflow:
        """
        Create workflow from high-level intent specification.

        Args:
            intent: Intent with objective, stakeholders, timeline, metrics

        Returns:
            Generated workflow
        """
        self.logger.info("Creating workflow from intent: %s", intent.get('objective'))

        objective = intent.get("objective", "")
        stakeholders = intent.get("stakeholders", [])
        timeline = intent.get("timeline", "")
        success_metrics = intent.get("success_metrics", [])

        # Generate workflow steps based on intent
        steps = []

        # Planning phase
        steps.append(WorkflowStep(
            step_id="plan",
            agent_id=stakeholders[0] if stakeholders else "planner",
            task=f"create_plan: {objective} (timeline: {timeline})",
            depends_on=[]
        ))

        # Execution phases for each stakeholder
        for i, stakeholder in enumerate(stakeholders[1:], 1):
            steps.append(WorkflowStep(
                step_id=f"execute_{i}",
                agent_id=stakeholder,
                task=f"execute_phase: {objective} (metrics: {', '.join(success_metrics)})",
                depends_on=["plan"] + [f"execute_{j}" for j in range(1, i)]
            ))

        # Review and validation
        steps.append(WorkflowStep(
            step_id="review",
            agent_id=stakeholders[0] if stakeholders else "reviewer",
            task=f"review_results: {', '.join(success_metrics)}",
            depends_on=[f"execute_{i}" for i in range(1, len(stakeholders))]
        ))

        workflow = Workflow.from_steps(
            workflow_id=f"intent_{datetime.utcnow().timestamp()}",
            steps=steps
        )
        workflow.metadata = {"intent": intent}
        return workflow

    async def _decompose_goal(
        self,
        goal: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Break down high-level goal into executable steps"""
        # Simple decomposition - can be enhanced with ML models
        steps = []

        # Default workflow pattern
        steps.append({
            "type": "research",
            "description": f"Research for {goal}",
            "estimated_duration": timedelta(hours=2)
        })

        steps.append({
            "type": "analysis",
            "description": f"Analyze data for {goal}",
            "estimated_duration": timedelta(hours=4),
            "depends_on": ["research"]
        })

        steps.append({
            "type": "execution",
            "description": f"Execute plan for {goal}",
            "estimated_duration": timedelta(hours=8),
            "depends_on": ["analysis"]
        })

        steps.append({
            "type": "validation",
            "description": f"Validate results for {goal}",
            "estimated_duration": timedelta(hours=2),
            "depends_on": ["execution"]
        })

        return steps

    async def _assign_agents(
        self,
        steps: List[Dict[str, Any]],
        available_agents: List[str]
    ) -> List[WorkflowStep]:
        """Assign agents to workflow steps based on capabilities"""
        assigned_steps = []

        for i, step in enumerate(steps):
            # Simple round-robin assignment - can be enhanced with capability matching
            agent_id = available_agents[i % len(available_agents)] if available_agents else "default_agent"

            workflow_step = WorkflowStep(
                step_id=f"step_{i}",
                agent_id=agent_id,
                task=f"{step['type']}: {step['description']}",
                depends_on=step.get("depends_on", [])
            )
            assigned_steps.append(workflow_step)

        return assigned_steps

    async def _optimize_workflow(
        self,
        steps: List[WorkflowStep],
        constraints: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Optimize workflow structure based on constraints"""
        # Apply optimizations
        constraints.get("budget")
        constraints.get("timeline_days")

        # For now, return as-is
        # Can add parallelization, resource optimization, etc.
        return steps

    def register_template(self, template_id: str, template: Dict[str, Any]):
        """Register a reusable workflow template"""
        self.workflow_templates[template_id] = template
        self.logger.info("Registered workflow template: %s", template_id)

    def register_agent_capabilities(
        self,
        agent_id: str,
        capabilities: List[str]
    ):
        """Register agent capabilities for intelligent assignment"""
        self.agent_capabilities[agent_id] = capabilities
        self.logger.debug("Registered capabilities for %s: %s", agent_id, capabilities)
