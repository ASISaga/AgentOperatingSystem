#!/usr/bin/env python3
"""GitHub Actions workflow helper CLI.

Provides subcommands consumed by the ``infrastructure-deploy.yml`` workflow:

* **check-trigger** — decide whether a deployment should run and extract
  environment / resource-group / location from the workflow inputs or PR
  labels.
* **select-regions** — pick the optimal primary and ML regions for a given
  environment and geography.
* **analyze-output** — classify the orchestrator's exit code and log output
  as *success*, *transient failure*, or *logic error*.
* **retry** — re-run the deployment up to ``--max-retries`` times.
* **extract-summary** — read audit JSON files and emit a GitHub Actions
  summary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _output(key: str, value: str) -> None:
    """Write a key=value pair to ``$GITHUB_OUTPUT`` (or stdout as fallback)."""
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write(f"{key}={value}\n")
    print(f"  {key}={value}")


# ------------------------------------------------------------------
# Subcommand implementations
# ------------------------------------------------------------------

def _check_trigger(_args: argparse.Namespace) -> None:
    """Determine whether a deployment should be triggered."""
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    env = os.environ.get("INPUT_ENVIRONMENT", "dev")
    rg = os.environ.get("INPUT_RESOURCE_GROUP", "")
    location = os.environ.get("INPUT_LOCATION", "")
    geography = os.environ.get("INPUT_GEOGRAPHY", "")
    template = os.environ.get("INPUT_TEMPLATE", "deployment/main-modular.bicep")
    skip_health = os.environ.get("INPUT_SKIP_HEALTH_CHECKS", "false")

    should_deploy = False
    is_dry_run = False

    if event == "workflow_dispatch":
        should_deploy = True
    elif event == "pull_request":
        deploy_dev = os.environ.get("PR_LABEL_DEPLOY_DEV", "false") == "true"
        deploy_staging = os.environ.get("PR_LABEL_DEPLOY_STAGING", "false") == "true"
        action_deploy = os.environ.get("PR_LABEL_ACTION_DEPLOY", "false") == "true"
        approved = os.environ.get("PR_LABEL_STATUS_APPROVED", "false") == "true"

        if deploy_dev:
            env = "dev"
            is_dry_run = True
            should_deploy = True
        elif deploy_staging and approved:
            env = "staging"
            should_deploy = True
        elif action_deploy:
            should_deploy = True
    elif event == "issue_comment":
        body = os.environ.get("COMMENT_BODY", "")
        if "/deploy" in body:
            should_deploy = True
            match = re.search(r"/deploy\s+(dev|staging|prod)", body)
            if match:
                env = match.group(1)
            is_dry_run = "plan" in body

    if not rg:
        rg = f"rg-aos-{env}"

    params_file = f"deployment/parameters/{env}.bicepparam"

    _output("should_deploy", str(should_deploy).lower())
    _output("is_dry_run", str(is_dry_run).lower())
    _output("environment", env)
    _output("resource_group", rg)
    _output("location", location)
    _output("geography", geography)
    _output("template", template)
    _output("parameters_file", params_file)
    _output("skip_health_checks", skip_health)


def _select_regions(args: argparse.Namespace) -> None:
    """Select optimal primary and ML regions."""
    env = args.environment
    location = args.location
    geography = getattr(args, "geography", "") or ""

    region_map: dict[str, dict[str, str]] = {
        "americas": {"primary": "eastus", "ml": "eastus"},
        "europe": {"primary": "westeurope", "ml": "westeurope"},
        "asia": {"primary": "southeastasia", "ml": "southeastasia"},
    }
    defaults = {"primary": "eastus", "ml": "eastus"}

    if location:
        primary = location
    elif geography and geography in region_map:
        primary = region_map[geography]["primary"]
    else:
        primary = defaults["primary"]

    if geography and geography in region_map:
        ml = region_map[geography]["ml"]
    else:
        ml = primary

    # Staging/prod may want separate ML region
    if env in ("staging", "prod") and primary == "eastus":
        ml = "eastus2"

    print(f"  Primary region: {primary}")
    print(f"  ML region:      {ml}")
    _output("primary_region", primary)
    _output("ml_region", ml)


_TRANSIENT_PATTERNS = [
    "RetryableError",
    "Timeout",
    "ThrottlingException",
    "ServiceUnavailable",
    "InternalServerError",
    "ECONNRESET",
    "socket hang up",
    "could not resolve host",
]


def _analyze_output(args: argparse.Namespace) -> None:
    """Classify deployment outcome from the orchestrator log."""
    log_file = getattr(args, "log_file", None) or ""
    exit_code = int(getattr(args, "exit_code", "0") or "0")

    log_text = ""
    if log_file and Path(log_file).exists():
        log_text = Path(log_file).read_text()

    if exit_code == 0:
        _output("status", "success")
        _output("failure_type", "")
        _output("should_retry", "false")
        _output("is_transient", "false")
        return

    is_transient = any(p.lower() in log_text.lower() for p in _TRANSIENT_PATTERNS)
    failure_type = "environmental" if is_transient else "logic"

    _output("status", "failed")
    _output("failure_type", failure_type)
    _output("should_retry", str(is_transient).lower())
    _output("is_transient", str(is_transient).lower())

    # Persist error message for downstream steps
    error_file = "error-message.txt"
    error_lines = [ln for ln in log_text.splitlines() if "error" in ln.lower()]
    Path(error_file).write_text("\n".join(error_lines[-50:]) if error_lines else log_text[-2000:])
    _output("error_file", error_file)


def _retry(args: argparse.Namespace) -> None:
    """Retry the deployment up to ``--max-retries`` times."""
    max_retries = int(getattr(args, "max_retries", 3))
    deploy_args = [
        "python3", "deployment/deploy.py", "deploy",
        "--resource-group", args.resource_group,
        "--location", args.location,
        "--location-ml", getattr(args, "location_ml", args.location),
        "--environment", args.environment,
        "--template", args.template,
        "--allow-warnings",
    ]
    params = getattr(args, "parameters", "")
    if params:
        deploy_args += ["--parameters", params]
    git_sha = getattr(args, "git_sha", "")
    if git_sha:
        deploy_args += ["--git-sha", git_sha]

    for attempt in range(1, max_retries + 1):
        print(f"\n🔄 Retry attempt {attempt}/{max_retries}")
        result = subprocess.run(deploy_args, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            _output("retry_success", "true")
            _output("retry_count", str(attempt))
            return

    _output("retry_success", "false")
    _output("retry_count", str(max_retries))


def _extract_summary(args: argparse.Namespace) -> None:
    """Read audit logs and emit summary outputs."""
    audit_dir = Path(getattr(args, "audit_dir", "deployment/audit"))
    deployed_resources = 0
    duration = "N/A"

    if audit_dir.exists():
        for f in sorted(audit_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text())
                if data.get("status") == "success":
                    deployed_resources = data.get("deployed_resources", 0)
                    duration = data.get("duration", "N/A")
            except (json.JSONDecodeError, OSError):
                continue

    _output("deployed_resources", str(deployed_resources))
    _output("duration", str(duration))


# ------------------------------------------------------------------
# Argument parser
# ------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workflow_helper",
        description="GitHub Actions workflow helper for AOS deployments",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check-trigger", help="Decide whether to deploy")

    p_regions = sub.add_parser("select-regions", help="Pick optimal regions")
    p_regions.add_argument("--environment", required=True)
    p_regions.add_argument("--location", default="")
    p_regions.add_argument("--geography", default="")

    p_analyze = sub.add_parser("analyze-output", help="Classify orchestrator outcome")
    p_analyze.add_argument("--log-file", default="")
    p_analyze.add_argument("--exit-code", default="0")

    p_retry = sub.add_parser("retry", help="Retry deployment")
    p_retry.add_argument("--resource-group", required=True)
    p_retry.add_argument("--location", required=True)
    p_retry.add_argument("--location-ml", default="")
    p_retry.add_argument("--environment", required=True)
    p_retry.add_argument("--template", required=True)
    p_retry.add_argument("--parameters", default="")
    p_retry.add_argument("--git-sha", default="")
    p_retry.add_argument("--max-retries", default=3, type=int)

    p_summary = sub.add_parser("extract-summary", help="Emit deployment summary")
    p_summary.add_argument("--audit-dir", default="deployment/audit")

    return parser


_DISPATCH: dict[str, object] = {
    "check-trigger": _check_trigger,
    "select-regions": _select_regions,
    "analyze-output": _analyze_output,
    "retry": _retry,
    "extract-summary": _extract_summary,
}


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = _DISPATCH.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    handler(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
