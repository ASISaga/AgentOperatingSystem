"""Tests for AOSClient."""

import pytest

from aos_client.client import AOSClient
from aos_client.models import OrchestrationPurpose, OrchestrationRequest


class TestAOSClient:
    """AOSClient unit tests."""

    def test_init_defaults(self):
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        assert client.endpoint == "https://my-aos.azurewebsites.net"
        assert client.realm_endpoint == "https://my-aos.azurewebsites.net"

    def test_init_separate_realm(self):
        client = AOSClient(
            endpoint="https://my-aos.azurewebsites.net",
            realm_endpoint="https://my-realm.azurewebsites.net",
        )
        assert client.realm_endpoint == "https://my-realm.azurewebsites.net"

    def test_trailing_slash_stripped(self):
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net/")
        assert client.endpoint == "https://my-aos.azurewebsites.net"

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_get(self):
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        with pytest.raises(RuntimeError, match="context manager"):
            await client.list_agents()

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_submit(self):
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        request = OrchestrationRequest(
            agent_ids=["ceo"],
            purpose=OrchestrationPurpose(purpose="Test purpose"),
        )
        with pytest.raises(RuntimeError, match="context manager"):
            await client.submit_orchestration(request)

    def test_no_run_orchestration_method(self):
        """run_orchestration is removed — orchestrations are perpetual."""
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        assert not hasattr(client, "run_orchestration")

    def test_has_start_orchestration_method(self):
        """start_orchestration replaces the old task-driven run_orchestration."""
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        assert hasattr(client, "start_orchestration")

    def test_has_stop_orchestration_method(self):
        """stop_orchestration supports the perpetual lifecycle."""
        client = AOSClient(endpoint="https://my-aos.azurewebsites.net")
        assert hasattr(client, "stop_orchestration")
