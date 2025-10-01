#!/usr/bin/env python3
"""
Test Enhanced Orchestration Integration

Comprehensive test of the enhanced orchestration system integrated from SelfLearningAgent.
Tests all major components: UnifiedOrchestrator, MultiAgentCoordinator, AgentRegistry, 
MCPClientManager, ModelOrchestrator, and AzureIntegration.
"""

import asyncio
import logging
import json
from pathlib import Path
import sys
from typing import Dict, Any

# Add the AOS directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from aos.orchestration.enhanced import (
    UnifiedOrchestrator, ExecutionMode, RequestType,
    MultiAgentCoordinator, CoordinationMode,
    AgentRegistry,
    MCPClientManager,
    ModelOrchestrator, ModelType,
    AzureIntegration, AzureServiceType
)
from aos.agents.base import BaseAgent
from aos.messaging.types import Message, MessageType


class MockAgent(BaseAgent):
    """Mock agent for testing"""
    
    def __init__(self, agent_id: str, domain: str = "general"):
        super().__init__(agent_id)
        self.domain = domain
        self.processed_messages = []
        self.is_running = False
    
    def get_message_handlers(self) -> Dict[MessageType, Any]:
        """Return message handlers"""
        return {
            MessageType.USER_REQUEST: self.handle_user_request,
            MessageType.AGENT_REQUEST: self.handle_agent_request,
            MessageType.SYSTEM_COMMAND: self.handle_system_command
        }
    
    async def start(self) -> None:
        """Start the agent"""
        self.is_running = True
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.is_running = False
    
    async def handle_user_request(self, message: Message) -> Dict[str, Any]:
        """Handle user request"""
        return await self.process_message(message.content)
    
    async def handle_agent_request(self, message: Message) -> Dict[str, Any]:
        """Handle agent request"""
        return await self.process_message(message.content)
    
    async def handle_system_command(self, message: Message) -> Dict[str, Any]:
        """Handle system command"""
        return await self.process_message(message.content)
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message"""
        self.processed_messages.append(message)
        
        return {
            "success": True,
            "response": f"Mock response from {self.agent_id} for domain {self.domain}",
            "agent_id": self.agent_id,
            "domain": self.domain,
            "message_type": message.get("type", "unknown"),
            "timestamp": "2024-01-01T00:00:00Z"
        }


class MockMCPClient:
    """Mock MCP client for testing"""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.requests_processed = []
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request"""
        self.requests_processed.append(request)
        
        return {
            "success": True,
            "response": f"Mock MCP response from {self.client_id}",
            "client_id": self.client_id,
            "request_id": request.get("request_id", "unknown"),
            "data": {"mock_data": f"from_{self.client_id}"}
        }


async def test_agent_registry():
    """Test the AgentRegistry component"""
    print("\\n=== Testing AgentRegistry ===")
    
    # Create logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    
    # Create registry
    registry = AgentRegistry(logger=logger)
    
    # Create mock agents
    sales_agent = MockAgent("sales_agent", "sales")
    leadership_agent = MockAgent("leadership_agent", "leadership")
    
    # Test agent registration
    result = await registry.register_domain_agent("sales", sales_agent, {"capabilities": ["crm", "pipeline"]})
    print(f"Sales agent registration: {result['success']}")
    
    result = await registry.register_domain_agent("leadership", leadership_agent, {"capabilities": ["strategy", "planning"]})
    print(f"Leadership agent registration: {result['success']}")
    
    # Test registry status
    status = await registry.get_registry_statistics()
    print(f"Registry status: {status['active_agents']} agents, {status['total_domains']} domains")
    
    # Test agent lookup
    agent = await registry.get_domain_agent("sales")
    print(f"Sales domain agent: {'found' if agent else 'not found'}")
    
    return registry


async def test_mcp_client_manager():
    """Test the MCPClientManager component"""
    print("\\n=== Testing MCPClientManager ===")
    
    # Create manager
    manager = MCPClientManager()
    
    # Create mock MCP clients
    github_client = MockMCPClient("github")
    linkedin_client = MockMCPClient("linkedin")
    
    # Test client registration
    result = await manager.register_mcp_client("github", github_client)
    print(f"GitHub client registration: {result['success']}")
    
    result = await manager.register_mcp_client("linkedin", linkedin_client)
    print(f"LinkedIn client registration: {result['success']}")
    
    # Test request processing
    request = {
        "type": "test_request",
        "message": "Test MCP functionality",
        "data": {"test": True}
    }
    
    result = await manager.process_mcp_request("github", request)
    print(f"GitHub request processing: {result['success']}")
    
    # Test batch processing
    batch_requests = [
        {"client_id": "github", "message": "Batch request 1"},
        {"client_id": "linkedin", "message": "Batch request 2"}
    ]
    
    batch_result = await manager.batch_process_requests(batch_requests)
    print(f"Batch processing: {batch_result['successful_requests']}/{batch_result['total_requests']} successful")
    
    # Test health check
    health = await manager.health_check_all_clients()
    print(f"MCP health check: {health['overall_health']}")
    
    return manager


async def test_multi_agent_coordinator():
    """Test the MultiAgentCoordinator component"""
    print("\\n=== Testing MultiAgentCoordinator ===")
    
    # Create registered agents dict
    registered_agents = {
        "sales_agent": MockAgent("sales_agent", "sales"),
        "leadership_agent": MockAgent("leadership_agent", "leadership"),
        "analytics_agent": MockAgent("analytics_agent", "analytics")
    }
    
    # Create coordinator
    coordinator = MultiAgentCoordinator(registered_agents=registered_agents)
    
    # Test sequential coordination
    result = await coordinator.handle_multiagent_request(
        agent_id="sales_agent",
        domain="sales",
        user_input="Generate comprehensive sales report with strategic analysis",
        conv_id="test_conv_001",
        coordination_mode=CoordinationMode.SEQUENTIAL
    )
    
    print(f"Sequential coordination: {result['success']}")
    print(f"Agents involved: {len(result.get('agents_involved', []))}")
    
    # Test parallel coordination  
    result = await coordinator.handle_multiagent_request(
        agent_id="leadership_agent",
        domain="leadership", 
        user_input="Analyze market trends for strategic planning",
        conv_id="test_conv_002",
        coordination_mode=CoordinationMode.PARALLEL
    )
    
    print(f"Parallel coordination: {result['success']}")
    
    # Test coordinator status
    status = await coordinator.get_coordination_status()
    print(f"Coordinator status: {status['completed_workflows']} workflows completed")
    
    return coordinator


async def test_model_orchestrator():
    """Test the ModelOrchestrator component"""
    print("\\n=== Testing ModelOrchestrator ===")
    
    # Create orchestrator
    orchestrator = ModelOrchestrator()
    
    # Wait for initialization
    await asyncio.sleep(1)
    
    # Test model selection
    optimal_model = await orchestrator.select_optimal_model("leadership", "high", "low_latency")
    print(f"Optimal model for leadership domain: {optimal_model.value}")
    
    # Test orchestrator status
    status = await orchestrator.get_orchestrator_status()
    print(f"Model orchestrator status: {len(status['service_availability'])} services checked")
    
    return orchestrator


async def test_azure_integration():
    """Test the AzureIntegration component"""
    print("\\n=== Testing AzureIntegration ===")
    
    # Create integration
    azure_integration = AzureIntegration()
    
    # Wait for initialization
    await asyncio.sleep(1)
    
    # Test status
    status = await azure_integration.get_azure_status()
    print(f"Azure integration status: SDK available = {status['azure_sdk_available']}")
    
    # Test health check
    health = await azure_integration.health_check()
    print(f"Azure health check: {health['overall_health']}")
    
    return azure_integration


async def test_unified_orchestrator():
    """Test the UnifiedOrchestrator component"""
    print("\\n=== Testing UnifiedOrchestrator ===")
    
    # Create registered agents and MCP clients
    registered_agents = {
        "sales_agent": MockAgent("sales_agent", "sales"),
        "leadership_agent": MockAgent("leadership_agent", "leadership")
    }
    
    mcp_clients = {
        "github": MockMCPClient("github"),
        "linkedin": MockMCPClient("linkedin")
    }
    
    # Create unified orchestrator
    orchestrator = UnifiedOrchestrator(
        registered_agents=registered_agents,
        mcp_clients=mcp_clients
    )
    
    # Test single agent execution
    request = {
        "type": "user_query",
        "domain": "leadership",
        "content": "Provide strategic analysis for Q4 planning",
        "conversation_id": "test_unified_001"
    }
    
    result = await orchestrator.orchestrate_request(request)
    print(f"Single agent orchestration: {result.get('success', False)}")
    
    # Test multi-agent execution
    complex_request = {
        "type": "user_query", 
        "domain": "sales",
        "content": "Generate comprehensive report with analysis, strategy, and multiple data integrations",
        "conversation_id": "test_unified_002"
    }
    
    result = await orchestrator.orchestrate_request(complex_request)
    print(f"Multi-agent orchestration: {result.get('success', False)}")
    
    # Test orchestration status
    status = await orchestrator.get_orchestration_status()
    print(f"Orchestration status: {status['total_executions']} total executions")
    
    return orchestrator


async def test_integration_workflow():
    """Test complete integration workflow"""
    print("\\n=== Testing Complete Integration Workflow ===")
    
    # Create all components
    registry = await test_agent_registry()
    mcp_manager = await test_mcp_client_manager()
    coordinator = await test_multi_agent_coordinator()
    model_orchestrator = await test_model_orchestrator()
    azure_integration = await test_azure_integration()
    
    # Create unified orchestrator with all components
    unified_orchestrator = UnifiedOrchestrator(
        registered_agents={
            "sales_agent": MockAgent("sales_agent", "sales"),
            "leadership_agent": MockAgent("leadership_agent", "leadership")
        },
        mcp_clients={
            "github": MockMCPClient("github"),
            "linkedin": MockMCPClient("linkedin")
        }
    )
    
    # Test complex workflow
    complex_workflow_request = {
        "type": "user_query",
        "domain": "sales",
        "content": "Create integrated business report using GitHub data, LinkedIn insights, with multi-agent collaboration and Azure storage",
        "conversation_id": "test_workflow_001",
        "priority": "high"
    }
    
    result = await unified_orchestrator.orchestrate_request(complex_workflow_request)
    
    print(f"\\nComplex workflow result:")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Execution Mode: {result.get('orchestration', {}).get('execution_mode', 'unknown')}")
    print(f"  Agents Involved: {len(result.get('orchestration', {}).get('participating_agents', []))}")
    print(f"  MCP Clients Used: {len(result.get('orchestration', {}).get('participating_mcp', []))}")
    
    return result


async def main():
    """Main test function"""
    print("Enhanced Orchestration Integration Test")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test individual components
        await test_agent_registry()
        await test_mcp_client_manager()
        await test_multi_agent_coordinator()
        await test_model_orchestrator()
        await test_azure_integration()
        await test_unified_orchestrator()
        
        # Test complete integration workflow
        final_result = await test_integration_workflow()
        
        print("\\n" + "=" * 50)
        print("✅ All enhanced orchestration tests completed successfully!")
        print(f"Final integration test success: {final_result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)