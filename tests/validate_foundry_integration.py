"""
Tests for Azure Foundry Agent Service integration.
"""
import os

import pytest

SRC_ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'AgentOperatingSystem')


class TestFoundryIntegration:
    """Validate Foundry Agent Service integration files and structure."""

    def test_foundry_service_file_syntax(self):
        path = os.path.join(SRC_ROOT, 'ml', 'foundry_agent_service.py')
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')

    def test_model_orchestration_file_syntax(self):
        path = os.path.join(SRC_ROOT, 'orchestration', 'model_orchestration.py')
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')

    def test_ml_config_file_syntax(self):
        path = os.path.join(SRC_ROOT, 'config', 'ml.py')
        with open(path, 'r') as f:
            compile(f.read(), path, 'exec')

    def test_foundry_client_has_required_classes(self):
        path = os.path.join(SRC_ROOT, 'ml', 'foundry_agent_service.py')
        with open(path, 'r') as f:
            content = f.read()
        for cls in ['FoundryAgentServiceConfig', 'FoundryAgentServiceClient',
                     'FoundryResponse', 'ThreadInfo']:
            assert f'class {cls}' in content, f"{cls} not found"

    def test_foundry_client_has_required_methods(self):
        path = os.path.join(SRC_ROOT, 'ml', 'foundry_agent_service.py')
        with open(path, 'r') as f:
            content = f.read()
        for method in ['async def initialize', 'async def send_message',
                       'async def create_thread', 'async def health_check',
                       'def get_metrics']:
            assert method in content, f"{method} not found"

    def test_model_type_enum_has_foundry(self):
        path = os.path.join(SRC_ROOT, 'orchestration', 'model_orchestration.py')
        with open(path, 'r') as f:
            content = f.read()
        assert 'FOUNDRY_AGENT_SERVICE = "foundry_agent_service"' in content

    def test_ml_config_has_foundry_fields(self):
        path = os.path.join(SRC_ROOT, 'config', 'ml.py')
        with open(path, 'r') as f:
            content = f.read()
        for field in ['enable_foundry_agent_service', 'foundry_model']:
            assert field in content, f"{field} not found in MLConfig"
