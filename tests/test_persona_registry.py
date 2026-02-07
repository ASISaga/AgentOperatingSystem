"""
Test persona registry and LoRA adapter mapping architecture.
"""


class MockAOS:
    """Mock AgentOperatingSystem with persona registry."""

    def __init__(self):
        self.persona_registry = {
            "generic": "general",
            "leadership": "leadership",
            "marketing": "marketing",
            "finance": "finance",
            "operations": "operations",
        }

    def get_available_personas(self):
        return list(self.persona_registry.keys())

    def get_adapter_for_persona(self, persona_name):
        return self.persona_registry.get(persona_name)

    def validate_personas(self, personas):
        return all(p in self.persona_registry for p in personas)

    def register_persona(self, persona_name, adapter_name):
        self.persona_registry[persona_name] = adapter_name


class TestPersonaRegistry:
    """Verify persona registry and adapter mapping."""

    def test_initial_personas(self):
        aos = MockAOS()
        personas = aos.get_available_personas()
        assert "generic" in personas
        assert "leadership" in personas
        assert "marketing" in personas

    def test_adapter_mapping(self):
        aos = MockAOS()
        assert aos.get_adapter_for_persona("generic") == "general"
        assert aos.get_adapter_for_persona("leadership") == "leadership"

    def test_validate_existing_personas(self):
        aos = MockAOS()
        assert aos.validate_personas(["marketing", "leadership"]) is True

    def test_validate_invalid_persona(self):
        aos = MockAOS()
        assert aos.validate_personas(["marketing", "invalid_persona"]) is False

    def test_dynamic_persona_registration(self):
        aos = MockAOS()
        aos.register_persona("technology", "cto")
        assert "technology" in aos.get_available_personas()
        assert aos.get_adapter_for_persona("technology") == "cto"

    def test_composable_personas(self):
        """CMO should use both marketing and leadership personas."""
        aos = MockAOS()
        cmo_personas = ["marketing", "leadership"]
        assert aos.validate_personas(cmo_personas)
        adapters = [aos.get_adapter_for_persona(p) for p in cmo_personas]
        assert adapters == ["marketing", "leadership"]
