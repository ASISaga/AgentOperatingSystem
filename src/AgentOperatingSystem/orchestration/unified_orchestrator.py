"""
Unified Orchestrator for AOS

Enhanced orchestration system integrated from SelfLearningAgent.
Provides comprehensive coordination between agents, MCP clients, and Azure services.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import json

from ..agents.leadership_agent import LeadershipAgent
from .multi_agent_coordinator import MultiAgentCoordinator, CoordinationMode
from .agent_registry import AgentRegistry


class ExecutionMode(Enum):
    """Different execution modes for the orchestrator"""
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT = "multi_agent"
    MCP_INTEGRATION = "mcp_integration"
    AZURE_WORKFLOW = "azure_workflow"
    HYBRID = "hybrid"


class RequestType(Enum):
    """Different types of requests the orchestrator can handle"""
    USER_QUERY = "user_query"
    AGENT_TO_AGENT = "agent_to_agent"
    SYSTEM_COMMAND = "system_command"
    SCHEDULED_TASK = "scheduled_task"
    MCP_REQUEST = "mcp_request"
    AZURE_FUNCTION = "azure_function"


class UnifiedOrchestrator:
    """
    Unified orchestration system that coordinates all AOS components:
    - Agent-to-agent communication
    - MCP client integrations
    - Azure service workflows
    - Multi-modal request handling
    """
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 send_message_func: Optional[Callable] = None,
                 registered_agents: Optional[Dict[str, LeadershipAgent]] = None,
                 mcp_clients: Optional[Dict[str, Any]] = None,
                 azure_clients: Optional[Dict[str, Any]] = None):
        
        self.logger = logger or logging.getLogger("AOS.UnifiedOrchestrator")
        self.send_message_func = send_message_func
        
        # Core components
        self.agent_registry = AgentRegistry(logger=self.logger)
        self.multi_agent_coordinator = MultiAgentCoordinator(
            logger=self.logger, 
            send_message_func=send_message_func,
            registered_agents=registered_agents
        )
        
        # External integrations
        self.mcp_clients = mcp_clients or {}
        self.azure_clients = azure_clients or {}
        self.registered_agents = registered_agents or {}
        
        # Orchestration state
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Configuration
        self.max_concurrent_executions = 20
        self.default_timeout = 600  # 10 minutes
        self.retry_attempts = 3
        
        # Request routing configuration
        self.domain_routing = {
            "sales": {"agents": ["sales_agent"], "mcp": ["crm"], "execution_mode": ExecutionMode.MULTI_AGENT},
            "erp": {"agents": ["erp_agent"], "mcp": ["erpnext"], "execution_mode": ExecutionMode.MCP_INTEGRATION},
            "leadership": {"agents": ["leadership_agent"], "mcp": [], "execution_mode": ExecutionMode.SINGLE_AGENT},
            "github": {"agents": ["github_agent"], "mcp": ["github"], "execution_mode": ExecutionMode.MCP_INTEGRATION},
            "linkedin": {"agents": ["linkedin_agent"], "mcp": ["linkedin"], "execution_mode": ExecutionMode.MCP_INTEGRATION},
            "reddit": {"agents": ["reddit_agent"], "mcp": ["reddit"], "execution_mode": ExecutionMode.MCP_INTEGRATION}
        }
    
    async def orchestrate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method that routes and handles all types of requests.
        
        Args:
            request: Request containing type, domain, content, and routing information
            
        Returns:
            Orchestrated response with results from all relevant components
        """
        execution_id = f"exec_{datetime.utcnow().timestamp()}"
        start_time = datetime.utcnow()
        
        try:
            # Analyze and classify the request
            request_analysis = await self._analyze_request(request)
            
            # Create execution context
            execution_context = await self._create_execution_context(
                execution_id, request, request_analysis
            )
            
            self.active_executions[execution_id] = execution_context
            
            # Route to appropriate execution handler
            execution_mode = request_analysis["execution_mode"]
            
            if execution_mode == ExecutionMode.SINGLE_AGENT:
                result = await self._execute_single_agent(execution_context)
            elif execution_mode == ExecutionMode.MULTI_AGENT:
                result = await self._execute_multi_agent(execution_context)
            elif execution_mode == ExecutionMode.MCP_INTEGRATION:
                result = await self._execute_mcp_integration(execution_context)
            elif execution_mode == ExecutionMode.AZURE_WORKFLOW:
                result = await self._execute_azure_workflow(execution_context)
            elif execution_mode == ExecutionMode.HYBRID:
                result = await self._execute_hybrid_workflow(execution_context)
            else:
                raise ValueError(f"Unsupported execution mode: {execution_mode}")
            
            # Record successful execution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_execution_success(execution_id, result, execution_time)
            
            # Enhance result with orchestration metadata
            enhanced_result = await self._enhance_result_with_metadata(result, execution_context)
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Orchestration failed for execution {execution_id}: {e}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self._record_execution_failure(execution_id, str(e), execution_time)
            
            return {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "source": "unified_orchestrator"
            }
        
        finally:
            # Clean up active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _analyze_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze incoming request to determine optimal execution strategy"""
        
        domain = request.get("domain", "general").lower()
        request_type = RequestType(request.get("type", "user_query"))
        content = request.get("content", request.get("user_input", ""))
        
        # Get domain configuration
        domain_config = self.domain_routing.get(domain, {
            "agents": ["general_agent"],
            "mcp": [],
            "execution_mode": ExecutionMode.SINGLE_AGENT
        })
        
        # Analyze content for complexity and requirements
        complexity_analysis = await self._analyze_content_complexity(content)
        
        # Determine execution mode based on analysis
        execution_mode = await self._determine_execution_mode(
            domain_config, complexity_analysis, request_type
        )
        
        # Select participating components
        participating_agents = await self._select_participating_agents(
            domain, content, domain_config["agents"]
        )
        
        participating_mcp = await self._select_participating_mcp(
            domain, content, domain_config["mcp"]
        )
        
        return {
            "domain": domain,
            "request_type": request_type,
            "execution_mode": execution_mode,
            "complexity": complexity_analysis,
            "participating_agents": participating_agents,
            "participating_mcp": participating_mcp,
            "estimated_duration": complexity_analysis.get("estimated_duration", 30),
            "priority": request.get("priority", "normal")
        }
    
    async def _analyze_content_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze content to determine complexity and resource requirements"""
        
        # Simple heuristic-based analysis (can be enhanced with ML)
        word_count = len(content.split())
        
        # Detect complex operations
        complex_keywords = [
            "report", "analysis", "comprehensive", "detailed", "integrate",
            "workflow", "process", "multiple", "collaborate", "coordinate"
        ]
        
        complexity_score = 0
        detected_operations = []
        
        content_lower = content.lower()
        for keyword in complex_keywords:
            if keyword in content_lower:
                complexity_score += 1
                detected_operations.append(keyword)
        
        # Estimate duration based on complexity
        base_duration = 30  # seconds
        if complexity_score == 0:
            estimated_duration = base_duration
            complexity_level = "simple"
        elif complexity_score <= 2:
            estimated_duration = base_duration * 2
            complexity_level = "moderate"
        else:
            estimated_duration = base_duration * 4
            complexity_level = "complex"
        
        return {
            "word_count": word_count,
            "complexity_score": complexity_score,
            "complexity_level": complexity_level,
            "detected_operations": detected_operations,
            "estimated_duration": estimated_duration,
            "requires_multi_agent": complexity_score >= 2,
            "requires_mcp": any(op in content_lower for op in ["data", "integrate", "sync", "api"])
        }
    
    async def _determine_execution_mode(self, domain_config: Dict[str, Any], 
                                       complexity: Dict[str, Any], 
                                       request_type: RequestType) -> ExecutionMode:
        """Determine the optimal execution mode based on analysis"""
        
        # Default to domain configuration
        suggested_mode = domain_config.get("execution_mode", ExecutionMode.SINGLE_AGENT)
        
        # Override based on complexity analysis
        if complexity["requires_multi_agent"] and complexity["requires_mcp"]:
            return ExecutionMode.HYBRID
        elif complexity["requires_multi_agent"]:
            return ExecutionMode.MULTI_AGENT
        elif complexity["requires_mcp"]:
            return ExecutionMode.MCP_INTEGRATION
        elif request_type in [RequestType.AZURE_FUNCTION, RequestType.SYSTEM_COMMAND]:
            return ExecutionMode.AZURE_WORKFLOW
        
        return suggested_mode
    
    async def _select_participating_agents(self, domain: str, content: str, 
                                         suggested_agents: List[str]) -> List[str]:
        """Select which agents should participate in the execution"""
        
        participating = []
        
        # Always include domain-specific agents
        for agent_id in suggested_agents:
            if agent_id in self.registered_agents:
                participating.append(agent_id)
        
        # Add content-based agents
        content_lower = content.lower()
        
        # Keyword-based agent selection
        if "report" in content_lower or "analytics" in content_lower:
            if "analytics_agent" in self.registered_agents:
                participating.append("analytics_agent")
        
        if "strategy" in content_lower or "planning" in content_lower:
            if "strategy_agent" in self.registered_agents:
                participating.append("strategy_agent")
        
        if "compliance" in content_lower or "regulation" in content_lower:
            if "compliance_agent" in self.registered_agents:
                participating.append("compliance_agent")
        
        # Remove duplicates and limit
        return list(set(participating))[:5]
    
    async def _select_participating_mcp(self, domain: str, content: str, 
                                       suggested_mcp: List[str]) -> List[str]:
        """Select which MCP clients should participate in the execution"""
        
        participating = []
        
        # Include domain-specific MCP clients
        for mcp_id in suggested_mcp:
            if mcp_id in self.mcp_clients:
                participating.append(mcp_id)
        
        # Content-based MCP selection
        content_lower = content.lower()
        
        if "github" in content_lower or "repository" in content_lower:
            if "github" in self.mcp_clients:
                participating.append("github")
        
        if "linkedin" in content_lower or "professional" in content_lower:
            if "linkedin" in self.mcp_clients:
                participating.append("linkedin")
        
        if "reddit" in content_lower or "social" in content_lower:
            if "reddit" in self.mcp_clients:
                participating.append("reddit")
        
        return list(set(participating))
    
    async def _create_execution_context(self, execution_id: str, request: Dict[str, Any], 
                                       analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive execution context"""
        
        return {
            "execution_id": execution_id,
            "created_at": datetime.utcnow().isoformat(),
            "request": request,
            "analysis": analysis,
            "status": "initialized",
            "steps": [],
            "results": {},
            "metadata": {
                "orchestrator_version": "1.0.0",
                "execution_mode": analysis["execution_mode"].value,
                "estimated_duration": analysis["estimated_duration"]
            }
        }
    
    async def _execute_single_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request using a single agent"""
        
        participating_agents = context["analysis"]["participating_agents"]
        if not participating_agents:
            raise ValueError("No participating agents available for single agent execution")
        
        primary_agent = participating_agents[0]
        
        # Prepare message for agent
        message = {
            "type": "user_request",
            "content": context["request"].get("content", context["request"].get("user_input", "")),
            "domain": context["analysis"]["domain"],
            "conversation_id": context["request"].get("conversation_id", context["execution_id"]),
            "execution_context": {
                "execution_id": context["execution_id"],
                "orchestrated": True
            }
        }
        
        # Send to agent
        result = await self._send_agent_message(primary_agent, message)
        
        context["steps"].append({
            "step": "single_agent_execution",
            "agent": primary_agent,
            "status": "completed" if result and "error" not in result else "failed",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "execution_mode": "single_agent",
            "primary_agent": primary_agent,
            "result": result,
            "success": result is not None and "error" not in result
        }
    
    async def _execute_multi_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request using multiple agents with coordination"""
        
        participating_agents = context["analysis"]["participating_agents"]
        if len(participating_agents) < 2:
            # Fall back to single agent
            return await self._execute_single_agent(context)
        
        # Determine coordination mode based on complexity
        complexity = context["analysis"]["complexity"]["complexity_level"]
        if complexity == "complex":
            coordination_mode = CoordinationMode.COLLABORATIVE
        elif complexity == "moderate":
            coordination_mode = CoordinationMode.PARALLEL
        else:
            coordination_mode = CoordinationMode.SEQUENTIAL
        
        # Use multi-agent coordinator
        request_data = {
            "agent_id": participating_agents[0],  # Primary agent
            "domain": context["analysis"]["domain"],
            "user_input": context["request"].get("content", context["request"].get("user_input", "")),
            "conv_id": context["request"].get("conversation_id", context["execution_id"])
        }
        
        result = await self.multi_agent_coordinator.handle_multiagent_request(
            **request_data,
            coordination_mode=coordination_mode
        )
        
        context["steps"].append({
            "step": "multi_agent_coordination",
            "coordination_mode": coordination_mode.value,
            "agents": participating_agents,
            "status": "completed" if result.get("success") else "failed",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "execution_mode": "multi_agent",
            "coordination_mode": coordination_mode.value,
            "participating_agents": participating_agents,
            "result": result,
            "success": result.get("success", False)
        }
    
    async def _execute_mcp_integration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request with MCP client integration"""
        
        participating_mcp = context["analysis"]["participating_mcp"]
        if not participating_mcp:
            # Fall back to agent execution
            return await self._execute_single_agent(context)
        
        results = {}
        
        # Execute MCP operations
        for mcp_id in participating_mcp:
            try:
                mcp_result = await self._execute_mcp_operation(mcp_id, context)
                results[mcp_id] = mcp_result
                
                context["steps"].append({
                    "step": "mcp_operation",
                    "mcp_client": mcp_id,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"MCP operation failed for {mcp_id}: {e}")
                results[mcp_id] = {"error": str(e)}
                
                context["steps"].append({
                    "step": "mcp_operation",
                    "mcp_client": mcp_id,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Combine MCP results with agent processing if needed
        agent_result = None
        participating_agents = context["analysis"]["participating_agents"]
        if participating_agents:
            # Prepare enhanced message with MCP context
            message = {
                "type": "mcp_enhanced_request",
                "content": context["request"].get("content", context["request"].get("user_input", "")),
                "domain": context["analysis"]["domain"],
                "mcp_context": results,
                "conversation_id": context["request"].get("conversation_id", context["execution_id"])
            }
            
            agent_result = await self._send_agent_message(participating_agents[0], message)
        
        return {
            "execution_mode": "mcp_integration",
            "mcp_results": results,
            "agent_result": agent_result,
            "participating_mcp": participating_mcp,
            "success": any("error" not in result for result in results.values())
        }
    
    async def _execute_azure_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute request as Azure workflow"""
        
        # Placeholder for Azure workflow execution
        # This would integrate with Azure Functions, Logic Apps, etc.
        
        azure_result = {
            "message": "Azure workflow execution not yet implemented",
            "execution_id": context["execution_id"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        context["steps"].append({
            "step": "azure_workflow",
            "status": "placeholder",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "execution_mode": "azure_workflow",
            "result": azure_result,
            "success": False,
            "note": "Azure workflow execution requires additional implementation"
        }
    
    async def _execute_hybrid_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid workflow combining multiple execution modes"""
        
        results = {}
        
        # Execute MCP integration first
        mcp_result = await self._execute_mcp_integration(context)
        results["mcp"] = mcp_result
        
        # Then execute multi-agent coordination with MCP context
        enhanced_context = context.copy()
        enhanced_context["request"]["mcp_context"] = mcp_result
        
        multi_agent_result = await self._execute_multi_agent(enhanced_context)
        results["multi_agent"] = multi_agent_result
        
        return {
            "execution_mode": "hybrid",
            "mcp_result": mcp_result,
            "multi_agent_result": multi_agent_result,
            "combined_results": results,
            "success": mcp_result.get("success", False) or multi_agent_result.get("success", False)
        }
    
    async def _execute_mcp_operation(self, mcp_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation with specific MCP client"""
        
        if mcp_id not in self.mcp_clients:
            raise ValueError(f"MCP client {mcp_id} not available")
        
        mcp_client = self.mcp_clients[mcp_id]
        request_content = context["request"].get("content", context["request"].get("user_input", ""))
        
        # Simple MCP operation dispatch (can be enhanced)
        if hasattr(mcp_client, 'process_request'):
            return await mcp_client.process_request(request_content)
        elif hasattr(mcp_client, 'handle_request'):
            return await mcp_client.handle_request(request_content)
        else:
            return {"error": f"MCP client {mcp_id} does not support request processing"}
    
    async def _send_agent_message(self, agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to specific agent"""
        
        if self.send_message_func:
            try:
                return await self.send_message_func("orchestrator", agent_id, message)
            except Exception as e:
                self.logger.error(f"Failed to send message to {agent_id}: {e}")
                return {"error": f"Failed to communicate with {agent_id}: {str(e)}"}
        else:
            # Fallback: direct agent invocation
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                if hasattr(agent, 'process_message'):
                    return await agent.process_message(message)
            
            return {"error": f"No communication method available for {agent_id}"}
    
    async def _enhance_result_with_metadata(self, result: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance result with orchestration metadata"""
        
        enhanced = result.copy()
        enhanced.update({
            "orchestration": {
                "execution_id": context["execution_id"],
                "execution_mode": context["analysis"]["execution_mode"].value,
                "participating_agents": context["analysis"]["participating_agents"],
                "participating_mcp": context["analysis"]["participating_mcp"],
                "complexity_analysis": context["analysis"]["complexity"],
                "steps_completed": len(context["steps"]),
                "orchestrated_at": datetime.utcnow().isoformat()
            }
        })
        
        return enhanced
    
    async def _record_execution_success(self, execution_id: str, result: Dict[str, Any], 
                                       execution_time: float) -> None:
        """Record successful execution metrics"""
        
        execution_record = {
            "execution_id": execution_id,
            "status": "success",
            "execution_time": execution_time,
            "completed_at": datetime.utcnow().isoformat(),
            "result_summary": {
                "success": result.get("success", True),
                "execution_mode": result.get("execution_mode", "unknown")
            }
        }
        
        self.execution_history.append(execution_record)
        self._update_performance_metrics(execution_record)
    
    async def _record_execution_failure(self, execution_id: str, error: str, 
                                       execution_time: float) -> None:
        """Record failed execution metrics"""
        
        execution_record = {
            "execution_id": execution_id,
            "status": "failed",
            "error": error,
            "execution_time": execution_time,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        self.execution_history.append(execution_record)
        self._update_performance_metrics(execution_record)
    
    def _update_performance_metrics(self, execution_record: Dict[str, Any]) -> None:
        """Update orchestrator performance metrics"""
        
        if "performance" not in self.performance_metrics:
            self.performance_metrics["performance"] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0,
                "execution_modes": {}
            }
        
        metrics = self.performance_metrics["performance"]
        metrics["total_executions"] += 1
        
        if execution_record["status"] == "success":
            metrics["successful_executions"] += 1
            
            # Track execution mode metrics
            execution_mode = execution_record.get("result_summary", {}).get("execution_mode", "unknown")
            if execution_mode not in metrics["execution_modes"]:
                metrics["execution_modes"][execution_mode] = {"count": 0, "average_time": 0}
            
            mode_metrics = metrics["execution_modes"][execution_mode]
            mode_metrics["count"] += 1
            mode_metrics["average_time"] = (
                (mode_metrics["average_time"] * (mode_metrics["count"] - 1) + 
                 execution_record["execution_time"]) / mode_metrics["count"]
            )
        else:
            metrics["failed_executions"] += 1
        
        # Update average execution time
        if metrics["total_executions"] == 1:
            metrics["average_execution_time"] = execution_record["execution_time"]
        else:
            metrics["average_execution_time"] = (
                (metrics["average_execution_time"] * (metrics["total_executions"] - 1) + 
                 execution_record["execution_time"]) / metrics["total_executions"]
            )
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration system status"""
        
        return {
            "active_executions": len(self.active_executions),
            "total_executions": len(self.execution_history),
            "registered_agents": len(self.registered_agents),
            "available_mcp_clients": len(self.mcp_clients),
            "performance_metrics": self.performance_metrics,
            "multi_agent_status": await self.multi_agent_coordinator.get_coordination_status(),
            "agent_registry_status": await self.agent_registry.get_registry_statistics(),
            "system_health": await self._assess_system_health()
        }
    
    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        
        health_score = 100
        issues = []
        
        # Check agent availability
        if len(self.registered_agents) == 0:
            health_score -= 30
            issues.append("No registered agents available")
        
        # Check recent failure rate
        if len(self.execution_history) > 0:
            recent_executions = self.execution_history[-10:]  # Last 10 executions
            failed_recent = sum(1 for exec in recent_executions if exec["status"] == "failed")
            failure_rate = failed_recent / len(recent_executions)
            
            if failure_rate > 0.5:
                health_score -= 25
                issues.append(f"High failure rate: {failure_rate:.1%}")
            elif failure_rate > 0.2:
                health_score -= 10
                issues.append(f"Elevated failure rate: {failure_rate:.1%}")
        
        # Check active executions
        if len(self.active_executions) > self.max_concurrent_executions * 0.8:
            health_score -= 15
            issues.append("High concurrent execution load")
        
        return {
            "health_score": max(0, health_score),
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
            "issues": issues,
            "assessed_at": datetime.utcnow().isoformat()
        }