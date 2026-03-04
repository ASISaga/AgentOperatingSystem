"""
Tests for CTOAgent.

Coverage targets
----------------
- CTOAgent can be created with default parameters.
- Default purpose, adapter names, and role are set correctly.
- get_agent_type() returns ["technology", "leadership"].
- get_adapter_for_purpose() returns correct adapter names.
- get_adapter_for_purpose() raises ValueError for unknown purpose types.
- execute_with_purpose() returns result with purpose_type and adapter_used.
- execute_with_purpose() raises ValueError for unknown purpose type.
- execute_with_purpose() restores adapter_name after execution.
- get_status() returns dual-purpose status structure.
- initialize() succeeds.
"""

import pytest

from cto_agent import CTOAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """CTOAgent can be created with only agent_id."""
        cto = CTOAgent(agent_id="cto-001")
        assert cto.agent_id == "cto-001"

    def test_default_name(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert cto.name == "CTO"

    def test_default_role(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert cto.role == "CTO"

    def test_default_technology_adapter(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert cto.technology_adapter_name == "technology"

    def test_default_leadership_adapter(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert cto.leadership_adapter_name == "leadership"

    def test_primary_adapter_is_technology(self) -> None:
        """Primary (active) adapter defaults to technology."""
        cto = CTOAgent(agent_id="cto-001")
        assert cto.adapter_name == "technology"

    def test_custom_technology_purpose(self) -> None:
        cto = CTOAgent(
            agent_id="cto-001",
            technology_purpose="Custom technology purpose",
        )
        assert cto.technology_purpose == "Custom technology purpose"

    def test_custom_adapters(self) -> None:
        cto = CTOAgent(
            agent_id="cto-001",
            technology_adapter_name="infra",
            leadership_adapter_name="exec-leadership",
        )
        assert cto.technology_adapter_name == "infra"
        assert cto.leadership_adapter_name == "exec-leadership"

    def test_combined_purpose_contains_both(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert "Technology" in cto.purpose
        assert "Leadership" in cto.purpose

    def test_purpose_adapter_mapping_keys(self) -> None:
        cto = CTOAgent(agent_id="cto-001")
        assert "technology" in cto.purpose_adapter_mapping
        assert "leadership" in cto.purpose_adapter_mapping


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_both_personas(self, basic_cto: CTOAgent) -> None:
        personas = basic_cto.get_agent_type()
        assert "technology" in personas
        assert "leadership" in personas

    def test_returns_list(self, basic_cto: CTOAgent) -> None:
        assert isinstance(basic_cto.get_agent_type(), list)

    def test_returns_exactly_two(self, basic_cto: CTOAgent) -> None:
        assert len(basic_cto.get_agent_type()) == 2


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_cto: CTOAgent) -> None:
        result = await basic_cto.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.start()
        assert result is True
        assert initialised_cto.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(self, initialised_cto: CTOAgent) -> None:
        await initialised_cto.start()
        result = await initialised_cto.stop()
        assert result is True
        assert not initialised_cto.is_running


# ---------------------------------------------------------------------------
# get_adapter_for_purpose
# ---------------------------------------------------------------------------


class TestGetAdapterForPurpose:
    def test_technology_returns_technology_adapter(
        self, basic_cto: CTOAgent
    ) -> None:
        assert basic_cto.get_adapter_for_purpose("technology") == "technology"

    def test_leadership_returns_leadership_adapter(
        self, basic_cto: CTOAgent
    ) -> None:
        assert basic_cto.get_adapter_for_purpose("leadership") == "leadership"

    def test_case_insensitive(self, basic_cto: CTOAgent) -> None:
        assert basic_cto.get_adapter_for_purpose("TECHNOLOGY") == "technology"
        assert basic_cto.get_adapter_for_purpose("Leadership") == "leadership"

    def test_unknown_raises_value_error(self, basic_cto: CTOAgent) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            basic_cto.get_adapter_for_purpose("marketing")

    def test_custom_adapters_returned(self) -> None:
        cto = CTOAgent(
            agent_id="custom-cto",
            technology_adapter_name="infra-v2",
            leadership_adapter_name="exec-v2",
        )
        assert cto.get_adapter_for_purpose("technology") == "infra-v2"
        assert cto.get_adapter_for_purpose("leadership") == "exec-v2"


# ---------------------------------------------------------------------------
# execute_with_purpose
# ---------------------------------------------------------------------------


class TestExecuteWithPurpose:
    @pytest.mark.asyncio
    async def test_technology_execution_returns_success(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.execute_with_purpose(
            {"type": "architecture_review", "data": {}},
            purpose_type="technology",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_result_includes_purpose_type(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.execute_with_purpose(
            {"type": "tech_roadmap", "data": {}},
            purpose_type="technology",
        )
        assert result["purpose_type"] == "technology"

    @pytest.mark.asyncio
    async def test_result_includes_adapter_used(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.execute_with_purpose(
            {"type": "tech_roadmap", "data": {}},
            purpose_type="technology",
        )
        assert result["adapter_used"] == "technology"

    @pytest.mark.asyncio
    async def test_leadership_execution(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.execute_with_purpose(
            {"type": "team_restructure"},
            purpose_type="leadership",
        )
        assert result["purpose_type"] == "leadership"
        assert result["adapter_used"] == "leadership"

    @pytest.mark.asyncio
    async def test_adapter_restored_after_execution(
        self, initialised_cto: CTOAgent
    ) -> None:
        """Primary adapter is restored to technology after any execution."""
        original = initialised_cto.adapter_name
        await initialised_cto.execute_with_purpose(
            {"type": "test"}, purpose_type="leadership"
        )
        assert initialised_cto.adapter_name == original

    @pytest.mark.asyncio
    async def test_unknown_purpose_raises_value_error(
        self, initialised_cto: CTOAgent
    ) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            await initialised_cto.execute_with_purpose(
                {"type": "test"}, purpose_type="marketing"
            )

    @pytest.mark.asyncio
    async def test_default_purpose_is_technology(
        self, initialised_cto: CTOAgent
    ) -> None:
        result = await initialised_cto.execute_with_purpose({"type": "default_test"})
        assert result["purpose_type"] == "technology"


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_status_contains_agent_type(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert status["agent_type"] == "CTOAgent"

    @pytest.mark.asyncio
    async def test_status_contains_purposes(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert "purposes" in status
        assert "technology" in status["purposes"]
        assert "leadership" in status["purposes"]

    @pytest.mark.asyncio
    async def test_status_purposes_have_adapter(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert status["purposes"]["technology"]["adapter"] == "technology"
        assert status["purposes"]["leadership"]["adapter"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_purpose_adapter_mapping(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert "purpose_adapter_mapping" in status
        assert status["purpose_adapter_mapping"]["technology"] == "technology"
        assert status["purpose_adapter_mapping"]["leadership"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_primary_adapter(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert status["primary_adapter"] == "technology"

    @pytest.mark.asyncio
    async def test_status_inherits_purpose_status_keys(
        self, initialised_cto: CTOAgent
    ) -> None:
        status = await initialised_cto.get_status()
        assert "agent_id" in status
        assert "purpose" in status
        assert "metrics" in status
