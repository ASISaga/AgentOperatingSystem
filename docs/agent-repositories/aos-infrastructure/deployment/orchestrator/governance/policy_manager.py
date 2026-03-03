"""Governance pillar — Azure Policy enforcement and compliance.

``PolicyManager`` evaluates policy compliance for a resource group,
assigns built-in policy initiatives, and reports non-compliant resources.
All policy operations use ``az policy`` commands via subprocess.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


# Built-in AOS governance policy definitions (initiative/policy display names)
_AOS_BUILT_IN_POLICIES: list[dict[str, str]] = [
    {
        "name": "tag-environment",
        "displayName": "Require environment tag on resources",
        "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/871b6d14-10aa-478d-b590-94f262ecfa99",
    },
    {
        "name": "allowed-locations",
        "displayName": "Allowed locations for resources",
        "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c",
    },
    {
        "name": "require-https-storage",
        "displayName": "Secure transfer to storage accounts should be enabled",
        "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9",
    },
    {
        "name": "keyvault-soft-delete",
        "displayName": "Key vaults should have soft delete enabled",
        "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d",
    },
    {
        "name": "servicebus-private-endpoint",
        "displayName": "Azure Service Bus namespaces should use private link",
        "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/1c06e275-d63d-4540-b761-71f364c2111d",
    },
]

# Compliance state constants
_STATE_COMPLIANT = "Compliant"
_STATE_NON_COMPLIANT = "NonCompliant"


class PolicyManager:
    """Manages Azure Policy assignments and compliance evaluation for AOS."""

    def __init__(self, resource_group: str, subscription_id: str = "") -> None:
        self.resource_group = resource_group
        self.subscription_id = subscription_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate_compliance(self) -> dict[str, Any]:
        """Return a compliance summary for the resource group.

        Returns a dict with keys:
        - ``total``: total policy states queried
        - ``compliant``: count of compliant states
        - ``non_compliant``: count of non-compliant states
        - ``violations``: list of non-compliant resource details
        """
        print(f"🔍 Evaluating policy compliance for {self.resource_group}")
        result = self._az([
            "policy", "state", "list",
            "--resource-group", self.resource_group,
            "--output", "json",
        ])
        if result is None:
            return {"total": 0, "compliant": 0, "non_compliant": 0, "violations": []}

        states: list[dict[str, Any]] = json.loads(result)
        total = len(states)
        compliant = sum(1 for s in states if s.get("complianceState") == _STATE_COMPLIANT)
        non_compliant = total - compliant
        violations = [
            {
                "resource": s.get("resourceId", "N/A"),
                "policy": s.get("policyDefinitionName", "N/A"),
                "state": s.get("complianceState", "N/A"),
            }
            for s in states
            if s.get("complianceState") != _STATE_COMPLIANT
        ]
        summary = {
            "total": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "violations": violations,
        }
        self._print_summary(summary)
        return summary

    def assign_aos_policies(self, environment: str, allowed_locations: list[str] | None = None) -> bool:
        """Assign the standard AOS governance policies to the resource group.

        Returns ``True`` if all assignments succeed (or already exist).
        """
        print(f"📋 Assigning AOS governance policies to {self.resource_group}")
        scope = self._scope()
        all_ok = True
        for policy in _AOS_BUILT_IN_POLICIES:
            ok = self._assign_policy(
                policy["name"],
                policy["policyDefinitionId"],
                scope,
                environment=environment,
                allowed_locations=allowed_locations or [],
            )
            icon = "✅" if ok else "⚠️"
            print(f"  {icon} {policy['displayName']}")
            if not ok:
                all_ok = False
        return all_ok

    def enforce_required_tags(self, required_tags: dict[str, str]) -> dict[str, list[str]]:
        """Identify resources in the resource group that are missing required tags.

        Returns a dict mapping tag key → list of resource names missing that tag.
        """
        print(f"🏷️  Checking required tags in {self.resource_group}")
        result = self._az([
            "resource", "list",
            "--resource-group", self.resource_group,
            "--output", "json",
        ])
        if result is None:
            return {}

        resources: list[dict[str, Any]] = json.loads(result)
        missing: dict[str, list[str]] = {tag: [] for tag in required_tags}
        for res in resources:
            resource_tags: dict[str, str] = res.get("tags") or {}
            name = res.get("name", "N/A")
            for tag_key, _ in required_tags.items():
                if tag_key not in resource_tags:
                    missing[tag_key].append(name)

        for tag_key, resources_missing in missing.items():
            if resources_missing:
                print(f"  ⚠️  Missing tag '{tag_key}': {', '.join(resources_missing)}")
            else:
                print(f"  ✅ Tag '{tag_key}': all resources compliant")
        return missing

    def get_policy_assignments(self) -> list[dict[str, Any]]:
        """Return all policy assignments for the resource group."""
        result = self._az([
            "policy", "assignment", "list",
            "--resource-group", self.resource_group,
            "--output", "json",
        ])
        if result is None:
            return []
        return json.loads(result)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assign_policy(
        self,
        name: str,
        definition_id: str,
        scope: str,
        environment: str,
        allowed_locations: list[str],
    ) -> bool:
        """Assign a single policy to the given scope."""
        cmd = [
            "az", "policy", "assignment", "create",
            "--name", f"aos-{name}-{environment}",
            "--policy", definition_id,
            "--scope", scope,
            "--output", "json",
        ]
        if allowed_locations and name == "allowed-locations":
            params = json.dumps({"listOfAllowedLocations": {"value": allowed_locations}})
            cmd += ["--params", params]

        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        return result.returncode == 0

    def _scope(self) -> str:
        """Build the policy scope string for the resource group."""
        if self.subscription_id:
            return (
                f"/subscriptions/{self.subscription_id}"
                f"/resourceGroups/{self.resource_group}"
            )
        # Fall back to querying the current subscription
        result = subprocess.run(
            ["az", "account", "show", "--query", "id", "--output", "tsv"],
            capture_output=True,
            text=True,
        )  # noqa: S603
        sub = result.stdout.strip() if result.returncode == 0 else "unknown"
        return f"/subscriptions/{sub}/resourceGroups/{self.resource_group}"

    def _az(self, args: list[str]) -> str | None:
        """Run an ``az`` command and return stdout, or *None* on failure."""
        result = subprocess.run(["az"] + args, capture_output=True, text=True)  # noqa: S603
        if result.returncode != 0:
            print(f"  az command failed (rc={result.returncode})", file=sys.stderr)
            if result.stderr:
                print(f"  {result.stderr.strip()}", file=sys.stderr)
            return None
        return result.stdout

    @staticmethod
    def _print_summary(summary: dict[str, Any]) -> None:
        total = summary["total"]
        compliant = summary["compliant"]
        non_compliant = summary["non_compliant"]
        print(f"\n  Policy compliance: {compliant}/{total} compliant "
              f"({non_compliant} non-compliant)")
        for v in summary["violations"][:10]:
            print(f"    ⚠️  {v['resource']} — {v['policy']}: {v['state']}")
