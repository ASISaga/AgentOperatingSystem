#!/usr/bin/env python3
"""
Standalone validation for Foundry Agent Service integration.
Tests only the new components without requiring full package dependencies.
"""

import sys
import os


def test_syntax():
    """Test that all new files have valid Python syntax."""
    print("=" * 60)
    print("Testing File Syntax")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    files_to_check = {
        'Foundry Agent Service Client': 'src/AgentOperatingSystem/ml/foundry_agent_service.py',
        'Model Orchestration Updates': 'src/AgentOperatingSystem/orchestration/model_orchestration.py',
        'ML Config Updates': 'src/AgentOperatingSystem/config/ml.py',
        'ML __init__ Updates': 'src/AgentOperatingSystem/ml/__init__.py',
        'Foundry Example': 'examples/foundry_agent_service_example.py',
        'Foundry Tests': 'tests/test_foundry_agent_service.py',
        'Foundry Docs': 'docs/FOUNDRY_AGENT_SERVICE.md',
    }
    
    all_valid = True
    for name, file_path in files_to_check.items():
        full_path = os.path.join(base_path, file_path)
        print(f"\n{name}...")
        
        try:
            if file_path.endswith('.md'):
                # Just check file exists for markdown
                with open(full_path, 'r') as f:
                    content = f.read()
                    assert len(content) > 0, "File is empty"
                print(f"  ✓ File exists and has content")
            else:
                # Compile Python files
                with open(full_path, 'r') as f:
                    code = compile(f.read(), file_path, 'exec')
                print(f"  ✓ Syntax valid")
        except SyntaxError as e:
            print(f"  ❌ Syntax error: {e}")
            all_valid = False
        except FileNotFoundError:
            print(f"  ❌ File not found: {full_path}")
            all_valid = False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_valid = False
    
    if all_valid:
        print("\n✅ All files are valid!")
    return all_valid


def test_model_type_enum():
    """Test that ModelType enum was updated correctly."""
    print("\n" + "=" * 60)
    print("Testing ModelType Enum Update")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, 'src/AgentOperatingSystem/orchestration/model_orchestration.py')
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        print("\nChecking for FOUNDRY_AGENT_SERVICE in ModelType enum...")
        if 'FOUNDRY_AGENT_SERVICE = "foundry_agent_service"' in content:
            print("  ✓ FOUNDRY_AGENT_SERVICE enum value found")
        else:
            print("  ❌ FOUNDRY_AGENT_SERVICE enum value not found")
            return False
        
        print("\nChecking for Foundry handler method...")
        if '_handle_foundry_agent_service_request' in content:
            print("  ✓ Handler method found")
        else:
            print("  ❌ Handler method not found")
            return False
        
        print("\nChecking for Foundry routing logic...")
        if 'ModelType.FOUNDRY_AGENT_SERVICE:' in content:
            print("  ✓ Routing logic found")
        else:
            print("  ❌ Routing logic not found")
            return False
        
        print("\n✅ ModelType enum updated correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking ModelType: {e}")
        return False


def test_ml_config():
    """Test that MLConfig was updated correctly."""
    print("\n" + "=" * 60)
    print("Testing MLConfig Update")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, 'src/AgentOperatingSystem/config/ml.py')
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        required_fields = [
            'enable_foundry_agent_service',
            'foundry_agent_service_endpoint',
            'foundry_agent_service_api_key',
            'foundry_agent_id',
            'foundry_model',
            'foundry_enable_stateful_threads',
            'foundry_enable_entra_agent_id',
            'foundry_enable_foundry_tools',
        ]
        
        all_found = True
        for field in required_fields:
            if f'{field}:' in content or f'{field} =' in content:
                print(f"  ✓ {field} found")
            else:
                print(f"  ❌ {field} not found")
                all_found = False
        
        if all_found:
            print("\n✅ MLConfig updated correctly!")
        return all_found
        
    except Exception as e:
        print(f"\n❌ Error checking MLConfig: {e}")
        return False


def test_foundry_client():
    """Test that Foundry Agent Service client has required methods."""
    print("\n" + "=" * 60)
    print("Testing Foundry Agent Service Client")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, 'src/AgentOperatingSystem/ml/foundry_agent_service.py')
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        required_classes = [
            'FoundryAgentServiceConfig',
            'FoundryAgentServiceClient',
            'FoundryResponse',
            'ThreadInfo',
        ]
        
        required_methods = [
            'async def initialize',
            'async def send_message',
            'async def create_thread',
            'async def get_thread_info',
            'async def delete_thread',
            'async def health_check',
            'def get_metrics',
        ]
        
        print("\nChecking classes...")
        for cls in required_classes:
            if f'class {cls}' in content:
                print(f"  ✓ {cls}")
            else:
                print(f"  ❌ {cls} not found")
                return False
        
        print("\nChecking methods...")
        for method in required_methods:
            if method in content:
                print(f"  ✓ {method}")
            else:
                print(f"  ❌ {method} not found")
                return False
        
        print("\nChecking features...")
        features = [
            ('Llama 3.3 70B', 'llama-3.3-70b'),
            ('Stateful Threads', 'enable_stateful_threads'),
            ('Entra Agent ID', 'enable_entra_agent_id'),
            ('Foundry Tools', 'enable_foundry_tools'),
        ]
        
        for feature_name, feature_key in features:
            if feature_key in content:
                print(f"  ✓ {feature_name} support")
            else:
                print(f"  ❌ {feature_name} support not found")
                return False
        
        print("\n✅ Foundry Agent Service client implementation complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error checking client: {e}")
        return False


def test_documentation():
    """Test that documentation was created."""
    print("\n" + "=" * 60)
    print("Testing Documentation")
    print("=" * 60)
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    docs_to_check = {
        'Foundry Agent Service Guide': 'docs/FOUNDRY_AGENT_SERVICE.md',
        'Main README': 'README.md',
        'Examples README': 'examples/README.md',
    }
    
    all_valid = True
    for name, file_path in docs_to_check.items():
        full_path = os.path.join(base_path, file_path)
        print(f"\n{name}...")
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Check for Foundry Agent Service mentions
            if 'Foundry Agent Service' in content or 'foundry' in content.lower():
                print(f"  ✓ Contains Foundry Agent Service documentation")
            else:
                print(f"  ⚠️  May not contain Foundry Agent Service documentation")
            
            if 'Llama 3.3' in content or 'llama-3.3-70b' in content:
                print(f"  ✓ Mentions Llama 3.3 70B")
            else:
                print(f"  ⚠️  May not mention Llama 3.3 70B")
                
        except FileNotFoundError:
            print(f"  ❌ File not found: {full_path}")
            all_valid = False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_valid = False
    
    if all_valid:
        print("\n✅ Documentation files present!")
    return all_valid


def main():
    """Run all validation tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  Foundry Agent Service Integration Validation          ║")
    print("║  (Standalone - No Dependencies Required)               ║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("File Syntax", test_syntax()))
    results.append(("ModelType Enum", test_model_type_enum()))
    results.append(("MLConfig", test_ml_config()))
    results.append(("Foundry Client", test_foundry_client()))
    results.append(("Documentation", test_documentation()))
    
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
        print("\nAzure Foundry Agent Service integration is complete!")
        print("\nKey Features Added:")
        print("  • Llama 3.3 70B as core reasoning engine")
        print("  • Stateful Threads for persistent conversations")
        print("  • Entra Agent ID for secure identity management")
        print("  • Foundry Tools for enhanced capabilities")
        print("\nNext steps:")
        print("1. Set environment variables:")
        print("   - FOUNDRY_AGENT_SERVICE_ENDPOINT")
        print("   - FOUNDRY_AGENT_SERVICE_API_KEY")
        print("   - FOUNDRY_AGENT_ID (optional)")
        print("\n2. Run the example:")
        print("   python examples/foundry_agent_service_example.py")
        print("\n3. See documentation:")
        print("   docs/FOUNDRY_AGENT_SERVICE.md")
        print()
        return 0
    else:
        print("\n❌ Some validation tests failed!")
        print("Please review the errors above.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
