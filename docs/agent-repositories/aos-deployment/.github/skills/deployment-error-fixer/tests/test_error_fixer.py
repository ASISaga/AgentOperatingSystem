#!/usr/bin/env python3
"""
Tests for autonomous deployment error fixer.

Tests the error analysis and fixing logic for both Python and Bicep errors.
"""

import sys
import os
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from fix_error import DeploymentErrorFixer, ErrorType


class TestErrorAnalysis(unittest.TestCase):
    """Test error analysis functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.fixer = DeploymentErrorFixer(self.test_dir, dry_run=True)
    
    def test_detect_bicep_bcp029(self):
        """Test detection of BCP029 error."""
        error_text = """
Error BCP029: The resource type is not valid. 
Specify a valid resource type of format '<types>@<apiVersion>'.
File: deployment/modules/storage.bicep
Line: 5
"""
        # Create temp error file
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.BICEP_VALIDATION)
        self.assertEqual(analysis['bcp_code'], 'BCP029')
        self.assertTrue(analysis['can_auto_fix'])
        self.assertEqual(analysis['risk_level'], 'low')
        self.assertIn('storage.bicep', analysis['file_path'])
        self.assertEqual(analysis['line_number'], 5)
    
    def test_detect_bicep_bcp033(self):
        """Test detection of BCP033 error."""
        error_text = """
Error BCP033: Expected a value of type "int" but the provided value is of type "string".
File: deployment/parameters/dev.bicepparam
Line: 10
"""
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.BICEP_VALIDATION)
        self.assertEqual(analysis['bcp_code'], 'BCP033')
        self.assertTrue(analysis['can_auto_fix'])
    
    def test_detect_python_syntax_error(self):
        """Test detection of Python syntax error."""
        error_text = """
  File "deployment/orchestrator/cli/deploy.py", line 42
    def main()
             ^
SyntaxError: invalid syntax
"""
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.PYTHON_SYNTAX)
        self.assertTrue(analysis['can_auto_fix'])
        self.assertEqual(analysis['risk_level'], 'low')
        self.assertIn('deploy.py', analysis['file_path'])
        self.assertEqual(analysis['line_number'], 42)
    
    def test_detect_python_indentation_error(self):
        """Test detection of Python indentation error."""
        error_text = """
  File "deployment/deploy.py", line 15
    return result
         ^
IndentationError: unexpected indent
"""
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.PYTHON_SYNTAX)
        self.assertTrue(analysis['can_auto_fix'])
    
    def test_detect_python_import_error(self):
        """Test detection of Python import error."""
        error_text = """
Traceback (most recent call last):
  File "deployment/orchestrator/cli/deploy.py", line 5, in <module>
    from pathlib import Path
ModuleNotFoundError: No module named 'pathlib'
"""
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.PYTHON_IMPORT)
        self.assertTrue(analysis['can_auto_fix'])
        self.assertEqual(analysis['module_name'], 'pathlib')
    
    def test_detect_parameter_validation_error(self):
        """Test detection of parameter validation error."""
        error_text = """
Error: Missing required parameter 'projectName'
File: deployment/parameters/dev.bicepparam
"""
        error_file = os.path.join(self.test_dir, 'error.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertEqual(analysis['error_type'], ErrorType.PARAMETER_VALIDATION)
        self.assertTrue(analysis['can_auto_fix'])
        self.assertEqual(analysis['risk_level'], 'medium')


class TestBicepErrorFix(unittest.TestCase):
    """Test Bicep error fixing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.fixer = DeploymentErrorFixer(self.test_dir, dry_run=False)
    
    def test_fix_bcp029(self):
        """Test fixing BCP029 error (missing API version)."""
        # Create test Bicep file
        bicep_content = """
resource storage 'Microsoft.Storage/storageAccounts' = {
  name: 'teststorage'
  location: 'eastus'
}
"""
        bicep_file = os.path.join(self.test_dir, 'test.bicep')
        with open(bicep_file, 'w', encoding='utf-8') as f:
            f.write(bicep_content)
        
        # Fix line 2 (resource declaration)
        result = self.fixer.fix_bcp029(bicep_file, 2)
        
        self.assertTrue(result)
        
        # Verify fix was applied
        with open(bicep_file, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        
        self.assertIn('@2023-01-01', fixed_content)
        self.assertIn("Microsoft.Storage/storageAccounts@2023-01-01", fixed_content)
        
        # Verify fix was logged
        self.assertEqual(len(self.fixer.fixes_applied), 1)
        self.assertEqual(self.fixer.fixes_applied[0]['type'], 'BCP029')


class TestPythonErrorFix(unittest.TestCase):
    """Test Python error fixing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.fixer = DeploymentErrorFixer(self.test_dir, dry_run=False)
    
    def test_fix_missing_colon(self):
        """Test fixing missing colon in function definition."""
        # Create test Python file with missing colon
        python_content = """
def main()
    return True
"""
        python_file = os.path.join(self.test_dir, 'test.py')
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        # Fix line 2 (function definition)
        result = self.fixer.fix_python_syntax(python_file, 2)
        
        self.assertTrue(result)
        
        # Verify fix was applied
        with open(python_file, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        
        self.assertIn('def main():', fixed_content)
        
        # Verify fix was logged
        self.assertEqual(len(self.fixer.fixes_applied), 1)
        self.assertEqual(self.fixer.fixes_applied[0]['type'], 'Python Syntax')
    
    def test_fix_indentation_tabs(self):
        """Test fixing indentation (tabs to spaces)."""
        # Create test Python file with tabs
        python_content = "def main():\n\treturn True\n"
        python_file = os.path.join(self.test_dir, 'test.py')
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        # Fix line 2 (indented line)
        result = self.fixer.fix_python_syntax(python_file, 2)
        
        self.assertTrue(result)
        
        # Verify tabs converted to spaces
        with open(python_file, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        
        self.assertNotIn('\t', fixed_content)
        self.assertIn('    return True', fixed_content)


class TestErrorClassification(unittest.TestCase):
    """Test overall error classification logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.fixer = DeploymentErrorFixer(self.test_dir, dry_run=True)
    
    def test_auto_fixable_bicep_errors(self):
        """Test that known BCP errors are classified as auto-fixable."""
        auto_fixable_bcps = ['BCP029', 'BCP033', 'BCP037', 'BCP051', 'BCP062', 'BCP068', 'BCP073']
        
        for bcp_code in auto_fixable_bcps:
            error_text = f"Error {bcp_code}: Some error message\nFile: test.bicep\nLine: 1"
            error_file = os.path.join(self.test_dir, f'{bcp_code}.txt')
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_text)
            
            analysis = self.fixer.analyze_error(error_file)
            
            self.assertTrue(analysis['can_auto_fix'], 
                          f"{bcp_code} should be auto-fixable")
            self.assertEqual(analysis['risk_level'], 'low',
                           f"{bcp_code} should be low risk")
    
    def test_non_auto_fixable_error(self):
        """Test that unknown errors are not auto-fixable."""
        error_text = "Error: Something went wrong but we don't know what"
        error_file = os.path.join(self.test_dir, 'unknown.txt')
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(error_text)
        
        analysis = self.fixer.analyze_error(error_file)
        
        self.assertFalse(analysis['can_auto_fix'])
        self.assertEqual(analysis['error_type'], ErrorType.UNKNOWN)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestErrorAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestBicepErrorFix))
    suite.addTests(loader.loadTestsFromTestCase(TestPythonErrorFix))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorClassification))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
