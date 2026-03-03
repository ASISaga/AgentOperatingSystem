"""Governance pillar — Azure RBAC assignment and access review.

``RbacManager`` manages role assignments on AOS resource groups and
managed identities, and can report on over-privileged principals.
It uses ``az role assignment`` commands via subprocess.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


# AOS standard role mappings: principal type → minimum required role
_AOS_REQUIRED_ROLES: dict[str, str] = {
    "aos-dispatcher": "Contributor",
    "aos-realm-of-agents": "Contributor",
    "aos-mcp-servers": "Reader",
    "aos-infrastructure": "Owner",
}

# Roles considered over-privileged for non-deployment principals
_PRIVILEGED_ROLES: set[str] = {
    "Owner",
    "User Access Administrator",
    "Security Admin",
}

# Built-in role definition IDs
_ROLE_DEFINITION_IDS: dict[str, str] = {
    "Owner": "8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
    "Contributor": "b24988ac-6180-42a0-ab88-20f7382dd24c",
    "Reader": "acdd72a7-3385-48ef-bd42-f606fba81ae7",
    "Cognitive Services User": "a97b65f3-24c7-4388-baec-2e87135dc908",
    "Storage Blob Data Contributor": "ba92f5b4-2d11-453d-a403-e96b0029c9fe",
    "Key Vault Secrets User": "4633458b-17de-408a-b874-0445c86b69e6",
    "Service Bus Data Receiver": "4f6d3b9b-027b-4f4c-9142-0e5a2a2247e0",
    "Service Bus Data Sender": "69a216fc-b8fb-44d8-bc22-1f3c2cd27a39",
}


class RbacManager:
    """Manages Azure RBAC assignments and access reviews for AOS."""

    def __init__(self, resource_group: str, subscription_id: str = "") -> None:
        self.resource_group = resource_group
        self.subscription_id = subscription_id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_assignments(self) -> list[dict[str, Any]]:
        """Return all role assignments for the resource group."""
        result = self._az([
            "role", "assignment", "list",
            "--resource-group", self.resource_group,
            "--output", "json",
        ])
        if result is None:
            return []
        assignments: list[dict[str, Any]] = json.loads(result)
        print(f"  Found {len(assignments)} role assignments in {self.resource_group}")
        for a in assignments:
            principal = a.get("principalName", a.get("principalId", "N/A"))
            role = a.get("roleDefinitionName", "N/A")
            print(f"    {principal}: {role}")
        return assignments

    def assign_role(
        self,
        principal_id: str,
        role_name: str,
        principal_type: str = "ServicePrincipal",
    ) -> bool:
        """Assign a built-in role to a principal on the resource group.

        Parameters
        ----------
        principal_id:
            Object ID of the principal (user, group, or service principal).
        role_name:
            Built-in role name (e.g., ``"Contributor"``).
        principal_type:
            Type of the principal: ``"User"``, ``"Group"``, or
            ``"ServicePrincipal"`` (default).
        """
        role_id = _ROLE_DEFINITION_IDS.get(role_name)
        if role_id is None:
            print(f"  ⚠️  Unknown role '{role_name}'; using role name directly")

        cmd = [
            "az", "role", "assignment", "create",
            "--assignee-object-id", principal_id,
            "--assignee-principal-type", principal_type,
            "--role", role_id or role_name,
            "--resource-group", self.resource_group,
            "--output", "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        ok = result.returncode == 0
        icon = "✅" if ok else "⚠️"
        print(f"  {icon} Assign '{role_name}' to {principal_id}: {'ok' if ok else 'failed'}")
        return ok

    def remove_role(self, principal_id: str, role_name: str) -> bool:
        """Remove a role assignment from a principal on the resource group."""
        role_id = _ROLE_DEFINITION_IDS.get(role_name)
        cmd = [
            "az", "role", "assignment", "delete",
            "--assignee", principal_id,
            "--role", role_id or role_name,
            "--resource-group", self.resource_group,
            "--output", "json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        ok = result.returncode == 0
        icon = "✅" if ok else "⚠️"
        print(f"  {icon} Remove '{role_name}' from {principal_id}: {'ok' if ok else 'failed'}")
        return ok

    def review_privileged_access(self) -> list[dict[str, Any]]:
        """Return role assignments where a non-deployment principal holds a privileged role.

        Returns a list of dicts with keys: ``principal``, ``role``, ``recommendation``.
        """
        print(f"🔐 Reviewing privileged access in {self.resource_group}")
        assignments = self.list_assignments()
        findings: list[dict[str, Any]] = []
        for a in assignments:
            role = a.get("roleDefinitionName", "")
            principal = a.get("principalName", a.get("principalId", "N/A"))
            ptype = a.get("principalType", "")

            if role in _PRIVILEGED_ROLES and ptype != "ServicePrincipal":
                findings.append({
                    "principal": principal,
                    "role": role,
                    "recommendation": (
                        f"Review whether '{principal}' requires '{role}'. "
                        "Consider downgrading to 'Contributor' or lower."
                    ),
                })

        if findings:
            print(f"  ⚠️  {len(findings)} privileged access finding(s):")
            for f in findings:
                print(f"    • {f['principal']} ({f['role']}): {f['recommendation']}")
        else:
            print("  ✅ No privileged access concerns found.")
        return findings

    def enforce_least_privilege(self, aos_component: str, principal_id: str) -> bool:
        """Ensure a principal holds exactly the minimum required role for a component.

        Removes over-privileged assignments before granting the correct role.
        """
        required_role = _AOS_REQUIRED_ROLES.get(aos_component)
        if not required_role:
            print(f"  ⚠️  No minimum role defined for component '{aos_component}'")
            return False

        print(f"🔒 Enforcing least-privilege for '{aos_component}' on {self.resource_group}")

        # Remove over-privileged roles
        assignments = self.list_assignments()
        for a in assignments:
            pid = a.get("principalId", "")
            if pid != principal_id:
                continue
            role = a.get("roleDefinitionName", "")
            if role != required_role and role in _PRIVILEGED_ROLES:
                self.remove_role(principal_id, role)

        # Assign the required role
        return self.assign_role(principal_id, required_role)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _az(self, args: list[str]) -> str | None:
        """Run an ``az`` command and return stdout, or *None* on failure."""
        result = subprocess.run(["az"] + args, capture_output=True, text=True)  # noqa: S603
        if result.returncode != 0:
            print(f"  az command failed (rc={result.returncode})", file=sys.stderr)
            if result.stderr:
                print(f"  {result.stderr.strip()}", file=sys.stderr)
            return None
        return result.stdout
