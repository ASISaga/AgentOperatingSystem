"""
Command-Line Interface for Bicep Orchestrator

Provides a CLI for executing deployments with the orchestrator.
"""

import argparse
import json
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


def _auto_select_location(environment: str, geography: Optional[str] = None) -> dict:
    """
    Auto-select primary and ML regions using the regional tool.

    Returns a dict with 'primary' and 'ml' keys.
    """
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).parent.parent))
    from validators.regional_validator import RegionalValidator, ServiceType

    env_services = {
        'dev': {ServiceType.STORAGE, ServiceType.KEY_VAULT,
                ServiceType.FUNCTIONS_CONSUMPTION, ServiceType.SERVICE_BUS_STANDARD,
                ServiceType.APP_INSIGHTS, ServiceType.LOG_ANALYTICS,
                ServiceType.MANAGED_IDENTITY},
        'staging': {ServiceType.STORAGE, ServiceType.KEY_VAULT,
                    ServiceType.FUNCTIONS_PREMIUM, ServiceType.SERVICE_BUS_STANDARD,
                    ServiceType.APP_INSIGHTS, ServiceType.LOG_ANALYTICS,
                    ServiceType.MANAGED_IDENTITY, ServiceType.AZURE_ML},
        'prod': {ServiceType.STORAGE, ServiceType.KEY_VAULT,
                 ServiceType.FUNCTIONS_PREMIUM, ServiceType.SERVICE_BUS_PREMIUM,
                 ServiceType.APP_INSIGHTS, ServiceType.LOG_ANALYTICS,
                 ServiceType.MANAGED_IDENTITY, ServiceType.AZURE_ML,
                 ServiceType.CONTAINER_REGISTRY},
    }

    services = env_services.get(environment, env_services['dev'])
    validator = RegionalValidator()
    return validator.select_optimal_regions(services, environment=environment,
                                            preferred_geography=geography)


def _ensure_resource_group(resource_group: str, location: str) -> str:
    """
    Create the resource group if it does not already exist.

    If the resource group already exists in a different location, reuses the
    existing location (Azure does not allow moving a resource group).

    Returns the actual location of the resource group (may differ from the
    requested ``location`` when the group pre-exists in another region).
    """
    # Check whether the resource group already exists to avoid a
    # InvalidResourceGroupLocation error when the RG is in a different region.
    try:
        check = subprocess.run(
            ["az", "group", "show", "--name", resource_group,
             "--query", "location", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if check.returncode == 0 and check.stdout.strip():
            existing_location = check.stdout.strip()
            if existing_location != location:
                print(
                    f"  ℹ️  Resource group '{resource_group}' already exists in"
                    f" '{existing_location}' (requested '{location}')"
                    f" – using existing location to avoid InvalidResourceLocation errors.",
                    file=sys.stderr,
                )
            else:
                print(f"  ✅ Resource group '{resource_group}' already exists in '{existing_location}' – matches requested location (skipping creation)")
            return existing_location
    except Exception as exc:
        print(f"  ⚠️  Could not query resource group: {exc}", file=sys.stderr)

    # Resource group does not exist – create it in the requested location.
    try:
        result = subprocess.run(
            [
                "az", "group", "create",
                "--name", resource_group,
                "--location", location,
                "--output", "json",
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            state = data.get("properties", {}).get("provisioningState", "")
            actual_location = data.get("location", location)
            print(f"  Resource group '{resource_group}' is {state} in '{actual_location}'")
            return actual_location
        print(f"  ⚠️  Could not create resource group '{resource_group}': {result.stderr}",
              file=sys.stderr)
        return location
    except Exception as exc:
        print(f"  ⚠️  Resource group creation error: {exc}", file=sys.stderr)
        return location


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Azure Bicep Deployment Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deployment with explicit location
  %(prog)s -g my-rg -l eastus -t main.bicep

  # Deployment with auto-selected regions (recommended)
  %(prog)s -g my-rg -t main.bicep --auto-region --environment dev

  # Explicit ML region when primary lacks Azure ML support
  %(prog)s -g my-rg -l eastasia -t main.bicep --location-ml eastus

  # With parameters file
  %(prog)s -g my-rg -l eastus -t main.bicep -p dev.bicepparam

  # Allow warnings and skip health checks
  %(prog)s -g my-rg -l eastus -t main.bicep --allow-warnings --skip-health

  # Parameter overrides
  %(prog)s -g my-rg -l eastus -t main.bicep --param environment=prod
        """
    )

    # Required arguments
    parser.add_argument(
        "-g", "--resource-group",
        required=True,
        help="Azure resource group name"
    )

    parser.add_argument(
        "-t", "--template",
        required=True,
        type=Path,
        help="Path to Bicep template file"
    )

    # Location arguments – all optional when --auto-region is used
    loc_group = parser.add_mutually_exclusive_group()
    loc_group.add_argument(
        "-l", "--location",
        help="Primary Azure region (e.g., eastus). Omit to auto-select."
    )
    loc_group.add_argument(
        "--auto-region",
        action="store_true",
        help="Automatically select the optimal region for each service"
    )

    parser.add_argument(
        "--location-ml",
        help="Azure region for Azure ML / Container Registry resources. "
             "Defaults to the primary location. Use when Azure ML is unavailable "
             "in the primary region."
    )

    parser.add_argument(
        "--environment",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Target environment used for auto-region selection (default: dev)"
    )

    parser.add_argument(
        "--geography",
        choices=["americas", "europe", "asia"],
        help="Geographic preference for auto-region selection"
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

    # -------------------------------------------------------------------------
    # Resolve locations (auto-select if needed)
    # -------------------------------------------------------------------------
    location = args.location
    location_ml = args.location_ml

    if args.auto_region or not location:
        if not args.auto_region and not location:
            print("ℹ️  No --location provided – auto-selecting optimal regions…")
        else:
            print("🌍 Auto-selecting optimal regions for all services…")

        regions = _auto_select_location(args.environment, args.geography)
        location = location or regions['primary']
        location_ml = location_ml or regions['ml']

        if regions['multi_region']:
            print(f"   ⚠️  Multi-region deployment:")
            print(f"      Core services → {location}")
            print(f"      Azure ML/ACR  → {location_ml}")
        else:
            print(f"   ✅ Single-region deployment: {location}")

    # Default ML location to primary when not specified
    if not location_ml:
        location_ml = location

    # -------------------------------------------------------------------------
    # Ensure resource group exists
    # -------------------------------------------------------------------------
    print(f"\n📂 Ensuring resource group '{args.resource_group}' exists in '{location}'…")
    actual_location = _ensure_resource_group(args.resource_group, location)
    if actual_location != location:
        print(f"ℹ️  Adjusting deployment location from '{location}' to existing"
              f" resource group location '{actual_location}'")
        # Re-align ML location only if it was not explicitly specified by the user
        # and was derived from the original primary location (single-region deployment).
        if not args.location_ml and location_ml == location:
            location_ml = actual_location
        location = actual_location

    # Create a separate ML resource group when deploying to a different region
    ml_resource_group = args.resource_group
    if location_ml != location:
        base = args.resource_group[:-3] if args.resource_group.endswith('-rg') else args.resource_group
        ml_rg_name = base + '-ml-rg'
        print(f"📂 Ensuring ML resource group '{ml_rg_name}' exists in '{location_ml}'…")
        actual_ml_location = _ensure_resource_group(ml_rg_name, location_ml)
        if actual_ml_location != location_ml:
            print(f"ℹ️  Adjusting ML deployment location from '{location_ml}' to existing"
                  f" ML resource group location '{actual_ml_location}'")
            location_ml = actual_ml_location
        ml_resource_group = ml_rg_name

    # -------------------------------------------------------------------------
    # Build deployment configuration
    # -------------------------------------------------------------------------
    config = DeploymentConfig(
        resource_group=args.resource_group,
        location=location,
        template_file=args.template,
        parameters_file=args.parameters,
        allow_warnings=args.allow_warnings,
        require_confirmation_for_deletes=not args.no_confirm_deletes,
        skip_health_checks=args.skip_health,
        audit_dir=args.audit_dir
    )

    # Always inject resolved locations as parameter overrides so Bicep uses them
    config.add_parameter_override("location", location)
    config.add_parameter_override("locationML", location_ml)

    # Add user-supplied parameter overrides
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
    print(f"Resource Group : {config.resource_group}")
    print(f"Primary Region : {location}")
    print(f"ML Region      : {location_ml}")
    if location_ml != location:
        print(f"ML Resource Grp: {ml_resource_group}")
    print(f"Template       : {config.template_file}")
    print(f"Parameters     : {config.parameters_file or 'None'}")
    print(f"Allow Warnings : {config.allow_warnings}")
    print(f"Skip Health    : {config.skip_health_checks}")
    print(f"Audit Directory: {config.audit_dir}")

    if config.parameter_overrides:
        print("\nParameter Overrides:")
        for key, value in config.parameter_overrides.items():
            print(f"  {key} = {value}")

    print("=" * 60)
    print()

    # Create and run orchestrator
    orchestrator = BicepOrchestrator(config, git_sha)

    print("🚀 Starting deployment…")
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
