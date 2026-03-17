"""
Tests for CMOAgent.

Coverage targets
----------------
- CMOAgent can be created with default parameters.
- Default purpose, adapter names, and role are set correctly.
- get_agent_type() returns ["marketing", "leadership"].
- get_adapter_for_purpose() returns correct adapter names.
- get_adapter_for_purpose() raises ValueError for unknown purpose types.
- execute_with_purpose() returns result with purpose_type and adapter_used.
- execute_with_purpose() raises ValueError for unknown purpose type.
- execute_with_purpose() restores adapter_name after execution.
- get_status() returns dual-purpose status structure.
- initialize() succeeds.
"""

import pytest

from cmo_agent import CMOAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """CMOAgent can be created with only agent_id."""
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.agent_id == "cmo-001"

    def test_default_name(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.name == "CMO"

    def test_default_role(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.role == "CMO"

    def test_default_marketing_adapter(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.marketing_adapter_name == "marketing"

    def test_default_leadership_adapter(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.leadership_adapter_name == "leadership"

    def test_primary_adapter_is_marketing(self) -> None:
        """Primary (active) adapter defaults to marketing."""
        cmo = CMOAgent(agent_id="cmo-001")
        assert cmo.adapter_name == "marketing"

    def test_custom_marketing_purpose(self) -> None:
        cmo = CMOAgent(
            agent_id="cmo-001",
            marketing_purpose="Custom marketing purpose",
        )
        assert cmo.marketing_purpose == "Custom marketing purpose"

    def test_custom_adapters(self) -> None:
        cmo = CMOAgent(
            agent_id="cmo-001",
            marketing_adapter_name="brand",
            leadership_adapter_name="exec-leadership",
        )
        assert cmo.marketing_adapter_name == "brand"
        assert cmo.leadership_adapter_name == "exec-leadership"

    def test_combined_purpose_contains_both(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert "Marketing" in cmo.purpose
        assert "Leadership" in cmo.purpose

    def test_purpose_adapter_mapping_keys(self) -> None:
        cmo = CMOAgent(agent_id="cmo-001")
        assert "marketing" in cmo.purpose_adapter_mapping
        assert "leadership" in cmo.purpose_adapter_mapping


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_both_personas(self, basic_cmo: CMOAgent) -> None:
        personas = basic_cmo.get_agent_type()
        assert "marketing" in personas
        assert "leadership" in personas

    def test_returns_list(self, basic_cmo: CMOAgent) -> None:
        assert isinstance(basic_cmo.get_agent_type(), list)

    def test_returns_exactly_two(self, basic_cmo: CMOAgent) -> None:
        assert len(basic_cmo.get_agent_type()) == 2


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_cmo: CMOAgent) -> None:
        result = await basic_cmo.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.start()
        assert result is True
        assert initialised_cmo.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(self, initialised_cmo: CMOAgent) -> None:
        await initialised_cmo.start()
        result = await initialised_cmo.stop()
        assert result is True
        assert not initialised_cmo.is_running


# ---------------------------------------------------------------------------
# get_adapter_for_purpose
# ---------------------------------------------------------------------------


class TestGetAdapterForPurpose:
    def test_marketing_returns_marketing_adapter(
        self, basic_cmo: CMOAgent
    ) -> None:
        assert basic_cmo.get_adapter_for_purpose("marketing") == "marketing"

    def test_leadership_returns_leadership_adapter(
        self, basic_cmo: CMOAgent
    ) -> None:
        assert basic_cmo.get_adapter_for_purpose("leadership") == "leadership"

    def test_case_insensitive(self, basic_cmo: CMOAgent) -> None:
        assert basic_cmo.get_adapter_for_purpose("MARKETING") == "marketing"
        assert basic_cmo.get_adapter_for_purpose("Leadership") == "leadership"

    def test_unknown_raises_value_error(self, basic_cmo: CMOAgent) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            basic_cmo.get_adapter_for_purpose("finance")

    def test_custom_adapters_returned(self) -> None:
        cmo = CMOAgent(
            agent_id="custom-cmo",
            marketing_adapter_name="brand-v2",
            leadership_adapter_name="exec-v2",
        )
        assert cmo.get_adapter_for_purpose("marketing") == "brand-v2"
        assert cmo.get_adapter_for_purpose("leadership") == "exec-v2"


# ---------------------------------------------------------------------------
# execute_with_purpose
# ---------------------------------------------------------------------------


class TestExecuteWithPurpose:
    @pytest.mark.asyncio
    async def test_marketing_execution_returns_success(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.execute_with_purpose(
            {"type": "brand_event", "data": {}},
            purpose_type="marketing",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_result_includes_purpose_type(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.execute_with_purpose(
            {"type": "campaign", "data": {}},
            purpose_type="marketing",
        )
        assert result["purpose_type"] == "marketing"

    @pytest.mark.asyncio
    async def test_result_includes_adapter_used(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.execute_with_purpose(
            {"type": "campaign", "data": {}},
            purpose_type="marketing",
        )
        assert result["adapter_used"] == "marketing"

    @pytest.mark.asyncio
    async def test_leadership_execution(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.execute_with_purpose(
            {"type": "strategy_review"},
            purpose_type="leadership",
        )
        assert result["purpose_type"] == "leadership"
        assert result["adapter_used"] == "leadership"

    @pytest.mark.asyncio
    async def test_adapter_restored_after_marketing(
        self, initialised_cmo: CMOAgent
    ) -> None:
        """Primary adapter is restored to marketing after any execution."""
        original = initialised_cmo.adapter_name
        await initialised_cmo.execute_with_purpose(
            {"type": "test"}, purpose_type="leadership"
        )
        assert initialised_cmo.adapter_name == original

    @pytest.mark.asyncio
    async def test_adapter_restored_after_error(
        self, initialised_cmo: CMOAgent
    ) -> None:
        """Primary adapter is restored even when a handler raises.

        handle_event() catches handler exceptions internally (matching AOS source
        behaviour), so execute_with_purpose() still succeeds.  The key guarantee
        is that adapter_name is always restored to its original value.
        """
        original = initialised_cmo.adapter_name

        async def bad_handler(data: dict) -> dict:
            raise RuntimeError("Handler error")

        await initialised_cmo.subscribe_to_event("fail_event", bad_handler)

        # handle_event catches handler errors internally — result is still "success"
        result = await initialised_cmo.execute_with_purpose(
            {"type": "fail_event"}, purpose_type="leadership"
        )
        assert result["status"] == "success"
        # Adapter is always restored
        assert initialised_cmo.adapter_name == original

    @pytest.mark.asyncio
    async def test_unknown_purpose_raises_value_error(
        self, initialised_cmo: CMOAgent
    ) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            await initialised_cmo.execute_with_purpose(
                {"type": "test"}, purpose_type="finance"
            )

    @pytest.mark.asyncio
    async def test_default_purpose_is_marketing(
        self, initialised_cmo: CMOAgent
    ) -> None:
        result = await initialised_cmo.execute_with_purpose({"type": "default_test"})
        assert result["purpose_type"] == "marketing"


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_status_contains_agent_type(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert status["agent_type"] == "CMOAgent"

    @pytest.mark.asyncio
    async def test_status_contains_purposes(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert "purposes" in status
        assert "marketing" in status["purposes"]
        assert "leadership" in status["purposes"]

    @pytest.mark.asyncio
    async def test_status_purposes_have_adapter(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert status["purposes"]["marketing"]["adapter"] == "marketing"
        assert status["purposes"]["leadership"]["adapter"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_purpose_adapter_mapping(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert "purpose_adapter_mapping" in status
        assert status["purpose_adapter_mapping"]["marketing"] == "marketing"
        assert status["purpose_adapter_mapping"]["leadership"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_primary_adapter(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert status["primary_adapter"] == "marketing"

    @pytest.mark.asyncio
    async def test_status_inherits_purpose_status_keys(
        self, initialised_cmo: CMOAgent
    ) -> None:
        status = await initialised_cmo.get_status()
        assert "agent_id" in status
        assert "purpose" in status
        assert "metrics" in status
