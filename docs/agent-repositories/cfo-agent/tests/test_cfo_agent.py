"""
Tests for CFOAgent.

Coverage targets
----------------
- CFOAgent can be created with default parameters.
- Default purpose, adapter names, and role are set correctly.
- get_agent_type() returns ["finance", "leadership"].
- get_adapter_for_purpose() returns correct adapter names.
- get_adapter_for_purpose() raises ValueError for unknown purpose types.
- execute_with_purpose() returns result with purpose_type and adapter_used.
- execute_with_purpose() raises ValueError for unknown purpose type.
- execute_with_purpose() restores adapter_name after execution.
- get_status() returns dual-purpose status structure.
- initialize() succeeds.
"""

import pytest

from cfo_agent import CFOAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """CFOAgent can be created with only agent_id."""
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.agent_id == "cfo-001"

    def test_default_name(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.name == "CFO"

    def test_default_role(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.role == "CFO"

    def test_default_finance_adapter(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.finance_adapter_name == "finance"

    def test_default_leadership_adapter(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.leadership_adapter_name == "leadership"

    def test_primary_adapter_is_finance(self) -> None:
        """Primary (active) adapter defaults to finance."""
        cfo = CFOAgent(agent_id="cfo-001")
        assert cfo.adapter_name == "finance"

    def test_custom_finance_purpose(self) -> None:
        cfo = CFOAgent(
            agent_id="cfo-001",
            finance_purpose="Custom finance purpose",
        )
        assert cfo.finance_purpose == "Custom finance purpose"

    def test_custom_adapters(self) -> None:
        cfo = CFOAgent(
            agent_id="cfo-001",
            finance_adapter_name="fiscal",
            leadership_adapter_name="exec-leadership",
        )
        assert cfo.finance_adapter_name == "fiscal"
        assert cfo.leadership_adapter_name == "exec-leadership"

    def test_combined_purpose_contains_both(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert "Financial" in cfo.purpose
        assert "Leadership" in cfo.purpose

    def test_purpose_adapter_mapping_keys(self) -> None:
        cfo = CFOAgent(agent_id="cfo-001")
        assert "finance" in cfo.purpose_adapter_mapping
        assert "leadership" in cfo.purpose_adapter_mapping


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_both_personas(self, basic_cfo: CFOAgent) -> None:
        personas = basic_cfo.get_agent_type()
        assert "finance" in personas
        assert "leadership" in personas

    def test_returns_list(self, basic_cfo: CFOAgent) -> None:
        assert isinstance(basic_cfo.get_agent_type(), list)

    def test_returns_exactly_two(self, basic_cfo: CFOAgent) -> None:
        assert len(basic_cfo.get_agent_type()) == 2


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_cfo: CFOAgent) -> None:
        result = await basic_cfo.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.start()
        assert result is True
        assert initialised_cfo.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(self, initialised_cfo: CFOAgent) -> None:
        await initialised_cfo.start()
        result = await initialised_cfo.stop()
        assert result is True
        assert not initialised_cfo.is_running


# ---------------------------------------------------------------------------
# get_adapter_for_purpose
# ---------------------------------------------------------------------------


class TestGetAdapterForPurpose:
    def test_finance_returns_finance_adapter(
        self, basic_cfo: CFOAgent
    ) -> None:
        assert basic_cfo.get_adapter_for_purpose("finance") == "finance"

    def test_leadership_returns_leadership_adapter(
        self, basic_cfo: CFOAgent
    ) -> None:
        assert basic_cfo.get_adapter_for_purpose("leadership") == "leadership"

    def test_case_insensitive(self, basic_cfo: CFOAgent) -> None:
        assert basic_cfo.get_adapter_for_purpose("FINANCE") == "finance"
        assert basic_cfo.get_adapter_for_purpose("Leadership") == "leadership"

    def test_unknown_raises_value_error(self, basic_cfo: CFOAgent) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            basic_cfo.get_adapter_for_purpose("marketing")

    def test_custom_adapters_returned(self) -> None:
        cfo = CFOAgent(
            agent_id="custom-cfo",
            finance_adapter_name="fiscal-v2",
            leadership_adapter_name="exec-v2",
        )
        assert cfo.get_adapter_for_purpose("finance") == "fiscal-v2"
        assert cfo.get_adapter_for_purpose("leadership") == "exec-v2"


# ---------------------------------------------------------------------------
# execute_with_purpose
# ---------------------------------------------------------------------------


class TestExecuteWithPurpose:
    @pytest.mark.asyncio
    async def test_finance_execution_returns_success(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.execute_with_purpose(
            {"type": "budget_audit", "data": {}},
            purpose_type="finance",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_result_includes_purpose_type(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.execute_with_purpose(
            {"type": "revenue_forecast", "data": {}},
            purpose_type="finance",
        )
        assert result["purpose_type"] == "finance"

    @pytest.mark.asyncio
    async def test_result_includes_adapter_used(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.execute_with_purpose(
            {"type": "revenue_forecast", "data": {}},
            purpose_type="finance",
        )
        assert result["adapter_used"] == "finance"

    @pytest.mark.asyncio
    async def test_leadership_execution(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.execute_with_purpose(
            {"type": "resource_allocation"},
            purpose_type="leadership",
        )
        assert result["purpose_type"] == "leadership"
        assert result["adapter_used"] == "leadership"

    @pytest.mark.asyncio
    async def test_adapter_restored_after_execution(
        self, initialised_cfo: CFOAgent
    ) -> None:
        """Primary adapter is restored to finance after any execution."""
        original = initialised_cfo.adapter_name
        await initialised_cfo.execute_with_purpose(
            {"type": "test"}, purpose_type="leadership"
        )
        assert initialised_cfo.adapter_name == original

    @pytest.mark.asyncio
    async def test_unknown_purpose_raises_value_error(
        self, initialised_cfo: CFOAgent
    ) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            await initialised_cfo.execute_with_purpose(
                {"type": "test"}, purpose_type="marketing"
            )

    @pytest.mark.asyncio
    async def test_default_purpose_is_finance(
        self, initialised_cfo: CFOAgent
    ) -> None:
        result = await initialised_cfo.execute_with_purpose({"type": "default_test"})
        assert result["purpose_type"] == "finance"


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_status_contains_agent_type(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert status["agent_type"] == "CFOAgent"

    @pytest.mark.asyncio
    async def test_status_contains_purposes(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert "purposes" in status
        assert "finance" in status["purposes"]
        assert "leadership" in status["purposes"]

    @pytest.mark.asyncio
    async def test_status_purposes_have_adapter(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert status["purposes"]["finance"]["adapter"] == "finance"
        assert status["purposes"]["leadership"]["adapter"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_purpose_adapter_mapping(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert "purpose_adapter_mapping" in status
        assert status["purpose_adapter_mapping"]["finance"] == "finance"
        assert status["purpose_adapter_mapping"]["leadership"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_primary_adapter(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert status["primary_adapter"] == "finance"

    @pytest.mark.asyncio
    async def test_status_inherits_purpose_status_keys(
        self, initialised_cfo: CFOAgent
    ) -> None:
        status = await initialised_cfo.get_status()
        assert "agent_id" in status
        assert "purpose" in status
        assert "metrics" in status
