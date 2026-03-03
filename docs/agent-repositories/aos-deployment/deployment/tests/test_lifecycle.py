"""Tests for the Governance and Reliability pillars.

Covers PolicyManager, CostManager, RbacManager, DriftDetector, HealthMonitor,
and the updated DeploymentConfig / InfrastructureManager using mocked az calls.
"""

from __future__ import annotations

import json
import subprocess
from unittest import mock

import pytest

from orchestrator.core.config import DeploymentConfig, GovernanceConfig, ReliabilityConfig
from orchestrator.core.manager import InfrastructureManager
from orchestrator.governance.cost_manager import CostManager
from orchestrator.governance.policy_manager import PolicyManager
from orchestrator.governance.rbac_manager import RbacManager
from orchestrator.reliability.drift_detector import DriftDetector, DriftFinding, DriftKind
from orchestrator.reliability.health_monitor import HealthMonitor, HealthStatus, ResourceHealth


# ====================================================================
# GovernanceConfig / ReliabilityConfig — unit tests
# ====================================================================


class TestGovernanceConfig:
    def test_defaults(self) -> None:
        gc = GovernanceConfig()
        assert gc.enforce_policies is False
        assert gc.budget_amount == 0.0
        assert gc.required_tags == {}
        assert gc.review_rbac is False

    def test_custom_values(self) -> None:
        gc = GovernanceConfig(
            enforce_policies=True,
            budget_amount=500.0,
            required_tags={"environment": "prod"},
            review_rbac=True,
            allowed_locations=["eastus", "westeurope"],
        )
        assert gc.enforce_policies is True
        assert gc.budget_amount == 500.0
        assert gc.required_tags == {"environment": "prod"}
        assert "eastus" in gc.allowed_locations


class TestReliabilityConfig:
    def test_defaults(self) -> None:
        rc = ReliabilityConfig()
        assert rc.enable_drift_detection is False
        assert rc.drift_manifest == []
        assert rc.sla_target is None
        assert rc.check_dr_readiness is False

    def test_custom_values(self) -> None:
        rc = ReliabilityConfig(
            enable_drift_detection=True,
            drift_manifest=[{"name": "res1", "type": "Microsoft.Storage/storageAccounts"}],
            sla_target=99.9,
            check_dr_readiness=True,
        )
        assert rc.enable_drift_detection is True
        assert len(rc.drift_manifest) == 1
        assert rc.sla_target == 99.9


class TestDeploymentConfigWithPillars:
    def test_default_pillar_configs(self) -> None:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
        )
        assert isinstance(cfg.governance, GovernanceConfig)
        assert isinstance(cfg.reliability, ReliabilityConfig)

    def test_governance_embedded(self) -> None:
        cfg = DeploymentConfig(
            environment="prod",
            resource_group="rg-prod",
            location="westeurope",
            governance=GovernanceConfig(enforce_policies=True, budget_amount=1000.0),
        )
        assert cfg.governance.enforce_policies is True
        assert cfg.governance.budget_amount == 1000.0

    def test_reliability_embedded(self) -> None:
        cfg = DeploymentConfig(
            environment="staging",
            resource_group="rg-stg",
            location="eastus",
            reliability=ReliabilityConfig(enable_drift_detection=True),
        )
        assert cfg.reliability.enable_drift_detection is True


# ====================================================================
# PolicyManager tests
# ====================================================================


class TestPolicyManager:
    @pytest.fixture()
    def pm(self) -> PolicyManager:
        return PolicyManager("rg-test", "sub-123")

    @mock.patch.object(PolicyManager, "_az")
    def test_evaluate_compliance_all_compliant(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        states = [
            {"complianceState": "Compliant", "resourceId": "/rg/res1", "policyDefinitionName": "p1"},
            {"complianceState": "Compliant", "resourceId": "/rg/res2", "policyDefinitionName": "p2"},
        ]
        mock_az.return_value = json.dumps(states)
        result = pm.evaluate_compliance()
        assert result["total"] == 2
        assert result["compliant"] == 2
        assert result["non_compliant"] == 0
        assert result["violations"] == []

    @mock.patch.object(PolicyManager, "_az")
    def test_evaluate_compliance_with_violations(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        states = [
            {"complianceState": "Compliant", "resourceId": "/rg/res1", "policyDefinitionName": "p1"},
            {"complianceState": "NonCompliant", "resourceId": "/rg/res2", "policyDefinitionName": "p2"},
        ]
        mock_az.return_value = json.dumps(states)
        result = pm.evaluate_compliance()
        assert result["non_compliant"] == 1
        assert len(result["violations"]) == 1
        assert result["violations"][0]["policy"] == "p2"

    @mock.patch.object(PolicyManager, "_az")
    def test_evaluate_compliance_az_failure(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        mock_az.return_value = None
        result = pm.evaluate_compliance()
        assert result == {"total": 0, "compliant": 0, "non_compliant": 0, "violations": []}

    @mock.patch.object(PolicyManager, "_az")
    def test_enforce_required_tags_all_present(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        resources = [
            {"name": "res1", "tags": {"environment": "dev", "team": "platform"}},
        ]
        mock_az.return_value = json.dumps(resources)
        missing = pm.enforce_required_tags({"environment": "dev", "team": "platform"})
        assert missing["environment"] == []
        assert missing["team"] == []

    @mock.patch.object(PolicyManager, "_az")
    def test_enforce_required_tags_missing(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        resources = [
            {"name": "res1", "tags": {}},
            {"name": "res2", "tags": {"environment": "dev"}},
        ]
        mock_az.return_value = json.dumps(resources)
        missing = pm.enforce_required_tags({"environment": "dev", "team": "platform"})
        assert "res1" in missing["environment"]
        assert "res1" in missing["team"]
        assert "res2" in missing["team"]

    @mock.patch.object(PolicyManager, "_az")
    def test_get_policy_assignments(self, mock_az: mock.Mock, pm: PolicyManager) -> None:
        mock_az.return_value = json.dumps([{"name": "aos-allowed-locations-dev"}])
        assignments = pm.get_policy_assignments()
        assert len(assignments) == 1


# ====================================================================
# CostManager tests
# ====================================================================


class TestCostManager:
    @pytest.fixture()
    def cm(self) -> CostManager:
        return CostManager("rg-test", "sub-123")

    @mock.patch.object(CostManager, "_az")
    def test_get_current_spend_empty(self, mock_az: mock.Mock, cm: CostManager) -> None:
        mock_az.return_value = json.dumps([])
        result = cm.get_current_spend()
        assert result["total_cost"] == 0.0
        assert result["by_service"] == []

    @mock.patch.object(CostManager, "_az")
    def test_get_current_spend_with_data(self, mock_az: mock.Mock, cm: CostManager) -> None:
        usage = [
            {
                "instanceId": "/subscriptions/sub/resourceGroups/rg-test/providers/Microsoft.Storage/storage1",
                "pretaxCost": "12.50",
                "currency": "USD",
                "meterCategory": "Storage",
            },
            {
                "instanceId": "/subscriptions/sub/resourceGroups/rg-test/providers/Microsoft.Web/func1",
                "pretaxCost": "8.00",
                "currency": "USD",
                "meterCategory": "Azure Functions",
            },
        ]
        mock_az.return_value = json.dumps(usage)
        result = cm.get_current_spend()
        assert result["total_cost"] == pytest.approx(20.50, abs=0.01)
        assert result["currency"] == "USD"
        assert len(result["by_service"]) == 2

    @mock.patch.object(CostManager, "_az")
    def test_list_budgets_empty(self, mock_az: mock.Mock, cm: CostManager) -> None:
        mock_az.return_value = json.dumps([])
        budgets = cm.list_budgets()
        assert budgets == []

    @mock.patch.object(CostManager, "_az")
    def test_check_budget_alerts_no_alerts(self, mock_az: mock.Mock, cm: CostManager) -> None:
        budgets = [{"name": "aos-budget-dev", "amount": 500, "currentSpend": {"amount": 100}}]
        mock_az.return_value = json.dumps(budgets)
        alerts = cm.check_budget_alerts()
        assert alerts == []

    @mock.patch.object(CostManager, "_az")
    def test_check_budget_alerts_threshold_exceeded(self, mock_az: mock.Mock, cm: CostManager) -> None:
        budgets = [{"name": "aos-budget-prod", "amount": 500, "currentSpend": {"amount": 450}}]
        mock_az.return_value = json.dumps(budgets)
        alerts = cm.check_budget_alerts()
        assert "aos-budget-prod" in alerts


# ====================================================================
# RbacManager tests
# ====================================================================


class TestRbacManager:
    @pytest.fixture()
    def rm(self) -> RbacManager:
        return RbacManager("rg-test", "sub-123")

    @mock.patch.object(RbacManager, "_az")
    def test_list_assignments(self, mock_az: mock.Mock, rm: RbacManager) -> None:
        assignments = [
            {"principalName": "svc-aos-dispatcher", "principalId": "oid-1",
             "roleDefinitionName": "Contributor", "principalType": "ServicePrincipal"},
        ]
        mock_az.return_value = json.dumps(assignments)
        result = rm.list_assignments()
        assert len(result) == 1
        assert result[0]["roleDefinitionName"] == "Contributor"

    @mock.patch.object(RbacManager, "_az")
    def test_review_privileged_access_no_findings(self, mock_az: mock.Mock, rm: RbacManager) -> None:
        assignments = [
            {"principalName": "svc-aos-deployment", "principalId": "oid-1",
             "roleDefinitionName": "Contributor", "principalType": "ServicePrincipal"},
        ]
        mock_az.return_value = json.dumps(assignments)
        findings = rm.review_privileged_access()
        assert findings == []

    @mock.patch.object(RbacManager, "_az")
    def test_review_privileged_access_with_findings(self, mock_az: mock.Mock, rm: RbacManager) -> None:
        assignments = [
            {"principalName": "john.doe@contoso.com", "principalId": "oid-2",
             "roleDefinitionName": "Owner", "principalType": "User"},
        ]
        mock_az.return_value = json.dumps(assignments)
        findings = rm.review_privileged_access()
        assert len(findings) == 1
        assert findings[0]["role"] == "Owner"
        assert "john.doe@contoso.com" in findings[0]["principal"]


# ====================================================================
# DriftDetector tests
# ====================================================================


class TestDriftDetector:
    @pytest.fixture()
    def dd(self) -> DriftDetector:
        return DriftDetector("rg-test")

    def test_detect_drift_from_manifest_no_drift(self) -> None:
        dd = DriftDetector("rg-test")
        manifest = [{"name": "storage1", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"}]
        live = [{"name": "storage1", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"}]
        with mock.patch.object(dd, "_list_live_resources", return_value=live):
            findings = dd.detect_drift_from_manifest(manifest)
        assert findings == []

    def test_detect_drift_missing_resource(self) -> None:
        dd = DriftDetector("rg-test")
        manifest = [{"name": "storage1", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"}]
        live: list = []
        with mock.patch.object(dd, "_list_live_resources", return_value=live):
            findings = dd.detect_drift_from_manifest(manifest)
        assert len(findings) == 1
        assert findings[0].kind == DriftKind.MISSING

    def test_detect_drift_unexpected_resource(self) -> None:
        dd = DriftDetector("rg-test")
        manifest: list = []
        live = [{"name": "rogue-storage", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"}]
        with mock.patch.object(dd, "_list_live_resources", return_value=live):
            findings = dd.detect_drift_from_manifest(manifest)
        assert len(findings) == 1
        assert findings[0].kind == DriftKind.UNEXPECTED

    def test_detect_drift_location_changed(self) -> None:
        dd = DriftDetector("rg-test")
        manifest = [{"name": "kv1", "type": "Microsoft.KeyVault/vaults", "location": "eastus"}]
        live = [{"name": "kv1", "type": "Microsoft.KeyVault/vaults", "location": "westus2"}]
        with mock.patch.object(dd, "_list_live_resources", return_value=live):
            findings = dd.detect_drift_from_manifest(manifest)
        assert len(findings) == 1
        assert findings[0].kind == DriftKind.CHANGED
        assert "location" in findings[0].details

    def test_snapshot_state(self) -> None:
        dd = DriftDetector("rg-test")
        live = [
            {"name": "r1", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"},
            {"name": "r2", "type": "Microsoft.KeyVault/vaults", "location": "eastus"},
        ]
        with mock.patch.object(dd, "_list_live_resources", return_value=live):
            snapshot = dd.snapshot_state()
        assert len(snapshot) == 2
        assert snapshot[0]["name"] == "r1"

    def test_parse_what_if_create(self) -> None:
        what_if = {
            "changes": [
                {"changeType": "Create", "resourceId": "/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/st1"},
            ]
        }
        findings = DriftDetector._parse_what_if(what_if)
        assert len(findings) == 1
        assert findings[0].kind == DriftKind.MISSING

    def test_parse_what_if_no_change(self) -> None:
        what_if = {
            "changes": [
                {"changeType": "NoChange", "resourceId": "/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/st1"},
            ]
        }
        findings = DriftDetector._parse_what_if(what_if)
        assert findings == []

    def test_drift_finding_to_dict(self) -> None:
        f = DriftFinding(
            kind=DriftKind.CHANGED,
            resource_name="res1",
            resource_type="Microsoft.Storage/storageAccounts",
            details="location changed",
        )
        d = f.to_dict()
        assert d["kind"] == "changed"
        assert d["resource_name"] == "res1"
        assert d["details"] == "location changed"


# ====================================================================
# HealthMonitor tests
# ====================================================================


class TestHealthMonitor:
    @pytest.fixture()
    def hm(self) -> HealthMonitor:
        return HealthMonitor("rg-test", "dev")

    def test_sla_target_dev(self) -> None:
        hm = HealthMonitor("rg-test", "dev")
        assert hm.sla_target == 99.0

    def test_sla_target_staging(self) -> None:
        hm = HealthMonitor("rg-test", "staging")
        assert hm.sla_target == 99.5

    def test_sla_target_prod(self) -> None:
        hm = HealthMonitor("rg-test", "prod")
        assert hm.sla_target == 99.9

    def test_aggregate_status_all_healthy(self) -> None:
        healths = [
            ResourceHealth("r1", "t1", HealthStatus.HEALTHY),
            ResourceHealth("r2", "t2", HealthStatus.HEALTHY),
        ]
        assert HealthMonitor._aggregate_status(healths) == HealthStatus.HEALTHY

    def test_aggregate_status_one_degraded(self) -> None:
        healths = [
            ResourceHealth("r1", "t1", HealthStatus.HEALTHY),
            ResourceHealth("r2", "t2", HealthStatus.DEGRADED),
        ]
        assert HealthMonitor._aggregate_status(healths) == HealthStatus.DEGRADED

    def test_aggregate_status_one_unhealthy(self) -> None:
        healths = [
            ResourceHealth("r1", "t1", HealthStatus.HEALTHY),
            ResourceHealth("r2", "t2", HealthStatus.UNHEALTHY),
        ]
        assert HealthMonitor._aggregate_status(healths) == HealthStatus.UNHEALTHY

    def test_aggregate_status_empty(self) -> None:
        assert HealthMonitor._aggregate_status([]) == HealthStatus.UNKNOWN

    def test_check_sla_compliance_compliant(self, hm: HealthMonitor) -> None:
        with mock.patch.object(hm, "check_all", return_value=(HealthStatus.HEALTHY, [])):
            result = hm.check_sla_compliance(observed_uptime_pct=100.0)
        assert result["compliant"] is True
        assert result["gap"] == pytest.approx(1.0, abs=0.01)

    def test_check_sla_compliance_non_compliant(self, hm: HealthMonitor) -> None:
        result = hm.check_sla_compliance(observed_uptime_pct=95.0)
        assert result["compliant"] is False
        assert result["gap"] < 0

    def test_check_sla_compliance_derived_from_resources(self, hm: HealthMonitor) -> None:
        healths = [
            ResourceHealth("r1", "t1", HealthStatus.HEALTHY),
            ResourceHealth("r2", "t2", HealthStatus.HEALTHY),
            ResourceHealth("r3", "t3", HealthStatus.UNHEALTHY),
            ResourceHealth("r4", "t4", HealthStatus.HEALTHY),
        ]
        with mock.patch.object(hm, "check_all", return_value=(HealthStatus.DEGRADED, healths)):
            result = hm.check_sla_compliance()
        # 3/4 = 75% — not compliant against 99% target
        assert result["observed_uptime"] == pytest.approx(75.0, abs=0.1)
        assert result["compliant"] is False

    def test_resource_health_is_healthy(self) -> None:
        h = ResourceHealth("r1", "t1", HealthStatus.HEALTHY, provisioning_state="Succeeded")
        assert h.is_healthy() is True

    def test_resource_health_not_healthy(self) -> None:
        h = ResourceHealth("r1", "t1", HealthStatus.UNHEALTHY, provisioning_state="Failed")
        assert h.is_healthy() is False

    def test_check_resource_succeeded(self, hm: HealthMonitor) -> None:
        res = {"name": "kv1", "type": "Microsoft.KeyVault/vaults", "provisioningState": "Succeeded", "id": ""}
        h = hm._check_resource(res)
        assert h.status == HealthStatus.HEALTHY

    def test_check_resource_failed(self, hm: HealthMonitor) -> None:
        res = {"name": "sb1", "type": "Microsoft.ServiceBus/namespaces", "provisioningState": "Failed", "id": ""}
        h = hm._check_resource(res)
        assert h.status == HealthStatus.UNHEALTHY


# ====================================================================
# InfrastructureManager — governance + reliability pillar tests
# ====================================================================


class TestInfrastructureManagerPillars:
    @pytest.fixture()
    def manager_with_governance(self) -> InfrastructureManager:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            template="deployment/main-modular.bicep",
            governance=GovernanceConfig(
                enforce_policies=True,
                required_tags={"environment": "dev"},
                review_rbac=True,
                budget_amount=500.0,
            ),
        )
        return InfrastructureManager(cfg)

    @pytest.fixture()
    def manager_with_reliability(self) -> InfrastructureManager:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            template="deployment/main-modular.bicep",
            reliability=ReliabilityConfig(
                enable_drift_detection=True,
                drift_manifest=[{"name": "st1", "type": "Microsoft.Storage/storageAccounts", "location": "eastus"}],
                check_dr_readiness=True,
            ),
        )
        return InfrastructureManager(cfg)

    def test_govern_method_exists(self, manager_with_governance: InfrastructureManager) -> None:
        assert callable(manager_with_governance.govern)

    def test_reliability_check_method_exists(self, manager_with_reliability: InfrastructureManager) -> None:
        assert callable(manager_with_reliability.reliability_check)

    @mock.patch("orchestrator.governance.policy_manager.PolicyManager.evaluate_compliance")
    @mock.patch("orchestrator.governance.policy_manager.PolicyManager.enforce_required_tags")
    @mock.patch("orchestrator.governance.cost_manager.CostManager.check_budget_alerts")
    @mock.patch("orchestrator.governance.rbac_manager.RbacManager.review_privileged_access")
    def test_govern_no_issues(
        self,
        mock_rbac: mock.Mock,
        mock_budget: mock.Mock,
        mock_tags: mock.Mock,
        mock_policy: mock.Mock,
        manager_with_governance: InfrastructureManager,
    ) -> None:
        mock_policy.return_value = {"total": 5, "compliant": 5, "non_compliant": 0, "violations": []}
        mock_tags.return_value = {"environment": []}
        mock_budget.return_value = []
        mock_rbac.return_value = []
        result = manager_with_governance.govern()
        assert result is True

    @mock.patch("orchestrator.governance.policy_manager.PolicyManager.evaluate_compliance")
    @mock.patch("orchestrator.governance.policy_manager.PolicyManager.enforce_required_tags")
    @mock.patch("orchestrator.governance.cost_manager.CostManager.check_budget_alerts")
    @mock.patch("orchestrator.governance.rbac_manager.RbacManager.review_privileged_access")
    def test_govern_with_violations(
        self,
        mock_rbac: mock.Mock,
        mock_budget: mock.Mock,
        mock_tags: mock.Mock,
        mock_policy: mock.Mock,
        manager_with_governance: InfrastructureManager,
    ) -> None:
        mock_policy.return_value = {
            "total": 5, "compliant": 4, "non_compliant": 1,
            "violations": [{"resource": "/rg/res1", "policy": "p1", "state": "NonCompliant"}],
        }
        mock_tags.return_value = {"environment": ["res2"]}
        mock_budget.return_value = []
        mock_rbac.return_value = []
        result = manager_with_governance.govern()
        assert result is False

    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_all")
    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_sla_compliance")
    @mock.patch("orchestrator.reliability.drift_detector.DriftDetector.detect_drift_from_manifest")
    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_disaster_recovery_readiness")
    def test_reliability_check_healthy(
        self,
        mock_dr: mock.Mock,
        mock_drift: mock.Mock,
        mock_sla: mock.Mock,
        mock_health: mock.Mock,
        manager_with_reliability: InfrastructureManager,
    ) -> None:
        mock_health.return_value = (HealthStatus.HEALTHY, [ResourceHealth("r1", "t1", HealthStatus.HEALTHY)])
        mock_sla.return_value = {"environment": "dev", "sla_target": 99.0, "observed_uptime": 100.0, "compliant": True, "gap": 1.0}
        mock_drift.return_value = []
        mock_dr.return_value = {"ready": True, "findings": []}
        result = manager_with_reliability.reliability_check()
        assert result is True

    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_all")
    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_sla_compliance")
    @mock.patch("orchestrator.reliability.drift_detector.DriftDetector.detect_drift_from_manifest")
    @mock.patch("orchestrator.reliability.health_monitor.HealthMonitor.check_disaster_recovery_readiness")
    def test_reliability_check_unhealthy(
        self,
        mock_dr: mock.Mock,
        mock_drift: mock.Mock,
        mock_sla: mock.Mock,
        mock_health: mock.Mock,
        manager_with_reliability: InfrastructureManager,
    ) -> None:
        mock_health.return_value = (HealthStatus.UNHEALTHY, [])
        mock_sla.return_value = {"environment": "dev", "sla_target": 99.0, "observed_uptime": 80.0, "compliant": False, "gap": -19.0}
        mock_drift.return_value = [
            DriftFinding(kind=DriftKind.MISSING, resource_name="st1", resource_type="Microsoft.Storage/storageAccounts")
        ]
        mock_dr.return_value = {"ready": False, "findings": ["Key Vault: soft-delete not enabled"]}
        result = manager_with_reliability.reliability_check()
        assert result is False
