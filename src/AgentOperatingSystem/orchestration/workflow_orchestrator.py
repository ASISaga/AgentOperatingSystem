"""
AOS Generic Workflow Orchestrator

Generic workflow orchestration capabilities moved from BusinessInfinity.
Provides Agent Framework-based workflow building and execution for any domain.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable, TYPE_CHECKING
from datetime import datetime

try:
    from agent_framework import WorkflowBuilder, ChatAgent
    AGENT_FRAMEWORK_AVAILABLE = True
except ImportError:
    AGENT_FRAMEWORK_AVAILABLE = False
    logging.warning("Agent Framework not available for workflow orchestration")

if TYPE_CHECKING:
    from agent_framework import ChatAgent


class WorkflowOrchestrator:
    """
    Generic workflow orchestrator for multi-agent systems using Agent Framework.
    Moved from BusinessInfinity to provide domain-agnostic orchestration capabilities.
    """
    
    def __init__(self, name: str = "GenericWorkflow"):
        self.name = name
        self.logger = logging.getLogger(f"AOS.WorkflowOrchestrator.{name}")
        self.agents: Dict[str, 'ChatAgent'] = {}
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
            self.workflow_builder = WorkflowBuilder()
            self.is_initialized = True
            self.logger.info(f"Workflow orchestrator '{self.name}' initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow orchestrator: {e}")
            raise
    
    def add_agent(self, name: str, agent: 'ChatAgent') -> str:
        """Add an agent to the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")
        
        self.agents[name] = agent
        # Register agent with workflow builder (replaces deprecated add_executor)
        node_id = self.workflow_builder.register_agent(agent)
        self.executors[name] = node_id
        
        self.logger.info(f"Added agent '{name}' to workflow")
        return node_id
    
    def add_executor(self, name: str, executor: Any) -> str:
        """Add a generic executor to the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")
        
        # Register executor with workflow builder (replaces deprecated add_executor)
        node_id = self.workflow_builder.register_executor(executor)
        self.executors[name] = node_id
        
        self.logger.info(f"Added executor '{name}' to workflow")
        return node_id
    
    def add_workflow_edge(self, from_executor: Union[str, List[str]], to_executor: Union[str, List[str]]):
        """Add an edge between executors in the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")
        
        # Convert names to node IDs
        from_nodes = self._resolve_executor_nodes(from_executor)
        to_nodes = self._resolve_executor_nodes(to_executor)
        
        self.workflow_builder.add_edge(from_nodes, to_nodes)
        self.logger.info(f"Added workflow edge: {from_executor} -> {to_executor}")
    
    def _resolve_executor_nodes(self, executor_ref: Union[str, List[str]]) -> Union[str, List[str]]:
        """Resolve executor names to node IDs"""
        if isinstance(executor_ref, str):
            if executor_ref in self.executors:
                return self.executors[executor_ref]
            else:
                raise ValueError(f"Executor '{executor_ref}' not found")
        elif isinstance(executor_ref, list):
            return [self.executors[name] for name in executor_ref if name in self.executors]
        else:
            raise ValueError("Executor reference must be string or list of strings")
    
    def set_start_executor(self, executor_name: str):
        """Set the starting executor for the workflow"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")
        
        if executor_name not in self.executors:
            raise ValueError(f"Executor '{executor_name}' not found")
        
        start_node = self.executors[executor_name]
        self.workflow_builder.set_start_executor(start_node)
        self.logger.info(f"Set start executor: {executor_name}")
    
    def build_workflow(self):
        """Build the workflow from the configured components"""
        if not self.is_initialized:
            raise RuntimeError("Workflow orchestrator not initialized")
        
        try:
            self.workflow = self.workflow_builder.build()
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
    
    def create_sequential_workflow(self, agents: List['ChatAgent'], agent_names: List[str] = None) -> 'WorkflowOrchestrator':
        """Create a simple sequential workflow from a list of agents"""
        if not agent_names:
            agent_names = [f"agent_{i}" for i in range(len(agents))]
        
        if len(agents) != len(agent_names):
            raise ValueError("Number of agents must match number of agent names")
        
        # Add all agents
        node_ids = []
        for name, agent in zip(agent_names, agents):
            node_id = self.add_agent(name, agent)
            node_ids.append((name, node_id))
        
        # Create sequential edges
        for i in range(len(node_ids) - 1):
            current_name = node_ids[i][0]
            next_name = node_ids[i + 1][0]
            self.add_workflow_edge(current_name, next_name)
        
        # Set first agent as start
        if node_ids:
            self.set_start_executor(node_ids[0][0])
        
        return self
    
    def create_parallel_workflow(self, agents: List['ChatAgent'], agent_names: List[str] = None, 
                                aggregator_agent: 'ChatAgent' = None) -> 'WorkflowOrchestrator':
        """Create a parallel workflow where all agents process simultaneously"""
        if not agent_names:
            agent_names = [f"agent_{i}" for i in range(len(agents))]
        
        if len(agents) != len(agent_names):
            raise ValueError("Number of agents must match number of agent names")
        
        # Add all agents
        parallel_agents = []
        for name, agent in zip(agent_names, agents):
            self.add_agent(name, agent)
            parallel_agents.append(name)
        
        # If aggregator provided, connect all parallel agents to it
        if aggregator_agent:
            aggregator_name = "aggregator"
            self.add_agent(aggregator_name, aggregator_agent)
            self.add_workflow_edge(parallel_agents, aggregator_name)
            
            # Set first parallel agent as start
            if parallel_agents:
                self.set_start_executor(parallel_agents[0])
        
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
    
    def get_agent(self, name: str) -> Optional['ChatAgent']:
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
    def create_boardroom_workflow(agents: Dict[str, 'ChatAgent'], decision_integrator: Any = None) -> WorkflowOrchestrator:
        """
        Create a boardroom-style workflow pattern.
        Moved from BusinessInfinity as a reusable pattern.
        """
        orchestrator = WorkflowOrchestrator("BoardroomWorkflow")
        orchestrator.initialize()
        
        # Expected agents: founder, investor, ceo, cfo, cto, coo, cmo, chro, cso
        # Add all agents
        node_mappings = {}
        for name, agent in agents.items():
            node_mappings[name] = orchestrator.add_agent(name, agent)
        
        # Add decision integrator if provided
        if decision_integrator:
            node_mappings["decision_integrator"] = orchestrator.add_executor("decision_integrator", decision_integrator)
        
        # Build boardroom workflow pattern
        if "founder" in node_mappings and "investor" in node_mappings:
            orchestrator.add_workflow_edge("founder", "investor")
            orchestrator.set_start_executor("founder")
        
        if "investor" in node_mappings and "ceo" in node_mappings:
            orchestrator.add_workflow_edge("investor", "ceo")
        
        # CEO delegates to C-Suite
        c_suite = [name for name in ["cfo", "cto", "coo", "cmo", "chro", "cso"] if name in node_mappings]
        if "ceo" in node_mappings and c_suite:
            orchestrator.add_workflow_edge("ceo", c_suite)
        
        # C-Suite reports to decision integrator
        if "decision_integrator" in node_mappings and c_suite:
            orchestrator.add_workflow_edge(c_suite + ["investor"], "decision_integrator")
            orchestrator.add_workflow_edge("decision_integrator", "ceo")
        
        return orchestrator
    
    @staticmethod
    def create_simple_sequential(agents: List['ChatAgent'], names: List[str] = None) -> WorkflowOrchestrator:
        """Create a simple sequential workflow"""
        orchestrator = WorkflowOrchestrator("SequentialWorkflow")
        orchestrator.initialize()
        return orchestrator.create_sequential_workflow(agents, names)
    
    @staticmethod
    def create_simple_parallel(agents: List['ChatAgent'], names: List[str] = None, 
                              aggregator: 'ChatAgent' = None) -> WorkflowOrchestrator:
        """Create a simple parallel workflow"""
        orchestrator = WorkflowOrchestrator("ParallelWorkflow")
        orchestrator.initialize()
        return orchestrator.create_parallel_workflow(agents, names, aggregator)