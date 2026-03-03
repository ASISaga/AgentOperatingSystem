"""Tests for the Automation pillar and integration bridges.

Covers:
- AutomationConfig defaults and custom values
- PipelineManager stage invocations
- LifecycleManager operations (deprovision, modify, upgrade, scale)
- SDKBridge availability and status queries
- KernelBridge output translation and config validation
- InfrastructureManager.automate() integration
- Updated deploy.py CLI subcommands (govern, reliability, automate, lifecycle)
"""

from __future__ import annotations

import argparse
import json
import subprocess
from unittest import mock

import pytest

from orchestrator.automation.lifecycle import (
    LifecycleManager,
    LifecycleOperation,
    LifecycleResult,
    _SKU_PROPERTY_MAP,
    _PATCHABLE_TYPES,
)
from orchestrator.automation.pipeline import PipelineManager
from orchestrator.core.config import (
    AutomationConfig,
    DeploymentConfig,
    GovernanceConfig,
    ReliabilityConfig,
)
from orchestrator.core.manager import InfrastructureManager
from orchestrator.integration.kernel_bridge import KernelBridge, _OUTPUT_TO_ENV_MAP
from orchestrator.integration.sdk_bridge import SDKBridge, AppDeploymentStatus


# ====================================================================
# AutomationConfig — unit tests
# ====================================================================


class TestAutomationConfig:
    def test_defaults(self) -> None:
        ac = AutomationConfig()
        assert ac.deploy_function_apps is False
        assert ac.app_names == []
        assert ac.sync_kernel_config is False
        assert ac.enable_lifecycle_ops is False
        assert ac.target_version == ""
        assert ac.scale_overrides == {}
        assert ac.region_shift_target == ""

    def test_custom_values(self) -> None:
        ac = AutomationConfig(
            deploy_function_apps=True,
            app_names=["aos-dispatcher", "aos-realm-of-agents"],
            sync_kernel_config=True,
            enable_lifecycle_ops=True,
            target_version="5.0.0",
            scale_overrides={"func-aos-dispatcher-dev": "EP2"},
            region_shift_target="westeurope",
        )
        assert ac.deploy_function_apps is True
        assert len(ac.app_names) == 2
        assert ac.sync_kernel_config is True
        assert ac.target_version == "5.0.0"
        assert ac.region_shift_target == "westeurope"


class TestDeploymentConfigAllPillars:
    """Verify that all three pillar configs are present in DeploymentConfig."""

    def test_all_three_pillars_default(self) -> None:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
        )
        assert isinstance(cfg.governance, GovernanceConfig)
        assert isinstance(cfg.automation, AutomationConfig)
        assert isinstance(cfg.reliability, ReliabilityConfig)

    def test_automation_embedded(self) -> None:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            automation=AutomationConfig(deploy_function_apps=True),
        )
        assert cfg.automation.deploy_function_apps is True

    def test_from_args_includes_automation(self) -> None:
        ns = argparse.Namespace(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            location_ml="",
            template="t.bicep",
            parameters="",
            subscription_id="",
            git_sha="",
            allow_warnings=False,
            skip_health=False,
            no_confirm_deletes=False,
            # governance
            enforce_policies=False,
            budget_amount=0,
            required_tags={},
            review_rbac=False,
            # automation
            deploy_function_apps=True,
            sync_kernel_config=True,
            enable_lifecycle_ops=False,
            region_shift_target="",
            # reliability
            enable_drift_detection=False,
            check_dr_readiness=False,
        )
        cfg = DeploymentConfig.from_args(ns)
        assert cfg.automation.deploy_function_apps is True
        assert cfg.automation.sync_kernel_config is True


# ====================================================================
# PipelineManager — unit tests
# ====================================================================


class TestPipelineManager:
    @pytest.fixture()
    def pm(self) -> PipelineManager:
        return PipelineManager(
            resource_group="rg-test",
            environment="dev",
            location="eastus",
            template="deployment/main-modular.bicep",
        )

    @mock.patch.object(PipelineManager, "_run")
    def test_lint_success(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "", "")
        assert pm.lint() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_lint_failure(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 1, "", "lint error")
        assert pm.lint() is False

    def test_lint_no_template(self) -> None:
        pm = PipelineManager(
            resource_group="rg-test",
            environment="dev",
            location="eastus",
            template="",
        )
        assert pm.lint() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_validate_success(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        assert pm.validate() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_what_if_success(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        assert pm.what_if() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_deploy_success(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        assert pm.deploy() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_health_check_all_succeeded(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        resources = json.dumps([
            {"name": "r1", "state": "Succeeded"},
            {"name": "r2", "state": "Succeeded"},
        ])
        mock_run.return_value = subprocess.CompletedProcess([], 0, resources, "")
        assert pm.health_check() is True

    @mock.patch.object(PipelineManager, "_run")
    def test_health_check_one_failed(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        resources = json.dumps([
            {"name": "r1", "state": "Succeeded"},
            {"name": "r2", "state": "Failed"},
        ])
        mock_run.return_value = subprocess.CompletedProcess([], 0, resources, "")
        assert pm.health_check() is False

    @mock.patch.object(PipelineManager, "_run")
    def test_plan_runs_three_stages(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        assert pm.plan() is True
        assert mock_run.call_count == 3  # lint + validate + what-if

    @mock.patch.object(PipelineManager, "_run")
    def test_full_deploy_runs_all_stages(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, json.dumps([{"name": "r1", "state": "Succeeded"}]), ""
        )
        assert pm.full_deploy() is True
        assert mock_run.call_count == 5  # lint + validate + what-if + deploy + health-check

    @mock.patch.object(PipelineManager, "_run")
    def test_full_deploy_skip_health(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        assert pm.full_deploy(skip_health=True) is True
        assert mock_run.call_count == 4  # no health-check

    @mock.patch.object(PipelineManager, "_run")
    def test_full_deploy_stops_on_failure(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 1, "", "lint error")
        assert pm.full_deploy() is False
        assert mock_run.call_count == 1  # stopped after lint

    @mock.patch.object(PipelineManager, "_run")
    def test_full_deploy_allow_warnings(self, mock_run: mock.Mock, pm: PipelineManager) -> None:
        # lint fails but allow_warnings=True — should continue
        results = [
            subprocess.CompletedProcess([], 1, "", "lint warning"),  # lint
            subprocess.CompletedProcess([], 0, "{}", ""),  # validate
            subprocess.CompletedProcess([], 0, "{}", ""),  # what-if
            subprocess.CompletedProcess([], 0, "{}", ""),  # deploy
            subprocess.CompletedProcess([], 0, json.dumps([{"name": "r1", "state": "Succeeded"}]), ""),
        ]
        mock_run.side_effect = results
        assert pm.full_deploy(allow_warnings=True) is True
        assert mock_run.call_count == 5

    def test_deployment_cmd_includes_env(self, pm: PipelineManager) -> None:
        cmd = pm._deployment_cmd("create")
        cmd_str = " ".join(cmd)
        assert "environment=dev" in cmd_str
        assert "location=eastus" in cmd_str

    def test_deployment_cmd_with_valid_sha(self) -> None:
        pm = PipelineManager(
            resource_group="rg",
            environment="prod",
            location="westeurope",
            template="t.bicep",
            git_sha="abc1234def",
        )
        cmd = pm._deployment_cmd("create")
        assert any("gitSha" in p for p in cmd)

    def test_deployment_cmd_with_invalid_sha(self) -> None:
        pm = PipelineManager(
            resource_group="rg",
            environment="prod",
            location="westeurope",
            template="t.bicep",
            git_sha="not-a-sha!",
        )
        cmd = pm._deployment_cmd("create")
        assert not any("gitSha" in p for p in cmd)


# ====================================================================
# LifecycleManager — unit tests
# ====================================================================


class TestLifecycleManager:
    @pytest.fixture()
    def lm(self) -> LifecycleManager:
        return LifecycleManager("rg-test", "sub-123")

    def test_lifecycle_result_to_dict(self) -> None:
        r = LifecycleResult(
            operation=LifecycleOperation.DEPROVISION,
            resource_name="st1",
            resource_type="Microsoft.Storage/storageAccounts",
            success=True,
            message="deleted",
        )
        d = r.to_dict()
        assert d["operation"] == "deprovision"
        assert d["success"] is True
        assert d["resource_name"] == "st1"

    @mock.patch("subprocess.run")
    def test_deprovision_success(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        result = lm.deprovision("st1", "Microsoft.Storage/storageAccounts", confirm=False)
        assert result.success is True
        assert result.operation == LifecycleOperation.DEPROVISION

    @mock.patch("subprocess.run")
    def test_deprovision_failure(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 1, "", "Resource not found")
        result = lm.deprovision("missing-st", "Microsoft.Storage/storageAccounts", confirm=False)
        assert result.success is False
        assert "Resource not found" in result.message

    @mock.patch("subprocess.run")
    def test_modify_success(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        result = lm.modify(
            "func-dispatcher",
            "microsoft.web/sites",
            {"properties.httpsOnly": True},
        )
        assert result.success is True
        assert result.operation == LifecycleOperation.MODIFY
        assert result.details == {"properties.httpsOnly": True}

    @mock.patch("subprocess.run")
    def test_upgrade_success(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        result = lm.upgrade(
            "storage-account-1",
            "microsoft.storage/storageaccounts",
            "Standard_ZRS",
        )
        assert result.success is True
        assert result.operation == LifecycleOperation.UPGRADE
        assert result.details["new_sku"] == "Standard_ZRS"

    @mock.patch("subprocess.run")
    def test_upgrade_failure(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 1, "", "Invalid SKU")
        result = lm.upgrade("st1", "microsoft.storage/storageaccounts", "Premium_ZRS")
        assert result.success is False

    @mock.patch("subprocess.run")
    def test_scale_success_all_settings(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "{}", "")
        result = lm.scale(
            "apim-aos-dev",
            "microsoft.apimanagement/service",
            {"sku.capacity": 2},
        )
        assert result.success is True
        assert result.operation == LifecycleOperation.SCALE

    @mock.patch("subprocess.run")
    def test_scale_partial_failure(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        mock_run.side_effect = [
            subprocess.CompletedProcess([], 0, "{}", ""),   # first setting ok
            subprocess.CompletedProcess([], 1, "", "error"),  # second setting fails
        ]
        result = lm.scale(
            "sb-aos-dev",
            "microsoft.servicebus/namespaces",
            {"sku.capacity": 2, "properties.messagingUnits": 4},
        )
        assert result.success is False

    @mock.patch("subprocess.run")
    def test_list_lifecycle_candidates(self, mock_run: mock.Mock, lm: LifecycleManager) -> None:
        resources = [
            {"name": "st1", "type": "Microsoft.Storage/storageAccounts",
             "location": "eastus", "provisioningState": "Succeeded"},
            {"name": "sb1", "type": "Microsoft.ServiceBus/namespaces",
             "location": "eastus", "provisioningState": "Failed"},
        ]
        mock_run.return_value = subprocess.CompletedProcess([], 0, json.dumps(resources), "")
        candidates = lm.list_lifecycle_candidates()
        assert len(candidates) == 2
        # Storage supports upgrade
        st = next(c for c in candidates if c["name"] == "st1")
        assert st["supports_upgrade"] is True

    def test_sku_property_map_coverage(self) -> None:
        assert "microsoft.storage/storageaccounts" in _SKU_PROPERTY_MAP
        assert "microsoft.servicebus/namespaces" in _SKU_PROPERTY_MAP
        assert "microsoft.apimanagement/service" in _SKU_PROPERTY_MAP

    def test_patchable_types_coverage(self) -> None:
        assert "microsoft.web/sites" in _PATCHABLE_TYPES
        assert "microsoft.keyvault/vaults" in _PATCHABLE_TYPES


# ====================================================================
# SDKBridge — unit tests
# ====================================================================


class TestSDKBridge:
    @pytest.fixture()
    def bridge(self) -> SDKBridge:
        return SDKBridge(
            resource_group="rg-test",
            environment="dev",
            subscription_id="sub-123",
            location="eastus",
        )

    def test_is_sdk_available_when_absent(self, bridge: SDKBridge) -> None:
        # In the test environment the SDK may or may not be installed.
        # The method should return a bool without raising.
        result = SDKBridge.is_sdk_available()
        assert isinstance(result, bool)

    def test_deploy_function_apps_skipped_when_sdk_unavailable(
        self, bridge: SDKBridge
    ) -> None:
        with mock.patch.object(SDKBridge, "is_sdk_available", return_value=False):
            statuses = bridge.deploy_function_apps(["aos-dispatcher"])
        assert len(statuses) == 1
        assert statuses[0].status == "skipped"
        assert statuses[0].error is not None

    def test_app_deployment_status_defaults(self) -> None:
        s = AppDeploymentStatus(app_name="test")
        assert s.status == "unknown"
        assert s.url is None
        assert s.error is None

    @mock.patch("subprocess.run")
    def test_get_function_app_status_not_found(
        self, mock_run: mock.Mock, bridge: SDKBridge
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 1, "", "Not found")
        status = bridge.get_function_app_status("nonexistent-app")
        assert status.status == "unknown"

    @mock.patch("subprocess.run")
    def test_get_function_app_status_running(
        self, mock_run: mock.Mock, bridge: SDKBridge
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, json.dumps({"state": "Running", "url": "my-app.azurewebsites.net"}), ""
        )
        status = bridge.get_function_app_status("my-app")
        assert status.status == "running"
        assert status.url == "https://my-app.azurewebsites.net"

    @mock.patch("subprocess.run")
    def test_sync_app_settings_success(
        self, mock_run: mock.Mock, bridge: SDKBridge
    ) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, "[]", "")
        ok = bridge.sync_app_settings("my-app", {"KEY": "value"})
        assert ok is True

    @mock.patch("subprocess.run")
    def test_sync_app_settings_empty_is_noop(
        self, mock_run: mock.Mock, bridge: SDKBridge
    ) -> None:
        ok = bridge.sync_app_settings("my-app", {})
        assert ok is True
        mock_run.assert_not_called()

    @mock.patch("subprocess.run")
    def test_get_aos_endpoint(self, mock_run: mock.Mock, bridge: SDKBridge) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, "func-aos-dispatcher-dev.azurewebsites.net\n", ""
        )
        endpoint = bridge.get_aos_endpoint()
        assert endpoint == "https://func-aos-dispatcher-dev.azurewebsites.net"


# ====================================================================
# KernelBridge — unit tests
# ====================================================================


class TestKernelBridge:
    @pytest.fixture()
    def kb(self) -> KernelBridge:
        return KernelBridge("rg-test", "main-deploy-dev", "sub-123")

    def test_output_to_env_map_coverage(self) -> None:
        assert "aiServicesEndpoint" in _OUTPUT_TO_ENV_MAP
        assert "aiProjectDiscoveryUrl" in _OUTPUT_TO_ENV_MAP
        assert "keyVaultName" in _OUTPUT_TO_ENV_MAP
        assert "serviceBusNamespace" in _OUTPUT_TO_ENV_MAP
        assert "loraInferenceScoringUri" in _OUTPUT_TO_ENV_MAP

    def test_translate_outputs_standard(self, kb: KernelBridge) -> None:
        outputs = {
            "aiServicesEndpoint": {"value": "https://ai.example.com"},
            "keyVaultName": {"value": "kv-aos-dev"},
            "serviceBusNamespace": {"value": "sb-aos-dev"},
            "storageAccountName": {"value": "staoasdev"},
            "aiProjectDiscoveryUrl": {"value": "https://proj.foundry.com"},
        }
        env_vars = KernelBridge._translate_outputs(outputs)
        assert env_vars["AZURE_AI_SERVICES_ENDPOINT"] == "https://ai.example.com"
        assert env_vars["KEY_VAULT_NAME"] == "kv-aos-dev"
        assert env_vars["SERVICE_BUS_NAMESPACE"] == "sb-aos-dev"
        assert env_vars["AOS_STORAGE_ACCOUNT"] == "staoasdev"
        assert env_vars["FOUNDRY_PROJECT_ENDPOINT"] == "https://proj.foundry.com"

    def test_translate_outputs_empty(self, kb: KernelBridge) -> None:
        env_vars = KernelBridge._translate_outputs({})
        assert env_vars == {}

    def test_validate_kernel_config_all_present(self, kb: KernelBridge) -> None:
        env_vars = {
            "AZURE_AI_SERVICES_ENDPOINT": "https://ai.example.com",
            "FOUNDRY_PROJECT_ENDPOINT": "https://proj.foundry.com",
            "KEY_VAULT_NAME": "kv-aos-dev",
            "SERVICE_BUS_NAMESPACE": "sb-aos-dev",
            "AOS_STORAGE_ACCOUNT": "staoasdev",
        }
        result = kb.validate_kernel_config(env_vars)
        assert result["missing"] == []
        assert len(result["present"]) == 5

    def test_validate_kernel_config_missing(self, kb: KernelBridge) -> None:
        env_vars = {
            "AZURE_AI_SERVICES_ENDPOINT": "https://ai.example.com",
        }
        result = kb.validate_kernel_config(env_vars)
        assert len(result["missing"]) > 0

    @mock.patch.object(KernelBridge, "_get_deployment_outputs")
    def test_extract_kernel_env_with_outputs(
        self, mock_outputs: mock.Mock, kb: KernelBridge
    ) -> None:
        mock_outputs.return_value = {
            "keyVaultName": {"value": "kv-test"},
            "serviceBusNamespace": {"value": "sb-test"},
        }
        env = kb.extract_kernel_env()
        assert env["KEY_VAULT_NAME"] == "kv-test"
        assert env["SERVICE_BUS_NAMESPACE"] == "sb-test"

    @mock.patch.object(KernelBridge, "_get_deployment_outputs")
    def test_extract_kernel_env_no_outputs(
        self, mock_outputs: mock.Mock, kb: KernelBridge
    ) -> None:
        mock_outputs.return_value = None
        env = kb.extract_kernel_env()
        assert env == {}

    def test_write_env_file(self, tmp_path, kb: KernelBridge) -> None:
        env_path = str(tmp_path / ".env")
        env_vars = {"KEY_VAULT_NAME": "kv-test", "SERVICE_BUS_NAMESPACE": "sb-test"}
        ok = kb.write_env_file(env_vars, env_path)
        assert ok is True
        content = (tmp_path / ".env").read_text()
        assert "KEY_VAULT_NAME=kv-test" in content
        assert "SERVICE_BUS_NAMESPACE=sb-test" in content


# ====================================================================
# InfrastructureManager.automate() — integration tests
# ====================================================================


class TestInfrastructureManagerAutomate:
    @pytest.fixture()
    def manager(self) -> InfrastructureManager:
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            template="deployment/main-modular.bicep",
            automation=AutomationConfig(
                deploy_function_apps=False,
                sync_kernel_config=False,
            ),
        )
        return InfrastructureManager(cfg)

    def test_automate_method_exists(self, manager: InfrastructureManager) -> None:
        assert callable(manager.automate)

    @mock.patch("orchestrator.automation.pipeline.PipelineManager.full_deploy")
    def test_automate_pipeline_success(
        self, mock_pipeline: mock.Mock, manager: InfrastructureManager
    ) -> None:
        mock_pipeline.return_value = True
        result = manager.automate()
        assert result is True

    @mock.patch("orchestrator.automation.pipeline.PipelineManager.full_deploy")
    def test_automate_pipeline_failure(
        self, mock_pipeline: mock.Mock, manager: InfrastructureManager
    ) -> None:
        mock_pipeline.return_value = False
        result = manager.automate()
        assert result is False

    @mock.patch("orchestrator.integration.sdk_bridge.SDKBridge.deploy_function_apps")
    @mock.patch("orchestrator.automation.pipeline.PipelineManager.full_deploy")
    def test_automate_with_sdk_bridge(
        self,
        mock_pipeline: mock.Mock,
        mock_sdk: mock.Mock,
    ) -> None:
        mock_pipeline.return_value = True
        mock_sdk.return_value = [
            AppDeploymentStatus(app_name="aos-dispatcher", status="succeeded"),
        ]
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            template="deployment/main-modular.bicep",
            automation=AutomationConfig(deploy_function_apps=True),
        )
        mgr = InfrastructureManager(cfg)
        result = mgr.automate()
        assert result is True
        mock_sdk.assert_called_once()

    @mock.patch("orchestrator.integration.kernel_bridge.KernelBridge.extract_kernel_env")
    @mock.patch("orchestrator.integration.kernel_bridge.KernelBridge.validate_kernel_config")
    @mock.patch("orchestrator.automation.pipeline.PipelineManager.full_deploy")
    def test_automate_with_kernel_sync(
        self,
        mock_pipeline: mock.Mock,
        mock_validate: mock.Mock,
        mock_extract: mock.Mock,
    ) -> None:
        mock_pipeline.return_value = True
        mock_extract.return_value = {"KEY_VAULT_NAME": "kv-test"}
        mock_validate.return_value = {"present": ["KEY_VAULT_NAME"], "missing": []}
        cfg = DeploymentConfig(
            environment="dev",
            resource_group="rg-test",
            location="eastus",
            template="deployment/main-modular.bicep",
            automation=AutomationConfig(sync_kernel_config=True),
        )
        mgr = InfrastructureManager(cfg)
        result = mgr.automate()
        assert result is True
        mock_extract.assert_called_once()


# ====================================================================
# deploy.py CLI — subcommand parsing tests
# ====================================================================


class TestDeployCLI:
    """Verify the CLI parser accepts the new subcommands without error."""

    def test_import_deploy_py(self) -> None:
        """Ensure deploy.py can be imported without errors."""
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "deploy",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        assert hasattr(mod, "_build_parser")
        assert hasattr(mod, "main")

    def test_parser_govern_subcommand(self) -> None:
        from pathlib import Path
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location(
            "deploy2",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        parser = mod._build_parser()
        args = parser.parse_args([
            "govern",
            "--resource-group", "rg-test",
            "--environment", "dev",
            "--review-rbac",
        ])
        assert args.command == "govern"
        assert args.review_rbac is True

    def test_parser_reliability_subcommand(self) -> None:
        from pathlib import Path
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location(
            "deploy3",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        parser = mod._build_parser()
        args = parser.parse_args([
            "reliability",
            "--resource-group", "rg-test",
            "--environment", "prod",
            "--enable-drift-detection",
            "--check-dr-readiness",
        ])
        assert args.command == "reliability"
        assert args.enable_drift_detection is True
        assert args.check_dr_readiness is True

    def test_parser_deprovision_subcommand(self) -> None:
        from pathlib import Path
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location(
            "deploy4",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        parser = mod._build_parser()
        args = parser.parse_args([
            "deprovision",
            "--resource-group", "rg-test",
            "--resource-name", "st1",
            "--resource-type", "Microsoft.Storage/storageAccounts",
            "--yes",
        ])
        assert args.command == "deprovision"
        assert args.resource_name == "st1"
        assert args.yes is True

    def test_parser_upgrade_subcommand(self) -> None:
        from pathlib import Path
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location(
            "deploy5",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        parser = mod._build_parser()
        args = parser.parse_args([
            "upgrade",
            "--resource-group", "rg-test",
            "--resource-name", "st1",
            "--resource-type", "microsoft.storage/storageaccounts",
            "--new-sku", "Standard_ZRS",
        ])
        assert args.command == "upgrade"
        assert args.new_sku == "Standard_ZRS"

    def test_parser_scale_subcommand(self) -> None:
        from pathlib import Path
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location(
            "deploy6",
            Path(__file__).resolve().parent.parent / "deploy.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        parser = mod._build_parser()
        args = parser.parse_args([
            "scale",
            "--resource-group", "rg-test",
            "--resource-name", "apim-aos-dev",
            "--resource-type", "microsoft.apimanagement/service",
            "--scale-settings", '{"sku.capacity": 2}',
        ])
        assert args.command == "scale"
        assert args.scale_settings == {"sku.capacity": 2}
