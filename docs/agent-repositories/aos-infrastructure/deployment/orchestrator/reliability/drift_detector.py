"""Reliability pillar — Infrastructure drift detection.

``DriftDetector`` compares the desired state (captured from a Bicep
what-if or a saved manifest) with the live Azure resource state to
identify configuration drift.  Drift is reported as a list of findings
categorised as ``missing``, ``unexpected``, or ``changed``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DriftKind(str, Enum):
    """Classification of a drift finding."""

    MISSING = "missing"          # Resource expected but not found
    UNEXPECTED = "unexpected"    # Resource found but not expected
    CHANGED = "changed"          # Resource found but properties differ


@dataclass
class DriftFinding:
    """A single infrastructure drift finding."""

    kind: DriftKind
    resource_name: str
    resource_type: str
    expected: dict[str, Any] = field(default_factory=dict)
    actual: dict[str, Any] = field(default_factory=dict)
    details: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "resource_name": self.resource_name,
            "resource_type": self.resource_type,
            "details": self.details,
        }


# Properties that are monitored for change (lowercase)
_MONITORED_PROPERTIES: set[str] = {
    "location",
    "sku",
    "kind",
    "properties.provisioningstate",
    "tags",
}


class DriftDetector:
    """Detects configuration drift between desired and live Azure infrastructure."""

    def __init__(self, resource_group: str) -> None:
        self.resource_group = resource_group

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_drift(
        self,
        template_file: str,
        parameters_file: str = "",
    ) -> list[DriftFinding]:
        """Detect drift by running a Bicep what-if and parsing the results.

        Returns a list of :class:`DriftFinding` objects categorised by kind.
        Any ``noChange`` result is not a finding.
        """
        print(f"🔍 Detecting infrastructure drift in {self.resource_group}")
        what_if = self._run_what_if(template_file, parameters_file)
        if what_if is None:
            print("  ⚠️  Could not run what-if; drift detection skipped.")
            return []

        findings = self._parse_what_if(what_if)
        self._report(findings)
        return findings

    def detect_drift_from_manifest(
        self, manifest: list[dict[str, Any]]
    ) -> list[DriftFinding]:
        """Detect drift by comparing a resource manifest against live state.

        ``manifest`` is a list of expected resource dicts with at minimum
        ``name`` and ``type`` keys.
        """
        print(f"🔍 Detecting drift from manifest in {self.resource_group}")
        live = self._list_live_resources()
        if live is None:
            return []

        live_by_name = {r["name"].lower(): r for r in live}
        expected_by_name = {r["name"].lower(): r for r in manifest}

        findings: list[DriftFinding] = []

        # Missing resources
        for name, expected in expected_by_name.items():
            if name not in live_by_name:
                findings.append(DriftFinding(
                    kind=DriftKind.MISSING,
                    resource_name=expected.get("name", name),
                    resource_type=expected.get("type", "Unknown"),
                    expected=expected,
                    details=f"Resource '{expected.get('name', name)}' is missing from Azure.",
                ))

        # Unexpected resources
        for name, actual in live_by_name.items():
            if name not in expected_by_name:
                findings.append(DriftFinding(
                    kind=DriftKind.UNEXPECTED,
                    resource_name=actual.get("name", name),
                    resource_type=actual.get("type", "Unknown"),
                    actual=actual,
                    details=f"Resource '{actual.get('name', name)}' exists in Azure but not in manifest.",
                ))

        # Changed resources (location or tags differ)
        for name in set(expected_by_name) & set(live_by_name):
            exp = expected_by_name[name]
            act = live_by_name[name]
            diffs = self._compare(exp, act)
            if diffs:
                findings.append(DriftFinding(
                    kind=DriftKind.CHANGED,
                    resource_name=act.get("name", name),
                    resource_type=act.get("type", "Unknown"),
                    expected=exp,
                    actual=act,
                    details="; ".join(diffs),
                ))

        self._report(findings)
        return findings

    def snapshot_state(self) -> list[dict[str, Any]]:
        """Return a snapshot of all live resources as a drift manifest."""
        live = self._list_live_resources()
        if live is None:
            return []
        snapshot = [
            {"name": r.get("name"), "type": r.get("type"), "location": r.get("location")}
            for r in live
        ]
        print(f"  📸 Snapshot: {len(snapshot)} resources in {self.resource_group}")
        return snapshot

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_what_if(self, template_file: str, parameters_file: str) -> dict[str, Any] | None:
        """Run ``az deployment group what-if`` and return the JSON result."""
        cmd = [
            "az", "deployment", "group", "what-if",
            "--resource-group", self.resource_group,
            "--template-file", template_file,
            "--output", "json",
        ]
        if parameters_file:
            cmd += ["--parameters", parameters_file]
        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        if result.returncode != 0:
            print(f"  az what-if failed: {result.stderr.strip()}", file=sys.stderr)
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    def _list_live_resources(self) -> list[dict[str, Any]] | None:
        """List all live resources in the resource group."""
        result = subprocess.run(
            [
                "az", "resource", "list",
                "--resource-group", self.resource_group,
                "--output", "json",
            ],
            capture_output=True, text=True,
        )  # noqa: S603
        if result.returncode != 0:
            print(f"  az resource list failed: {result.stderr.strip()}", file=sys.stderr)
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _parse_what_if(what_if_output: dict[str, Any]) -> list[DriftFinding]:
        """Parse ``az deployment group what-if`` JSON into DriftFindings."""
        findings: list[DriftFinding] = []
        changes = what_if_output.get("changes", [])
        for change in changes:
            change_type = change.get("changeType", "NoChange")
            resource_id = change.get("resourceId", "")
            parts = resource_id.split("/")
            name = parts[-1] if parts else resource_id
            rtype = "/".join(parts[-3:-1]) if len(parts) >= 3 else "Unknown"

            if change_type == "Create":
                findings.append(DriftFinding(
                    kind=DriftKind.MISSING,
                    resource_name=name,
                    resource_type=rtype,
                    details=f"Resource '{name}' will be created (missing from live state).",
                ))
            elif change_type == "Delete":
                findings.append(DriftFinding(
                    kind=DriftKind.UNEXPECTED,
                    resource_name=name,
                    resource_type=rtype,
                    details=f"Resource '{name}' will be deleted (not in template).",
                ))
            elif change_type in ("Modify", "Deploy"):
                # "Modify" — ARM will change one or more resource properties.
                # "Deploy" — ARM will re-deploy the resource without detectable changes
                # (can indicate a configuration re-application due to out-of-band drift).
                delta = change.get("delta", [])
                diffs = [
                    f"{d.get('path', '?')}: {d.get('before', '?')} → {d.get('after', '?')}"
                    for d in delta
                ]
                findings.append(DriftFinding(
                    kind=DriftKind.CHANGED,
                    resource_name=name,
                    resource_type=rtype,
                    details="; ".join(diffs) if diffs else f"'{name}' will be modified.",
                ))
        return findings

    @staticmethod
    def _compare(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
        """Return a list of human-readable differences between expected and actual."""
        diffs: list[str] = []
        for key in ("location", "tags"):
            exp_val = expected.get(key)
            act_val = actual.get(key)
            if exp_val is not None and exp_val != act_val:
                diffs.append(f"{key}: expected={exp_val!r}, actual={act_val!r}")
        return diffs

    @staticmethod
    def _report(findings: list[DriftFinding]) -> None:
        if not findings:
            print("  ✅ No drift detected.")
            return
        missing = sum(1 for f in findings if f.kind == DriftKind.MISSING)
        unexpected = sum(1 for f in findings if f.kind == DriftKind.UNEXPECTED)
        changed = sum(1 for f in findings if f.kind == DriftKind.CHANGED)
        print(
            f"\n  Drift summary: {len(findings)} finding(s) — "
            f"{missing} missing, {unexpected} unexpected, {changed} changed"
        )
        for f in findings:
            icon = {"missing": "❌", "unexpected": "⚠️", "changed": "🔄"}.get(f.kind.value, "❓")
            print(f"    {icon} [{f.kind.value.upper()}] {f.resource_name} ({f.resource_type}): {f.details}")
