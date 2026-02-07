"""
Validation tests for CMOAgent and LeadershipAgent structure.
"""
import os
import re

import pytest

AGENTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'AgentOperatingSystem', 'agents')


def _read_file(filename):
    path = os.path.join(AGENTS_DIR, filename)
    with open(path, 'r') as f:
        return f.read()


class TestAgentHierarchy:
    """Validate agent inheritance and purpose-adapter mapping."""

    def test_leadership_agent_syntax(self):
        path = os.path.join(AGENTS_DIR, 'leadership_agent.py')
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')

    def test_cmo_agent_syntax(self):
        path = os.path.join(AGENTS_DIR, 'cmo_agent.py')
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')

    def test_leadership_inherits_from_purpose_driven(self):
        content = _read_file('leadership_agent.py')
        assert re.search(r'class\s+LeadershipAgent\s*\(\s*PurposeDrivenAgent\s*\)', content)

    def test_cmo_inherits_from_leadership(self):
        content = _read_file('cmo_agent.py')
        assert re.search(r'class\s+CMOAgent\s*\(\s*LeadershipAgent\s*\)', content)

    def test_cmo_has_purpose_adapter_mapping(self):
        content = _read_file('cmo_agent.py')
        assert 'purpose_adapter_mapping' in content

    def test_cmo_has_dual_purposes(self):
        content = _read_file('cmo_agent.py')
        assert 'marketing_purpose' in content
        assert 'leadership_purpose' in content
        assert 'marketing_adapter_name' in content
        assert 'leadership_adapter_name' in content

    def test_cmo_exported_in_init(self):
        content = _read_file('__init__.py')
        assert 'CMOAgent' in content
