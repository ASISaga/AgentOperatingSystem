"""Tests for Azure Multi-LoRA inference classes.

Covers:
- LoRAAdapterRegistry: registration, lookup, deduplication
- LoRAInferenceClient: adapter resolution, stub responses, extra_body injection
- LoRAOrchestrationRouter: step mapping, agent-persona fallback, resolution
"""

from __future__ import annotations

import pytest

from aos_intelligence.ml.lora_adapter_registry import LoRAAdapterRegistry, BASE_MODEL_ID
from aos_intelligence.ml.lora_inference_client import LoRAInferenceClient
from aos_intelligence.ml.lora_orchestration_router import LoRAOrchestrationRouter
# Also importable from the package top-level
from aos_intelligence import LoRAAdapterRegistry as RegistryFromTopLevel


# ====================================================================
# BASE_MODEL_ID
# ====================================================================


def test_base_model_id():
    assert BASE_MODEL_ID == "Meta-Llama-3.3-70B-Instruct"


def test_top_level_export():
    """LoRAAdapterRegistry must be importable from aos_intelligence directly."""
    assert RegistryFromTopLevel is LoRAAdapterRegistry


# ====================================================================
# LoRAAdapterRegistry
# ====================================================================


class TestLoRAAdapterRegistry:
    """Unit tests for LoRAAdapterRegistry."""

    @pytest.mark.asyncio
    async def test_register_adapter_basic(self):
        reg = LoRAAdapterRegistry()
        record = await reg.register_adapter(
            persona_type="ceo",
            adapter_path="/tmp/adapters/ceo",
        )
        assert record["persona_type"] == "ceo"
        assert record["base_model_version"] == BASE_MODEL_ID
        assert record["adapter_id"]
        assert record["registry_name"] == ""

    @pytest.mark.asyncio
    async def test_register_adapter_with_tags(self):
        reg = LoRAAdapterRegistry()
        record = await reg.register_adapter(
            persona_type="cmo",
            adapter_path="/tmp/adapters/cmo",
            base_model_version="Meta-Llama-3.3-70B-Instruct:2",
            extra_tags={"department": "marketing"},
        )
        assert record["tags"]["persona_type"] == "cmo"
        assert record["tags"]["department"] == "marketing"

    @pytest.mark.asyncio
    async def test_get_adapter_by_persona(self):
        reg = LoRAAdapterRegistry()
        await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        record = reg.get_adapter_by_persona("ceo")
        assert record["persona_type"] == "ceo"

    @pytest.mark.asyncio
    async def test_get_adapter_by_persona_not_found(self):
        reg = LoRAAdapterRegistry()
        with pytest.raises(KeyError, match="ceo"):
            reg.get_adapter_by_persona("ceo")

    @pytest.mark.asyncio
    async def test_get_adapter_by_id(self):
        reg = LoRAAdapterRegistry()
        record = await reg.register_adapter("cfo", "/tmp/adapters/cfo")
        fetched = reg.get_adapter_by_id(record["adapter_id"])
        assert fetched["persona_type"] == "cfo"

    @pytest.mark.asyncio
    async def test_get_adapter_by_id_not_found(self):
        reg = LoRAAdapterRegistry()
        with pytest.raises(KeyError, match="not found"):
            reg.get_adapter_by_id("nonexistent-id")

    @pytest.mark.asyncio
    async def test_get_adapter_id(self):
        reg = LoRAAdapterRegistry()
        record = await reg.register_adapter("analyst", "/tmp/adapters/analyst")
        adapter_id = reg.get_adapter_id("analyst")
        assert adapter_id == record["adapter_id"]

    @pytest.mark.asyncio
    async def test_list_adapters_deduplication(self):
        reg = LoRAAdapterRegistry()
        await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        await reg.register_adapter("cfo", "/tmp/adapters/cfo")
        adapters = reg.list_adapters()
        # Each persona produces one unique record
        assert len(adapters) == 2
        personas = {a["persona_type"] for a in adapters}
        assert personas == {"ceo", "cfo"}

    @pytest.mark.asyncio
    async def test_adapter_count(self):
        reg = LoRAAdapterRegistry()
        assert reg.adapter_count == 0
        await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        assert reg.adapter_count == 1
        await reg.register_adapter("cmo", "/tmp/adapters/cmo")
        assert reg.adapter_count == 2

    @pytest.mark.asyncio
    async def test_register_adapter_version(self):
        reg = LoRAAdapterRegistry()
        record = await reg.register_adapter("ceo", "/tmp/adapters/ceo", version="3")
        assert record["version"] == "3"

    @pytest.mark.asyncio
    async def test_registry_name_stored(self):
        reg = LoRAAdapterRegistry(registry_name="mlreg-aos-dev-abc123")
        record = await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        assert record["registry_name"] == "mlreg-aos-dev-abc123"


# ====================================================================
# LoRAInferenceClient
# ====================================================================


class TestLoRAInferenceClient:
    """Unit tests for LoRAInferenceClient."""

    @pytest.fixture()
    async def client_with_ceo(self) -> LoRAInferenceClient:
        reg = LoRAAdapterRegistry()
        await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        return LoRAInferenceClient(registry=reg)

    @pytest.mark.asyncio
    async def test_complete_stub_no_adapter(self, client_with_ceo):
        response = await client_with_ceo.complete(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert "choices" in response
        assert response["adapter_id"] == ""

    @pytest.mark.asyncio
    async def test_complete_stub_with_persona(self, client_with_ceo):
        response = await client_with_ceo.complete(
            messages=[{"role": "user", "content": "Strategy?"}],
            persona="ceo",
        )
        assert response["adapter_id"] != ""

    @pytest.mark.asyncio
    async def test_complete_stub_explicit_adapter_id(self, client_with_ceo):
        response = await client_with_ceo.complete(
            messages=[{"role": "user", "content": "Budget?"}],
            adapter_id="explicit-adapter-123",
        )
        assert response["adapter_id"] == "explicit-adapter-123"

    @pytest.mark.asyncio
    async def test_complete_unknown_persona_graceful(self, client_with_ceo):
        response = await client_with_ceo.complete(
            messages=[{"role": "user", "content": "Hello"}],
            persona="unknown_persona",
        )
        assert response["adapter_id"] == ""
        assert "choices" in response

    @pytest.mark.asyncio
    async def test_complete_default_persona(self):
        reg = LoRAAdapterRegistry()
        await reg.register_adapter("cmo", "/tmp/adapters/cmo")
        client = LoRAInferenceClient(registry=reg, default_persona="cmo")
        response = await client.complete(
            messages=[{"role": "user", "content": "Marketing plan?"}],
        )
        assert response["adapter_id"] != ""

    @pytest.mark.asyncio
    async def test_stub_response_contains_model(self, client_with_ceo):
        response = await client_with_ceo.complete(
            messages=[{"role": "user", "content": "Test"}],
        )
        assert response["model"] == "Meta-Llama-3.3-70B-Instruct"

    @pytest.mark.asyncio
    async def test_complete_merges_extra_body(self):
        reg = LoRAAdapterRegistry()
        client = LoRAInferenceClient(registry=reg)
        response = await client.complete(
            messages=[{"role": "user", "content": "Test"}],
            extra_body={"custom_field": "value"},
        )
        assert "choices" in response


# ====================================================================
# LoRAOrchestrationRouter
# ====================================================================


class TestLoRAOrchestrationRouter:
    """Unit tests for LoRAOrchestrationRouter."""

    @pytest.fixture()
    async def router_with_adapters(self) -> LoRAOrchestrationRouter:
        reg = LoRAAdapterRegistry()
        await reg.register_adapter("ceo", "/tmp/adapters/ceo")
        await reg.register_adapter("cmo", "/tmp/adapters/cmo")
        await reg.register_adapter("cfo", "/tmp/adapters/cfo")
        return LoRAOrchestrationRouter(registry=reg)

    def test_register_step_mapping(self, router_with_adapters):
        router = router_with_adapters
        router.register_step_mapping("strategic_review", "executive_summary", ["ceo", "cfo"])
        assert router.step_mapping_count == 1

    def test_resolve_adapters_via_step_mapping(self, router_with_adapters):
        router = router_with_adapters
        router.register_step_mapping("strategic_review", "executive_summary", ["ceo", "cfo"])
        adapters = router.resolve_adapters("strategic_review", "executive_summary")
        assert len(adapters) == 2
        personas = {a["persona_type"] for a in adapters}
        assert personas == {"ceo", "cfo"}

    def test_resolve_adapters_via_agent_persona_fallback(self, router_with_adapters):
        router = router_with_adapters
        router.register_agent_persona("agent-ceo", "ceo")
        router.register_agent_persona("agent-cmo", "cmo")
        adapters = router.resolve_adapters(
            "content_campaign",
            "brand_messaging",
            agent_ids=["agent-ceo", "agent-cmo"],
        )
        assert len(adapters) == 2
        personas = {a["persona_type"] for a in adapters}
        assert personas == {"ceo", "cmo"}

    def test_resolve_adapters_no_mapping_returns_empty(self, router_with_adapters):
        router = router_with_adapters
        adapters = router.resolve_adapters("unknown_type", "unknown_step")
        assert adapters == []

    def test_resolve_adapters_skips_unknown_persona(self, router_with_adapters):
        router = router_with_adapters
        router.register_step_mapping("review", "step1", ["ceo", "nonexistent"])
        adapters = router.resolve_adapters("review", "step1")
        assert len(adapters) == 1
        assert adapters[0]["persona_type"] == "ceo"

    def test_get_adapter_id_for_agent(self, router_with_adapters):
        router = router_with_adapters
        router.register_agent_persona("agent-cfo", "cfo")
        aid = router.get_adapter_id_for_agent("agent-cfo")
        assert isinstance(aid, str) and len(aid) > 0

    def test_get_adapter_id_for_agent_no_persona(self, router_with_adapters):
        router = router_with_adapters
        with pytest.raises(KeyError, match="no persona mapping"):
            router.get_adapter_id_for_agent("unregistered-agent")

    def test_agent_persona_count(self, router_with_adapters):
        router = router_with_adapters
        assert router.agent_persona_count == 0
        router.register_agent_persona("a1", "ceo")
        assert router.agent_persona_count == 1

    def test_step_mapping_overrides_agent_fallback(self, router_with_adapters):
        router = router_with_adapters
        router.register_step_mapping("review", "summary", ["ceo"])
        router.register_agent_persona("agent-cmo", "cmo")
        # Step mapping takes priority
        adapters = router.resolve_adapters("review", "summary", agent_ids=["agent-cmo"])
        assert len(adapters) == 1
        assert adapters[0]["persona_type"] == "ceo"
