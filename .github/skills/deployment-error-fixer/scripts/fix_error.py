#!/usr/bin/env python3
"""
Autonomous Deployment Error Fixer

Analyzes deployment errors and autonomously fixes common logic errors in
Python and Bicep code.
"""

import sys
import re
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import json


class ErrorType:
    """Error type constants."""
    BICEP_VALIDATION = "bicep_validation"
    BICEP_SYNTAX = "bicep_syntax"
    PYTHON_SYNTAX = "python_syntax"
    PYTHON_IMPORT = "python_import"
    PARAMETER_VALIDATION = "parameter_validation"
    UNKNOWN = "unknown"


class DeploymentErrorFixer:
    """Autonomous deployment error fixer."""
    
    def __init__(self, deployment_dir: str, dry_run: bool = False):
        """
        Initialize error fixer.
        
        Args:
            deployment_dir: Path to deployment directory
            dry_run: If True, only analyze but don't apply fixes
        """
        self.deployment_dir = Path(deployment_dir)
        self.dry_run = dry_run
        self.fixes_applied = []
        
    def analyze_error(self, error_file: str) -> Dict:
        """
        Analyze error from orchestrator output.
        
        Args:
            error_file: Path to error log file
            
        Returns:
            Dict with error analysis
        """
        with open(error_file, 'r', encoding='utf-8') as f:
            error_text = f.read()
        
        result = {
            'error_type': ErrorType.UNKNOWN,
            'error_message': error_text,
            'file_path': None,
            'line_number': None,
            'bcp_code': None,
            'can_auto_fix': False,
            'fix_description': None,
            'risk_level': 'high'
        }
        
        # Detect Bicep errors
        if 'error BCP' in error_text or 'Error BCP' in error_text:
            result['error_type'] = ErrorType.BICEP_VALIDATION
            
            # Extract BCP code
            bcp_match = re.search(r'BCP(\d+)', error_text, re.IGNORECASE)
            if bcp_match:
                result['bcp_code'] = f"BCP{bcp_match.group(1)}"
            
            # Extract file and line
            file_match = re.search(r'File:?\s*([^\s,]+\.bicep)', error_text)
            if file_match:
                result['file_path'] = file_match.group(1)
                
            line_match = re.search(r'[Ll]ine:?\s*(\d+)', error_text)
            if line_match:
                result['line_number'] = int(line_match.group(1))
            
            # Determine if auto-fixable
            auto_fixable_bcps = ['BCP029', 'BCP033', 'BCP037', 'BCP051', 'BCP062', 'BCP068', 'BCP073']
            if result['bcp_code'] in auto_fixable_bcps:
                result['can_auto_fix'] = True
                result['risk_level'] = 'low'
                result['fix_description'] = self._get_bcp_fix_description(result['bcp_code'])
        
        # Detect Python syntax errors
        elif 'SyntaxError' in error_text or 'IndentationError' in error_text:
            result['error_type'] = ErrorType.PYTHON_SYNTAX
            result['can_auto_fix'] = True
            result['risk_level'] = 'low'
            result['fix_description'] = 'Fix Python syntax error'
            
            # Extract file and line
            file_match = re.search(r'File "([^"]+\.py)"', error_text)
            if file_match:
                result['file_path'] = file_match.group(1)
            
            line_match = re.search(r'line (\d+)', error_text)
            if line_match:
                result['line_number'] = int(line_match.group(1))
        
        # Detect Python import errors
        elif 'ImportError' in error_text or 'ModuleNotFoundError' in error_text:
            result['error_type'] = ErrorType.PYTHON_IMPORT
            result['can_auto_fix'] = True
            result['risk_level'] = 'low'
            result['fix_description'] = 'Add missing import'
            
            # Extract module name
            module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_text)
            if module_match:
                result['module_name'] = module_match.group(1)
        
        # Detect parameter validation errors
        elif re.search(r'missing.*parameter|invalid.*parameter', error_text, re.IGNORECASE):
            result['error_type'] = ErrorType.PARAMETER_VALIDATION
            result['can_auto_fix'] = True
            result['risk_level'] = 'medium'
            result['fix_description'] = 'Fix parameter validation'
        
        return result
    
    def _get_bcp_fix_description(self, bcp_code: str) -> str:
        """Get fix description for BCP error code."""
        descriptions = {
            'BCP029': 'Add API version to resource type',
            'BCP033': 'Fix type mismatch in parameter',
            'BCP037': 'Remove invalid property',
            'BCP051': 'Add missing keyword (resource/param/var)',
            'BCP062': 'Correct function name',
            'BCP068': 'Fix resource reference',
            'BCP073': 'Remove read-only property'
        }
        return descriptions.get(bcp_code, 'Fix Bicep error')
    
    def fix_bcp029(self, file_path: str, line_number: int) -> bool:
        """
        Fix BCP029: Missing API version.
        
        Args:
            file_path: Path to Bicep file
            line_number: Line number with error
            
        Returns:
            True if fixed successfully
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number > len(lines):
                return False
            
            # Get the line with error
            error_line = lines[line_number - 1]
            
            # Extract resource type (pattern: 'Microsoft.*/...')
            match = re.search(r"'(Microsoft\.[^'@]+)'", error_line)
            if not match:
                return False
            
            resource_type = match.group(1)
            
            # Use a sensible default API version
            api_version = "2023-01-01"
            
            # Replace in line
            fixed_line = error_line.replace(f"'{resource_type}'", f"'{resource_type}@{api_version}'")
            lines[line_number - 1] = fixed_line
            
            if not self.dry_run:
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.fixes_applied.append({
                    'type': 'BCP029',
                    'file': file_path,
                    'line': line_number,
                    'description': f'Added API version {api_version} to {resource_type}'
                })
            
            return True
        except Exception as e:
            print(f"Error fixing BCP029: {e}", file=sys.stderr)
            return False
    
    def fix_python_syntax(self, file_path: str, line_number: int) -> bool:
        """
        Fix common Python syntax errors.
        
        Args:
            file_path: Path to Python file
            line_number: Line number with error
            
        Returns:
            True if fixed successfully
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number > len(lines):
                return False
            
            error_line = lines[line_number - 1]
            fixed = False
            fix_desc = ''
            
            # Check for missing colon in function definition
            if 'def ' in error_line and not error_line.rstrip().endswith(':'):
                lines[line_number - 1] = error_line.rstrip() + ':\n'
                fixed = True
                fix_desc = 'Added missing colon to function definition'
            
            # Check for indentation issues (convert tabs to spaces)
            elif '\t' in error_line:
                lines[line_number - 1] = error_line.replace('\t', '    ')
                fixed = True
                fix_desc = 'Converted tabs to spaces'
            
            if fixed and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.fixes_applied.append({
                    'type': 'Python Syntax',
                    'file': file_path,
                    'line': line_number,
                    'description': fix_desc
                })
            
            return fixed
        except Exception as e:
            print(f"Error fixing Python syntax: {e}", file=sys.stderr)
            return False
    
    def apply_fix(self, analysis: Dict) -> bool:
        """
        Apply fix based on error analysis.
        
        Args:
            analysis: Error analysis dict
            
        Returns:
            True if fix was applied successfully
        """
        if not analysis['can_auto_fix']:
            return False
        
        error_type = analysis['error_type']
        file_path = analysis.get('file_path')
        line_number = analysis.get('line_number')
        
        # Resolve relative path
        if file_path and not file_path.startswith('/'):
            file_path = str(self.deployment_dir / file_path)
        
        if error_type == ErrorType.BICEP_VALIDATION:
            bcp_code = analysis.get('bcp_code')
            if bcp_code == 'BCP029' and file_path and line_number:
                return self.fix_bcp029(file_path, line_number)
        
        elif error_type == ErrorType.PYTHON_SYNTAX:
            if file_path and line_number:
                return self.fix_python_syntax(file_path, line_number)
        
        return False
    
    def validate_fix(self, analysis: Dict) -> bool:
        """
        Validate that the fix worked.
        
        Args:
            analysis: Error analysis dict
            
        Returns:
            True if validation passes
        """
        error_type = analysis['error_type']
        file_path = analysis.get('file_path')
        
        if not file_path:
            return False
        
        # Resolve relative path
        if not file_path.startswith('/'):
            file_path = str(self.deployment_dir / file_path)
        
        try:
            if error_type in [ErrorType.BICEP_VALIDATION, ErrorType.BICEP_SYNTAX]:
                # Validate Bicep file
                result = subprocess.run(
                    ['az', 'bicep', 'build', '--file', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0
            
            elif error_type in [ErrorType.PYTHON_SYNTAX, ErrorType.PYTHON_IMPORT]:
                # Validate Python file
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.returncode == 0
        
        except Exception as e:
            print(f"Error validating fix: {e}", file=sys.stderr)
            return False
        
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Autonomous deployment error fixer')
    parser.add_argument('--error-file', required=True, help='Path to error log file')
    parser.add_argument('--deployment-dir', default='deployment', help='Path to deployment directory')
    parser.add_argument('--dry-run', action='store_true', help='Analyze only, do not apply fixes')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically apply fixes')
    
    args = parser.parse_args()
    
    fixer = DeploymentErrorFixer(args.deployment_dir, args.dry_run)
    
    print("🔍 Analyzing deployment error...")
    analysis = fixer.analyze_error(args.error_file)
    
    print(f"\n📊 Error Analysis:")
    print(f"  Type: {analysis['error_type']}")
    print(f"  File: {analysis.get('file_path', 'Unknown')}")
    print(f"  Line: {analysis.get('line_number', 'Unknown')}")
    print(f"  BCP Code: {analysis.get('bcp_code', 'N/A')}")
    print(f"  Can Auto-Fix: {'Yes' if analysis['can_auto_fix'] else 'No'}")
    print(f"  Risk Level: {analysis['risk_level']}")
    if analysis['fix_description']:
        print(f"  Fix: {analysis['fix_description']}")
    
    if analysis['can_auto_fix'] and args.auto_fix:
        print(f"\n🔧 Applying fix...")
        
        if fixer.apply_fix(analysis):
            print("✅ Fix applied successfully")
            
            if not args.dry_run:
                print("\n🔍 Validating fix...")
                if fixer.validate_fix(analysis):
                    print("✅ Validation passed")
                    
                    # Output results as JSON for workflow
                    result = {
                        'fixed': True,
                        'validated': True,
                        'fixes': fixer.fixes_applied
                    }
                    print(f"\n{json.dumps(result)}")
                    sys.exit(0)
                else:
                    print("❌ Validation failed")
                    sys.exit(1)
        else:
            print("❌ Failed to apply fix")
            sys.exit(1)
    elif not analysis['can_auto_fix']:
        print("\n⚠️  This error cannot be auto-fixed")
        sys.exit(1)
    else:
        print("\n✅ Analysis complete (dry-run mode)")
        sys.exit(0)


if __name__ == '__main__':
    main()
