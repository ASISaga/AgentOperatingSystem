"""
Validation tests for ContextMCPServer and PurposeDrivenAgent implementation.
"""
import os

import pytest

# Base path for source code
SRC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'AgentOperatingSystem')


class TestImplementationStructure:
    """Validate that key implementation files exist and contain expected code."""

    def test_context_mcp_server_exists(self):
        path = os.path.join(SRC_ROOT, 'mcp', 'context_server.py')
        assert os.path.exists(path), "ContextMCPServer file not found"

    def test_context_mcp_server_has_required_methods(self):
        path = os.path.join(SRC_ROOT, 'mcp', 'context_server.py')
        with open(path, 'r') as f:
            content = f.read()
        assert "class ContextMCPServer" in content
        assert "async def initialize" in content
        assert "async def set_context" in content
        assert "async def get_context" in content

    def test_purpose_driven_agent_exists(self):
        path = os.path.join(SRC_ROOT, 'agents', 'purpose_driven.py')
        assert os.path.exists(path), "PurposeDrivenAgent file not found"

    def test_purpose_driven_agent_has_required_code(self):
        path = os.path.join(SRC_ROOT, 'agents', 'purpose_driven.py')
        with open(path, 'r') as f:
            content = f.read()
        assert "class PurposeDrivenAgent" in content
        assert "evaluate_purpose_alignment" in content
        assert "make_purpose_driven_decision" in content

    def test_agents_module_exports(self):
        path = os.path.join(SRC_ROOT, 'agents', '__init__.py')
        with open(path, 'r') as f:
            content = f.read()
        assert "PurposeDrivenAgent" in content

    def test_mcp_module_exports(self):
        path = os.path.join(SRC_ROOT, 'mcp', '__init__.py')
        with open(path, 'r') as f:
            content = f.read()
        assert "ContextMCPServer" in content
