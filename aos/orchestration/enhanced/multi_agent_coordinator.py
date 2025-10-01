"""
Multi-Agent Coordinator for AOS

Enhanced multi-agent coordination system integrated from SelfLearningAgent.
Provides advanced agent-to-agent communication and coordination capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from ...agents.base import BaseAgent
from ...messaging.types import Message, MessageType, MessagePriority


class CoordinationMode(Enum):
    """Different coordination modes for multi-agent scenarios"""
    SEQUENTIAL = "sequential"  # Execute agents one after another
    PARALLEL = "parallel"     # Execute agents simultaneously
    HIERARCHICAL = "hierarchical"  # Execute with priority/hierarchy
    COLLABORATIVE = "collaborative"  # Agents collaborate on shared task


class MultiAgentCoordinator:
    """
    Enhanced multi-agent coordinator that manages complex agent interactions,
    task distribution, and collaborative workflows.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, 
                 send_message_func: Optional[Callable] = None,
                 registered_agents: Optional[Dict[str, BaseAgent]] = None):
        self.logger = logger or logging.getLogger("AOS.MultiAgentCoordinator")
        self.send_message_func = send_message_func
        self.registered_agents = registered_agents or {}
        
        # Coordination state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.agent_assignments: Dict[str, List[str]] = {}  # workflow_id -> [agent_ids]
        self.coordination_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, Any]] = {}
        self.workflow_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_concurrent_workflows = 10
        self.default_timeout = 300  # 5 minutes
        self.retry_attempts = 3
    
    async def handle_multiagent_request(self, agent_id: str, domain: str, user_input: str, 
                                      conv_id: str, coordination_mode: CoordinationMode = CoordinationMode.SEQUENTIAL) -> Dict[str, Any]:
        """Handle a multi-agent request with specified coordination mode"""
        workflow_id = f"workflow_{conv_id}_{datetime.utcnow().timestamp()}"
        
        try:
            # Create workflow
            workflow = await self._create_workflow(
                workflow_id, agent_id, domain, user_input, conv_id, coordination_mode
            )
            
            # Execute based on coordination mode
            if coordination_mode == CoordinationMode.SEQUENTIAL:
                result = await self._execute_sequential_workflow(workflow)
            elif coordination_mode == CoordinationMode.PARALLEL:
                result = await self._execute_parallel_workflow(workflow)
            elif coordination_mode == CoordinationMode.HIERARCHICAL:
                result = await self._execute_hierarchical_workflow(workflow)
            elif coordination_mode == CoordinationMode.COLLABORATIVE:
                result = await self._execute_collaborative_workflow(workflow)
            else:
                raise ValueError(f"Unsupported coordination mode: {coordination_mode}")
            
            # Record metrics
            await self._record_workflow_completion(workflow_id, result)
            
            return {
                "conversationId": conv_id,
                "domain": domain,
                "workflow_id": workflow_id,
                "coordination_mode": coordination_mode.value,
                "reply": result.get("response", f"Multi-agent workflow completed"),
                "agents_involved": workflow.get("agents", []),
                "execution_time": result.get("execution_time", 0),
                "success": result.get("success", True),
                "source": "multiagent_coordinator"
            }
            
        except Exception as e:
            self.logger.error(f"Multi-agent request failed for workflow {workflow_id}: {e}")
            await self._record_workflow_failure(workflow_id, str(e))
            
            return {
                "conversationId": conv_id,
                "domain": domain,
                "workflow_id": workflow_id,
                "error": str(e),
                "success": False,
                "source": "multiagent_coordinator"
            }
    
    async def _create_workflow(self, workflow_id: str, primary_agent_id: str, domain: str, 
                             user_input: str, conv_id: str, coordination_mode: CoordinationMode) -> Dict[str, Any]:
        """Create a new multi-agent workflow"""
        
        # Determine participating agents based on domain and requirements
        participating_agents = await self._select_agents_for_workflow(domain, user_input, primary_agent_id)
        
        workflow = {
            "workflow_id": workflow_id,
            "primary_agent": primary_agent_id,
            "domain": domain,
            "user_input": user_input,
            "conversation_id": conv_id,
            "coordination_mode": coordination_mode,
            "agents": participating_agents,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created",
            "steps": [],
            "results": {}
        }
        
        self.active_workflows[workflow_id] = workflow
        self.agent_assignments[workflow_id] = participating_agents
        
        self.logger.info(f"Created workflow {workflow_id} with agents: {participating_agents}")
        return workflow
    
    async def _select_agents_for_workflow(self, domain: str, user_input: str, primary_agent_id: str) -> List[str]:
        """Select appropriate agents for the workflow based on domain and input analysis"""
        agents = [primary_agent_id]  # Always include the primary agent
        
        # Simple domain-based agent selection (can be enhanced with ML/NLP)
        domain_agents = {
            "sales": ["sales_agent", "crm_agent"],
            "leadership": ["leadership_agent", "strategy_agent"],
            "erp": ["erp_agent", "finance_agent"],
            "crm": ["crm_agent", "sales_agent"],
            "finance": ["finance_agent", "accounting_agent"],
            "hr": ["hr_agent", "leadership_agent"]
        }
        
        # Add domain-specific agents
        if domain.lower() in domain_agents:
            for agent_id in domain_agents[domain.lower()]:
                if agent_id != primary_agent_id and agent_id in self.registered_agents:
                    agents.append(agent_id)
        
        # Keyword-based agent selection
        keywords_to_agents = {
            "report": ["reporting_agent"],
            "analysis": ["analytics_agent"],
            "strategy": ["strategy_agent"],
            "compliance": ["compliance_agent"],
            "security": ["security_agent"]
        }
        
        user_input_lower = user_input.lower()
        for keyword, keyword_agents in keywords_to_agents.items():
            if keyword in user_input_lower:
                for agent_id in keyword_agents:
                    if agent_id not in agents and agent_id in self.registered_agents:
                        agents.append(agent_id)
        
        return agents[:5]  # Limit to 5 agents max for performance
    
    async def _execute_sequential_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow where agents work sequentially"""
        start_time = datetime.utcnow()
        results = []
        accumulated_context = {"user_input": workflow["user_input"]}
        
        for agent_id in workflow["agents"]:
            try:
                # Prepare message with accumulated context
                message = {
                    "type": "workflow_step",
                    "domain": workflow["domain"],
                    "user_input": workflow["user_input"],
                    "conversation_id": workflow["conversation_id"],
                    "workflow_id": workflow["workflow_id"],
                    "context": accumulated_context,
                    "step_number": len(results) + 1
                }
                
                # Send message to agent
                result = await self._send_workflow_message(agent_id, message)
                results.append({
                    "agent_id": agent_id,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Update accumulated context with this agent's result
                if result and "response" in result:
                    accumulated_context[f"{agent_id}_output"] = result["response"]
                
                workflow["steps"].append({
                    "agent_id": agent_id,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Error in sequential workflow step for {agent_id}: {e}")
                results.append({
                    "agent_id": agent_id,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                workflow["steps"].append({
                    "agent_id": agent_id,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Compile final response
        final_response = self._compile_sequential_response(results, workflow)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "response": final_response,
            "results": results,
            "execution_time": execution_time,
            "success": len([r for r in results if "error" not in r]) > 0
        }
    
    async def _execute_parallel_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow where agents work in parallel"""
        start_time = datetime.utcnow()
        
        # Create tasks for all agents
        tasks = []
        for agent_id in workflow["agents"]:
            message = {
                "type": "parallel_workflow",
                "domain": workflow["domain"],
                "user_input": workflow["user_input"],
                "conversation_id": workflow["conversation_id"],
                "workflow_id": workflow["workflow_id"]
            }
            task = asyncio.create_task(self._send_workflow_message(agent_id, message))
            tasks.append((agent_id, task))
        
        # Wait for all tasks with timeout
        results = []
        try:
            completed_tasks = await asyncio.wait_for(
                asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                timeout=self.default_timeout
            )
            
            for i, (agent_id, _) in enumerate(tasks):
                task_result = completed_tasks[i]
                if isinstance(task_result, Exception):
                    results.append({
                        "agent_id": agent_id,
                        "error": str(task_result),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    results.append({
                        "agent_id": agent_id,
                        "result": task_result,
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        except asyncio.TimeoutError:
            self.logger.error(f"Parallel workflow {workflow['workflow_id']} timed out")
            # Cancel remaining tasks
            for _, task in tasks:
                if not task.done():
                    task.cancel()
            
            results.append({
                "error": "Workflow timed out",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Compile final response
        final_response = self._compile_parallel_response(results, workflow)
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "response": final_response,
            "results": results,
            "execution_time": execution_time,
            "success": len([r for r in results if "error" not in r]) > 0
        }
    
    async def _execute_hierarchical_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with hierarchical agent priority"""
        # For now, implement as sequential with priority ordering
        workflow["agents"] = await self._order_agents_by_priority(workflow["agents"], workflow["domain"])
        return await self._execute_sequential_workflow(workflow)
    
    async def _execute_collaborative_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow where agents collaborate on shared task"""
        # For now, implement as parallel with shared context
        return await self._execute_parallel_workflow(workflow)
    
    async def _send_workflow_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to an agent as part of a workflow"""
        if self.send_message_func:
            try:
                return await self.send_message_func("coordinator", agent_id, message)
            except Exception as e:
                self.logger.error(f"Failed to send message to {agent_id}: {e}")
                return {"error": f"Failed to communicate with {agent_id}: {str(e)}"}
        else:
            # Fallback: try direct agent invocation if available
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                if hasattr(agent, 'process_message'):
                    return await agent.process_message(message)
            
            return {"error": f"No communication method available for {agent_id}"}
    
    def _compile_sequential_response(self, results: List[Dict[str, Any]], workflow: Dict[str, Any]) -> str:
        """Compile final response from sequential workflow results"""
        successful_results = [r for r in results if "error" not in r and "result" in r]
        
        if not successful_results:
            return f"Workflow failed - no successful agent responses for domain: {workflow['domain']}"
        
        # Use the last successful result as primary response
        primary_response = successful_results[-1]["result"].get("response", "No response generated")
        
        # Add summary of all agent contributions
        if len(successful_results) > 1:
            summary = f"\\n\\nCollaborative input from {len(successful_results)} agents:"
            for i, result in enumerate(successful_results[:-1], 1):
                agent_response = result["result"].get("response", "")[:100]
                summary += f"\\n{i}. {result['agent_id']}: {agent_response}..."
            
            return primary_response + summary
        
        return primary_response
    
    def _compile_parallel_response(self, results: List[Dict[str, Any]], workflow: Dict[str, Any]) -> str:
        """Compile final response from parallel workflow results"""
        successful_results = [r for r in results if "error" not in r and "result" in r]
        
        if not successful_results:
            return f"Parallel workflow failed - no successful agent responses for domain: {workflow['domain']}"
        
        # Combine all successful responses
        combined_response = f"Collaborative response from {len(successful_results)} agents:\\n\\n"
        
        for i, result in enumerate(successful_results, 1):
            agent_response = result["result"].get("response", "No response")
            combined_response += f"{i}. **{result['agent_id']}**: {agent_response}\\n\\n"
        
        return combined_response.strip()
    
    async def _order_agents_by_priority(self, agent_ids: List[str], domain: str) -> List[str]:
        """Order agents by priority for hierarchical execution"""
        # Simple priority system (can be enhanced)
        priority_map = {
            "leadership_agent": 1,
            "strategy_agent": 2,
            "senior_agent": 3,
            "specialist_agent": 4,
            "general_agent": 5
        }
        
        def get_priority(agent_id: str) -> int:
            for key, priority in priority_map.items():
                if key in agent_id.lower():
                    return priority
            return 10  # Default low priority
        
        return sorted(agent_ids, key=get_priority)
    
    async def _record_workflow_completion(self, workflow_id: str, result: Dict[str, Any]) -> None:
        """Record successful workflow completion"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.utcnow().isoformat()
            workflow["final_result"] = result
            
            # Move to history
            self.coordination_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            # Update metrics
            self._update_workflow_metrics(workflow_id, workflow, result)
    
    async def _record_workflow_failure(self, workflow_id: str, error: str) -> None:
        """Record workflow failure"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["status"] = "failed"
            workflow["completed_at"] = datetime.utcnow().isoformat()
            workflow["error"] = error
            
            # Move to history
            self.coordination_history.append(workflow)
            del self.active_workflows[workflow_id]
    
    def _update_workflow_metrics(self, workflow_id: str, workflow: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Update workflow performance metrics"""
        execution_time = result.get("execution_time", 0)
        success = result.get("success", False)
        
        # Update per-agent metrics
        for agent_id in workflow.get("agents", []):
            if agent_id not in self.agent_performance:
                self.agent_performance[agent_id] = {
                    "total_workflows": 0,
                    "successful_workflows": 0,
                    "average_execution_time": 0,
                    "last_activity": None
                }
            
            metrics = self.agent_performance[agent_id]
            metrics["total_workflows"] += 1
            if success:
                metrics["successful_workflows"] += 1
            
            # Update average execution time
            if metrics["total_workflows"] == 1:
                metrics["average_execution_time"] = execution_time
            else:
                metrics["average_execution_time"] = (
                    (metrics["average_execution_time"] * (metrics["total_workflows"] - 1) + execution_time)
                    / metrics["total_workflows"]
                )
            
            metrics["last_activity"] = datetime.utcnow().isoformat()
        
        # Store workflow metrics
        self.workflow_metrics[workflow_id] = {
            "execution_time": execution_time,
            "success": success,
            "agents_count": len(workflow.get("agents", [])),
            "coordination_mode": workflow.get("coordination_mode").value if workflow.get("coordination_mode") else "unknown",
            "domain": workflow.get("domain", "unknown")
        }
    
    async def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination system status"""
        return {
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.coordination_history),
            "registered_agents": len(self.registered_agents),
            "average_workflow_time": self._calculate_average_workflow_time(),
            "success_rate": self._calculate_success_rate(),
            "workflow_metrics_summary": self._get_workflow_metrics_summary()
        }
    
    def _calculate_average_workflow_time(self) -> float:
        """Calculate average workflow execution time"""
        if not self.workflow_metrics:
            return 0.0
        
        total_time = sum(metrics["execution_time"] for metrics in self.workflow_metrics.values())
        return total_time / len(self.workflow_metrics)
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall workflow success rate"""
        if not self.workflow_metrics:
            return 0.0
        
        successful = sum(1 for metrics in self.workflow_metrics.values() if metrics["success"])
        return successful / len(self.workflow_metrics)
    
    def _get_workflow_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of workflow metrics"""
        if not self.workflow_metrics:
            return {}
        
        coordination_modes = {}
        domains = {}
        
        for metrics in self.workflow_metrics.values():
            mode = metrics["coordination_mode"]
            domain = metrics["domain"]
            
            coordination_modes[mode] = coordination_modes.get(mode, 0) + 1
            domains[domain] = domains.get(domain, 0) + 1
        
        return {
            "coordination_modes": coordination_modes,
            "domains": domains,
            "total_workflows": len(self.workflow_metrics)
        }