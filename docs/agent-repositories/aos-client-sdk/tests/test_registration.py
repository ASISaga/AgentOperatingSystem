"""Tests for AOSRegistration."""

import pytest

from aos_client.registration import AOSRegistration, AppRegistration


class TestAppRegistration:
    """AppRegistration model tests."""

    def test_create_minimal(self):
        reg = AppRegistration(app_name="test-app")
        assert reg.app_name == "test-app"
        assert reg.workflows == []
        assert reg.status == "pending"
        assert reg.request_queue == "aos-orchestration-requests"
        assert reg.result_topic == "aos-orchestration-results"

    def test_create_full(self):
        reg = AppRegistration(
            app_name="business-infinity",
            app_id="app-123",
            workflows=["strategic-review", "market-analysis"],
            service_bus_connection_string="Endpoint=sb://...",
            result_subscription="business-infinity",
            status="provisioned",
            provisioned_resources={
                "service_bus_queue": "aos-orchestration-requests",
            },
        )
        assert reg.app_name == "business-infinity"
        assert len(reg.workflows) == 2
        assert reg.status == "provisioned"
        assert reg.result_subscription == "business-infinity"


class TestAOSRegistration:
    """AOSRegistration unit tests."""

    def test_init(self):
        reg = AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net/")
        assert reg.aos_endpoint == "https://my-aos.azurewebsites.net"

    @pytest.mark.asyncio
    async def test_requires_context_manager(self):
        reg = AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net")
        with pytest.raises(RuntimeError, match="context manager"):
            await reg.register_app(app_name="test")

    @pytest.mark.asyncio
    async def test_get_status_requires_context_manager(self):
        reg = AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net")
        with pytest.raises(RuntimeError, match="context manager"):
            await reg.get_app_status(app_name="test")

    @pytest.mark.asyncio
    async def test_deregister_requires_context_manager(self):
        reg = AOSRegistration(aos_endpoint="https://my-aos.azurewebsites.net")
        with pytest.raises(RuntimeError, match="context manager"):
            await reg.deregister_app(app_name="test")
