#!/usr/bin/env python3
"""
Minimal test for YAML loading - tests just the from_yaml methods directly
"""

import sys
import os
from pathlib import Path
import yaml

def test_yaml_parsing():
    """Test that YAML files are valid and parseable"""
    print("Testing YAML file parsing...\n")
    
    yaml_files = [
        "config/agents/ceo_agent.yaml",
        "config/agents/leadership_agent.yaml",
        "config/agents/cmo_agent.yaml"
    ]
    
    for yaml_file in yaml_files:
        print(f"Testing {yaml_file}...")
        if not Path(yaml_file).exists():
            print(f"  ✗ File not found")
            return False
        
        try:
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate structure
            if not config.get("agent_id"):
                print(f"  ✗ Missing agent_id")
                return False
            
            if not config.get("purposes"):
                print(f"  ✗ Missing purposes")
                return False
            
            print(f"  ✓ Valid YAML")
            print(f"    - Agent ID: {config['agent_id']}")
            print(f"    - Purposes: {len(config['purposes'])}")
            
            # Validate purpose structure
            for i, purpose in enumerate(config['purposes']):
                if not purpose.get("name"):
                    print(f"    ✗ Purpose {i} missing name")
                    return False
                if not purpose.get("description"):
                    print(f"    ✗ Purpose {i} missing description")
                    return False
                if not purpose.get("adapter_name"):
                    print(f"    ✗ Purpose {i} missing adapter_name")
                    return False
                print(f"    - Purpose '{purpose['name']}' → Adapter '{purpose['adapter_name']}'")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "="*60)
    print("All YAML files are valid! ✓")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_yaml_parsing()
    sys.exit(0 if success else 1)
