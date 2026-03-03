#!/usr/bin/env python3
"""AOS Infrastructure CLI.

Main entry point for the full Azure infrastructure lifecycle — provisioning,
governance, automation, reliability, and lifecycle operations.

Usage:
    # Automation pillar
    python deploy.py deploy --resource-group RG --location REGION --environment ENV --template BICEP
    python deploy.py plan --resource-group RG --location REGION --environment ENV --template BICEP
    python deploy.py automate --resource-group RG --location REGION --environment ENV --template BICEP

    # Governance pillar
    python deploy.py govern --resource-group RG --environment ENV

    # Reliability pillar
    python deploy.py reliability --resource-group RG --environment ENV --template BICEP

    # Observability / diagnostics
    python deploy.py status --resource-group RG
    python deploy.py monitor --resource-group RG
    python deploy.py troubleshoot --resource-group RG

    # Lifecycle operations
    python deploy.py deprovision --resource-group RG --resource-name NAME --resource-type TYPE
    python deploy.py shift --resource-group RG --target-rg TARGET-RG --target-region REGION
    python deploy.py modify --resource-group RG --resource-name NAME --resource-type TYPE --properties '{"key":"val"}'
    python deploy.py upgrade --resource-group RG --resource-name NAME --resource-type TYPE --new-sku SKU
    python deploy.py scale --resource-group RG --resource-name NAME --resource-type TYPE --scale-settings '{"sku.capacity":2}'

    # Cleanup
    python deploy.py delete --resource-group RG
    python deploy.py list-resources --resource-group RG
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the deployment package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator.core.config import (
    AutomationConfig,
    DeploymentConfig,
    GovernanceConfig,
    ReliabilityConfig,
)
from orchestrator.core.manager import InfrastructureManager
from orchestrator.automation.lifecycle import LifecycleManager


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="deploy",
        description="AOS Infrastructure CLI — Governance, Automation, Reliability",
    )

    # ── Shared parents ─────────────────────────────────────────────────────
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--resource-group", required=True, help="Azure resource group name")

    deploy_parent = argparse.ArgumentParser(add_help=False, parents=[parent])
    deploy_parent.add_argument("--location", required=True, help="Primary Azure region")
    deploy_parent.add_argument("--location-ml", default="", help="Azure ML region")
    deploy_parent.add_argument("--environment", required=True, choices=["dev", "staging", "prod"])
    deploy_parent.add_argument("--template", required=True, help="Bicep template file path")
    deploy_parent.add_argument("--parameters", default="", help="Parameters file path")
    deploy_parent.add_argument("--subscription-id", default="", help="Azure subscription ID")
    deploy_parent.add_argument("--git-sha", default="", help="Git commit SHA for tagging")
    deploy_parent.add_argument("--allow-warnings", action="store_true", help="Continue on warnings")
    deploy_parent.add_argument("--skip-health", action="store_true", help="Skip health checks")
    deploy_parent.add_argument("--no-confirm-deletes", action="store_true", help="Dry-run mode")

    env_parent = argparse.ArgumentParser(add_help=False, parents=[parent])
    env_parent.add_argument("--environment", required=True, choices=["dev", "staging", "prod"])
    env_parent.add_argument("--subscription-id", default="")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── Automation pillar commands ─────────────────────────────────────────
    subparsers.add_parser("deploy", parents=[deploy_parent], help="Full deployment pipeline")
    subparsers.add_parser("plan", parents=[deploy_parent], help="Dry-run: lint, validate, what-if")

    p_automate = subparsers.add_parser("automate", parents=[deploy_parent], help="Automation pillar")
    p_automate.add_argument("--deploy-function-apps", action="store_true",
                            help="Deploy AOS Function Apps via SDK bridge after Bicep")
    p_automate.add_argument("--sync-kernel-config", action="store_true",
                            help="Sync kernel env vars to Function Apps after deployment")

    # ── Governance pillar command ──────────────────────────────────────────
    p_govern = subparsers.add_parser("govern", parents=[env_parent], help="Governance pillar")
    p_govern.add_argument("--location", default="eastus", help="Azure region")
    p_govern.add_argument("--enforce-policies", action="store_true", help="Assign AOS governance policies")
    p_govern.add_argument("--budget-amount", type=float, default=0.0, help="Monthly budget limit")
    p_govern.add_argument("--review-rbac", action="store_true", help="Run privileged-access review")
    p_govern.add_argument("--required-tags", type=json.loads, default={},
                          help='Required tags as JSON: \'{"environment":"dev"}\'')

    # ── Reliability pillar command ─────────────────────────────────────────
    p_reliability = subparsers.add_parser("reliability", parents=[env_parent], help="Reliability pillar")
    p_reliability.add_argument("--location", default="eastus", help="Azure region")
    p_reliability.add_argument("--template", default="", help="Bicep template for drift detection")
    p_reliability.add_argument("--enable-drift-detection", action="store_true", help="Run drift detection")
    p_reliability.add_argument("--check-dr-readiness", action="store_true", help="Assess DR readiness")

    # ── Observability / diagnostics ────────────────────────────────────────
    subparsers.add_parser("status", parents=[parent], help="Show deployment status")
    subparsers.add_parser("monitor", parents=[parent], help="Show resource health & metrics")
    subparsers.add_parser("troubleshoot", parents=[parent], help="Diagnose deployment issues")

    # ── Lifecycle operations ───────────────────────────────────────────────
    lc_parent = argparse.ArgumentParser(add_help=False, parents=[parent])
    lc_parent.add_argument("--resource-name", required=True, help="Azure resource name")
    lc_parent.add_argument("--resource-type", required=True, help="Full ARM resource type")
    lc_parent.add_argument("--subscription-id", default="")

    p_deprovision = subparsers.add_parser("deprovision", parents=[lc_parent],
                                          help="Remove a resource from the group")
    p_deprovision.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    p_shift = subparsers.add_parser("shift", parents=[parent], help="Shift resource group to new region")
    p_shift.add_argument("--target-rg", required=True, help="Target resource group name")
    p_shift.add_argument("--target-region", required=True, help="Target Azure region")
    p_shift.add_argument("--subscription-id", default="")
    p_shift.add_argument("--yes", action="store_true", help="Skip confirmation")

    p_modify = subparsers.add_parser("modify", parents=[lc_parent],
                                     help="Update resource properties in-place")
    p_modify.add_argument("--properties", type=json.loads, required=True,
                          help='Properties as JSON: \'{"properties.httpsOnly": true}\'')

    p_upgrade = subparsers.add_parser("upgrade", parents=[lc_parent],
                                      help="Upgrade a resource's SKU/tier")
    p_upgrade.add_argument("--new-sku", required=True, help="Target SKU name")

    p_scale = subparsers.add_parser("scale", parents=[lc_parent],
                                    help="Adjust capacity of a scalable resource")
    p_scale.add_argument("--scale-settings", type=json.loads, required=True,
                         help='Scale settings as JSON: \'{"sku.capacity": 2}\'')

    # ── Cleanup ────────────────────────────────────────────────────────────
    p_delete = subparsers.add_parser("delete", parents=[parent], help="Delete resource group")
    p_delete.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    subparsers.add_parser("list-resources", parents=[parent], help="List resources in group")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # ── Pillar commands ────────────────────────────────────────────────────
    if args.command in ("deploy", "plan", "automate"):
        config = DeploymentConfig.from_args(args)
        if args.command == "automate":
            config = DeploymentConfig(
                environment=args.environment,
                resource_group=args.resource_group,
                location=args.location,
                location_ml=getattr(args, "location_ml", ""),
                template=args.template,
                parameters_file=getattr(args, "parameters", ""),
                subscription_id=getattr(args, "subscription_id", ""),
                git_sha=getattr(args, "git_sha", ""),
                allow_warnings=getattr(args, "allow_warnings", False),
                skip_health=getattr(args, "skip_health", False),
                automation=AutomationConfig(
                    deploy_function_apps=getattr(args, "deploy_function_apps", False),
                    sync_kernel_config=getattr(args, "sync_kernel_config", False),
                ),
            )
        mgr = InfrastructureManager(config)
        if args.command == "deploy":
            return 0 if mgr.deploy() else 1
        if args.command == "plan":
            return 0 if mgr.plan() else 1
        return 0 if mgr.automate() else 1

    if args.command == "govern":
        config = DeploymentConfig(
            environment=args.environment,
            resource_group=args.resource_group,
            location=getattr(args, "location", "eastus"),
            subscription_id=getattr(args, "subscription_id", ""),
            governance=GovernanceConfig(
                enforce_policies=getattr(args, "enforce_policies", False),
                budget_amount=getattr(args, "budget_amount", 0.0),
                required_tags=getattr(args, "required_tags", {}),
                review_rbac=getattr(args, "review_rbac", False),
            ),
        )
        return 0 if InfrastructureManager(config).govern() else 1

    if args.command == "reliability":
        config = DeploymentConfig(
            environment=args.environment,
            resource_group=args.resource_group,
            location=getattr(args, "location", "eastus"),
            template=getattr(args, "template", ""),
            subscription_id=getattr(args, "subscription_id", ""),
            reliability=ReliabilityConfig(
                enable_drift_detection=getattr(args, "enable_drift_detection", False),
                check_dr_readiness=getattr(args, "check_dr_readiness", False),
            ),
        )
        return 0 if InfrastructureManager(config).reliability_check() else 1

    # ── Lifecycle operations ───────────────────────────────────────────────
    if args.command in ("deprovision", "shift", "modify", "upgrade", "scale"):
        lm = LifecycleManager(
            resource_group=args.resource_group,
            subscription_id=getattr(args, "subscription_id", ""),
        )
        if args.command == "deprovision":
            result = lm.deprovision(
                args.resource_name,
                args.resource_type,
                confirm=not getattr(args, "yes", False),
            )
        elif args.command == "shift":
            result = lm.shift_region(
                target_region=args.target_region,
                target_resource_group=args.target_rg,
                confirm=not getattr(args, "yes", False),
            )
        elif args.command == "modify":
            result = lm.modify(args.resource_name, args.resource_type, args.properties)
        elif args.command == "upgrade":
            result = lm.upgrade(args.resource_name, args.resource_type, args.new_sku)
        else:  # scale
            result = lm.scale(args.resource_name, args.resource_type, args.scale_settings)
        return 0 if result.success else 1

    # ── Generic commands that only need resource_group ────────────────────
    mgr = InfrastructureManager(
        DeploymentConfig(
            environment="dev",
            resource_group=args.resource_group,
            location="eastus",
            template="",
        )
    )
    if args.command == "status":
        ok = mgr.status()
    elif args.command == "monitor":
        ok = mgr.monitor()
    elif args.command == "troubleshoot":
        ok = mgr.troubleshoot()
    elif args.command == "delete":
        ok = mgr.delete(confirm=not getattr(args, "yes", False))
    elif args.command == "list-resources":
        ok = mgr.list_resources()
    else:
        parser.print_help()
        return 1

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
