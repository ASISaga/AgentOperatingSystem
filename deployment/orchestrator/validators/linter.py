"""
Bicep Linter Integration

Validates Bicep templates using Azure CLI bicep lint/build commands.
"""

import subprocess
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path


class LintSeverity:
    """Lint severity levels."""
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"


class LintResult:
    """Result of a lint operation."""
    
    def __init__(self, success: bool, errors: List[Dict[str, Any]], 
                 warnings: List[Dict[str, Any]], output: str):
        """
        Initialize lint result.
        
        Args:
            success: Whether linting passed (no errors)
            errors: List of error messages
            warnings: List of warning messages
            output: Raw output from linter
        """
        self.success = success
        self.errors = errors
        self.warnings = warnings
        self.output = output
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class BicepLinter:
    """
    Bicep template linter using Azure CLI.
    
    Performs static analysis to ensure templates are valid before deployment.
    """
    
    def __init__(self, allow_warnings: bool = True):
        """
        Initialize linter.
        
        Args:
            allow_warnings: Whether to allow warnings (True) or treat as errors (False)
        """
        self.allow_warnings = allow_warnings
    
    def lint_file(self, bicep_file: Path) -> LintResult:
        """
        Lint a Bicep file.
        
        Args:
            bicep_file: Path to the Bicep file
            
        Returns:
            LintResult containing the analysis results
        """
        if not bicep_file.exists():
            return LintResult(
                success=False,
                errors=[{"message": f"File not found: {bicep_file}"}],
                warnings=[],
                output=""
            )
        
        try:
            # Use 'az bicep build' to lint the file
            result = subprocess.run(
                ["az", "bicep", "build", "--file", str(bicep_file), "--stdout"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            errors = []
            warnings = []
            
            # Parse output for errors and warnings
            output_lines = result.stderr.split('\n') if result.stderr else []
            
            for line in output_lines:
                if not line.strip():
                    continue
                
                # Match error patterns
                error_match = re.search(r'Error\s+([A-Z0-9-]+):\s*(.+)', line, re.IGNORECASE)
                if error_match:
                    errors.append({
                        "code": error_match.group(1),
                        "message": error_match.group(2),
                        "severity": LintSeverity.ERROR
                    })
                    continue
                
                # Match warning patterns
                warning_match = re.search(r'Warning\s+([A-Z0-9-]+):\s*(.+)', line, re.IGNORECASE)
                if warning_match:
                    warnings.append({
                        "code": warning_match.group(1),
                        "message": warning_match.group(2),
                        "severity": LintSeverity.WARNING
                    })
            
            # Also check if the command failed
            if result.returncode != 0 and not errors:
                # Parse the entire stderr for any error
                if "error" in result.stderr.lower():
                    errors.append({
                        "code": "LINT_FAILED",
                        "message": result.stderr,
                        "severity": LintSeverity.ERROR
                    })
            
            success = len(errors) == 0 and (self.allow_warnings or len(warnings) == 0)
            
            return LintResult(
                success=success,
                errors=errors,
                warnings=warnings,
                output=result.stderr or result.stdout
            )
        
        except subprocess.TimeoutExpired:
            return LintResult(
                success=False,
                errors=[{"message": "Linting timed out after 60 seconds", "severity": LintSeverity.ERROR}],
                warnings=[],
                output=""
            )
        except FileNotFoundError:
            return LintResult(
                success=False,
                errors=[{"message": "Azure CLI (az) not found. Please install Azure CLI.", 
                        "severity": LintSeverity.ERROR}],
                warnings=[],
                output=""
            )
        except Exception as e:
            return LintResult(
                success=False,
                errors=[{"message": f"Unexpected error during linting: {str(e)}", 
                        "severity": LintSeverity.ERROR}],
                warnings=[],
                output=""
            )
    
    def lint_directory(self, directory: Path, pattern: str = "*.bicep") -> Dict[str, LintResult]:
        """
        Lint all Bicep files in a directory.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            
        Returns:
            Dictionary mapping file paths to lint results
        """
        results = {}
        
        for bicep_file in directory.glob(pattern):
            if bicep_file.is_file():
                results[str(bicep_file)] = self.lint_file(bicep_file)
        
        return results
    
    def format_results(self, results: LintResult) -> str:
        """
        Format lint results for display.
        
        Args:
            results: LintResult to format
            
        Returns:
            Formatted string
        """
        lines = []
        
        if results.has_errors():
            lines.append("❌ ERRORS:")
            for error in results.errors:
                code = error.get("code", "UNKNOWN")
                message = error.get("message", "")
                lines.append(f"  [{code}] {message}")
        
        if results.has_warnings():
            lines.append("⚠️  WARNINGS:")
            for warning in results.warnings:
                code = warning.get("code", "UNKNOWN")
                message = warning.get("message", "")
                lines.append(f"  [{code}] {message}")
        
        if not results.has_errors() and not results.has_warnings():
            lines.append("✅ No issues found")
        
        return "\n".join(lines)
