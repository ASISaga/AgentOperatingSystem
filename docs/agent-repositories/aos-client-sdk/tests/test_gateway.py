"""Tests for AI Gateway client."""

import pytest

from aos_client.gateway import AIGateway, GatewayConfig


class TestGatewayConfig:
    """GatewayConfig model tests."""

    def test_defaults(self):
        config = GatewayConfig(gateway_url="https://gw.example.com/ai")
        assert config.default_model == "gpt-4o"
        assert config.max_retries == 3
        assert config.backoff_factor == 0.5
        assert config.timeout_seconds == 30
        assert config.rate_limit_retry is True

    def test_custom(self):
        config = GatewayConfig(
            gateway_url="https://gw.example.com/ai",
            default_model="gpt-35-turbo",
            max_retries=5,
            backoff_factor=1.0,
            timeout_seconds=60,
            rate_limit_retry=False,
        )
        assert config.default_model == "gpt-35-turbo"
        assert config.max_retries == 5
        assert config.rate_limit_retry is False


class TestAIGateway:
    """AIGateway unit tests."""

    def test_init_defaults(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        assert gw.gateway_url == "https://gw.example.com/ai"
        assert gw.default_model == "gpt-4o"

    def test_init_custom(self):
        gw = AIGateway(
            gateway_url="https://gw.example.com/ai",
            default_model="gpt-35-turbo",
            retry_config={"max_retries": 5, "backoff_factor": 1.0},
        )
        assert gw.default_model == "gpt-35-turbo"

    def test_trailing_slash_stripped(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai/")
        assert gw.gateway_url == "https://gw.example.com/ai"

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        async with gw:
            assert gw._session is not None
        assert gw._session is None

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_chat(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        with pytest.raises(RuntimeError, match="context manager"):
            await gw.chat_completion(
                messages=[{"role": "user", "content": "Hello"}]
            )

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_completion(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        with pytest.raises(RuntimeError, match="context manager"):
            await gw.completion(prompt="Hello")

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_embedding(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        with pytest.raises(RuntimeError, match="context manager"):
            await gw.embedding(input_text="Hello world")

    @pytest.mark.asyncio
    async def test_requires_context_manager_for_list_models(self):
        gw = AIGateway(gateway_url="https://gw.example.com/ai")
        with pytest.raises(RuntimeError, match="context manager"):
            await gw.list_models()
