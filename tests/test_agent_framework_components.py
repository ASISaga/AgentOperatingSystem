"""
Tests for AOS Agent Framework Components

Tests the core Agent Framework functionality in AgentOperatingSystem.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Import AOS components
from AgentOperatingSystem.agents.agent_framework_system import AgentFrameworkSystem
from AgentOperatingSystem.agents.multi_agent import MultiAgentSystem, ApprovalTerminationStrategy
from AgentOperatingSystem.orchestration.workflow_orchestrator import WorkflowOrchestrator
from AgentOperatingSystem.orchestration.model_orchestration import ModelOrchestrator, ModelType


class TestAOSAgentFrameworkSystem:
    """Test AOS Agent Framework System core functionality"""
    
    @pytest.fixture
    def agent_system(self):
        return AgentFrameworkSystem()
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, agent_system):
        """Test that the Agent Framework system initializes correctly"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch.object(agent_system, '_setup_telemetry', new_callable=AsyncMock) as mock_telemetry:
                with patch('AgentOperatingSystem.agents.agent_framework_system.ChatAgent') as mock_chat_agent:
                    
                    # Mock ChatAgent creation
                    mock_agent_instances = []
                    for i in range(3):  # Default agents: BA, SE, PO
                        mock_agent = Mock()
                        mock_agent.name = f"Agent{i}"
                        mock_agent_instances.append(mock_agent)
                    
                    mock_chat_agent.side_effect = mock_agent_instances
                    
                    await agent_system.initialize()
                    
                    assert agent_system.is_initialized
                    assert len(agent_system.agents) == 3
                    mock_telemetry.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_conversation_workflow_creation(self, agent_system):
        """Test conversation workflow creation"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.agent_framework_system.WorkflowBuilder') as mock_builder_class:
                with patch('AgentOperatingSystem.agents.agent_framework_system.ChatAgent'):
                    
                    # Mock workflow builder
                    mock_workflow = Mock()
                    mock_workflow.execute = AsyncMock(return_value="Workflow result")
                    
                    mock_builder = Mock()
                    mock_builder.add_agent.return_value = mock_builder
                    mock_builder.build_sequential_workflow.return_value = mock_workflow
                    mock_builder_class.return_value = mock_builder
                    
                    await agent_system.initialize()
                    
                    # Test workflow creation
                    agents = list(agent_system.agents.values())[:2]  # Take first 2 agents
                    workflow = await agent_system._create_conversation_workflow(agents, "test message")
                    
                    assert workflow == mock_workflow
                    mock_builder.add_agent.assert_called()
                    mock_builder.build_sequential_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_workflow_execution(self, agent_system):
        """Test workflow execution"""
        mock_workflow = Mock()
        mock_workflow.execute = AsyncMock(return_value="Execution result")
        
        result = await agent_system._execute_workflow(mock_workflow)
        
        assert result["success"] is True
        assert result["result"] == "Execution result"
        mock_workflow.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_management(self, agent_system):
        """Test agent creation and removal"""
        with patch('AgentOperatingSystem.agents.agent_framework_system.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.agents.agent_framework_system.ChatAgent') as mock_chat_agent:
                
                mock_agent = Mock()
                mock_agent.name = "CustomAgent"
                mock_chat_agent.return_value = mock_agent
                
                await agent_system.initialize()
                
                # Test agent creation
                agent = await agent_system.create_agent("CustomAgent", "Custom instructions", ["custom_capability"])
                
                assert agent == mock_agent
                assert "CustomAgent" in agent_system.agents
                
                # Test agent removal
                removed = await agent_system.remove_agent("CustomAgent")
                
                assert removed is True
                assert "CustomAgent" not in agent_system.agents
    
    def test_statistics_tracking(self, agent_system):
        """Test statistics collection"""
        stats = agent_system.get_statistics()
        
        expected_keys = [
            "total_conversations", "successful_completions", "failed_completions",
            "total_agents", "is_initialized", "framework"
        ]
        
        for key in expected_keys:
            assert key in stats
        
        assert stats["framework"] == "Microsoft Agent Framework"


class TestAOSMultiAgentSystem:
    """Test AOS Multi-Agent System updated for Agent Framework"""
    
    @pytest.fixture
    def multi_agent_system(self):
        return MultiAgentSystem()
    
    @pytest.mark.asyncio
    async def test_initialization_flow(self, multi_agent_system):
        """Test the complete initialization flow"""
        with patch.object(multi_agent_system.agent_framework_system, 'initialize') as mock_init:
            with patch.object(multi_agent_system, '_initialize_default_agents') as mock_default_agents:
                
                await multi_agent_system.initialize()
                
                assert multi_agent_system.is_initialized
                mock_init.assert_called_once()
                mock_default_agents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_conversation_delegation(self, multi_agent_system):
        """Test that conversations are properly delegated to Agent Framework system"""
        expected_result = {
            "success": True,
            "result": "Test conversation result",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        with patch.object(multi_agent_system.agent_framework_system, 'run_multi_agent_conversation') as mock_run:
            mock_run.return_value = expected_result
            
            await multi_agent_system.initialize()
            result = await multi_agent_system.run_multi_agent_conversation("Test message", ["BusinessAnalyst"])
            
            assert result["success"] is True
            assert "conversation_id" in result
            assert result["result"] == expected_result["result"]
            
            mock_run.assert_called_once_with("Test message", ["BusinessAnalyst"])
    
    @pytest.mark.asyncio
    async def test_agent_operations_delegation(self, multi_agent_system):
        """Test that agent operations are delegated to Agent Framework system"""
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        
        # Test agent creation delegation
        with patch.object(multi_agent_system.agent_framework_system, 'create_agent') as mock_create:
            mock_create.return_value = mock_agent
            
            agent = await multi_agent_system.create_agent("TestAgent", "Test instructions")
            
            assert agent == mock_agent
            mock_create.assert_called_once_with("TestAgent", "Test instructions", None)
        
        # Test agent removal delegation
        with patch.object(multi_agent_system.agent_framework_system, 'remove_agent') as mock_remove:
            mock_remove.return_value = True
            
            removed = await multi_agent_system.remove_agent("TestAgent")
            
            assert removed is True
            mock_remove.assert_called_once_with("TestAgent")
    
    def test_agent_listing_integration(self, multi_agent_system):
        """Test agent listing integrates both legacy and framework agents"""
        multi_agent_system.agents = {"LegacyAgent": Mock()}
        
        with patch.object(multi_agent_system.agent_framework_system, 'list_agents') as mock_list:
            mock_list.return_value = ["FrameworkAgent1", "FrameworkAgent2"]
            
            agents = multi_agent_system.list_agents()
            
            assert "LegacyAgent" in agents
            assert "FrameworkAgent1" in agents
            assert "FrameworkAgent2" in agents
    
    @pytest.mark.asyncio
    async def test_system_shutdown(self, multi_agent_system):
        """Test complete system shutdown"""
        multi_agent_system.agents = {"TestAgent": Mock()}
        
        with patch.object(multi_agent_system.agent_framework_system, 'shutdown') as mock_shutdown:
            await multi_agent_system.shutdown()
            
            assert len(multi_agent_system.agents) == 0
            assert multi_agent_system.is_initialized is False
            mock_shutdown.assert_called_once()


class TestApprovalTerminationStrategy:
    """Test the updated ApprovalTerminationStrategy"""
    
    @pytest.fixture
    def termination_strategy(self):
        return ApprovalTerminationStrategy()
    
    @pytest.mark.asyncio
    async def test_should_terminate_with_approval(self, termination_strategy):
        """Test termination detection with approval token"""
        mock_messages = [
            Mock(content="Starting conversation"),
            Mock(content="Discussion continues"),
            Mock(content="Final decision %APPR%")
        ]
        
        mock_agent = Mock()
        should_terminate = await termination_strategy.should_agent_terminate(mock_agent, mock_messages)
        
        assert should_terminate is True
    
    @pytest.mark.asyncio
    async def test_should_not_terminate_without_approval(self, termination_strategy):
        """Test termination detection without approval token"""
        mock_messages = [
            Mock(content="Starting conversation"),
            Mock(content="Discussion continues"),
            Mock(content="Need more information")
        ]
        
        mock_agent = Mock()
        should_terminate = await termination_strategy.should_agent_terminate(mock_agent, mock_messages)
        
        assert should_terminate is False
    
    def test_should_terminate_direct_check(self, termination_strategy):
        """Test direct termination check"""
        messages_with_approval = [Mock(content="Decision approved %APPR%")]
        messages_without_approval = [Mock(content="Still discussing")]
        
        assert termination_strategy.should_terminate(messages_with_approval) is True
        assert termination_strategy.should_terminate(messages_without_approval) is False
    
    def test_custom_approval_token(self):
        """Test custom approval token"""
        custom_strategy = ApprovalTerminationStrategy(token="%DONE%")
        
        messages = [Mock(content="Task completed %DONE%")]
        
        assert custom_strategy.should_terminate(messages) is True


class TestAOSWorkflowOrchestrator:
    """Test AOS Workflow Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        return WorkflowOrchestrator("TestOrchestrator")
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.WorkflowBuilder') as mock_builder:
                mock_builder.return_value = Mock()
                
                await orchestrator.initialize()
                
                assert orchestrator.is_initialized
                assert orchestrator.workflow_builder is not None
                assert orchestrator.name == "TestOrchestrator"
    
    @pytest.mark.asyncio
    async def test_workflow_building_process(self, orchestrator):
        """Test the complete workflow building process"""
        with patch('AgentOperatingSystem.orchestration.workflow_orchestrator.AGENT_FRAMEWORK_AVAILABLE', True):
            mock_agent = Mock()
            mock_agent.name = "TestAgent"
            
            mock_workflow = Mock()
            mock_builder = Mock()
            mock_builder.register_agent.return_value = "node_123"  # Updated to use register_agent
            mock_builder.build.return_value = mock_workflow
            
            orchestrator.workflow_builder = mock_builder
            orchestrator.is_initialized = True
            
            # Add agent
            node_id = orchestrator.add_agent("TestAgent", mock_agent)
            assert node_id == "node_123"
            
            # Build workflow
            orchestrator.build_workflow()
            assert orchestrator.workflow == mock_workflow
            
            mock_builder.register_agent.assert_called_once_with(mock_agent)  # Updated to use register_agent
            mock_builder.build.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_workflow_execution_with_metrics(self, orchestrator):
        """Test workflow execution with performance metrics"""
        mock_workflow = Mock()
        mock_workflow.run = AsyncMock(return_value="Execution result")
        
        orchestrator.workflow = mock_workflow
        
        result = await orchestrator.execute_workflow("test input")
        
        assert result == "Execution result"
        assert orchestrator.stats["total_workflows_executed"] == 1
        assert orchestrator.stats["successful_executions"] == 1
        assert orchestrator.stats["average_execution_time"] > 0
    
    def test_workflow_edge_management(self, orchestrator):
        """Test workflow edge creation and management"""
        orchestrator.is_initialized = True
        orchestrator.executors = {
            "Agent1": "node1",
            "Agent2": "node2",
            "Agent3": "node3"
        }
        
        mock_builder = Mock()
        orchestrator.workflow_builder = mock_builder
        
        # Test single edge
        orchestrator.add_workflow_edge("Agent1", "Agent2")
        mock_builder.add_edge.assert_called_with("node1", "node2")
        
        # Test multiple edges
        orchestrator.add_workflow_edge(["Agent1", "Agent2"], "Agent3")
        mock_builder.add_edge.assert_called_with(["node1", "node2"], "node3")


class TestAOSModelOrchestration:
    """Test AOS Model Orchestration with Agent Framework"""
    
    @pytest.mark.asyncio
    async def test_agent_framework_initialization(self):
        """Test Agent Framework initialization in model orchestrator"""
        model_orchestrator = ModelOrchestrator()
        await model_orchestrator.initialize()
        with patch('AgentOperatingSystem.orchestration.model_orchestration.AGENT_FRAMEWORK_AVAILABLE', True):
            with patch('AgentOperatingSystem.orchestration.model_orchestration.ChatAgent') as mock_chat_agent:
                
                mock_agent = Mock()
                mock_agent.name = "ModelOrchestrator"
                mock_chat_agent.return_value = mock_agent
                
                await model_orchestrator._initialize_agent_framework()
                
                assert model_orchestrator.agent_framework_client == mock_agent
                mock_chat_agent.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_agent_framework_request_handling(self):
        """Test Agent Framework request handling"""
        model_orchestrator = ModelOrchestrator()
        await model_orchestrator.initialize()
        
        mock_agent = Mock()
        model_orchestrator.agent_framework_client = mock_agent
        
        result = await model_orchestrator._handle_agent_framework_request(
            "test_domain", "test_input", "conv_123"
        )
        
        assert result["success"] is True
        assert result["source"] == "agent_framework"
        assert result["conversationId"] == "conv_123"
        assert result["domain"] == "test_domain"
    
    @pytest.mark.asyncio
    async def test_model_type_routing_to_agent_framework(self):
        """Test that AGENT_FRAMEWORK model type routes correctly"""
        model_orchestrator = ModelOrchestrator()
        await model_orchestrator.initialize()
        model_orchestrator.agent_framework_client = Mock()
        
        with patch.object(model_orchestrator, '_handle_agent_framework_request') as mock_handle:
            mock_handle.return_value = {"success": True, "result": "test"}
            
            result = await model_orchestrator.process_model_request(
                ModelType.AGENT_FRAMEWORK, "test_domain", "test_input", "conv_123"
            )
            
            assert result["success"] is True
            mock_handle.assert_called_once_with("test_domain", "test_input", "conv_123")
    
    @pytest.mark.asyncio
    async def test_service_availability_reporting(self):
        """Test service availability reporting includes Agent Framework"""
        model_orchestrator = ModelOrchestrator()
        await model_orchestrator.initialize()
        availability = model_orchestrator.get_service_availability()
        
        assert "agent_framework" in availability


if __name__ == "__main__":
    pytest.main([__file__])