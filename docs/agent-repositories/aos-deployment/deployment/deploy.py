#!/usr/bin/env python3
"""AOS Infrastructure Deployment CLI.

Main entry point for deploying, planning, monitoring, troubleshooting,
and managing Azure infrastructure for the Agent Operating System.

Usage:
    python deploy.py deploy --resource-group RG --location REGION --environment ENV --template BICEP
    python deploy.py plan --resource-group RG --location REGION --environment ENV --template BICEP
    python deploy.py status --resource-group RG
    python deploy.py monitor --resource-group RG
    python deploy.py troubleshoot --resource-group RG
    python deploy.py delete --resource-group RG
    python deploy.py list-resources --resource-group RG
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the deployment package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from orchestrator.core.config import DeploymentConfig
from orchestrator.core.manager import InfrastructureManager


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="deploy",
        description="AOS Infrastructure Deployment CLI",
    )

    # Shared arguments
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--resource-group", required=True, help="Azure resource group name")

    # Deploy-specific parent
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

    subparsers = parser.add_subparsers(dest="command", required=True)

    # deploy
    subparsers.add_parser("deploy", parents=[deploy_parent], help="Full deployment pipeline")

    # plan
    subparsers.add_parser("plan", parents=[deploy_parent], help="Dry-run: lint, validate, what-if")

    # status
    subparsers.add_parser("status", parents=[parent], help="Show deployment status")

    # monitor
    subparsers.add_parser("monitor", parents=[parent], help="Show resource health & metrics")

    # troubleshoot
    subparsers.add_parser("troubleshoot", parents=[parent], help="Diagnose deployment issues")

    # delete
    p_delete = subparsers.add_parser("delete", parents=[parent], help="Delete resource group")
    p_delete.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    # list-resources
    subparsers.add_parser("list-resources", parents=[parent], help="List resources in group")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command in ("deploy", "plan"):
        config = DeploymentConfig.from_args(args)
        mgr = InfrastructureManager(config)

        if args.command == "deploy":
            ok = mgr.deploy()
        else:
            ok = mgr.plan()
        return 0 if ok else 1

    # Commands that only need resource_group
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
