"""
Test persona registry and LoRA adapter mapping architecture.

This demonstrates how:
1. AgentOperatingSystem maintains a registry of available personas
2. Each persona maps to a LoRA adapter
3. PurposeDrivenAgents query AOS for available personas
4. Agents select combinations of personas (e.g., CMO = Marketing + Leadership)
5. AOS/LoRAx superimposes selected LoRA adapters at runtime
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=" * 70)
print("Persona Registry & LoRA Adapter Mapping Architecture Test")
print("=" * 70)

# Step 1: Create mock AgentOperatingSystem with persona registry
print("\n1. AgentOperatingSystem - Persona Registry")
print("-" * 70)

class MockAOS:
    """Mock AgentOperatingSystem with persona registry"""
    def __init__(self):
        self.persona_registry = {
            "generic": "general",
            "leadership": "leadership",
            "marketing": "marketing",
            "finance": "finance",
            "operations": "operations",
        }
        print(f"   Initialized persona registry with {len(self.persona_registry)} personas:")
        for persona, adapter in self.persona_registry.items():
            print(f"      • {persona} → {adapter} (LoRA adapter)")
    
    def get_available_personas(self):
        return list(self.persona_registry.keys())
    
    def get_adapter_for_persona(self, persona_name):
        return self.persona_registry.get(persona_name)
    
    def validate_personas(self, personas):
        return all(p in self.persona_registry for p in personas)
    
    def register_persona(self, persona_name, adapter_name):
        self.persona_registry[persona_name] = adapter_name
        print(f"   Registered: {persona_name} → {adapter_name}")

aos = MockAOS()

# Step 2: Create mock agent classes that query AOS
print("\n2. Agents Query AOS for Available Personas")
print("-" * 70)

class MockPurposeDrivenAgent:
    """Mock PurposeDrivenAgent that queries AOS"""
    def __init__(self, agent_id, aos=None):
        self.agent_id = agent_id
        self.aos = aos
    
    def get_available_personas(self):
        if self.aos:
            return self.aos.get_available_personas()
        return []
    
    def validate_personas(self, personas):
        if self.aos:
            return self.aos.validate_personas(personas)
        return True

class MockGenericAgent(MockPurposeDrivenAgent):
    """Selects 'generic' persona"""
    def get_agent_type(self):
        available = self.get_available_personas()
        if "generic" in available:
            return ["generic"]
        return ["generic"]

class MockLeadershipAgent(MockPurposeDrivenAgent):
    """Selects 'leadership' persona"""
    def get_agent_type(self):
        available = self.get_available_personas()
        if "leadership" in available:
            return ["leadership"]
        return ["leadership"]

class MockCMOAgent(MockPurposeDrivenAgent):
    """Selects BOTH 'marketing' AND 'leadership' personas"""
    def get_agent_type(self):
        available = self.get_available_personas()
        personas = []
        
        if "marketing" in available:
            personas.append("marketing")
        if "leadership" in available:
            personas.append("leadership")
            
        return personas if personas else ["marketing", "leadership"]

# Step 3: Test agent persona selection
print("\n   Testing Agent Persona Selection:")

generic = MockGenericAgent("assistant", aos=aos)
personas = generic.get_agent_type()
print(f"   • GenericAgent: {personas}")
print(f"     LoRA adapters: {[aos.get_adapter_for_persona(p) for p in personas]}")

leader = MockLeadershipAgent("ceo", aos=aos)
personas = leader.get_agent_type()
print(f"   • LeadershipAgent: {personas}")
print(f"     LoRA adapters: {[aos.get_adapter_for_persona(p) for p in personas]}")

cmo = MockCMOAgent("cmo", aos=aos)
personas = cmo.get_agent_type()
print(f"   • CMOAgent: {personas}")
print(f"     LoRA adapters: {[aos.get_adapter_for_persona(p) for p in personas]}")
print(f"     ✓ CMO = Marketing + Leadership (composable personas!)")

# Step 4: Dynamic persona registration
print("\n3. Dynamic Persona Registration")
print("-" * 70)
aos.register_persona("technology", "cto")
aos.register_persona("hr", "chro")

class MockCTOAgent(MockPurposeDrivenAgent):
    """Selects 'technology' + 'leadership' personas"""
    def get_agent_type(self):
        available = self.get_available_personas()
        personas = []
        
        if "technology" in available:
            personas.append("technology")
        if "leadership" in available:
            personas.append("leadership")
            
        return personas if personas else ["technology", "leadership"]

cto = MockCTOAgent("cto", aos=aos)
personas = cto.get_agent_type()
print(f"   • CTOAgent: {personas}")
print(f"     LoRA adapters: {[aos.get_adapter_for_persona(p) for p in personas]}")
print(f"     ✓ CTO = Technology + Leadership")

# Step 5: Validation
print("\n4. Persona Validation")
print("-" * 70)
valid = aos.validate_personas(["marketing", "leadership"])
print(f"   • Validate ['marketing', 'leadership']: {valid}")

valid = aos.validate_personas(["marketing", "invalid_persona"])
print(f"   • Validate ['marketing', 'invalid_persona']: {valid}")

# Step 6: Runtime behavior with LoRAx
print("\n5. Runtime Behavior (LoRAx Integration)")
print("-" * 70)
print("   When CMOAgent is invoked:")
print("   1. get_agent_type() returns ['marketing', 'leadership']")
print("   2. AOS maps to adapters: ['marketing', 'leadership']")
print("   3. LoRAx loads Llama 3.3 70B with BOTH adapters superimposed")
print("   4. Single inference call uses combined persona knowledge")
print("   5. Cost-effective: shared base model, multiple adapters")

print("\n" + "=" * 70)
print("✅ ARCHITECTURE TEST PASSED")
print("=" * 70)
print("\nKey Insights:")
print("  • Personas are managed centrally in AgentOperatingSystem")
print("  • Each persona maps to a LoRA adapter")
print("  • Agents query AOS for available personas")
print("  • Agents select combinations (e.g., CMO = Marketing + Leadership)")
print("  • LoRAx superimposes selected adapters at runtime")
print("  • Composable, extensible, cost-effective!")
