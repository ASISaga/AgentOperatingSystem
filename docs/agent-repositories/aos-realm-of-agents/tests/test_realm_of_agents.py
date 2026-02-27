"""Tests for RealmOfAgents function app."""

import json
from pathlib import Path

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

