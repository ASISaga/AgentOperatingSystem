"""
Simple validation script for CMOAgent and LeadershipAgent

This script validates the basic structure and inheritance without
requiring full initialization of the AOS system.
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/AgentOperatingSystem/agents'))

# Import base classes by reading the files directly
def validate_file_syntax(filepath):
    """Validate Python syntax of a file"""
    with open(filepath, 'r') as f:
        code = f.read()
    try:
        compile(code, filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}")
        return False

def check_inheritance(filepath, class_name, expected_parent):
    """Check if a class inherits from expected parent"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Simple regex to check class definition
    import re
    pattern = rf'class\s+{class_name}\s*\(\s*{expected_parent}\s*\)'
    if re.search(pattern, content):
        return True
    return False

def check_purpose_adapter_mapping(filepath):
    """Check if file has purpose-adapter mapping"""
    with open(filepath, 'r') as f:
        content = f.read()
    return 'purpose_adapter_mapping' in content

def main():
    print("=" * 80)
    print("VALIDATING AGENT HIERARCHY AND PURPOSE-ADAPTER MAPPING")
    print("=" * 80)
    print()
    
    base_dir = os.path.join(os.path.dirname(__file__), '../src/AgentOperatingSystem/agents')
    
    # Test 1: Validate file syntax
    print("Test 1: Validating Python syntax...")
    leadership_file = os.path.join(base_dir, 'leadership_agent.py')
    cmo_file = os.path.join(base_dir, 'cmo_agent.py')
    
    assert validate_file_syntax(leadership_file), "❌ leadership_agent.py has syntax errors"
    print("  ✅ leadership_agent.py syntax is valid")
    
    assert validate_file_syntax(cmo_file), "❌ cmo_agent.py has syntax errors"
    print("  ✅ cmo_agent.py syntax is valid")
    print()
    
    # Test 2: Check LeadershipAgent inheritance
    print("Test 2: Checking LeadershipAgent inheritance...")
    assert check_inheritance(leadership_file, 'LeadershipAgent', 'PurposeDrivenAgent'), \
        "❌ LeadershipAgent doesn't inherit from PurposeDrivenAgent"
    print("  ✅ LeadershipAgent inherits from PurposeDrivenAgent")
    print()
    
    # Test 3: Check CMOAgent inheritance
    print("Test 3: Checking CMOAgent inheritance...")
    assert check_inheritance(cmo_file, 'CMOAgent', 'LeadershipAgent'), \
        "❌ CMOAgent doesn't inherit from LeadershipAgent"
    print("  ✅ CMOAgent inherits from LeadershipAgent")
    print()
    
    # Test 4: Check purpose-adapter mapping in CMOAgent
    print("Test 4: Checking purpose-adapter mapping...")
    assert check_purpose_adapter_mapping(cmo_file), \
        "❌ CMOAgent doesn't have purpose_adapter_mapping"
    print("  ✅ CMOAgent has purpose_adapter_mapping")
    print()
    
    # Test 5: Check for dual purposes
    print("Test 5: Checking dual purposes in CMOAgent...")
    with open(cmo_file, 'r') as f:
        content = f.read()
    assert 'marketing_purpose' in content, "❌ CMOAgent missing marketing_purpose"
    assert 'leadership_purpose' in content, "❌ CMOAgent missing leadership_purpose"
    assert 'marketing_adapter_name' in content, "❌ CMOAgent missing marketing_adapter_name"
    assert 'leadership_adapter_name' in content, "❌ CMOAgent missing leadership_adapter_name"
    print("  ✅ CMOAgent has marketing_purpose and marketing_adapter_name")
    print("  ✅ CMOAgent has leadership_purpose and leadership_adapter_name")
    print()
    
    # Test 6: Check exports in __init__.py
    print("Test 6: Checking exports...")
    init_file = os.path.join(base_dir, '__init__.py')
    with open(init_file, 'r') as f:
        content = f.read()
    assert 'from .cmo_agent import CMOAgent' in content, "❌ CMOAgent not exported in __init__.py"
    
    # Check if CMOAgent is in __all__
    if '__all__ = [' in content:
        all_section = content.split('__all__ = [')
        if len(all_section) > 1:
            assert 'CMOAgent' in all_section[1], "❌ CMOAgent not in __all__"
    
    print("  ✅ CMOAgent is properly exported")
    print()
    
    # Test 7: Check documentation in .github/instructions
    print("Test 7: Checking documentation...")
    
    # Check Readme.md
    readme_file = os.path.join(os.path.dirname(__file__), '../.github/instructions/Readme.md')
    with open(readme_file, 'r') as f:
        content = f.read()
    assert 'CMOAgent' in content, "❌ CMOAgent not documented in .github/instructions/Readme.md"
    assert 'LeadershipAgent' in content, "❌ LeadershipAgent not documented in Readme.md"
    print("  ✅ CMOAgent and LeadershipAgent documented in Readme.md")
    
    # Check agents.instructions.md
    agents_file = os.path.join(os.path.dirname(__file__), '../.github/instructions/agents.instructions.md')
    with open(agents_file, 'r') as f:
        content = f.read()
    assert 'CMOAgent' in content, "❌ CMOAgent not documented in agents.instructions.md"
    # Check for purpose-adapter or purpose to adapter mapping
    purpose_adapter_found = (
        'purpose-adapter' in content.lower() or 
        'purpose adapter' in content.lower() or
        'purpose to adapter' in content.lower() or
        'purposes to lora adapters' in content.lower()
    )
    assert purpose_adapter_found, \
        "❌ Purpose-adapter mapping not documented in agents.instructions.md"
    assert 'LeadershipAgent' in content, "❌ LeadershipAgent not documented in agents.instructions.md"
    assert 'LoRA' in content, "❌ LoRA adapter information not documented"
    print("  ✅ Purpose-adapter mapping documented in agents.instructions.md")
    print("  ✅ LoRA adapter architecture documented")
    print()
    
    print("=" * 80)
    print("✅ ALL VALIDATION TESTS PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print("  • LeadershipAgent inherits from PurposeDrivenAgent")
    print("  • CMOAgent inherits from LeadershipAgent")
    print("  • CMOAgent has dual purposes: Marketing and Leadership")
    print("  • Each purpose is mapped to its respective LoRA adapter")
    print("  • Documentation updated in .github/instructions")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
