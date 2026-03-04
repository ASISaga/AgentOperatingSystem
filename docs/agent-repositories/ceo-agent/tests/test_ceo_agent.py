"""
Tests for CEOAgent.

Coverage targets
----------------
- CEOAgent can be created with default parameters.
- Default purpose, adapter names, and role are set correctly.
- get_agent_type() returns ["executive", "leadership"].
- get_adapter_for_purpose() returns correct adapter names.
- get_adapter_for_purpose() raises ValueError for unknown purpose types.
- execute_with_purpose() returns result with purpose_type and adapter_used.
- execute_with_purpose() raises ValueError for unknown purpose type.
- execute_with_purpose() restores adapter_name after execution.
- get_status() returns dual-purpose status structure.
- Boardroom orchestration: enroll, get tools, get instructions.
- initialize() succeeds.
"""

import pytest

from ceo_agent import CEOAgent


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    def test_create_with_defaults(self) -> None:
        """CEOAgent can be created with only agent_id."""
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.agent_id == "ceo-001"

    def test_default_name(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.name == "CEO"

    def test_default_role(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.role == "CEO"

    def test_default_executive_adapter(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.executive_adapter_name == "executive"

    def test_default_leadership_adapter(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.leadership_adapter_name == "leadership"

    def test_primary_adapter_is_executive(self) -> None:
        """Primary (active) adapter defaults to executive."""
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.adapter_name == "executive"

    def test_custom_executive_purpose(self) -> None:
        ceo = CEOAgent(
            agent_id="ceo-001",
            executive_purpose="Custom executive purpose",
        )
        assert ceo.executive_purpose == "Custom executive purpose"

    def test_custom_adapters(self) -> None:
        ceo = CEOAgent(
            agent_id="ceo-001",
            executive_adapter_name="strategic",
            leadership_adapter_name="exec-leadership",
        )
        assert ceo.executive_adapter_name == "strategic"
        assert ceo.leadership_adapter_name == "exec-leadership"

    def test_combined_purpose_contains_both(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert "Executive" in ceo.purpose
        assert "Leadership" in ceo.purpose

    def test_purpose_adapter_mapping_keys(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert "executive" in ceo.purpose_adapter_mapping
        assert "leadership" in ceo.purpose_adapter_mapping

    def test_boardroom_tools_empty_by_default(self) -> None:
        ceo = CEOAgent(agent_id="ceo-001")
        assert ceo.boardroom_tools == []
        assert ceo.get_specialist_tools() == []


# ---------------------------------------------------------------------------
# get_agent_type
# ---------------------------------------------------------------------------


class TestGetAgentType:
    def test_returns_both_personas(self, basic_ceo: CEOAgent) -> None:
        personas = basic_ceo.get_agent_type()
        assert "executive" in personas
        assert "leadership" in personas

    def test_returns_list(self, basic_ceo: CEOAgent) -> None:
        assert isinstance(basic_ceo.get_agent_type(), list)

    def test_returns_exactly_two(self, basic_ceo: CEOAgent) -> None:
        assert len(basic_ceo.get_agent_type()) == 2


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:
    @pytest.mark.asyncio
    async def test_initialize_returns_true(self, basic_ceo: CEOAgent) -> None:
        result = await basic_ceo.initialize()
        assert result is True

    @pytest.mark.asyncio
    async def test_start_sets_is_running(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.start()
        assert result is True
        assert initialised_ceo.is_running

    @pytest.mark.asyncio
    async def test_stop_returns_true(self, initialised_ceo: CEOAgent) -> None:
        await initialised_ceo.start()
        result = await initialised_ceo.stop()
        assert result is True
        assert not initialised_ceo.is_running


# ---------------------------------------------------------------------------
# get_adapter_for_purpose
# ---------------------------------------------------------------------------


class TestGetAdapterForPurpose:
    def test_executive_returns_executive_adapter(
        self, basic_ceo: CEOAgent
    ) -> None:
        assert basic_ceo.get_adapter_for_purpose("executive") == "executive"

    def test_leadership_returns_leadership_adapter(
        self, basic_ceo: CEOAgent
    ) -> None:
        assert basic_ceo.get_adapter_for_purpose("leadership") == "leadership"

    def test_case_insensitive(self, basic_ceo: CEOAgent) -> None:
        assert basic_ceo.get_adapter_for_purpose("EXECUTIVE") == "executive"
        assert basic_ceo.get_adapter_for_purpose("Leadership") == "leadership"

    def test_unknown_raises_value_error(self, basic_ceo: CEOAgent) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            basic_ceo.get_adapter_for_purpose("finance")

    def test_custom_adapters_returned(self) -> None:
        ceo = CEOAgent(
            agent_id="custom-ceo",
            executive_adapter_name="strategic-v2",
            leadership_adapter_name="exec-v2",
        )
        assert ceo.get_adapter_for_purpose("executive") == "strategic-v2"
        assert ceo.get_adapter_for_purpose("leadership") == "exec-v2"


# ---------------------------------------------------------------------------
# execute_with_purpose
# ---------------------------------------------------------------------------


class TestExecuteWithPurpose:
    @pytest.mark.asyncio
    async def test_executive_execution_returns_success(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.execute_with_purpose(
            {"type": "strategic_review", "data": {}},
            purpose_type="executive",
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_result_includes_purpose_type(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.execute_with_purpose(
            {"type": "vision_setting", "data": {}},
            purpose_type="executive",
        )
        assert result["purpose_type"] == "executive"

    @pytest.mark.asyncio
    async def test_result_includes_adapter_used(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.execute_with_purpose(
            {"type": "vision_setting", "data": {}},
            purpose_type="executive",
        )
        assert result["adapter_used"] == "executive"

    @pytest.mark.asyncio
    async def test_leadership_execution(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.execute_with_purpose(
            {"type": "org_alignment"},
            purpose_type="leadership",
        )
        assert result["purpose_type"] == "leadership"
        assert result["adapter_used"] == "leadership"

    @pytest.mark.asyncio
    async def test_adapter_restored_after_execution(
        self, initialised_ceo: CEOAgent
    ) -> None:
        """Primary adapter is restored to executive after any execution."""
        original = initialised_ceo.adapter_name
        await initialised_ceo.execute_with_purpose(
            {"type": "test"}, purpose_type="leadership"
        )
        assert initialised_ceo.adapter_name == original

    @pytest.mark.asyncio
    async def test_unknown_purpose_raises_value_error(
        self, initialised_ceo: CEOAgent
    ) -> None:
        with pytest.raises(ValueError, match="Unknown purpose type"):
            await initialised_ceo.execute_with_purpose(
                {"type": "test"}, purpose_type="marketing"
            )

    @pytest.mark.asyncio
    async def test_default_purpose_is_executive(
        self, initialised_ceo: CEOAgent
    ) -> None:
        result = await initialised_ceo.execute_with_purpose({"type": "default_test"})
        assert result["purpose_type"] == "executive"


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    @pytest.mark.asyncio
    async def test_status_contains_agent_type(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert status["agent_type"] == "CEOAgent"

    @pytest.mark.asyncio
    async def test_status_contains_purposes(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert "purposes" in status
        assert "executive" in status["purposes"]
        assert "leadership" in status["purposes"]

    @pytest.mark.asyncio
    async def test_status_purposes_have_adapter(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert status["purposes"]["executive"]["adapter"] == "executive"
        assert status["purposes"]["leadership"]["adapter"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_purpose_adapter_mapping(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert "purpose_adapter_mapping" in status
        assert status["purpose_adapter_mapping"]["executive"] == "executive"
        assert status["purpose_adapter_mapping"]["leadership"] == "leadership"

    @pytest.mark.asyncio
    async def test_status_primary_adapter(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert status["primary_adapter"] == "executive"

    @pytest.mark.asyncio
    async def test_status_inherits_purpose_status_keys(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert "agent_id" in status
        assert "purpose" in status
        assert "metrics" in status

    @pytest.mark.asyncio
    async def test_status_specialist_tools_count(
        self, initialised_ceo: CEOAgent
    ) -> None:
        status = await initialised_ceo.get_status()
        assert status["specialist_tools_count"] == 0


# ---------------------------------------------------------------------------
# Boardroom orchestration
# ---------------------------------------------------------------------------


class TestBoardroom:
    def test_get_boardroom_instructions_returns_string(
        self, basic_ceo: CEOAgent
    ) -> None:
        instructions = basic_ceo.get_boardroom_instructions()
        assert isinstance(instructions, str)
        assert "CEO" in instructions
        assert "Chairperson" in instructions

    def test_get_boardroom_instructions_mentions_specialists(
        self, basic_ceo: CEOAgent
    ) -> None:
        instructions = basic_ceo.get_boardroom_instructions()
        assert "CTO" in instructions
        assert "CFO" in instructions
        assert "CSO" in instructions
        assert "CMO" in instructions

    def test_get_boardroom_tools_empty_initially(
        self, basic_ceo: CEOAgent
    ) -> None:
        assert basic_ceo.get_boardroom_tools() == []

    def test_enroll_boardroom_tools(self, basic_ceo: CEOAgent) -> None:
        """enroll_boardroom_tools stores tools from specialist agents."""

        class MockTool:
            """Stand-in for A2AAgentTool."""

        class MockSpecialist:
            """Stand-in for PurposeDrivenAgent with as_tool()."""

            def as_tool(self, thread_id=None):
                return MockTool()

        specialists = [MockSpecialist(), MockSpecialist()]
        tools = basic_ceo.enroll_boardroom_tools(specialists)
        assert len(tools) == 2
        assert len(basic_ceo.boardroom_tools) == 2

    def test_get_boardroom_tools_after_enroll(
        self, basic_ceo: CEOAgent
    ) -> None:

        class MockTool:
            pass

        class MockSpecialist:
            def as_tool(self, thread_id=None):
                return MockTool()

        basic_ceo.enroll_boardroom_tools([MockSpecialist()])
        tools = basic_ceo.get_boardroom_tools()
        assert len(tools) == 1

    def test_enroll_with_thread_id(self, basic_ceo: CEOAgent) -> None:

        class MockSpecialist:
            def as_tool(self, thread_id=None):
                return {"thread_id": thread_id}

        tools = basic_ceo.enroll_boardroom_tools(
            [MockSpecialist()], thread_id="thread-123"
        )
        assert tools[0]["thread_id"] == "thread-123"
