"""Tests for AOSDeployer."""

import pytest
from pathlib import Path

from aos_client.deployment import AOSDeployer, DeploymentResult


class TestAOSDeployer:
    """AOSDeployer unit tests."""

    def test_init_defaults(self):
        deployer = AOSDeployer(app_name="test-app")
        assert deployer.app_name == "test-app"
        assert deployer.resource_group == "rg-test-app"
        assert deployer.location == "eastus2"

    def test_init_custom(self):
        deployer = AOSDeployer(
            app_name="my-app",
            resource_group="rg-custom",
            subscription_id="sub-123",
            location="westeurope",
        )
        assert deployer.resource_group == "rg-custom"
        assert deployer.subscription_id == "sub-123"
        assert deployer.location == "westeurope"

    def test_get_required_files(self):
        deployer = AOSDeployer(app_name="test")
        files = deployer.get_required_files()
        assert "host.json" in files
        assert "requirements.txt" in files

    def test_ensure_host_json(self, tmp_path):
        deployer = AOSDeployer(app_name="test", project_path=str(tmp_path))
        host_json = deployer.ensure_host_json()
        assert host_json.exists()

        import json
        config = json.loads(host_json.read_text())
        assert config["version"] == "2.0"
        assert "serviceBus" in config["extensions"]

    def test_ensure_host_json_idempotent(self, tmp_path):
        deployer = AOSDeployer(app_name="test", project_path=str(tmp_path))
        deployer.ensure_host_json()
        # Write custom content
        host_json = tmp_path / "host.json"
        host_json.write_text('{"custom": true}')
        # Should not overwrite
        deployer.ensure_host_json()
        assert '"custom": true' in host_json.read_text()

    def test_ensure_local_settings(self, tmp_path):
        deployer = AOSDeployer(app_name="test", project_path=str(tmp_path))
        settings = deployer.ensure_local_settings(
            aos_endpoint="http://localhost:7071",
            service_bus_connection="Endpoint=sb://test",
        )
        assert settings.exists()

        import json
        config = json.loads(settings.read_text())
        assert config["Values"]["AOS_ENDPOINT"] == "http://localhost:7071"
        assert config["Values"]["SERVICE_BUS_CONNECTION"] == "Endpoint=sb://test"


class TestDeploymentResult:
    """DeploymentResult unit tests."""

    def test_create(self):
        result = DeploymentResult(
            app_name="test",
            url="https://test.azurewebsites.net",
            status="succeeded",
        )
        assert result.app_name == "test"
        assert result.url == "https://test.azurewebsites.net"
        assert result.status == "succeeded"

    def test_defaults(self):
        result = DeploymentResult(app_name="test")
        assert result.status == "unknown"
        assert result.url is None
        assert result.details == {}
