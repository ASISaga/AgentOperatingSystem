"""
Tests for CSOAgent.

Coverage targets
----------------
- CSOAgent can be created with default parameters.
- Default purpose, adapter names, and role are set correctly.
- get_agent_type() returns ["security", "leadership"].
- get_adapter_for_purpose() returns correct adapter names.
- get_adapter_for_purpose() raises ValueError for unknown purpose types.
- execute_with_purpose() returns result with purpose_type and adapter_used.
- execute_with_purpose() raises ValueError for unknown purpose type.
- execute_with_purpose() restores adapter_name after execution.
- get_status() returns dual-purpose status structure.
- initialize() succeeds.
"""

import pytest

from cso_agent import CSOAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """CSOAgent can be created with only agent_id."""
        cso = CSOAgent(agent_id="cso-001")
        assert cso.agent_id == "cso-001"

    def test_default_name(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert cso.name == "CSO"

    def test_default_role(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert cso.role == "CSO"

    def test_default_security_adapter(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert cso.security_adapter_name == "security"

    def test_default_leadership_adapter(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert cso.leadership_adapter_name == "leadership"

    def test_primary_adapter_is_security(self) -> None:
        """Primary (active) adapter defaults to security."""
        cso = CSOAgent(agent_id="cso-001")
        assert cso.adapter_name == "security"

    def test_custom_security_purpose(self) -> None:
        cso = CSOAgent(
            agent_id="cso-001",
            security_purpose="Custom security purpose",
        )
        assert cso.security_purpose == "Custom security purpose"

    def test_custom_adapters(self) -> None:
        cso = CSOAgent(
            agent_id="cso-001",
            security_adapter_name="cyber",
            leadership_adapter_name="exec-leadership",
        )
        assert cso.security_adapter_name == "cyber"
        assert cso.leadership_adapter_name == "exec-leadership"

    def test_combined_purpose_contains_both(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert "Security" in cso.purpose
        assert "Leadership" in cso.purpose

    def test_purpose_adapter_mapping_keys(self) -> None:
        cso = CSOAgent(agent_id="cso-001")
        assert "security" in cso.purpose_adapter_mapping
        assert "leadership" in cso.purpose_adapter_mapping


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_both_personas(self, basic_cso: CSOAgent) -> None:
        personas = basic_cso.get_agent_type()
        assert "security" in personas
        assert "leadership" in personas

    def test_returns_list(self, basic_cso: CSOAgent) -> None:
        assert isinstance(basic_cso.get_agent_type(), list)

    def test_returns_exactly_two(self, basic_cso: CSOAgent) -> None:
        assert len(basic_cso.get_agent_type()) == 2


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_cso: CSOAgent) -> None:
        result = await basic_cso.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.start()
        assert result is True
        assert initialised_cso.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(self, initialised_cso: CSOAgent) -> None:
        await initialised_cso.start()
        result = await initialised_cso.stop()
        assert result is True
        assert not initialised_cso.is_running


# ---------------------------------------------------------------------------
# get_adapter_for_purpose
# ---------------------------------------------------------------------------


class TestGetAdapterForPurpose:
    def test_security_returns_security_adapter(
        self, basic_cso: CSOAgent
    ) -> None:
        assert basic_cso.get_adapter_for_purpose("security") == "security"

    def test_leadership_returns_leadership_adapter(
        self, basic_cso: CSOAgent
    ) -> None:
        assert basic_cso.get_adapter_for_purpose("leadership") == "leadership"

    def test_case_insensitive(self, basic_cso: CSOAgent) -> None:
        assert basic_cso.get_adapter_for_purpose("SECURITY") == "security"
        assert basic_cso.get_adapter_for_purpose("Leadership") == "leadership"

    def test_unknown_raises_value_error(self, basic_cso: CSOAgent) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            basic_cso.get_adapter_for_purpose("marketing")

    def test_custom_adapters_returned(self) -> None:
        cso = CSOAgent(
            agent_id="custom-cso",
            security_adapter_name="cyber-v2",
            leadership_adapter_name="exec-v2",
        )
        assert cso.get_adapter_for_purpose("security") == "cyber-v2"
        assert cso.get_adapter_for_purpose("leadership") == "exec-v2"


# ---------------------------------------------------------------------------
# execute_with_purpose
# ---------------------------------------------------------------------------


class TestExecuteWithPurpose:
    @pytest.mark.asyncio
    async def test_security_execution_returns_success(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.execute_with_purpose(
            {"type": "risk_assessment", "data": {}},
            purpose_type="security",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_result_includes_purpose_type(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.execute_with_purpose(
            {"type": "compliance_check", "data": {}},
            purpose_type="security",
        )
        assert result["purpose_type"] == "security"

    @pytest.mark.asyncio
    async def test_result_includes_adapter_used(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.execute_with_purpose(
            {"type": "compliance_check", "data": {}},
            purpose_type="security",
        )
        assert result["adapter_used"] == "security"

    @pytest.mark.asyncio
    async def test_leadership_execution(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.execute_with_purpose(
            {"type": "compliance_review"},
            purpose_type="leadership",
        )
        assert result["purpose_type"] == "leadership"
        assert result["adapter_used"] == "leadership"

    @pytest.mark.asyncio
    async def test_adapter_restored_after_execution(
        self, initialised_cso: CSOAgent
    ) -> None:
        """Primary adapter is restored to security after any execution."""
        original = initialised_cso.adapter_name
        await initialised_cso.execute_with_purpose(
            {"type": "test"}, purpose_type="leadership"
        )
        assert initialised_cso.adapter_name == original

    @pytest.mark.asyncio
    async def test_unknown_purpose_raises_value_error(
        self, initialised_cso: CSOAgent
    ) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            await initialised_cso.execute_with_purpose(
                {"type": "test"}, purpose_type="marketing"
            )

    @pytest.mark.asyncio
    async def test_default_purpose_is_security(
        self, initialised_cso: CSOAgent
    ) -> None:
        result = await initialised_cso.execute_with_purpose({"type": "default_test"})
        assert result["purpose_type"] == "security"


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_status_contains_agent_type(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert status["agent_type"] == "CSOAgent"

    @pytest.mark.asyncio
    async def test_status_contains_purposes(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert "purposes" in status
        assert "security" in status["purposes"]
        assert "leadership" in status["purposes"]

    @pytest.mark.asyncio
    async def test_status_purposes_have_adapter(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert status["purposes"]["security"]["adapter"] == "security"
        assert status["purposes"]["leadership"]["adapter"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_purpose_adapter_mapping(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert "purpose_adapter_mapping" in status
        assert status["purpose_adapter_mapping"]["security"] == "security"
        assert status["purpose_adapter_mapping"]["leadership"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_primary_adapter(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert status["primary_adapter"] == "security"

    @pytest.mark.asyncio
    async def test_status_inherits_purpose_status_keys(
        self, initialised_cso: CSOAgent
    ) -> None:
        status = await initialised_cso.get_status()
        assert "agent_id" in status
        assert "purpose" in status
        assert "metrics" in status
