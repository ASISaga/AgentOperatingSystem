"""Tests for AOSClient."""

import pytest

from aos_client.client import AOSClient
from aos_client.models import OrchestrationRequest


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
            task={"type": "test"},
        )
        with pytest.raises(RuntimeError, match="context manager"):
            await client.submit_orchestration(request)
