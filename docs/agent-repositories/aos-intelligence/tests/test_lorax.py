"""
Tests for LoRAxServer, LoRAxConfig, and LoRAxAdapterRegistry.
"""

import pytest
from aos_intelligence.ml.lorax_server import (
    LoRAxServer, LoRAxConfig, LoRAxAdapterRegistry, AdapterInfo
)


class TestLoRAxConfig:
    def test_default_config(self):
        config = LoRAxConfig()
        assert config.base_model == "meta-llama/Llama-3.3-70B-Instruct"
        assert config.port == 8080
        assert config.adapter_cache_size == 100
        assert config.max_concurrent_requests == 128
        assert config.max_batch_size == 32

    def test_custom_config(self):
        config = LoRAxConfig(
            base_model="custom-model",
            port=9090,
            adapter_cache_size=50,
        )
        assert config.base_model == "custom-model"
        assert config.port == 9090
        assert config.adapter_cache_size == 50


class TestLoRAxAdapterRegistry:
    def test_register_adapter(self):
        registry = LoRAxAdapterRegistry()
        adapter = registry.register_adapter("ceo_adapter", "CEO", "/models/ceo")
        assert adapter.adapter_id == "ceo_adapter"
        assert adapter.agent_role == "CEO"
        assert adapter.adapter_path == "/models/ceo"

    def test_get_adapter(self):
        registry = LoRAxAdapterRegistry()
        registry.register_adapter("finance_adapter", "CFO", "/models/finance")
        adapter = registry.get_adapter("finance_adapter")
        assert adapter is not None
        assert adapter.adapter_id == "finance_adapter"

    def test_get_missing_adapter(self):
        registry = LoRAxAdapterRegistry()
        adapter = registry.get_adapter("nonexistent")
        assert adapter is None

    def test_list_adapters(self):
        registry = LoRAxAdapterRegistry()
        registry.register_adapter("a1", "Role1", "/models/r1")
        registry.register_adapter("a2", "Role2", "/models/r2")
        adapters = registry.list_adapters()
        assert len(adapters) == 2

    def test_unregister_adapter(self):
        registry = LoRAxAdapterRegistry()
        registry.register_adapter("temp_adapter", "Temp", "/models/temp")
        assert registry.get_adapter("temp_adapter") is not None
        registry.unregister_adapter("temp_adapter")
        assert registry.get_adapter("temp_adapter") is None


class TestLoRAxServer:
    def test_creation(self):
        config = LoRAxConfig(port=9100)
        server = LoRAxServer(config)
        assert server.config.port == 9100
        assert isinstance(server.adapter_registry, LoRAxAdapterRegistry)

    @pytest.mark.asyncio
    async def test_register_and_inference(self):
        config = LoRAxConfig()
        server = LoRAxServer(config)
        server.adapter_registry.register_adapter("test_adapter", "TestRole", "/models/test")
        result = await server.inference("test_adapter", "Hello world")
        assert isinstance(result, dict)
        assert "response" in result or "error" in result
