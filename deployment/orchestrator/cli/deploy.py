"""
Command-Line Interface for Bicep Orchestrator

Provides a CLI for executing deployments with the orchestrator.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import subprocess

from ..core.orchestrator import BicepOrchestrator, DeploymentConfig


def get_git_sha() -> Optional[str]:
    """Get current Git SHA if in a Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Azure Bicep Deployment Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic deployment
  %(prog)s -g my-rg -l eastus -t main.bicep
  
  # With parameters file
  %(prog)s -g my-rg -l eastus -t main.bicep -p dev.bicepparam
  
  # Allow warnings and skip health checks
  %(prog)s -g my-rg -l eastus -t main.bicep --allow-warnings --skip-health
  
  # Parameter overrides
  %(prog)s -g my-rg -l eastus -t main.bicep --param environment=prod --param instanceCount=3
  
  # No confirmation for deletes (use with caution!)
  %(prog)s -g my-rg -l eastus -t main.bicep --no-confirm-deletes
        """
    )
    
    # Required arguments
    parser.add_argument(
        "-g", "--resource-group",
        required=True,
        help="Azure resource group name"
    )
    
    parser.add_argument(
        "-l", "--location",
        required=True,
        help="Azure region (e.g., eastus, westeurope)"
    )
    
    parser.add_argument(
        "-t", "--template",
        required=True,
        type=Path,
        help="Path to Bicep template file"
    )
    
    # Optional arguments
    parser.add_argument(
        "-p", "--parameters",
        type=Path,
        help="Path to parameters file (.bicepparam or .json)"
    )
    
    parser.add_argument(
        "--param",
        action="append",
        dest="parameter_overrides",
        metavar="KEY=VALUE",
        help="Override a parameter (can be used multiple times)"
    )
    
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="Allow deployment despite linter warnings"
    )
    
    parser.add_argument(
        "--no-confirm-deletes",
        action="store_true",
        help="Skip confirmation for destructive changes (DANGEROUS!)"
    )
    
    parser.add_argument(
        "--skip-health",
        action="store_true",
        help="Skip post-deployment health checks"
    )
    
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=Path("./audit"),
        help="Directory for audit logs (default: ./audit)"
    )
    
    parser.add_argument(
        "--git-sha",
        help="Git commit SHA for audit trail (auto-detected if not provided)"
    )
    
    args = parser.parse_args()
    
    # Create deployment configuration
    config = DeploymentConfig(
        resource_group=args.resource_group,
        location=args.location,
        template_file=args.template,
        parameters_file=args.parameters,
        allow_warnings=args.allow_warnings,
        require_confirmation_for_deletes=not args.no_confirm_deletes,
        skip_health_checks=args.skip_health,
        audit_dir=args.audit_dir
    )
    
    # Add parameter overrides
    if args.parameter_overrides:
        for override in args.parameter_overrides:
            if "=" not in override:
                print(f"❌ Invalid parameter override format: {override}")
                print("   Expected format: KEY=VALUE")
                sys.exit(1)
            
            key, value = override.split("=", 1)
            config.add_parameter_override(key.strip(), value.strip())
    
    # Get Git SHA
    git_sha = args.git_sha or get_git_sha()
    if git_sha:
        print(f"📝 Git SHA: {git_sha}")
    
    # Display configuration
    print("=" * 60)
    print("DEPLOYMENT CONFIGURATION")
    print("=" * 60)
    print(f"Resource Group: {config.resource_group}")
    print(f"Location: {config.location}")
    print(f"Template: {config.template_file}")
    print(f"Parameters: {config.parameters_file or 'None'}")
    print(f"Allow Warnings: {config.allow_warnings}")
    print(f"Require Confirmation: {config.require_confirmation_for_deletes}")
    print(f"Skip Health Checks: {config.skip_health_checks}")
    print(f"Audit Directory: {config.audit_dir}")
    
    if config.parameter_overrides:
        print("\nParameter Overrides:")
        for key, value in config.parameter_overrides.items():
            print(f"  {key} = {value}")
    
    print("=" * 60)
    print()
    
    # Create and run orchestrator
    orchestrator = BicepOrchestrator(config, git_sha)
    
    print("🚀 Starting deployment...")
    print()
    
    success, message = orchestrator.deploy()
    
    print()
    print("=" * 60)
    if success:
        print("✅ DEPLOYMENT SUCCESSFUL")
        print("=" * 60)
        print(message)
        sys.exit(0)
    else:
        print("❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print(message)
        sys.exit(1)


if __name__ == "__main__":
    main()
