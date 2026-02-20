"""
What-If Planner

Analyzes deployment changes and assesses risks using Azure's what-if API.
"""

import subprocess
import json
import re
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from enum import Enum


class ChangeType(Enum):
    """Types of resource changes."""
    CREATE = "Create"
    MODIFY = "Modify"
    DELETE = "Delete"
    DEPLOY = "Deploy"
    NO_CHANGE = "NoChange"
    IGNORE = "Ignore"


class WhatIfChange:
    """Represents a single resource change."""
    
    def __init__(self, resource_type: str, resource_name: str, 
                 change_type: ChangeType, details: Optional[Dict[str, Any]] = None):
        """
        Initialize what-if change.
        
        Args:
            resource_type: Type of Azure resource
            resource_name: Name/ID of the resource
            change_type: Type of change
            details: Additional change details
        """
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.change_type = change_type
        self.details = details or {}
    
    def is_destructive(self) -> bool:
        """Check if this change is destructive."""
        return self.change_type == ChangeType.DELETE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "change_type": self.change_type.value,
            "is_destructive": self.is_destructive(),
            "details": self.details
        }


class WhatIfResult:
    """Result of a what-if analysis."""
    
    def __init__(self, changes: List[WhatIfChange], raw_output: str):
        """
        Initialize what-if result.
        
        Args:
            changes: List of detected changes
            raw_output: Raw CLI output
        """
        self.changes = changes
        self.raw_output = raw_output
    
    def get_destructive_changes(self) -> List[WhatIfChange]:
        """Get all destructive changes."""
        return [c for c in self.changes if c.is_destructive()]
    
    def has_destructive_changes(self) -> bool:
        """Check if there are any destructive changes."""
        return len(self.get_destructive_changes()) > 0
    
    def get_changes_by_type(self, change_type: ChangeType) -> List[WhatIfChange]:
        """Get changes filtered by type."""
        return [c for c in self.changes if c.change_type == change_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_changes": len(self.changes),
            "destructive_changes": len(self.get_destructive_changes()),
            "changes": [c.to_dict() for c in self.changes],
            "changes_by_type": {
                "create": len(self.get_changes_by_type(ChangeType.CREATE)),
                "modify": len(self.get_changes_by_type(ChangeType.MODIFY)),
                "delete": len(self.get_changes_by_type(ChangeType.DELETE)),
            }
        }


class WhatIfPlanner:
    """
    What-if deployment planner.
    
    Analyzes planned changes before deployment to assess risk and identify
    destructive operations.
    """
    
    def __init__(self):
        """Initialize planner."""
        pass
    
    def analyze(self, resource_group: str, template_file: Path, 
                parameters_file: Optional[Path] = None,
                location: Optional[str] = None,
                parameter_overrides: Optional[Dict[str, Any]] = None) -> WhatIfResult:
        """
        Perform what-if analysis on a deployment.
        
        Args:
            resource_group: Target resource group name
            template_file: Path to Bicep template
            parameters_file: Optional path to parameters file
            location: Required if resource group doesn't exist
            parameter_overrides: Optional dict of parameter key/value overrides
            
        Returns:
            WhatIfResult containing analysis
        """
        if not template_file.exists():
            return WhatIfResult([], f"Template file not found: {template_file}")
        
        try:
            # Build command
            cmd = [
                "az", "deployment", "group", "what-if",
                "--resource-group", resource_group,
                "--template-file", str(template_file),
                "--no-prompt"
            ]
            
            # Add parameters if provided
            if parameters_file and parameters_file.exists():
                cmd.extend(["--parameters", str(parameters_file)])
            
            # Add parameter overrides
            if parameter_overrides:
                for key, value in parameter_overrides.items():
                    cmd.extend(["--parameters", f"{key}={value}"])
            
            # Add location if provided (needed for new resource groups)
            if location:
                cmd.extend(["--location", location])
            
            # Execute what-if
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for what-if
            )
            
            # Parse the output
            changes = self._parse_what_if_output(result.stdout)
            
            return WhatIfResult(changes, result.stdout)
        
        except subprocess.TimeoutExpired:
            return WhatIfResult([], "What-if analysis timed out after 5 minutes")
        except FileNotFoundError:
            return WhatIfResult([], "Azure CLI (az) not found. Please install Azure CLI.")
        except Exception as e:
            return WhatIfResult([], f"Unexpected error during what-if analysis: {str(e)}")
    
    def _parse_what_if_output(self, output: str) -> List[WhatIfChange]:
        """
        Parse what-if output to extract changes.
        
        Args:
            output: Raw what-if output
            
        Returns:
            List of WhatIfChange objects
        """
        changes = []
        
        # Parse the output line by line
        lines = output.split('\n')
        current_change_type = None
        
        for line in lines:
            line = line.strip()
            
            # Detect change type sections
            if "Resource and property changes are indicated with this symbol:" in line:
                continue
            
            # Match change type indicators
            if re.match(r'^\+\s+Create', line):
                current_change_type = ChangeType.CREATE
            elif re.match(r'~\s+Modify', line):
                current_change_type = ChangeType.MODIFY
            elif re.match(r'-\s+Delete', line):
                current_change_type = ChangeType.DELETE
            elif re.match(r'!\s+Deploy', line):
                current_change_type = ChangeType.DEPLOY
            elif re.match(r'\*\s+Ignore', line):
                current_change_type = ChangeType.IGNORE
            
            # Match resource lines: typically in format [Symbol] ResourceType/ResourceName
            resource_match = re.match(r'^[+~\-!\*]\s+(\S+/\S+|\S+)\s*', line)
            if resource_match and current_change_type:
                resource_full = resource_match.group(1)
                
                # Split into type and name
                if '/' in resource_full:
                    parts = resource_full.rsplit('/', 1)
                    resource_type = parts[0] if len(parts) > 0 else "Unknown"
                    resource_name = parts[1] if len(parts) > 1 else resource_full
                else:
                    resource_type = "Unknown"
                    resource_name = resource_full
                
                changes.append(WhatIfChange(
                    resource_type=resource_type,
                    resource_name=resource_name,
                    change_type=current_change_type
                ))
        
        return changes
    
    def format_results(self, result: WhatIfResult) -> str:
        """
        Format what-if results for display.
        
        Args:
            result: WhatIfResult to format
            
        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("WHAT-IF ANALYSIS RESULTS")
        lines.append("=" * 60)
        
        if not result.changes:
            lines.append("\n✅ No changes detected")
            return "\n".join(lines)
        
        # Summary
        lines.append(f"\nTotal changes: {len(result.changes)}")
        
        # Group by change type
        creates = result.get_changes_by_type(ChangeType.CREATE)
        modifies = result.get_changes_by_type(ChangeType.MODIFY)
        deletes = result.get_changes_by_type(ChangeType.DELETE)
        
        if creates:
            lines.append(f"\n➕ CREATE ({len(creates)}):")
            for change in creates:
                lines.append(f"   - {change.resource_type}/{change.resource_name}")
        
        if modifies:
            lines.append(f"\n🔄 MODIFY ({len(modifies)}):")
            for change in modifies:
                lines.append(f"   - {change.resource_type}/{change.resource_name}")
        
        if deletes:
            lines.append(f"\n❌ DELETE ({len(deletes)}) - DESTRUCTIVE:")
            for change in deletes:
                lines.append(f"   - {change.resource_type}/{change.resource_name}")
            lines.append("\n⚠️  WARNING: Destructive changes detected!")
            lines.append("   These operations will DELETE resources and may cause data loss.")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
