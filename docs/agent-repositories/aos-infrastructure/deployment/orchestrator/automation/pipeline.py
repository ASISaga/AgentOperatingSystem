"""Automation pillar — formal deployment pipeline.

``PipelineManager`` encapsulates the sequential stages of the IaC deployment
pipeline (lint → validate → what-if → deploy → health-check).  It is the
formal code path for the Automation pillar, analogous to ``PolicyManager``
for Governance and ``HealthMonitor`` / ``DriftDetector`` for Reliability.

Each stage is independently invocable, enabling targeted re-runs and
fine-grained CI/CD gate control.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any


_SHA_RE = re.compile(r"^[a-fA-F0-9]{7,40}$")


class PipelineManager:
    """Manages the formal IaC deployment pipeline for AOS infrastructure.

    Stages
    ------
    1. **Lint** — ``az bicep build`` template syntax check
    2. **Validate** — ``az deployment group validate`` ARM pre-flight
    3. **What-If** — ``az deployment group what-if`` change preview
    4. **Deploy** — ``az deployment group create`` idempotent apply
    5. **Health-Check** — post-deploy resource state verification

    Each stage returns ``True`` on success and ``False`` on failure,
    allowing callers to short-circuit or continue with ``--allow-warnings``.
    """

    def __init__(
        self,
        resource_group: str,
        environment: str,
        location: str,
        template: str,
        parameters_file: str = "",
        location_ml: str = "",
        git_sha: str = "",
        subscription_id: str = "",
    ) -> None:
        self.resource_group = resource_group
        self.environment = environment
        self.location = location
        self.template = template
        self.parameters_file = parameters_file
        self.location_ml = location_ml or location
        self.git_sha = git_sha
        self.subscription_id = subscription_id

    # ------------------------------------------------------------------
    # Public pipeline stages
    # ------------------------------------------------------------------

    def lint(self) -> bool:
        """Stage 1 — Lint the Bicep template with ``az bicep build``."""
        if not self.template:
            print("  No template specified; skipping lint.")
            return True
        result = self._run(["az", "bicep", "build", "--file", self.template])
        ok = result.returncode == 0
        if not ok:
            print(f"  Lint failed: {result.stderr.strip()}", file=sys.stderr)
        return ok

    def validate(self) -> bool:
        """Stage 2 — Validate the template with ``az deployment group validate``."""
        result = self._run(self._deployment_cmd("validate"))
        ok = result.returncode == 0
        if not ok:
            print(f"  Validate failed: {result.stderr.strip()}", file=sys.stderr)
        return ok

    def what_if(self) -> bool:
        """Stage 3 — Preview changes with ``az deployment group what-if``."""
        result = self._run(self._deployment_cmd("what-if"))
        ok = result.returncode == 0
        if not ok:
            print(f"  What-If failed: {result.stderr.strip()}", file=sys.stderr)
        return ok

    def deploy(self) -> bool:
        """Stage 4 — Apply changes with ``az deployment group create``."""
        result = self._run(self._deployment_cmd("create"))
        ok = result.returncode == 0
        if not ok:
            print(f"  Deploy failed: {result.stderr.strip()}", file=sys.stderr)
        return ok

    def health_check(self) -> bool:
        """Stage 5 — Verify all resources reached ``Succeeded`` provisioning state."""
        output = self._az([
            "resource", "list",
            "--resource-group", self.resource_group,
            "--query", "[].{name:name, state:provisioningState}",
            "--output", "json",
        ])
        if output is None:
            return False
        resources = json.loads(output)
        all_ok = True
        for res in resources:
            state = res.get("state", "Unknown")
            if state != "Succeeded":
                print(f"  ⚠️  {res.get('name')}: {state}", file=sys.stderr)
                all_ok = False
            else:
                print(f"  ✅ {res.get('name')}: {state}")
        return all_ok

    # ------------------------------------------------------------------
    # Composite workflows
    # ------------------------------------------------------------------

    def plan(self, allow_warnings: bool = False) -> bool:
        """Lint + Validate + What-If (no infrastructure changes)."""
        for label, fn in [("Lint", self.lint), ("Validate", self.validate), ("What-If", self.what_if)]:
            ok = fn()
            if not ok and not allow_warnings:
                print(f"  ❌ {label} failed — stopping plan")
                return False
            print(f"  ✅ {label} passed")
        print("  📋 Plan complete — no resources were modified")
        return True

    def full_deploy(
        self,
        allow_warnings: bool = False,
        skip_health: bool = False,
    ) -> bool:
        """Lint + Validate + What-If + Deploy [+ Health-Check].

        Parameters
        ----------
        allow_warnings:
            Continue past lint/validate failures with a warning.
        skip_health:
            Skip the post-deploy health-check stage.
        """
        stages = [
            ("Lint", self.lint),
            ("Validate", self.validate),
            ("What-If", self.what_if),
            ("Deploy", self.deploy),
        ]
        if not skip_health:
            stages.append(("Health-Check", self.health_check))

        for label, fn in stages:
            ok = fn()
            if not ok:
                if label in ("Lint", "Validate") and allow_warnings:
                    print(f"  ⚠️  {label} had warnings — continuing")
                else:
                    print(f"  ❌ {label} failed — aborting")
                    return False
            print(f"  ✅ {label} succeeded")
        return True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _deployment_cmd(self, action: str) -> list[str]:
        cmd = [
            "az", "deployment", "group", action,
            "--resource-group", self.resource_group,
            "--template-file", self.template,
            "--output", "json",
        ]
        if self.parameters_file:
            cmd += ["--parameters", self.parameters_file]
        overrides: list[str] = [
            f"environment={self.environment}",
            f"location={self.location}",
        ]
        if self.location_ml:
            overrides.append(f"locationML={self.location_ml}")
        if self.git_sha and _SHA_RE.match(self.git_sha):
            overrides.append(f"tags={{gitSha:'{self.git_sha}'}}")
        cmd += ["--parameters"] + overrides
        return cmd

    def _az(self, args: list[str]) -> str | None:
        result = self._run(["az"] + args)
        if result.returncode != 0:
            print(f"  az command failed (rc={result.returncode}): {result.stderr.strip()}", file=sys.stderr)
            return None
        return result.stdout

    @staticmethod
    def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
