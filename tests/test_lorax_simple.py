"""
Simple test script for LoRAx functionality (no pytest required)
"""

import asyncio
import sys
from pathlib import Path

# Add AOS to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import LoRAx components
exec(open(Path(__file__).parent.parent / "src" / "AgentOperatingSystem" / "ml" / "lorax_server.py").read())


def test_config():
    """Test LoRAx configuration"""
    print("Testing LoRAx configuration...")
    
    config = LoRAxConfig()
    assert config.base_model == "meta-llama/Llama-3.1-8B-Instruct"
    assert config.port == 8080
    assert config.adapter_cache_size == 100
    
    print("  ✓ Default configuration works")
    
    custom_config = LoRAxConfig(base_model="custom", port=9090)
    assert custom_config.base_model == "custom"
    assert custom_config.port == 9090
    
    print("  ✓ Custom configuration works")


def test_registry():
    """Test adapter registry"""
    print("\nTesting adapter registry...")
    
    registry = LoRAxAdapterRegistry()
    
    # Register adapter
    adapter = registry.register_adapter("test_adapter", "TEST", "/models/test")
    assert adapter.adapter_id == "test_adapter"
    assert adapter.agent_role == "TEST"
    
    print("  ✓ Adapter registration works")
    
    # Get adapter
    retrieved = registry.get_adapter("test_adapter")
    assert retrieved is not None
    assert retrieved.adapter_id == "test_adapter"
    
    print("  ✓ Adapter retrieval works")
    
    # Get by agent role
    agent_adapter = registry.get_adapter_for_agent("TEST")
    assert agent_adapter is not None
    assert agent_adapter.agent_role == "TEST"
    
    print("  ✓ Agent role lookup works")
    
    # List adapters
    registry.register_adapter("test2", "TEST2", "/models/test2")
    adapters = registry.list_adapters()
    assert len(adapters) == 2
    
    print("  ✓ Adapter listing works")


async def test_server():
    """Test LoRAx server"""
    print("\nTesting LoRAx server...")
    
    config = LoRAxConfig()
    server = LoRAxServer(config)
    
    # Initial state
    assert not server.running
    print("  ✓ Server initialization works")
    
    # Start server
    started = await server.start()
    assert started
    assert server.running
    print("  ✓ Server start works")
    
    # Stop server
    stopped = await server.stop()
    assert stopped
    assert not server.running
    print("  ✓ Server stop works")


async def test_inference():
    """Test inference"""
    print("\nTesting inference...")
    
    config = LoRAxConfig()
    server = LoRAxServer(config)
    
    # Setup
    server.registry.register_adapter("test_adapter", "TEST", "/models/test")
    await server.start()
    
    # Single inference
    result = await server.inference("test_adapter", "Test prompt")
    assert result is not None
    assert "generated_text" in result
    assert "latency_ms" in result
    
    print("  ✓ Single inference works")
    
    # Batch inference
    requests = [
        {"adapter_id": "test_adapter", "prompt": "Test 1"},
        {"adapter_id": "test_adapter", "prompt": "Test 2"}
    ]
    results = await server.batch_inference(requests)
    assert len(results) == 2
    
    print("  ✓ Batch inference works")
    
    await server.stop()


async def test_metrics():
    """Test metrics tracking"""
    print("\nTesting metrics...")
    
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
    
    print("  ✓ Metrics tracking works")
    
    # Check adapter stats
    stats = server.get_adapter_stats("test_adapter")
    assert stats is not None
    assert stats["inference_count"] == 2
    
    print("  ✓ Adapter statistics work")
    
    await server.stop()


async def test_multi_agent():
    """Test multi-agent scenario"""
    print("\nTesting multi-agent scenario...")
    
    config = LoRAxConfig(adapter_cache_size=5)
    server = LoRAxServer(config)
    
    # Register multiple agents
    agents = ["CEO", "CFO", "COO", "CMO", "CTO"]
    for agent in agents:
        server.registry.register_adapter(
            f"{agent.lower()}_adapter",
            agent,
            f"/models/{agent.lower()}"
        )
    
    print(f"  ✓ Registered {len(agents)} agents")
    
    await server.start()
    
    # Batch inference for all agents
    requests = [
        {"adapter_id": f"{agent.lower()}_adapter", "prompt": f"{agent} analysis"}
        for agent in agents
    ]
    
    results = await server.batch_inference(requests)
    assert len(results) == len(agents)
    
    print(f"  ✓ Processed {len(results)} concurrent requests")
    
    # Check status
    status = server.get_status()
    assert status["total_adapters"] == len(agents)
    assert status["metrics"]["total_requests"] == len(agents)
    
    print(f"  ✓ All agents served successfully")
    
    await server.stop()


async def main():
    """Run all tests"""
    print("=" * 70)
    print("LoRAx Test Suite")
    print("=" * 70)
    
    try:
        test_config()
        test_registry()
        await test_server()
        await test_inference()
        await test_metrics()
        await test_multi_agent()
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
