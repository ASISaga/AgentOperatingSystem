#!/usr/bin/env python3
"""Regional validation CLI.

Validates Azure service availability per region and exposes three
subcommands used by the deployment workflow:

* **validate** — check that a region supports the given services.
* **summary** — print a table of service availability.
* **auto-select** — pick the best region for a geography/environment.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the deployment package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from orchestrator.validators.regional_validator import RegionalValidator


def _validate(args: argparse.Namespace) -> int:
    """Validate that *region* supports every listed service."""
    validator = RegionalValidator()
    region = args.region
    services = args.services

    print(f"🌍 Validating region '{region}' for services: {', '.join(services)}")
    result = validator.validate_region(region, services)

    exit_code = 0
    for svc, available in result.items():
        icon = "✅" if available else "⚠️"
        print(f"  {icon} {svc}: {'available' if available else 'not confirmed'}")
        if not available:
            exit_code = 1

    return exit_code


def _summary(args: argparse.Namespace) -> int:
    """Print a summary table for *region*."""
    validator = RegionalValidator()
    summary = validator.get_region_summary(args.region, args.services)
    print(f"\n📊 Region summary: {args.region}")
    print(f"  {'Service':<25} {'Status':<15}")
    print(f"  {'-' * 25} {'-' * 15}")
    for svc, status in summary.items():
        print(f"  {svc:<25} {status:<15}")
    return 0


def _auto_select(args: argparse.Namespace) -> int:
    """Auto-select the best regions for the given geography."""
    validator = RegionalValidator()
    regions = validator.select_optimal_regions(args.environment, args.geography)
    print(f"🌍 Auto-selected regions for {args.environment}/{args.geography}:")
    for key, val in regions.items():
        print(f"  {key}: {val}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="regional_tool",
        description="Regional validation CLI for AOS deployments",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Validate region supports services")
    p_val.add_argument("region", help="Azure region name")
    p_val.add_argument("services", nargs="+", help="Service names to validate")

    p_sum = sub.add_parser("summary", help="Service availability summary")
    p_sum.add_argument("region", help="Azure region name")
    p_sum.add_argument("services", nargs="+", help="Service names")

    p_auto = sub.add_parser("auto-select", help="Auto-select optimal regions")
    p_auto.add_argument("--environment", required=True)
    p_auto.add_argument("--geography", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "validate": _validate,
        "summary": _summary,
        "auto-select": _auto_select,
    }
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
