"""
Unit tests for LoRAx integration
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add AOS to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import LoRAx components directly to avoid dependency issues
from AgentOperatingSystem.ml.lorax_server import (
    LoRAxServer, LoRAxConfig, LoRAxAdapterRegistry, AdapterInfo
)


class TestLoRAxConfig:
    """Test LoRAx configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = LoRAxConfig()
        
        assert config.base_model == "meta-llama/Llama-3.3-70B-Instruct"
        assert config.port == 8080
        assert config.adapter_cache_size == 100
        assert config.max_concurrent_requests == 128
        assert config.max_batch_size == 32
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = LoRAxConfig(
            base_model="custom-model",
            port=9090,
            adapter_cache_size=50
        )
        
        assert config.base_model == "custom-model"
        assert config.port == 9090
        assert config.adapter_cache_size == 50


class TestLoRAxAdapterRegistry:
    """Test adapter registry functionality"""
    
    def test_register_adapter(self):
        """Test adapter registration"""
        registry = LoRAxAdapterRegistry()
        
        adapter = registry.register_adapter(
            "ceo_adapter",
            "CEO",
            "/models/ceo"
        )
        
        assert adapter.adapter_id == "ceo_adapter"
        assert adapter.agent_role == "CEO"
        assert adapter.adapter_path == "/models/ceo"
        assert not adapter.loaded
        assert adapter.inference_count == 0
    
    def test_get_adapter(self):
        """Test retrieving adapter by ID"""
        registry = LoRAxAdapterRegistry()
        registry.register_adapter("test_adapter", "TEST", "/models/test")
        
        adapter = registry.get_adapter("test_adapter")
        
        assert adapter is not None
        assert adapter.adapter_id == "test_adapter"
    
    def test_get_adapter_for_agent(self):
        """Test retrieving adapter by agent role"""
        registry = LoRAxAdapterRegistry()
        registry.register_adapter("ceo_adapter", "CEO", "/models/ceo")
        
        adapter = registry.get_adapter_for_agent("CEO")
        
        assert adapter is not None
        assert adapter.agent_role == "CEO"
    
    def test_list_adapters(self):
        """Test listing all adapters"""
        registry = LoRAxAdapterRegistry()
        
        registry.register_adapter("ceo_adapter", "CEO", "/models/ceo")
        registry.register_adapter("cfo_adapter", "CFO", "/models/cfo")
        
        adapters = registry.list_adapters()
        
        assert len(adapters) == 2
        assert any(a.adapter_id == "ceo_adapter" for a in adapters)
        assert any(a.adapter_id == "cfo_adapter" for a in adapters)
    
    def test_update_usage_stats(self):
        """Test updating adapter usage statistics"""
        registry = LoRAxAdapterRegistry()
        adapter = registry.register_adapter("test_adapter", "TEST", "/models/test")
        
        # Update stats
        registry.update_usage_stats("test_adapter", loaded=True)
        
        updated_adapter = registry.get_adapter("test_adapter")
        assert updated_adapter.loaded
        assert updated_adapter.load_count == 1
        assert updated_adapter.inference_count == 1


class TestLoRAxServer:
    """Test LoRAx server functionality"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server initialization"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        assert not server.running
        assert server.registry is not None
        assert server.request_counter == 0
    
    @pytest.mark.asyncio
    async def test_server_start_stop(self):
        """Test starting and stopping server"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        # Start server
        started = await server.start()
        assert started
        assert server.running
        
        # Stop server
        stopped = await server.stop()
        assert stopped
        assert not server.running
    
    @pytest.mark.asyncio
    async def test_adapter_registration(self):
        """Test adapter registration with server"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        # Register adapters
        server.registry.register_adapter("ceo_adapter", "CEO", "/models/ceo")
        server.registry.register_adapter("cfo_adapter", "CFO", "/models/cfo")
        
        status = server.get_status()
        assert status["total_adapters"] == 2
    
    @pytest.mark.asyncio
    async def test_inference(self):
        """Test single inference"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        # Register and start
        server.registry.register_adapter("test_adapter", "TEST", "/models/test")
        await server.start()
        
        # Run inference
        result = await server.inference(
            "test_adapter",
            "Test prompt",
            max_new_tokens=128
        )
        
        assert result is not None
        assert "generated_text" in result
        assert "latency_ms" in result
        assert result["adapter_id"] == "test_adapter"
        
        await server.stop()
    
    @pytest.mark.asyncio
    async def test_batch_inference(self):
        """Test batch inference"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        # Register multiple adapters
        server.registry.register_adapter("ceo_adapter", "CEO", "/models/ceo")
        server.registry.register_adapter("cfo_adapter", "CFO", "/models/cfo")
        await server.start()
        
        # Batch inference
        requests = [
            {"adapter_id": "ceo_adapter", "prompt": "Strategic analysis"},
            {"adapter_id": "cfo_adapter", "prompt": "Financial analysis"}
        ]
        
        results = await server.batch_inference(requests)
        
        assert len(results) == 2
        assert all("generated_text" in r for r in results)
        
        await server.stop()
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self):
        """Test metrics tracking"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        server.registry.register_adapter("test_adapter", "TEST", "/models/test")
        await server.start()
        
        # Run some inferences
        await server.inference("test_adapter", "Test 1")
        await server.inference("test_adapter", "Test 2")
        
        status = server.get_status()
        metrics = status["metrics"]
        
        assert metrics["total_requests"] == 2
        assert metrics["successful_requests"] == 2
        assert metrics["average_latency_ms"] > 0
        
        await server.stop()
    
    @pytest.mark.asyncio
    async def test_adapter_stats(self):
        """Test adapter statistics"""
        config = LoRAxConfig()
        server = LoRAxServer(config)
        
        server.registry.register_adapter("test_adapter", "TEST", "/models/test")
        await server.start()
        
        # Run inference to generate stats
        await server.inference("test_adapter", "Test prompt")
        
        stats = server.get_adapter_stats("test_adapter")
        
        assert stats is not None
        assert stats["adapter_id"] == "test_adapter"
        assert stats["inference_count"] > 0
        assert stats["loaded"]
        
        await server.stop()


class TestLoRAxIntegration:
    """Integration tests for LoRAx"""
    
    @pytest.mark.asyncio
    async def test_multi_agent_scenario(self):
        """Test realistic multi-agent scenario"""
        config = LoRAxConfig(adapter_cache_size=5)
        server = LoRAxServer(config)
        
        # Register C-suite agents
        agents = ["CEO", "CFO", "COO", "CMO", "CTO"]
        for agent in agents:
            server.registry.register_adapter(
                f"{agent.lower()}_adapter",
                agent,
                f"/models/{agent.lower()}"
            )
        
        await server.start()
        
        # Simulate multi-agent coordination
        batch_requests = [
            {"adapter_id": f"{agent.lower()}_adapter", "prompt": f"{agent} analysis"}
            for agent in agents
        ]
        
        results = await server.batch_inference(batch_requests)
        
        # Verify results
        assert len(results) == len(agents)
        assert all("generated_text" in r for r in results)
        
        # Check that all agents were processed
        status = server.get_status()
        assert status["total_adapters"] == len(agents)
        assert status["metrics"]["total_requests"] == len(agents)
        
        await server.stop()
    
    @pytest.mark.asyncio
    async def test_cache_behavior(self):
        """Test adapter caching behavior"""
        config = LoRAxConfig(adapter_cache_size=2)  # Small cache
        server = LoRAxServer(config)
        
        # Register more adapters than cache can hold
        for i in range(5):
            server.registry.register_adapter(
                f"adapter_{i}",
                f"AGENT_{i}",
                f"/models/agent_{i}"
            )
        
        await server.start()
        
        # Run inference on multiple adapters
        for i in range(5):
            await server.inference(f"adapter_{i}", f"Prompt {i}")
        
        status = server.get_status()
        
        # Verify cache hits and misses are tracked
        assert status["metrics"]["cache_hits"] >= 0
        assert status["metrics"]["cache_misses"] >= 0
        
        await server.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
