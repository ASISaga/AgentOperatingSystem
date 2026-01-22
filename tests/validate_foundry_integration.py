#!/usr/bin/env python3
"""
Validation script for Azure Foundry Agent Service integration.

This script validates that all components of the Foundry Agent Service
integration are properly configured and can be imported correctly.
"""

import sys
import os

def test_imports():
    """Test that all new modules can be imported."""
    print("=" * 60)
    print("Testing Imports")
    print("=" * 60)
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        # Test Foundry Agent Service module
        print("\n1. Testing Foundry Agent Service module...")
        from AgentOperatingSystem.ml.foundry_agent_service import (
            FoundryAgentServiceClient,
            FoundryAgentServiceConfig,
            FoundryResponse,
            ThreadInfo
        )
        print("   ✓ FoundryAgentServiceClient")
        print("   ✓ FoundryAgentServiceConfig")
        print("   ✓ FoundryResponse")
        print("   ✓ ThreadInfo")
        
        # Test ModelType update
        print("\n2. Testing ModelType enum...")
        from AgentOperatingSystem.orchestration.model_orchestration import ModelType
        assert hasattr(ModelType, 'FOUNDRY_AGENT_SERVICE'), "FOUNDRY_AGENT_SERVICE not in ModelType"
        print(f"   ✓ ModelType.FOUNDRY_AGENT_SERVICE = '{ModelType.FOUNDRY_AGENT_SERVICE.value}'")
        
        # Test MLConfig update
        print("\n3. Testing MLConfig...")
        from AgentOperatingSystem.config.ml import MLConfig
        config = MLConfig()
        assert hasattr(config, 'enable_foundry_agent_service'), "enable_foundry_agent_service not in MLConfig"
        assert hasattr(config, 'foundry_model'), "foundry_model not in MLConfig"
        print(f"   ✓ enable_foundry_agent_service = {config.enable_foundry_agent_service}")
        print(f"   ✓ foundry_model = {config.foundry_model}")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration from environment variables."""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from AgentOperatingSystem.ml.foundry_agent_service import FoundryAgentServiceConfig
        
        # Test default configuration
        print("\n1. Testing default configuration...")
        config = FoundryAgentServiceConfig()
        print(f"   ✓ Model: {config.model}")
        print(f"   ✓ Stateful Threads: {config.enable_stateful_threads}")
        print(f"   ✓ Entra Agent ID: {config.enable_entra_agent_id}")
        print(f"   ✓ Foundry Tools: {config.enable_foundry_tools}")
        print(f"   ✓ Temperature: {config.temperature}")
        print(f"   ✓ Max Tokens: {config.max_tokens}")
        
        # Test from_env
        print("\n2. Testing configuration from environment...")
        config_env = FoundryAgentServiceConfig.from_env()
        print(f"   ✓ Configuration loaded from environment")
        
        print("\n✅ Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_creation():
    """Test client creation and basic functionality."""
    print("\n" + "=" * 60)
    print("Testing Client Creation")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from AgentOperatingSystem.ml.foundry_agent_service import (
            FoundryAgentServiceClient,
            FoundryAgentServiceConfig
        )
        
        # Create client
        print("\n1. Creating Foundry Agent Service client...")
        config = FoundryAgentServiceConfig(
            endpoint_url="https://test-endpoint.azure.com",
            api_key="test-api-key",
            agent_id="test-agent",
            model="llama-3.3-70b"
        )
        client = FoundryAgentServiceClient(config)
        print("   ✓ Client created successfully")
        
        # Test client attributes
        print("\n2. Validating client attributes...")
        assert client.config.model == "llama-3.3-70b", "Model mismatch"
        assert client.config.endpoint_url == "https://test-endpoint.azure.com", "Endpoint mismatch"
        print("   ✓ All attributes correct")
        
        # Test metrics
        print("\n3. Testing metrics...")
        metrics = client.get_metrics()
        assert "total_requests" in metrics, "total_requests missing from metrics"
        assert "successful_requests" in metrics, "successful_requests missing"
        print("   ✓ Metrics structure valid")
        
        print("\n✅ Client creation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Client creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_orchestrator_integration():
    """Test integration with ModelOrchestrator."""
    print("\n" + "=" * 60)
    print("Testing Model Orchestrator Integration")
    print("=" * 60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from AgentOperatingSystem.orchestration.model_orchestration import ModelType
        
        print("\n1. Checking FOUNDRY_AGENT_SERVICE in ModelType...")
        assert hasattr(ModelType, 'FOUNDRY_AGENT_SERVICE'), "FOUNDRY_AGENT_SERVICE not found"
        print(f"   ✓ ModelType.FOUNDRY_AGENT_SERVICE exists")
        
        print("\n2. Validating model type value...")
        assert ModelType.FOUNDRY_AGENT_SERVICE.value == "foundry_agent_service"
        print(f"   ✓ Value is 'foundry_agent_service'")
        
        print("\n✅ Model Orchestrator integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model Orchestrator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_syntax():
    """Test that all new files have valid syntax."""
    print("\n" + "=" * 60)
    print("Testing File Syntax")
    print("=" * 60)
    
    base_path = os.path.join(os.path.dirname(__file__), '..')
    
    files_to_check = [
        'src/AgentOperatingSystem/ml/foundry_agent_service.py',
        'src/AgentOperatingSystem/orchestration/model_orchestration.py',
        'src/AgentOperatingSystem/config/ml.py',
        'examples/foundry_agent_service_example.py',
        'tests/test_foundry_agent_service.py'
    ]
    
    all_valid = True
    for file_path in files_to_check:
        full_path = os.path.join(base_path, file_path)
        print(f"\nChecking {file_path}...")
        
        try:
            with open(full_path, 'r') as f:
                code = compile(f.read(), file_path, 'exec')
            print(f"   ✓ Syntax valid")
        except SyntaxError as e:
            print(f"   ❌ Syntax error: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"   ❌ File not found")
            all_valid = False
    
    if all_valid:
        print("\n✅ All files have valid syntax!")
    else:
        print("\n❌ Some files have syntax errors!")
    
    return all_valid


def main():
    """Run all validation tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  Azure Foundry Agent Service Integration Validation    ║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("File Syntax", test_file_syntax()))
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    results.append(("Client Creation", test_client_creation()))
    results.append(("Model Orchestrator", test_model_orchestrator_integration()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print()
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All validation tests passed!")
        print("\nNext steps:")
        print("1. Set environment variables:")
        print("   - FOUNDRY_AGENT_SERVICE_ENDPOINT")
        print("   - FOUNDRY_AGENT_SERVICE_API_KEY")
        print("   - FOUNDRY_AGENT_ID (optional)")
        print("\n2. Run the example:")
        print("   python examples/foundry_agent_service_example.py")
        print("\n3. Run the tests:")
        print("   pytest tests/test_foundry_agent_service.py")
        print()
        return 0
    else:
        print("\n❌ Some validation tests failed!")
        print("Please review the errors above and fix any issues.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
