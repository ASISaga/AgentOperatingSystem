"""Infrastructure manager — orchestrates the full Azure infrastructure lifecycle.

``InfrastructureManager`` is the single orchestration class that every CLI
subcommand delegates to.  Each public method maps 1-to-1 with a user-facing
action and internally coordinates one or more pillar components.

The manager is organised around three formal lifecycle pillars, each with its
own sub-package and a top-level entrypoint method:

* **Governance** (``govern()``) — policy enforcement, cost management, RBAC
  access review and least-privilege enforcement
* **Automation** (``automate()``) — formal pipeline (lint/validate/what-if/
  deploy), infrastructure lifecycle operations (deprovision/shift/modify/
  upgrade/scale), and integration with ``aos-client-sdk`` and ``aos-kernel``
* **Reliability** (``reliability_check()``) — drift detection, SLA-aware
  health monitoring, and DR readiness assessment

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
from orchestrator.automation.lifecycle import LifecycleManager
from orchestrator.automation.pipeline import PipelineManager
from orchestrator.governance.cost_manager import CostManager
from orchestrator.governance.policy_manager import PolicyManager
from orchestrator.governance.rbac_manager import RbacManager
from orchestrator.integration.kernel_bridge import KernelBridge
from orchestrator.integration.sdk_bridge import SDKBridge
from orchestrator.reliability.drift_detector import DriftDetector
from orchestrator.reliability.health_monitor import HealthMonitor, HealthStatus

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
        """Full deployment pipeline: lint → validate → what-if → deploy → health-check.

        When governance or reliability settings are enabled in the config,
        the appropriate post-deployment lifecycle steps are also executed.
        """
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

        # --- Post-deploy lifecycle pillars ---
        # Governance and reliability hooks are advisory: their findings are
        # audit-logged and printed, but they do not fail the deployment itself.
        # To gate deployments on pillar results, call govern() / automate() /
        # reliability_check() as separate pipeline steps with explicit failure
        # conditions.
        if self.config.governance.enforce_policies:
            self._run_governance_pillar()
        if self.config.automation.deploy_function_apps or self.config.automation.sync_kernel_config:
            # Run only the SDK/kernel integration steps (pipeline already completed)
            auto = self.config.automation
            if auto.deploy_function_apps:
                bridge = SDKBridge(
                    resource_group=self.config.resource_group,
                    environment=self.config.environment,
                    subscription_id=self.config.subscription_id,
                    location=self.config.location,
                    app_names=auto.app_names or None,
                )
                bridge.deploy_function_apps()
            if auto.sync_kernel_config:
                kb = KernelBridge(
                    resource_group=self.config.resource_group,
                    subscription_id=self.config.subscription_id,
                )
                kb.validate_kernel_config(kb.extract_kernel_env())
        if self.config.reliability.enable_drift_detection or self.config.reliability.check_dr_readiness:
            self._run_reliability_pillar()

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
    # Governance pillar — public entrypoint
    # ------------------------------------------------------------------

    def govern(self) -> bool:
        """Run the full Governance lifecycle pillar.

        Executes in order:
        1. Policy compliance evaluation
        2. Required-tag enforcement (when configured)
        3. Budget status check (when configured)
        4. Privileged-access review (when configured)

        Returns ``True`` when all checks pass (or produce only warnings).
        """
        print(f"\n{'=' * 60}")
        print("  Pillar: Governance")
        print(f"{'=' * 60}")
        return self._run_governance_pillar()

    # ------------------------------------------------------------------
    # Reliability pillar — public entrypoint
    # ------------------------------------------------------------------

    def reliability_check(self) -> bool:
        """Run the full Reliability lifecycle pillar.

        Executes in order:
        1. Enhanced health monitoring with SLA compliance
        2. Drift detection (template what-if or manifest comparison)
        3. DR readiness assessment (when configured)

        Returns ``True`` when the environment is healthy and SLA-compliant.
        """
        print(f"\n{'=' * 60}")
        print("  Pillar: Reliability")
        print(f"{'=' * 60}")
        return self._run_reliability_pillar()

    # ------------------------------------------------------------------
    # Automation pillar — public entrypoint
    # ------------------------------------------------------------------

    def automate(self) -> bool:
        """Run the full Automation lifecycle pillar.

        Executes in order:
        1. Formal pipeline (lint → validate → what-if → deploy → health-check)
           using :class:`~orchestrator.automation.pipeline.PipelineManager`
        2. Function App deployment via the SDK bridge (when configured)
        3. Kernel config sync to all Function Apps (when configured)
        4. Infrastructure lifecycle operations (deprovision/shift/modify/
           upgrade/scale) when ``enable_lifecycle_ops`` is set

        Returns ``True`` when all configured steps succeed.
        """
        print(f"\n{'=' * 60}")
        print("  Pillar: Automation")
        print(f"{'=' * 60}")
        return self._run_automation_pillar()

    # ------------------------------------------------------------------
    # Private helpers — three-pillar lifecycle
    # ------------------------------------------------------------------

    def _run_automation_pillar(self) -> bool:
        """Execute the Automation pillar steps."""
        auto = self.config.automation
        all_ok = True

        # 1. Formal pipeline via PipelineManager
        pm = PipelineManager(
            resource_group=self.config.resource_group,
            environment=self.config.environment,
            location=self.config.location,
            template=self.config.template,
            parameters_file=self.config.parameters_file,
            location_ml=self.config.location_ml,
            git_sha=self.config.git_sha,
            subscription_id=self.config.subscription_id,
        )
        pipeline_ok = pm.full_deploy(
            allow_warnings=self.config.allow_warnings,
            skip_health=self.config.skip_health,
        )
        if not pipeline_ok:
            self._audit("automate", {"step": "pipeline", "status": "failed"})
            return False

        # 2. SDK bridge — deploy Function Apps
        if auto.deploy_function_apps:
            bridge = SDKBridge(
                resource_group=self.config.resource_group,
                environment=self.config.environment,
                subscription_id=self.config.subscription_id,
                location=self.config.location,
                app_names=auto.app_names or None,
            )
            print("\n  📦 Deploying Function Apps via SDK bridge …")
            statuses = bridge.deploy_function_apps()
            failed_apps = [s.app_name for s in statuses if s.status == "failed"]
            if failed_apps:
                print(f"  ⚠️  {len(failed_apps)} app(s) failed: {', '.join(failed_apps)}")
                all_ok = False

        # 3. Kernel config sync
        if auto.sync_kernel_config:
            kb = KernelBridge(
                resource_group=self.config.resource_group,
                subscription_id=self.config.subscription_id,
            )
            print("\n  🔗 Syncing kernel config …")
            env_vars = kb.extract_kernel_env()
            kb.validate_kernel_config(env_vars)

        self._audit("automate", {"status": "ok" if all_ok else "warnings"})
        return all_ok

    def _run_governance_pillar(self) -> bool:
        """Execute the Governance pillar steps."""
        gov = self.config.governance
        pm = PolicyManager(self.config.resource_group, self.config.subscription_id)
        cm = CostManager(self.config.resource_group, self.config.subscription_id)

        all_ok = True

        # 1. Policy compliance
        summary = pm.evaluate_compliance()
        if summary["non_compliant"] > 0:
            print(f"  ⚠️  {summary['non_compliant']} non-compliant policy state(s)")
            all_ok = False

        # 2. Required tag enforcement
        if gov.required_tags:
            missing = pm.enforce_required_tags(gov.required_tags)
            if any(missing.values()):
                all_ok = False

        # 3. Budget status
        if gov.budget_amount > 0:
            alerts = cm.check_budget_alerts()
            if alerts:
                print(f"  ⚠️  Budget alert(s): {', '.join(alerts)}")

        # 4. RBAC access review
        if gov.review_rbac:
            rm = RbacManager(self.config.resource_group, self.config.subscription_id)
            findings = rm.review_privileged_access()
            if findings:
                print(f"  ⚠️  {len(findings)} privileged-access finding(s)")

        self._audit("govern", {"status": "ok" if all_ok else "warnings", **summary})
        return all_ok

    def _run_reliability_pillar(self) -> bool:
        """Execute the Reliability pillar steps."""
        rel = self.config.reliability
        hm = HealthMonitor(self.config.resource_group, self.config.environment)
        dd = DriftDetector(self.config.resource_group)

        # 1. Health + SLA compliance
        overall, _ = hm.check_all()
        sla = hm.check_sla_compliance()
        healthy = overall in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

        # 2. Drift detection
        drift_findings: list[Any] = []
        if rel.enable_drift_detection:
            if rel.drift_manifest:
                drift_findings = dd.detect_drift_from_manifest(rel.drift_manifest)
            elif self.config.template:
                drift_findings = dd.detect_drift(
                    self.config.template,
                    self.config.parameters_file,
                )

        # 3. DR readiness
        dr: dict[str, Any] = {}
        if rel.check_dr_readiness:
            dr = hm.check_disaster_recovery_readiness()

        self._audit("reliability", {
            "health": overall.value,
            "sla_compliant": sla["compliant"],
            "drift_findings": len(drift_findings),
            "dr_ready": dr.get("ready", None),
        })
        return healthy and sla["compliant"]

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
