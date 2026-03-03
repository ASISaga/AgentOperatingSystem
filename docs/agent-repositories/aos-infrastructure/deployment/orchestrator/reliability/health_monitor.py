"""Reliability pillar — Enhanced health monitoring with SLA tracking.

``HealthMonitor`` extends basic health checks with SLA objective tracking,
multi-resource deep health probes, and an availability summary for AOS
infrastructure.  It uses ``az`` commands to interrogate resource state.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Overall health status of a resource or the environment."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ResourceHealth:
    """Health state of a single Azure resource."""

    name: str
    resource_type: str
    status: HealthStatus
    provisioning_state: str = ""
    availability_state: str = ""
    details: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY


# SLA targets per environment (uptime percentage)
_SLA_TARGETS: dict[str, float] = {
    "dev": 99.0,
    "staging": 99.5,
    "prod": 99.9,
}

# Resource types that support Azure Resource Health
_RESOURCE_HEALTH_SUPPORTED: set[str] = {
    "microsoft.web/sites",
    "microsoft.storage/storageaccounts",
    "microsoft.servicebus/namespaces",
    "microsoft.keyvault/vaults",
    "microsoft.insights/components",
    "microsoft.machinelearningservices/workspaces",
    "microsoft.cognitiveservices/accounts",
    "microsoft.apimanagement/service",
}


class HealthMonitor:
    """Monitors AOS infrastructure health and tracks SLA compliance."""

    def __init__(self, resource_group: str, environment: str = "dev") -> None:
        self.resource_group = resource_group
        self.environment = environment
        self.sla_target = _SLA_TARGETS.get(environment, 99.0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_all(self) -> tuple[HealthStatus, list[ResourceHealth]]:
        """Run a full health check across all resources in the resource group.

        Returns ``(overall_status, resource_healths)``.
        """
        print(f"🏥 Running full health check for {self.resource_group} ({self.environment})")
        resources = self._list_resources()
        if not resources:
            print("  No resources found.")
            return HealthStatus.UNKNOWN, []

        healths: list[ResourceHealth] = []
        for res in resources:
            h = self._check_resource(res)
            healths.append(h)

        overall = self._aggregate_status(healths)
        self._print_health_report(healths, overall)
        return overall, healths

    def check_sla_compliance(self, observed_uptime_pct: float | None = None) -> dict[str, Any]:
        """Report SLA compliance for the environment.

        Parameters
        ----------
        observed_uptime_pct:
            Optional uptime percentage from an external monitoring system.
            If not provided, derives it from the current resource health.

        Returns a dict with keys:
        - ``environment``: the environment name
        - ``sla_target``: target uptime percentage
        - ``observed_uptime``: measured uptime percentage
        - ``compliant``: whether SLA is met
        - ``gap``: how far above/below target (positive = above)
        """
        print(f"📈 SLA compliance check for {self.resource_group} "
              f"(target: {self.sla_target}%)")

        if observed_uptime_pct is None:
            _, healths = self.check_all()
            if not healths:
                observed_uptime_pct = 0.0
            else:
                healthy_count = sum(1 for h in healths if h.is_healthy())
                observed_uptime_pct = 100.0 * healthy_count / len(healths)

        compliant = observed_uptime_pct >= self.sla_target
        gap = round(observed_uptime_pct - self.sla_target, 3)

        result = {
            "environment": self.environment,
            "sla_target": self.sla_target,
            "observed_uptime": round(observed_uptime_pct, 3),
            "compliant": compliant,
            "gap": gap,
        }
        icon = "✅" if compliant else "❌"
        print(f"  {icon} Uptime: {observed_uptime_pct:.2f}% "
              f"(target: {self.sla_target}%, gap: {gap:+.3f}%)")
        return result

    def check_disaster_recovery_readiness(self) -> dict[str, Any]:
        """Assess DR readiness: backup state, geo-replication, and soft-delete status.

        Returns a summary dict with a boolean ``ready`` flag and a list of
        ``findings``.
        """
        print(f"🆘 DR readiness check for {self.resource_group}")
        findings: list[str] = []

        # Check Key Vault soft-delete / purge protection
        kv_ok = self._check_keyvault_dr()
        if not kv_ok:
            findings.append("Key Vault: soft-delete or purge protection not enabled")

        # Check Storage geo-redundancy
        st_ok = self._check_storage_geo()
        if not st_ok:
            findings.append("Storage: no geo-redundant accounts found (consider GRS/GZRS for prod)")

        ready = len(findings) == 0
        icon = "✅" if ready else "⚠️"
        print(f"  {icon} DR readiness: {'ready' if ready else 'action required'}")
        for f in findings:
            print(f"    • {f}")
        return {"ready": ready, "findings": findings}

    def get_resource_health(self, resource_name: str) -> ResourceHealth | None:
        """Return the health state of a specific named resource."""
        resources = self._list_resources()
        for res in resources:
            if res.get("name", "").lower() == resource_name.lower():
                return self._check_resource(res)
        print(f"  ⚠️  Resource '{resource_name}' not found in {self.resource_group}")
        return None

    # ------------------------------------------------------------------
    # Private helpers — per-resource checks
    # ------------------------------------------------------------------

    def _check_resource(self, res: dict[str, Any]) -> ResourceHealth:
        """Derive a :class:`ResourceHealth` for a single resource dict."""
        name = res.get("name", "N/A")
        rtype = (res.get("type") or "").lower()
        pstate = res.get("provisioningState", "Unknown")

        status = HealthStatus.HEALTHY if pstate == "Succeeded" else (
            HealthStatus.UNHEALTHY if pstate in ("Failed", "Canceled") else HealthStatus.DEGRADED
        )

        availability_state = ""
        if rtype in _RESOURCE_HEALTH_SUPPORTED:
            availability_state = self._query_resource_health(res.get("id", ""))

        return ResourceHealth(
            name=name,
            resource_type=rtype,
            status=status,
            provisioning_state=pstate,
            availability_state=availability_state,
            details=f"provisioningState={pstate}",
        )

    def _query_resource_health(self, resource_id: str) -> str:
        """Query Azure Resource Health for a specific resource ID."""
        if not resource_id:
            return ""
        result = subprocess.run(
            [
                "az", "rest",
                "--method", "GET",
                "--url", (
                    f"{resource_id}/providers/Microsoft.ResourceHealth"
                    "/availabilityStatuses/current?api-version=2022-10-01"
                ),
                "--output", "json",
            ],
            capture_output=True, text=True,
        )  # noqa: S603
        if result.returncode != 0:
            return ""
        try:
            data = json.loads(result.stdout)
            return data.get("properties", {}).get("availabilityState", "")
        except json.JSONDecodeError:
            return ""

    def _check_keyvault_dr(self) -> bool:
        """Return True if at least one Key Vault has soft-delete + purge protection."""
        result = subprocess.run(
            [
                "az", "keyvault", "list",
                "--resource-group", self.resource_group,
                "--query",
                "[?properties.enableSoftDelete && properties.enablePurgeProtection].name",
                "--output", "json",
            ],
            capture_output=True, text=True,
        )  # noqa: S603
        if result.returncode != 0:
            return False
        try:
            vaults = json.loads(result.stdout)
            return len(vaults) > 0
        except json.JSONDecodeError:
            return False

    def _check_storage_geo(self) -> bool:
        """Return True if at least one geo-redundant storage account exists."""
        result = subprocess.run(
            [
                "az", "storage", "account", "list",
                "--resource-group", self.resource_group,
                "--query",
                "[?sku.name=='Standard_GRS' || sku.name=='Standard_RAGRS' "
                "|| sku.name=='Standard_GZRS' || sku.name=='Standard_RAGZRS'].name",
                "--output", "json",
            ],
            capture_output=True, text=True,
        )  # noqa: S603
        if result.returncode != 0:
            return False
        try:
            accounts = json.loads(result.stdout)
            return len(accounts) > 0
        except json.JSONDecodeError:
            return False

    def _list_resources(self) -> list[dict[str, Any]]:
        """Return a list of all resources in the resource group."""
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
            return []
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []

    # ------------------------------------------------------------------
    # Private helpers — display
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate_status(healths: list[ResourceHealth]) -> HealthStatus:
        if not healths:
            return HealthStatus.UNKNOWN
        statuses = {h.status for h in healths}
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    @staticmethod
    def _print_health_report(
        healths: list[ResourceHealth], overall: HealthStatus
    ) -> None:
        icons = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.UNKNOWN: "❓",
        }
        print(f"\n  Overall: {icons[overall]} {overall.value.upper()}")
        for h in healths:
            avail = f" [{h.availability_state}]" if h.availability_state else ""
            print(f"  {icons[h.status]} {h.name} ({h.resource_type}): "
                  f"{h.provisioning_state}{avail}")
