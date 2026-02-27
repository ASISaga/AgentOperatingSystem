"""Infrastructure manager — wraps Azure CLI operations.

``InfrastructureManager`` is the single orchestration class that every CLI
subcommand delegates to.  Each public method maps 1-to-1 with a user-facing
action (deploy, plan, status, monitor, troubleshoot, delete, list_resources)
and internally shells out to ``az`` via :func:`subprocess.run`.

All mutating operations are audit-logged to JSON files under
``deployment/audit/``.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestrator.core.config import DeploymentConfig

_AUDIT_DIR = Path(__file__).resolve().parent.parent.parent / "audit"


class InfrastructureManager:
    """Orchestrates Azure infrastructure deployments for AOS."""

    def __init__(self, config: DeploymentConfig) -> None:
        self.config = config
        _AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deploy(self) -> bool:
        """Full deployment pipeline: lint → validate → what-if → deploy → health-check."""
        print(f"🚀 Starting deployment to {self.config.resource_group} "
              f"({self.config.environment}) in {self.config.location}")

        steps = [
            ("Lint", self._lint),
            ("Validate", self._validate),
            ("What-If", self._what_if),
            ("Deploy", self._deploy),
        ]
        if not self.config.skip_health:
            steps.append(("Health-Check", self._health_check))

        for label, fn in steps:
            print(f"\n{'=' * 60}")
            print(f"  Step: {label}")
            print(f"{'=' * 60}")
            ok = fn()
            if not ok:
                if label in ("Lint", "Validate") and self.config.allow_warnings:
                    print(f"⚠️  {label} had warnings — continuing (--allow-warnings)")
                else:
                    print(f"❌ {label} failed")
                    self._audit("deploy", {"step": label, "status": "failed"})
                    return False
            print(f"✅ {label} succeeded")

        self._audit("deploy", {"status": "success"})
        print("\n✅ Deployment completed successfully")
        return True

    def plan(self) -> bool:
        """Dry-run: lint → validate → what-if (no actual deployment)."""
        print(f"📋 Running plan for {self.config.resource_group} "
              f"({self.config.environment}) in {self.config.location}")

        for label, fn in [("Lint", self._lint), ("Validate", self._validate), ("What-If", self._what_if)]:
            print(f"\n--- {label} ---")
            ok = fn()
            if not ok and not self.config.allow_warnings:
                print(f"❌ {label} failed")
                return False
            print(f"✅ {label} passed")

        self._audit("plan", {"status": "success"})
        print("\n📋 Plan completed — no resources were modified")
        return True

    def status(self) -> bool:
        """Show deployment status for the resource group."""
        print(f"📊 Deployment status for {self.config.resource_group}")
        result = self._az([
            "deployment", "group", "list",
            "--resource-group", self.config.resource_group,
            "--output", "json",
        ])
        if result is None:
            return False
        deployments = json.loads(result)
        if not deployments:
            print("  No deployments found.")
            return True
        for dep in deployments[:10]:
            name = dep.get("name", "N/A")
            state = dep.get("properties", {}).get("provisioningState", "N/A")
            ts = dep.get("properties", {}).get("timestamp", "N/A")
            print(f"  {name}: {state} ({ts})")
        return True

    def monitor(self) -> bool:
        """Show health and metrics for deployed resources."""
        print(f"🔍 Monitoring resources in {self.config.resource_group}\n")
        checks = [
            ("Function Apps", self._monitor_function_apps),
            ("Storage Accounts", self._monitor_storage),
            ("Service Bus", self._monitor_servicebus),
            ("Application Insights", self._monitor_insights),
        ]
        for label, fn in checks:
            print(f"--- {label} ---")
            fn()
            print()
        return True

    def troubleshoot(self) -> bool:
        """Diagnose issues: deployment failures, activity logs, resource errors."""
        print(f"🔧 Troubleshooting {self.config.resource_group}\n")

        # Recent failed deployments
        print("--- Failed Deployments ---")
        result = self._az([
            "deployment", "group", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[?properties.provisioningState=='Failed']",
            "--output", "json",
        ])
        if result:
            failed = json.loads(result)
            if failed:
                for dep in failed:
                    name = dep.get("name", "N/A")
                    err = dep.get("properties", {}).get("error", {}).get("message", "No details")
                    print(f"  {name}: {err}")
            else:
                print("  No failed deployments found.")

        # Recent activity log errors
        print("\n--- Activity Log Errors (last 24h) ---")
        self._az([
            "monitor", "activity-log", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[?level=='Error'].{time:eventTimestamp, op:operationName.localizedValue, "
                       "status:status.localizedValue}",
            "--output", "table",
        ], print_output=True)

        # Resources in failed state
        print("\n--- Resources in Failed State ---")
        self._az([
            "resource", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[?provisioningState=='Failed'].{name:name, type:type}",
            "--output", "table",
        ], print_output=True)

        return True

    def delete(self, confirm: bool = True) -> bool:
        """Delete the resource group."""
        if confirm:
            answer = input(
                f"⚠️  Delete resource group '{self.config.resource_group}'? [y/N]: "
            )
            if answer.strip().lower() != "y":
                print("Aborted.")
                return False

        print(f"🗑️  Deleting resource group {self.config.resource_group} …")
        result = self._az([
            "group", "delete",
            "--name", self.config.resource_group,
            "--yes", "--no-wait",
            "--output", "json",
        ])
        if result is not None:
            self._audit("delete", {"resource_group": self.config.resource_group})
            print("✅ Deletion initiated (--no-wait)")
            return True
        return False

    def list_resources(self) -> bool:
        """List all resources in the resource group."""
        print(f"📦 Resources in {self.config.resource_group}\n")
        result = self._az([
            "resource", "list",
            "--resource-group", self.config.resource_group,
            "--output", "json",
        ])
        if result is None:
            return False
        resources = json.loads(result)
        if not resources:
            print("  No resources found.")
            return True
        for res in resources:
            name = res.get("name", "N/A")
            rtype = res.get("type", "N/A")
            loc = res.get("location", "N/A")
            state = res.get("provisioningState", "N/A")
            print(f"  {name} ({rtype}) — {loc} [{state}]")
        return True

    # ------------------------------------------------------------------
    # Private helpers — deployment pipeline
    # ------------------------------------------------------------------

    def _lint(self) -> bool:
        """Run ``az bicep build`` to lint the template."""
        if not self.config.template:
            print("  No template specified; skipping lint.")
            return True
        result = self._run(["az", "bicep", "build", "--file", self.config.template])
        return result.returncode == 0

    def _validate(self) -> bool:
        """Run ``az deployment group validate``."""
        cmd = self._deployment_cmd("validate")
        result = self._run(cmd)
        return result.returncode == 0

    def _what_if(self) -> bool:
        """Run ``az deployment group what-if``."""
        cmd = self._deployment_cmd("what-if")
        result = self._run(cmd)
        return result.returncode == 0

    def _deploy(self) -> bool:
        """Run ``az deployment group create``."""
        cmd = self._deployment_cmd("create")
        result = self._run(cmd)
        return result.returncode == 0

    def _health_check(self) -> bool:
        """Verify key resources exist and are in a healthy state."""
        result = self._az([
            "resource", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[].{name:name, state:provisioningState}",
            "--output", "json",
        ])
        if result is None:
            return False
        resources = json.loads(result)
        all_ok = True
        for res in resources:
            state = res.get("state", "Unknown")
            if state != "Succeeded":
                print(f"  ⚠️  {res.get('name')}: {state}")
                all_ok = False
            else:
                print(f"  ✅ {res.get('name')}: {state}")
        return all_ok

    # ------------------------------------------------------------------
    # Private helpers — monitoring
    # ------------------------------------------------------------------

    def _monitor_function_apps(self) -> None:
        result = self._az([
            "functionapp", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[].{name:name, state:state, hostName:defaultHostName}",
            "--output", "json",
        ])
        if not result:
            print("  No Function Apps found.")
            return
        for app in json.loads(result):
            print(f"  {app.get('name')}: {app.get('state')} — {app.get('hostName')}")

    def _monitor_storage(self) -> None:
        result = self._az([
            "storage", "account", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[].{name:name, status:statusOfPrimary, location:primaryLocation}",
            "--output", "json",
        ])
        if not result:
            print("  No Storage Accounts found.")
            return
        for sa in json.loads(result):
            print(f"  {sa.get('name')}: {sa.get('status')} in {sa.get('location')}")

    def _monitor_servicebus(self) -> None:
        result = self._az([
            "servicebus", "namespace", "list",
            "--resource-group", self.config.resource_group,
            "--query", "[].{name:name, status:status}",
            "--output", "json",
        ])
        if not result:
            print("  No Service Bus namespaces found.")
            return
        for ns in json.loads(result):
            print(f"  {ns.get('name')}: {ns.get('status')}")

    def _monitor_insights(self) -> None:
        result = self._az([
            "monitor", "app-insights", "component", "show",
            "--resource-group", self.config.resource_group,
            "--query", "[].{name:name, instrumentationKey:instrumentationKey}",
            "--output", "json",
        ])
        if not result:
            print("  No Application Insights found.")
            return
        for ai in json.loads(result):
            print(f"  {ai.get('name')}: key={ai.get('instrumentationKey', 'N/A')}")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    _SHA_RE = re.compile(r"^[a-fA-F0-9]{7,40}$")

    def _deployment_cmd(self, action: str) -> list[str]:
        """Build the ``az deployment group <action>`` command list."""
        cmd = [
            "az", "deployment", "group", action,
            "--resource-group", self.config.resource_group,
            "--template-file", self.config.template,
            "--output", "json",
        ]
        if self.config.parameters_file:
            cmd += ["--parameters", self.config.parameters_file]

        # Inline Bicep parameter overrides
        overrides: list[str] = []
        overrides.append(f"environment={self.config.environment}")
        overrides.append(f"location={self.config.location}")
        if self.config.location_ml:
            overrides.append(f"locationML={self.config.location_ml}")
        if self.config.git_sha and self._SHA_RE.match(self.config.git_sha):
            overrides.append(f"tags={{gitSha:'{self.config.git_sha}'}}")
        if overrides:
            cmd += ["--parameters"] + overrides
        return cmd

    def _az(self, args: list[str], *, print_output: bool = False) -> str | None:
        """Run an ``az`` command and return stdout, or *None* on failure."""
        result = self._run(["az"] + args)
        if result.returncode != 0:
            print(f"  az command failed (rc={result.returncode})", file=sys.stderr)
            if result.stderr:
                print(f"  {result.stderr.strip()}", file=sys.stderr)
            return None
        if print_output and result.stdout:
            print(result.stdout)
        return result.stdout

    @staticmethod
    def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        """Execute a command and return the completed process."""
        return subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603

    def _audit(self, action: str, data: dict[str, Any]) -> None:
        """Write an audit-log entry as a JSON file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "environment": self.config.environment,
            "resource_group": self.config.resource_group,
            "location": self.config.location,
            **data,
        }
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = _AUDIT_DIR / f"{action}_{ts}.json"
        path.write_text(json.dumps(entry, indent=2))
        print(f"📝 Audit log written to {path}")
