#!/usr/bin/env python3
"""
Workflow Helper CLI

Provides Python implementations for the complex steps in the
infrastructure-deploy.yml GitHub Actions workflow, replacing fragile
inline bash scripts with well-tested, structured Python code.

Sub-commands
------------
check-trigger   Determine deployment intent from the GitHub event context.
analyze-output  Classify orchestrator output log as success/logic/environmental.
retry           Re-run the deployment orchestrator with exponential back-off.
extract-summary Extract key metrics from audit logs.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# GitHub Actions helpers
# ---------------------------------------------------------------------------

def _write_github_output(key: str, value: str) -> None:
    """Append a key=value pair to $GITHUB_OUTPUT (or print to stdout)."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")
    else:
        print(f"::set-output name={key}::{value}")


def _write_github_summary(text: str) -> None:
    """Append markdown text to $GITHUB_STEP_SUMMARY."""
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")


# ---------------------------------------------------------------------------
# Sub-command: check-trigger
# ---------------------------------------------------------------------------
# Reads GitHub event context from environment variables and writes
# deployment-intent outputs.  All inputs arrive via the environment so the
# YAML step stays minimal.
#
# Expected env vars (set in the YAML `env:` block of the step):
#   GITHUB_EVENT_NAME          – github.event_name
#   INPUT_ENVIRONMENT          – github.event.inputs.environment
#   INPUT_RESOURCE_GROUP       – github.event.inputs.resource_group  (optional)
#   INPUT_LOCATION             – github.event.inputs.location         (optional)
#   INPUT_GEOGRAPHY            – github.event.inputs.geography        (optional)
#   INPUT_TEMPLATE             – github.event.inputs.template         (optional)
#   INPUT_SKIP_HEALTH_CHECKS   – github.event.inputs.skip_health_checks (optional)
#   PR_LABEL_DEPLOY_DEV        – 'true'/'false'
#   PR_LABEL_DEPLOY_STAGING    – 'true'/'false'
#   PR_LABEL_STATUS_APPROVED   – 'true'/'false'
#   PR_LABEL_ACTION_DEPLOY     – 'true'/'false'
#   COMMENT_BODY               – github.event.comment.body            (optional)
# ---------------------------------------------------------------------------

def cmd_check_trigger(_args: argparse.Namespace) -> int:
    """Determine deployment intent from the GitHub event context."""

    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    input_env = os.environ.get("INPUT_ENVIRONMENT", "dev")
    resource_group = os.environ.get("INPUT_RESOURCE_GROUP", "")
    location = os.environ.get("INPUT_LOCATION", "")
    geography = os.environ.get("INPUT_GEOGRAPHY", "")
    template = os.environ.get("INPUT_TEMPLATE", "deployment/main-modular.bicep")
    parameters_file = ""

    should_deploy = False
    is_dry_run = True
    environment = "dev"

    print(f"🔍 Analyzing deployment intent (event: {event_name})...")

    if event_name == "workflow_dispatch":
        print("📋 Manual deployment requested")
        should_deploy = True
        is_dry_run = False
        environment = input_env
        parameters_file = f"deployment/parameters/{environment}.bicepparam"

    elif event_name == "pull_request":
        print("🔀 Pull request event detected")
        label_dev = os.environ.get("PR_LABEL_DEPLOY_DEV", "false") == "true"
        label_staging = os.environ.get("PR_LABEL_DEPLOY_STAGING", "false") == "true"
        label_approved = os.environ.get("PR_LABEL_STATUS_APPROVED", "false") == "true"
        label_action_deploy = os.environ.get("PR_LABEL_ACTION_DEPLOY", "false") == "true"

        if label_dev:
            print("🏷️  Label 'deploy:dev' found – will deploy to dev")
            should_deploy = True
            environment = "dev"
            parameters_file = "deployment/parameters/dev.bicepparam"
        elif label_staging:
            print("🏷️  Label 'deploy:staging' found – will deploy to staging")
            should_deploy = True
            environment = "staging"
            parameters_file = "deployment/parameters/staging.bicepparam"
        elif label_approved and label_action_deploy:
            print("🏷️  Labels 'status:approved' + 'action:deploy' found – will deploy to prod")
            should_deploy = True
            is_dry_run = False
            environment = "prod"
            parameters_file = "deployment/parameters/prod.bicepparam"
        else:
            print("📊 No deployment labels – will run plan/dry-run only")
            is_dry_run = True

        if not resource_group:
            resource_group = f"aos-{environment}-rg"

    elif event_name == "issue_comment":
        print("💬 Comment event detected")
        comment_body = os.environ.get("COMMENT_BODY", "")

        deploy_match = re.match(r"^/deploy\s+(dev|staging|prod)", comment_body.strip())
        plan_match = re.match(r"^/plan", comment_body.strip())

        if deploy_match:
            environment = deploy_match.group(1)
            print(f"🚀 Deployment command found: /deploy {environment}")
            should_deploy = True
            is_dry_run = False
            resource_group = f"aos-{environment}-rg"
            parameters_file = f"deployment/parameters/{environment}.bicepparam"
        elif plan_match:
            print("📋 Plan command found: /plan")
            is_dry_run = True
            resource_group = f"aos-{environment}-rg"

    # Default resource group when none was supplied
    if not resource_group:
        resource_group = f"aos-{environment}-rg"

    # Write outputs
    _write_github_output("should_deploy", str(should_deploy).lower())
    _write_github_output("is_dry_run", str(is_dry_run).lower())
    _write_github_output("environment", environment)
    _write_github_output("resource_group", resource_group)
    _write_github_output("location", location)
    _write_github_output("geography", geography)
    _write_github_output("template", template)
    _write_github_output("parameters_file", parameters_file)

    # Write step summary
    _write_github_summary("## Deployment Intent Analysis")
    _write_github_summary(f"- **Should Deploy**: {str(should_deploy).lower()}")
    _write_github_summary(f"- **Dry Run**: {str(is_dry_run).lower()}")
    _write_github_summary(f"- **Environment**: {environment}")
    _write_github_summary(f"- **Resource Group**: {resource_group}")
    _write_github_summary(f"- **Location (user-provided)**: {location or '(auto-select)'}")
    _write_github_summary(f"- **Template**: {template}")
    _write_github_summary(f"- **Parameters**: {parameters_file}")

    return 0


# ---------------------------------------------------------------------------
# Sub-command: analyze-output
# ---------------------------------------------------------------------------
# Classifies the orchestrator output log and writes GitHub Actions outputs.
#
# Uses the same pattern sets as deployment/orchestrator/core/failure_classifier.py
# so there is a single source of truth.
# ---------------------------------------------------------------------------

# Logic failure patterns sourced from FailureClassifier.LOGIC_FAILURE_PATTERNS
# plus additional patterns observed from Azure documentation and real deployments.
_LOGIC_PATTERNS = re.compile(
    r"lint.*error"
    r"|bicep.*error"
    r"|syntax.*error"
    r"|validation.*failed"
    r"|invalid.*parameter"
    r"|invalid.*bicep"
    r"|missing.*required.*parameter"
    r"|template.*validation.*error"
    r"|circular.*dependency"
    r"|resource.*type.*not.*found"
    r"|api.*version.*not.*supported"
    r"|property.*not.*allowed"
    r"|deployment.*template.*validation.*failed"
    r"|parameter.*must be"
    r"|error\s*bcp\d+"
    r"|invalidtemplatedeployment"
    r"|template deployment.*is not valid"
    r"|logic.*failure.*detected"
    r"|InvalidResourceLocation"
    r"|InvalidResourceGroupLocation"
    r"|already.*exists.*in.*location"
    r"|resource.*already.*exists.*location",
    re.IGNORECASE,
)

# Environmental failure patterns sourced from FailureClassifier.ENVIRONMENTAL_FAILURE_PATTERNS
# plus additional patterns from Azure SDK error codes and service documentation.
_ENV_PATTERNS = re.compile(
    r"timeout"
    r"|throttl(?:ed|ing)"
    r"|rate.*limit"
    r"|service.*unavailable"
    r"|internal.*server.*error"
    r"|network.*error"
    r"|network.*timeout"
    r"|connection.*refused"
    r"|connection.*timeout"
    r"|temporary.*failure"
    r"|quota.*exceeded"
    r"|capacity.*unavailable"
    r"|region.*unavailable"
    r"|sku.*not.*available"
    r"|conflict.*another.*operation"
    r"|code:\s*conflict"
    r"|another operation.*in progress",
    re.IGNORECASE,
)


def _extract_error_excerpt(log_text: str, context_before: int = 30, context_after: int = 10) -> str:
    """
    Extract relevant lines around the DEPLOYMENT FAILED marker.

    Returns the surrounding context, or the last ``context_before`` lines when
    no marker is found.
    """
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        if "DEPLOYMENT FAILED" in line:
            start = max(0, i - context_before)
            end = min(len(lines), i + context_after + 1)
            return "\n".join(lines[start:end])
    return "\n".join(lines[-context_before:])


def _classify_log(log_text: str) -> tuple:
    """
    Classify log text into (status, failure_type, should_retry, is_transient).

    Returns
    -------
    tuple: (status, failure_type, should_retry, is_transient)
        status        – 'success' | 'failed' | 'unknown'
        failure_type  – 'none' | 'logic' | 'environmental' | 'unknown'
        should_retry  – bool
        is_transient  – bool
    """
    if "DEPLOYMENT SUCCESSFUL" in log_text:
        return ("success", "none", False, False)

    if "DEPLOYMENT FAILED" not in log_text and not log_text.strip():
        return ("unknown", "unknown", False, False)

    error_message = _extract_error_excerpt(log_text)

    # Classify: logic takes precedence over environmental
    if _LOGIC_PATTERNS.search(error_message):
        return ("failed", "logic", False, False)

    if _ENV_PATTERNS.search(error_message):
        return ("failed", "environmental", True, True)

    # Fallback: scan full log for orchestrator-emitted classification markers
    if "Environmental failure" in log_text:
        return ("failed", "environmental", True, True)
    if "Logic failure detected" in log_text:
        return ("failed", "logic", False, False)

    return ("failed", "unknown", False, False)


def cmd_analyze_output(args: argparse.Namespace) -> int:
    """Analyze orchestrator output log and classify failure type."""

    log_file = Path(args.log_file) if args.log_file else None
    exit_code = int(args.exit_code) if args.exit_code else 0

    print("🧠 Agent analyzing orchestrator output...")

    if not log_file or not log_file.is_file():
        print("⚠️  No output file found")
        if exit_code != 0:
            _write_github_output("status", "failed")
        else:
            _write_github_output("status", "unknown")
        _write_github_output("failure_type", "unknown")
        return 0

    log_text = log_file.read_text(encoding="utf-8", errors="replace")

    # If exit code is non-zero but DEPLOYMENT SUCCESSFUL not present, treat as failure
    if exit_code != 0 and "DEPLOYMENT SUCCESSFUL" not in log_text:
        if "DEPLOYMENT FAILED" not in log_text:
            log_text += "\nDEPLOYMENT FAILED"

    status, failure_type, should_retry, is_transient = _classify_log(log_text)

    if status == "success":
        print("✅ Deployment succeeded")
        _write_github_output("status", "success")
        _write_github_output("failure_type", "none")
        return 0

    if status == "failed":
        print(f"❌ Deployment failed – failure type: {failure_type}")

        # Save error message excerpt for downstream steps
        error_excerpt = _extract_error_excerpt(log_text)
        error_file = Path("error-message.txt")
        error_file.write_text(error_excerpt, encoding="utf-8")

        _write_github_output("status", "failed")
        _write_github_output("failure_type", failure_type)
        _write_github_output("should_retry", str(should_retry).lower())
        _write_github_output("is_transient", str(is_transient).lower())
        _write_github_output("error_file", str(error_file))

        if failure_type == "logic":
            print("🔴 Logic failure – no retry will be attempted")
        elif failure_type == "environmental":
            print("🟡 Environmental failure – transient Azure issue, retry eligible")
        else:
            print("🟠 Unknown failure type")
    else:
        print("⚠️  Deployment status unknown")
        _write_github_output("status", "unknown")
        _write_github_output("failure_type", "unknown")

    return 0


# ---------------------------------------------------------------------------
# Sub-command: retry
# ---------------------------------------------------------------------------
# Runs the deployment orchestrator with exponential back-off for transient
# (environmental) failures.
# ---------------------------------------------------------------------------

def _build_deploy_cmd(
    resource_group: str,
    location: str,
    location_ml: str,
    environment: str,
    template: str,
    parameters_file: str,
    git_sha: str,
) -> list:
    """Build the deploy.py argument list (no shell evaluation required)."""
    cmd = [
        sys.executable,
        "deployment/deploy.py",
        "--resource-group", resource_group,
        "--location", location,
        "--location-ml", location_ml,
        "--environment", environment,
        "--template", template,
        "--allow-warnings",
    ]
    if parameters_file and Path(parameters_file).is_file():
        cmd += ["--parameters", parameters_file]
    if git_sha:
        cmd += ["--git-sha", git_sha]
    return cmd


def cmd_retry(args: argparse.Namespace) -> int:
    """
    Re-run the deployment orchestrator with exponential back-off.

    Exits 0 when a retry attempt succeeds, 1 when all retries are exhausted.
    """
    max_retries = args.max_retries
    retry_count = 0
    base_delay = 30  # seconds – yields 60 s, 120 s, 240 s for attempts 1-3

    cmd = _build_deploy_cmd(
        resource_group=args.resource_group,
        location=args.location,
        location_ml=args.location_ml,
        environment=args.environment,
        template=args.template,
        parameters_file=args.parameters or "",
        git_sha=args.git_sha or "",
    )

    print(f"🔄 Self-healing: up to {max_retries} retries for transient failure...")

    while retry_count < max_retries:
        retry_count += 1
        # Exponential back-off matching original workflow: attempt 1→60s, 2→120s, 3→240s
        delay = base_delay * (2 ** retry_count)

        print(f"🕐 Retry attempt {retry_count}/{max_retries} – waiting {delay} s...")
        time.sleep(delay)

        log_path = f"orchestrator-retry-{retry_count}.log"
        print(f"🔄 Attempting deployment (retry {retry_count})...")

        with open(log_path, "w", encoding="utf-8") as log_fh:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )
            log_fh.write(result.stdout)

        # Echo to console
        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ Retry {retry_count} succeeded!")
            _write_github_output("retry_success", "true")
            _write_github_output("retry_count", str(retry_count))
            return 0

        print(f"❌ Retry {retry_count} failed")

        # Check whether the failure is still transient
        if not _ENV_PATTERNS.search(result.stdout):
            print("Error changed to non-transient – stopping retries")
            break

    print(f"❌ All {retry_count} retries exhausted")
    _write_github_output("retry_success", "false")
    _write_github_output("retry_count", str(retry_count))
    return 1


# ---------------------------------------------------------------------------
# Sub-command: select-regions
# ---------------------------------------------------------------------------
# Runs auto-region selection and writes primary_region / ml_region outputs.
# Intended to replace the inline Python one-liners in the YAML region step.
# ---------------------------------------------------------------------------

def cmd_select_regions(args: argparse.Namespace) -> int:
    """Auto-select optimal Azure regions and write GitHub Actions outputs."""

    # Add orchestrator to Python path so we can import regional_validator
    orchestrator_dir = Path(__file__).parent.parent
    if str(orchestrator_dir) not in sys.path:
        sys.path.insert(0, str(orchestrator_dir))

    try:
        from validators.regional_validator import RegionalValidator  # type: ignore[import]
    except ImportError as exc:
        print(f"❌ Could not import RegionalValidator: {exc}", file=sys.stderr)
        return 1

    environment = args.environment
    user_location = args.location or ""
    geography = args.geography or None

    validator = RegionalValidator()

    if user_location:
        print(f"ℹ️  User specified primary region: {user_location}")
        primary_region = user_location

        # Auto-select an ML region in case the primary doesn't support Azure ML
        regions = validator.select_optimal_regions(
            set(),  # service set not needed – just want ML region recommendation
            environment=environment,
            preferred_geography=geography,
        )
        ml_region = regions.get("ml", primary_region)

        # Check whether the primary region supports Azure ML; if so, reuse it
        try:
            from validators.regional_validator import ServiceType  # type: ignore[import]
            capability = validator.get_region_capability(primary_region)
            if ServiceType.AZURE_ML in capability.available_services:
                ml_region = primary_region
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"⚠️  Could not verify Azure ML support for '{primary_region}': {exc}",
                  file=sys.stderr)
    else:
        print("ℹ️  No region specified – running auto-selection...")
        regions = validator.select_optimal_regions(
            set(),
            environment=environment,
            preferred_geography=geography,
        )
        primary_region = regions["primary"]
        ml_region = regions["ml"]

        if regions.get("multi_region"):
            print(f"⚠️  Multi-region deployment: core → {primary_region}, ML/ACR → {ml_region}")
        else:
            print(f"✅ Single-region deployment: {primary_region}")

    _write_github_output("primary_region", primary_region)
    _write_github_output("ml_region", ml_region)

    _write_github_summary("## 🌍 Auto-Selected Regions")
    _write_github_summary(f"- **Primary Region**: `{primary_region}`")
    _write_github_summary(f"- **Azure ML Region**: `{ml_region}`")
    if primary_region != ml_region:
        _write_github_summary(
            f"- ⚠️  **Multi-Region**: core services in `{primary_region}`, Azure ML in `{ml_region}`"
        )

    return 0


# ---------------------------------------------------------------------------
# Sub-command: extract-summary
# ---------------------------------------------------------------------------

def cmd_extract_summary(args: argparse.Namespace) -> int:
    """Extract key metrics from the most recent audit log."""

    audit_dir = Path(args.audit_dir)
    if not audit_dir.is_dir():
        print("⚠️  Audit directory not found – no summary available")
        return 0

    audit_files = sorted(audit_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not audit_files:
        print("⚠️  No audit log files found")
        return 0

    latest_audit = audit_files[0]
    print(f"📋 Found audit log: {latest_audit}")

    try:
        data = json.loads(latest_audit.read_text(encoding="utf-8"))
        deployed_resources = len(data.get("deployed_resources", []))
        duration = data.get("duration_seconds", "N/A")

        _write_github_output("deployed_resources", str(deployed_resources))
        _write_github_output("duration", str(duration))
        _write_github_output("audit_file", str(latest_audit))

        print(f"  Deployed Resources : {deployed_resources}")
        print(f"  Duration (seconds) : {duration}")
    except (json.JSONDecodeError, OSError) as exc:
        print(f"⚠️  Could not parse audit log: {exc}")

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Actions workflow helper for infrastructure deployment",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command")

    # ---- check-trigger ----
    subparsers.add_parser(
        "check-trigger",
        help="Determine deployment intent from the GitHub event context",
    )

    # ---- analyze-output ----
    analyze_parser = subparsers.add_parser(
        "analyze-output",
        help="Classify orchestrator output log as success/logic/environmental",
    )
    analyze_parser.add_argument("--log-file", help="Path to orchestrator output log")
    analyze_parser.add_argument("--exit-code", default="0", help="Exit code from orchestrator")

    # ---- retry ----
    retry_parser = subparsers.add_parser(
        "retry",
        help="Re-run the deployment orchestrator with exponential back-off",
    )
    retry_parser.add_argument("--resource-group", required=True)
    retry_parser.add_argument("--location", required=True)
    retry_parser.add_argument("--location-ml", required=True)
    retry_parser.add_argument("--environment", required=True)
    retry_parser.add_argument("--template", required=True)
    retry_parser.add_argument("--parameters", default="")
    retry_parser.add_argument("--git-sha", default="")
    retry_parser.add_argument("--max-retries", type=int, default=3)

    # ---- select-regions ----
    regions_parser = subparsers.add_parser(
        "select-regions",
        help="Auto-select optimal Azure regions for deployment",
    )
    regions_parser.add_argument("--environment", default="dev", choices=["dev", "staging", "prod"])
    regions_parser.add_argument("--location", default="", help="User-specified primary region (empty = auto)")
    regions_parser.add_argument("--geography", default="",
                                help="Geographic preference (americas, europe, asia, or empty)")

    # ---- extract-summary ----
    summary_parser = subparsers.add_parser(
        "extract-summary",
        help="Extract deployment metrics from audit logs",
    )
    summary_parser.add_argument("--audit-dir", default="deployment/audit")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    dispatch = {
        "check-trigger": cmd_check_trigger,
        "analyze-output": cmd_analyze_output,
        "retry": cmd_retry,
        "select-regions": cmd_select_regions,
        "extract-summary": cmd_extract_summary,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
