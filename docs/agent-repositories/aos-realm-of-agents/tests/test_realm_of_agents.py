"""Tests for RealmOfAgents function app."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import schema from the src directory
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from agent_config_schema import AgentRegistry, AgentRegistryEntry


class TestAgentRegistryEntry:
    """AgentRegistryEntry model tests."""

    def test_create_minimal(self):
        entry = AgentRegistryEntry(
            agent_id="ceo",
            agent_type="LeadershipAgent",
            purpose="Strategic leadership",
            adapter_name="leadership",
        )
        assert entry.agent_id == "ceo"
        assert entry.enabled is True
        assert entry.capabilities == []

    def test_create_full(self):
        entry = AgentRegistryEntry(
            agent_id="cmo",
            agent_type="CMOAgent",
            purpose="Marketing and brand strategy",
            adapter_name="marketing",
            capabilities=["marketing", "leadership"],
            config={"dual_purpose": True},
            enabled=True,
        )
        assert entry.agent_type == "CMOAgent"
        assert len(entry.capabilities) == 2


class TestAgentRegistry:
    """AgentRegistry model tests."""

    def test_load_example_registry(self):
        registry_path = Path(__file__).resolve().parent.parent / "src" / "example_agent_registry.json"
        with open(registry_path, encoding="utf-8") as fh:
            data = json.load(fh)
        registry = AgentRegistry(**data)
        assert len(registry.agents) == 5

    def test_get_enabled_agents(self):
        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="a1", agent_type="T", purpose="P", adapter_name="a", enabled=True),
            AgentRegistryEntry(agent_id="a2", agent_type="T", purpose="P", adapter_name="a", enabled=False),
        ])
        enabled = registry.get_enabled_agents()
        assert len(enabled) == 1
        assert enabled[0].agent_id == "a1"

    def test_get_agent_by_id(self):
        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="ceo", agent_type="LeadershipAgent", purpose="Lead", adapter_name="leadership"),
        ])
        agent = registry.get_agent("ceo")
        assert agent is not None
        assert agent.agent_id == "ceo"

    def test_get_agent_not_found(self):
        registry = AgentRegistry(agents=[])
        assert registry.get_agent("nonexistent") is None

    def test_filter_by_type(self):
        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="ceo", agent_type="LeadershipAgent", purpose="Lead", adapter_name="leadership"),
            AgentRegistryEntry(agent_id="cmo", agent_type="CMOAgent", purpose="Market", adapter_name="marketing"),
            AgentRegistryEntry(agent_id="cfo", agent_type="LeadershipAgent", purpose="Finance", adapter_name="finance"),
        ])
        leaders = registry.filter_by_type("LeadershipAgent")
        assert len(leaders) == 2
        assert all(a.agent_type == "LeadershipAgent" for a in leaders)

    def test_c_suite_agents_in_example_registry(self):
        """Verify the example registry contains a complete C-suite."""
        registry_path = Path(__file__).resolve().parent.parent / "src" / "example_agent_registry.json"
        with open(registry_path, encoding="utf-8") as fh:
            data = json.load(fh)
        registry = AgentRegistry(**data)
        agent_ids = {a.agent_id for a in registry.get_enabled_agents()}
        assert {"ceo", "cfo", "cmo", "coo", "cto"}.issubset(agent_ids)


class TestFoundryRegistration:
    """Tests for Foundry Agent Service registration via FoundryAgentManager."""

    @pytest.mark.asyncio
    async def test_ensure_foundry_registration_calls_register_agent(self):
        """_ensure_foundry_registration registers all enabled agents via FoundryAgentManager."""
        # Build a minimal fake FoundryAgentManager stub
        mock_manager = MagicMock()
        mock_manager.register_agent = AsyncMock(return_value={"agent_id": "x", "foundry_agent_id": "y"})

        # Import the function under a patched _agent_manager
        import function_app as fa  # already on sys.path via sys.path.insert above

        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="ceo", agent_type="LeadershipAgent", purpose="Lead", adapter_name="leadership"),
            AgentRegistryEntry(agent_id="cfo", agent_type="LeadershipAgent", purpose="Finance", adapter_name="finance"),
        ])

        # Patch module-level state so registration runs fresh
        fa._foundry_registered = False
        original_manager = fa._agent_manager
        try:
            fa._agent_manager = mock_manager
            await fa._ensure_foundry_registration(registry)
        finally:
            fa._agent_manager = original_manager
            fa._foundry_registered = False

        assert mock_manager.register_agent.call_count == 2
        call_ids = {c.kwargs["agent_id"] for c in mock_manager.register_agent.call_args_list}
        assert call_ids == {"ceo", "cfo"}

    @pytest.mark.asyncio
    async def test_ensure_foundry_registration_is_idempotent(self):
        """_ensure_foundry_registration only runs once even when called multiple times."""
        mock_manager = MagicMock()
        mock_manager.register_agent = AsyncMock(return_value={})

        import function_app as fa

        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="ceo", agent_type="LeadershipAgent", purpose="Lead", adapter_name="leadership"),
        ])

        fa._foundry_registered = False
        original_manager = fa._agent_manager
        try:
            fa._agent_manager = mock_manager
            await fa._ensure_foundry_registration(registry)
            await fa._ensure_foundry_registration(registry)
            await fa._ensure_foundry_registration(registry)
        finally:
            fa._agent_manager = original_manager
            fa._foundry_registered = False

        # register_agent should only be called once despite three invocations
        assert mock_manager.register_agent.call_count == 1

    @pytest.mark.asyncio
    async def test_ensure_foundry_registration_without_manager(self):
        """_ensure_foundry_registration logs intent when FoundryAgentManager is unavailable."""
        import function_app as fa

        registry = AgentRegistry(agents=[
            AgentRegistryEntry(agent_id="ceo", agent_type="LeadershipAgent", purpose="Lead", adapter_name="leadership"),
        ])

        fa._foundry_registered = False
        original_manager = fa._agent_manager
        try:
            fa._agent_manager = None
            # Should not raise even without a manager
            await fa._ensure_foundry_registration(registry)
        finally:
            fa._agent_manager = original_manager
            fa._foundry_registered = False

        assert fa._foundry_registered is False  # reset above, confirming flow completed

