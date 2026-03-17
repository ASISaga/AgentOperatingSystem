"""
AOS Generic Workflow Orchestrator

Generic workflow orchestration capabilities for AOS.
Provides Agent Framework-based workflow building and execution using the
1.0.0rc1 API with WorkflowBuilder, add_chain(), add_edge(), and
agent-framework-orchestrations builders.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, TYPE_CHECKING
from datetime import datetime

try:
    from agent_framework import Agent, WorkflowBuilder, Runner
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    logging.warning("Agent Framework not available for workflow orchestration")

try:
    from agent_framework_orchestrations import (
        SequentialBuilder,
        ConcurrentBuilder,
    )
    ORCHESTRATIONS_AVAILABLE = True
except ImportError:
    ORCHESTRATIONS_AVAILABLE = False

if TYPE_CHECKING:
    from agent_framework import Agent


class WorkflowOrchestrator:
    """
    Generic workflow orchestrator for multi-agent systems using Agent Framework 1.0.0rc1.
    Uses WorkflowBuilder with add_chain()/add_edge() and agent-framework-orchestrations
    builders (SequentialBuilder, ConcurrentBuilder) for composing workflows.
    """

    def __init__(self, name: str = "GenericWorkflow"):
        self.name = name
        self.logger = logging.getLogger(f"AOS.WorkflowOrchestrator.{name}")
        self.agents: Dict[str, 'Agent'] = {}
        self.executors: Dict[str, Any] = {}
        self.workflow = None
        self.workflow_builder = None
        self.is_initialized = False

        # Statistics
        self.stats = {
            "total_workflows_executed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0
        }

        if not AGENT_FRAMEWORK_AVAILABLE:
            raise ImportError("Agent Framework not available for workflow orchestration")

    async def initialize(self):
        """Initialize the workflow orchestrator"""
        try:
            self.is_initialized = True
            self.logger.info(f"Workflow orchestrator '{self.name}' initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow orchestrator: {e}")
            raise

    def add_agent(self, name: str, agent: 'Agent') -> 'Agent':
        """Add an agent to the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")

        self.agents[name] = agent
        self.executors[name] = agent

        self.logger.info(f"Added agent '{name}' to workflow")
        return agent

    def add_executor(self, name: str, executor: Any) -> Any:
        """Add a generic executor to the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")

        self.executors[name] = executor

        self.logger.info(f"Added executor '{name}' to workflow")
        return executor

    def add_workflow_edge(self, from_executor: Union[str, List[str]], to_executor: Union[str, List[str]]):
        """Add an edge between executors in the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")

        from_nodes = self._resolve_executor_nodes(from_executor)
        to_nodes = self._resolve_executor_nodes(to_executor)

        # Store edge info for workflow building
        if not hasattr(self, '_edges'):
            self._edges = []
        self._edges.append((from_nodes, to_nodes))

        self.logger.info(f"Added workflow edge: {from_executor} -> {to_executor}")

    def _resolve_executor_nodes(self, executor_ref: Union[str, List[str]]) -> Union[Any, List[Any]]:
        """Resolve executor names to executor objects"""
        if isinstance(executor_ref, str):
            if executor_ref in self.executors:
                return self.executors[executor_ref]
            else:
                raise ValueError(f"Executor '{executor_ref}' not found")
        elif isinstance(executor_ref, list):
            return [self.executors[name] for name in executor_ref if name in self.executors]
        else:
            raise ValueError("Executor reference must be string or list of strings")

    def build_workflow(self):
        """Build the workflow from the configured components"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")

        try:
            executors = list(self.executors.values())
            if not executors:
                raise ValueError("No executors configured for workflow")

            # Use SequentialBuilder if available and appropriate
            if ORCHESTRATIONS_AVAILABLE and len(executors) > 1:
                builder = SequentialBuilder(participants=executors)
                self.workflow = builder.build()
            else:
                # Fall back to WorkflowBuilder with add_chain
                wb = WorkflowBuilder(start_executor=executors[0])
                if len(executors) > 1:
                    wb.add_chain(executors)
                self.workflow = wb.build()

            self.logger.info(f"Workflow '{self.name}' built successfully")
        except Exception as e:
            self.logger.error(f"Failed to build workflow: {e}")
            raise

    async def execute_workflow(self, input_data: Any) -> Any:
        """Execute the workflow with the given input"""
        if not self.workflow:
            raise RuntimeError("Workflow not built. Call build_workflow() first.")

        start_time = datetime.utcnow()

        try:
            self.logger.info(f"Starting workflow execution: {self.name}")
            result = await self.workflow.run(input_data)

            # Update statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats["total_workflows_executed"] += 1
            self.stats["successful_executions"] += 1

            # Update average execution time
            total_time = (self.stats["average_execution_time"] *
                         (self.stats["successful_executions"] - 1) + execution_time)
            self.stats["average_execution_time"] = total_time / self.stats["successful_executions"]

            self.logger.info(f"Workflow execution completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats["total_workflows_executed"] += 1
            self.stats["failed_executions"] += 1

            self.logger.error(f"Workflow execution failed after {execution_time:.2f}s: {e}")
            raise

    def create_sequential_workflow(self, agents: List['Agent'], agent_names: List[str] = None) -> 'WorkflowOrchestrator':
        """Create a simple sequential workflow from a list of agents"""
        if not agent_names:
            agent_names = [f"agent_{i}" for i in range(len(agents))]

        if len(agents) != len(agent_names):
            raise ValueError("Number of agents must match number of agent names")

        for name, agent in zip(agent_names, agents):
            self.add_agent(name, agent)

        return self

    def create_parallel_workflow(self, agents: List['Agent'], agent_names: List[str] = None,
                                aggregator_agent: 'Agent' = None) -> 'WorkflowOrchestrator':
        """Create a parallel workflow where all agents process simultaneously"""
        if not agent_names:
            agent_names = [f"agent_{i}" for i in range(len(agents))]

        if len(agents) != len(agent_names):
            raise ValueError("Number of agents must match number of agent names")

        for name, agent in zip(agent_names, agents):
            self.add_agent(name, agent)

        if aggregator_agent:
            self.add_agent("aggregator", aggregator_agent)

        return self

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow orchestrator statistics"""
        return {
            **self.stats,
            "name": self.name,
            "total_agents": len(self.agents),
            "total_executors": len(self.executors),
            "workflow_built": self.workflow is not None,
            "is_initialized": self.is_initialized
        }

    def list_agents(self) -> List[str]:
        """List all agents in the workflow"""
        return list(self.agents.keys())

    def list_executors(self) -> List[str]:
        """List all executors in the workflow"""
        return list(self.executors.keys())

    def get_agent(self, name: str) -> Optional['Agent']:
        """Get an agent by name"""
        return self.agents.get(name)

    async def shutdown(self):
        """Shutdown the workflow orchestrator"""
        try:
            self.agents.clear()
            self.executors.clear()
            self.workflow = None
            self.workflow_builder = None
            self.is_initialized = False

            self.logger.info(f"Workflow orchestrator '{self.name}' shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


class WorkflowOrchestratorFactory:
    """Factory for creating common workflow patterns"""

    @staticmethod
    def create_boardroom_workflow(agents: Dict[str, 'Agent'], decision_integrator: Any = None) -> WorkflowOrchestrator:
        """
        Create a boardroom-style workflow pattern.
        """
        orchestrator = WorkflowOrchestrator("BoardroomWorkflow")
        orchestrator.initialize()

        for name, agent in agents.items():
            orchestrator.add_agent(name, agent)

        if decision_integrator:
            orchestrator.add_executor("decision_integrator", decision_integrator)

        return orchestrator

    @staticmethod
    def create_simple_sequential(agents: List['Agent'], names: List[str] = None) -> WorkflowOrchestrator:
        """Create a simple sequential workflow"""
        orchestrator = WorkflowOrchestrator("SequentialWorkflow")
        orchestrator.initialize()
        return orchestrator.create_sequential_workflow(agents, names)

    @staticmethod
    def create_simple_parallel(agents: List['Agent'], names: List[str] = None,
                              aggregator: 'Agent' = None) -> WorkflowOrchestrator:
        """Create a simple parallel workflow"""
        orchestrator = WorkflowOrchestrator("ParallelWorkflow")
        orchestrator.initialize()
        return orchestrator.create_parallel_workflow(agents, names, aggregator)