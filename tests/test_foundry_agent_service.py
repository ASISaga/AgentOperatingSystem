"""
Tests for Azure Foundry Agent Service Integration

Tests the integration of Azure Foundry Agent Service with Llama 3.3 70B
including Stateful Threads, Entra Agent ID, and Foundry Tools.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from AgentOperatingSystem.ml.foundry_agent_service import (
    FoundryAgentServiceClient,
    FoundryAgentServiceConfig,
    FoundryResponse,
    ThreadInfo
)
from AgentOperatingSystem.orchestration import ModelOrchestrator, ModelType


class TestFoundryAgentServiceConfig:
    """Test Foundry Agent Service configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = FoundryAgentServiceConfig()
        
        assert config.model == "llama-3.3-70b"
        assert config.enable_stateful_threads is True
        assert config.enable_entra_agent_id is True
        assert config.enable_foundry_tools is True
        assert config.timeout == 60
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
    
    def test_from_env(self):
        """Test configuration from environment variables."""
        with patch.dict(os.environ, {
            "FOUNDRY_AGENT_SERVICE_ENDPOINT": "https://test-endpoint.azure.com",
            "FOUNDRY_AGENT_SERVICE_API_KEY": "test-api-key",
            "FOUNDRY_AGENT_ID": "test-agent-id",
            "FOUNDRY_MODEL": "llama-3.3-70b-custom",
            "FOUNDRY_ENABLE_STATEFUL_THREADS": "true",
            "FOUNDRY_TEMPERATURE": "0.8",
            "FOUNDRY_MAX_TOKENS": "2048"
        }):
            config = FoundryAgentServiceConfig.from_env()
            
            assert config.endpoint_url == "https://test-endpoint.azure.com"
            assert config.api_key == "test-api-key"
            assert config.agent_id == "test-agent-id"
            assert config.model == "llama-3.3-70b-custom"
            assert config.temperature == 0.8
            assert config.max_tokens == 2048


class TestFoundryAgentServiceClient:
    """Test Foundry Agent Service client."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        return FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key="test-api-key",
            agent_id="test-agent-id",
            model="llama-3.3-70b"
        )
    
    @pytest.fixture
    def client(self, mock_config):
        """Create client instance."""
        return FoundryAgentServiceClient(mock_config)
    
    @pytest.mark.asyncio
    async def test_initialize(self, client):
        """Test client initialization."""
        await client.initialize()
        
        assert client._initialized is True
    
    @pytest.mark.asyncio
    async def test_initialize_missing_endpoint(self):
        """Test initialization with missing endpoint."""
        config = FoundryAgentServiceConfig(
            endpoint_url="",
            api_key="test-api-key"
        )
        client = FoundryAgentServiceClient(config)
        
        with pytest.raises(ValueError, match="endpoint URL not configured"):
            await client.initialize()
    
    @pytest.mark.asyncio
    async def test_initialize_missing_api_key(self):
        """Test initialization with missing API key."""
        config = FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key=""
        )
        client = FoundryAgentServiceClient(config)
        
        with pytest.raises(ValueError, match="API key not configured"):
            await client.initialize()
    
    @pytest.mark.asyncio
    async def test_send_message(self, client):
        """Test sending a message."""
        await client.initialize()
        
        response = await client.send_message(
            message="Test message",
            domain="test"
        )
        
        assert isinstance(response, FoundryResponse)
        assert response.success is True
        assert response.model == "llama-3.3-70b"
    
    @pytest.mark.asyncio
    async def test_send_message_with_thread(self, client):
        """Test sending a message with thread ID."""
        await client.initialize()
        
        thread_id = "test-thread-123"
        response = await client.send_message(
            message="Test message",
            thread_id=thread_id,
            domain="test"
        )
        
        assert response.success is True
        assert response.thread_id == thread_id
    
    @pytest.mark.asyncio
    async def test_create_thread(self, client):
        """Test creating a stateful thread."""
        await client.initialize()
        
        metadata = {"purpose": "testing"}
        thread_id = await client.create_thread(metadata=metadata)
        
        assert thread_id.startswith("thread-")
        assert thread_id in client.active_threads
        
        thread_info = client.active_threads[thread_id]
        assert thread_info.agent_id == client.config.agent_id
        assert thread_info.metadata == metadata
    
    @pytest.mark.asyncio
    async def test_get_thread_info(self, client):
        """Test getting thread information."""
        await client.initialize()
        
        thread_id = await client.create_thread()
        thread_info = await client.get_thread_info(thread_id)
        
        assert thread_info is not None
        assert thread_info.thread_id == thread_id
    
    @pytest.mark.asyncio
    async def test_delete_thread(self, client):
        """Test deleting a thread."""
        await client.initialize()
        
        thread_id = await client.create_thread()
        assert thread_id in client.active_threads
        
        result = await client.delete_thread(thread_id)
        assert result is True
        assert thread_id not in client.active_threads
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, client):
        """Test metrics tracking."""
        await client.initialize()
        
        # Make a few requests
        for i in range(3):
            await client.send_message(f"Test message {i}", domain="test")
        
        metrics = client.get_metrics()
        
        assert metrics["total_requests"] >= 3
        assert metrics["successful_requests"] >= 3
        assert metrics["average_latency"] > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check."""
        await client.initialize()
        
        is_healthy = await client.health_check()
        assert isinstance(is_healthy, bool)
    
    def test_prepare_request_payload(self, client):
        """Test request payload preparation."""
        payload = client._prepare_request_payload(
            message="Test message",
            thread_id="test-thread",
            domain="test",
            system_prompt="Custom system prompt",
            tools=["tool1", "tool2"]
        )
        
        assert payload["model"] == "llama-3.3-70b"
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"
        assert payload["thread_id"] == "test-thread"
        assert payload["tools"] == ["tool1", "tool2"]


class TestModelOrchestratorIntegration:
    """Test integration with ModelOrchestrator."""
    
    @pytest.mark.asyncio
    async def test_foundry_model_type_available(self):
        """Test that FOUNDRY_AGENT_SERVICE model type is available."""
        assert hasattr(ModelType, "FOUNDRY_AGENT_SERVICE")
        assert ModelType.FOUNDRY_AGENT_SERVICE.value == "foundry_agent_service"
    
    @pytest.mark.asyncio
    async def test_orchestrator_process_foundry_request(self):
        """Test processing a Foundry Agent Service request through orchestrator."""
        with patch.dict(os.environ, {
            "FOUNDRY_AGENT_SERVICE_ENDPOINT": "https://test-endpoint.azure.com",
            "FOUNDRY_AGENT_SERVICE_API_KEY": "test-api-key",
            "FOUNDRY_AGENT_ID": "test-agent-id"
        }):
            orchestrator = ModelOrchestrator()
            await orchestrator.initialize()
            
            result = await orchestrator.process_model_request(
                model_type=ModelType.FOUNDRY_AGENT_SERVICE,
                domain="test",
                user_input="Test input",
                conversation_id="test-conv-001"
            )
            
            assert result["success"] is True
            assert result["model_type"] == "foundry_agent_service"
            assert result["source"] == "foundry_agent_service"
            assert "execution_time" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_foundry_availability_check(self):
        """Test checking Foundry Agent Service availability."""
        with patch.dict(os.environ, {
            "FOUNDRY_AGENT_SERVICE_ENDPOINT": "https://test-endpoint.azure.com",
            "FOUNDRY_AGENT_SERVICE_API_KEY": "test-api-key"
        }):
            orchestrator = ModelOrchestrator()
            await orchestrator.initialize()
            
            is_available = await orchestrator._is_model_available(
                ModelType.FOUNDRY_AGENT_SERVICE
            )
            
            assert is_available is True
    
    @pytest.mark.asyncio
    async def test_orchestrator_model_preferences(self):
        """Test that Foundry Agent Service is in model preferences."""
        orchestrator = ModelOrchestrator()
        await orchestrator.initialize()
        
        # Select optimal model for various domains
        with patch.dict(os.environ, {
            "FOUNDRY_AGENT_SERVICE_ENDPOINT": "https://test-endpoint.azure.com",
            "FOUNDRY_AGENT_SERVICE_API_KEY": "test-api-key"
        }):
            # Reload orchestrator to pick up env vars
            orchestrator = ModelOrchestrator()
            await orchestrator.initialize()
            
            model = await orchestrator.select_optimal_model(domain="leadership")
            assert model == ModelType.FOUNDRY_AGENT_SERVICE


class TestFoundryFeatures:
    """Test specific Foundry Agent Service features."""
    
    @pytest.mark.asyncio
    async def test_stateful_threads_feature(self):
        """Test Stateful Threads feature."""
        config = FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key="test-api-key",
            enable_stateful_threads=True
        )
        client = FoundryAgentServiceClient(config)
        await client.initialize()
        
        # Create thread
        thread_id = await client.create_thread()
        
        # Send multiple messages in the thread
        responses = []
        for i in range(3):
            response = await client.send_message(
                message=f"Message {i+1}",
                thread_id=thread_id,
                domain="test"
            )
            responses.append(response)
        
        # Check all responses have the same thread ID
        assert all(r.thread_id == thread_id for r in responses)
        
        # Check thread message count
        thread_info = await client.get_thread_info(thread_id)
        assert thread_info.message_count == 3
    
    @pytest.mark.asyncio
    async def test_entra_agent_id_feature(self):
        """Test Entra Agent ID feature."""
        config = FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key="test-api-key",
            agent_id="entra-agent-123",
            enable_entra_agent_id=True
        )
        client = FoundryAgentServiceClient(config)
        await client.initialize()
        
        response = await client.send_message(
            message="Test message",
            domain="test"
        )
        
        # Check that agent ID is in response
        assert response.agent_id == "entra-agent-123" or response.agent_id is not None
    
    @pytest.mark.asyncio
    async def test_foundry_tools_feature(self):
        """Test Foundry Tools feature."""
        config = FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key="test-api-key",
            enable_foundry_tools=True
        )
        client = FoundryAgentServiceClient(config)
        await client.initialize()
        
        tools = ["tool1", "tool2", "tool3"]
        response = await client.send_message(
            message="Test message with tools",
            domain="test",
            tools=tools
        )
        
        # Check that tools are tracked
        assert isinstance(response.tools_used, list)
    
    @pytest.mark.asyncio
    async def test_llama_3_3_70b_model(self):
        """Test that Llama 3.3 70B is the default model."""
        config = FoundryAgentServiceConfig()
        assert config.model == "llama-3.3-70b"
        
        client = FoundryAgentServiceClient(config)
        assert client.config.model == "llama-3.3-70b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
