"""
Compliance assertions for AgentOperatingSystem

Declarative mapping between actions and compliance controls (SOC2, ISO 27001, etc.)
with pre/post enforcement.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    CUSTOM = "CUSTOM"


class ControlMapping(BaseModel):
    """Mapping of an action to compliance controls"""
    control_id: str
    framework: ComplianceFramework
    control_name: str
    description: str
    requirements: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class ComplianceAssertion(BaseModel):
    """
    Assertion that an action complies with specific controls.
    """
    assertion_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str  # Action being asserted
    resource: str  # Resource affected
    actor: str  # Who performed the action

    # Control mappings
    controls: List[ControlMapping] = Field(default_factory=list)

    # Assertion details
    is_compliant: bool
    pre_conditions_met: bool
    post_conditions_met: bool
    evidence: List[str] = Field(default_factory=list)  # Evidence links
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ComplianceEngine:
    """
    Engine for managing compliance assertions and control mappings.
    """

    def __init__(self):
        """Initialize compliance engine"""
        self._control_mappings: Dict[str, List[ControlMapping]] = {}
        self._assertions: List[ComplianceAssertion] = []

    def register_control_mapping(
        self,
        action_pattern: str,
        control: ControlMapping
    ):
        """
        Register a control mapping for an action pattern.

        Args:
            action_pattern: Pattern matching actions (e.g., "decision:*")
            control: Control to map
        """
        if action_pattern not in self._control_mappings:
            self._control_mappings[action_pattern] = []
        self._control_mappings[action_pattern].append(control)

    def get_controls_for_action(self, action: str) -> List[ControlMapping]:
        """Get all controls applicable to an action"""
        controls = []

        for pattern, pattern_controls in self._control_mappings.items():
            # Simple pattern matching (exact or wildcard)
            if pattern == action or pattern.endswith("*") and action.startswith(pattern[:-1]):
                controls.extend(pattern_controls)

        return controls

    def assert_compliance(
        self,
        action: str,
        resource: str,
        actor: str,
        pre_conditions: Dict[str, bool],
        post_conditions: Dict[str, bool],
        evidence: Optional[List[str]] = None
    ) -> ComplianceAssertion:
        """
        Create a compliance assertion for an action.

        Args:
            action: Action being performed
            resource: Resource affected
            actor: Who is performing the action
            pre_conditions: Pre-condition check results
            post_conditions: Post-condition check results
            evidence: Links to supporting evidence

        Returns:
            Compliance assertion
        """
        controls = self.get_controls_for_action(action)

        pre_met = all(pre_conditions.values())
        post_met = all(post_conditions.values())
        is_compliant = pre_met and post_met

        assertion = ComplianceAssertion(
            action=action,
            resource=resource,
            actor=actor,
            controls=controls,
            is_compliant=is_compliant,
            pre_conditions_met=pre_met,
            post_conditions_met=post_met,
            evidence=evidence or []
        )

        self._assertions.append(assertion)
        return assertion

    def query_assertions(
        self,
        action: Optional[str] = None,
        framework: Optional[ComplianceFramework] = None,
        is_compliant: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ComplianceAssertion]:
        """
        Query compliance assertions with filters.

        Args:
            action: Filter by action
            framework: Filter by framework
            is_compliant: Filter by compliance status
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number to return

        Returns:
            List of matching assertions
        """
        results = []

        for assertion in self._assertions:
            if action and assertion.action != action:
                continue
            if is_compliant is not None and assertion.is_compliant != is_compliant:
                continue
            if start_time and assertion.timestamp < start_time:
                continue
            if end_time and assertion.timestamp > end_time:
                continue
            if framework:
                # Check if any control matches the framework
                if not any(c.framework == framework for c in assertion.controls):
                    continue

            results.append(assertion)

            if len(results) >= limit:
                break

        return results

    def get_compliance_summary(
        self,
        framework: Optional[ComplianceFramework] = None
    ) -> Dict[str, Any]:
        """
        Get compliance summary statistics.

        Args:
            framework: Optional framework to filter by

        Returns:
            Summary statistics
        """
        assertions = self._assertions

        if framework:
            assertions = [
                a for a in assertions
                if any(c.framework == framework for c in a.controls)
            ]

        total = len(assertions)
        compliant = sum(1 for a in assertions if a.is_compliant)
        non_compliant = total - compliant

        # Control coverage
        control_ids = set()
        for assertion in assertions:
            for control in assertion.controls:
                control_ids.add(control.control_id)

        return {
            "framework": framework.value if framework else "all",
            "total_assertions": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "compliance_rate": compliant / total if total > 0 else 0,
            "unique_controls_covered": len(control_ids)
        }


# Predefined control mappings for common frameworks

def register_soc2_controls(engine: ComplianceEngine):
    """Register SOC2 Type II controls"""
    # CC6.1 - Logical Access
    engine.register_control_mapping(
        "decision:*",
        ControlMapping(
            control_id="CC6.1",
            framework=ComplianceFramework.SOC2,
            control_name="Logical and Physical Access Controls",
            description="The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives.",
            requirements=[
                "Proper authorization before decision execution",
                "Audit logging of all decisions"
            ]
        )
    )

    # CC7.2 - System Monitoring
    engine.register_control_mapping(
        "*",
        ControlMapping(
            control_id="CC7.2",
            framework=ComplianceFramework.SOC2,
            control_name="System Monitoring",
            description="The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors affecting the entity's ability to meet its objectives.",
            requirements=[
                "Continuous monitoring of system operations",
                "Alerting on anomalies"
            ]
        )
    )


def register_iso27001_controls(engine: ComplianceEngine):
    """Register ISO 27001 controls"""
    # A.9.4.1 - Information access restriction
    engine.register_control_mapping(
        "decision:*",
        ControlMapping(
            control_id="A.9.4.1",
            framework=ComplianceFramework.ISO27001,
            control_name="Information access restriction",
            description="Access to information and application system functions shall be restricted in accordance with the access control policy.",
            requirements=[
                "Role-based access control",
                "Attribute-based access control where applicable"
            ]
        )
    )

    # A.12.4.1 - Event logging
    engine.register_control_mapping(
        "*",
        ControlMapping(
            control_id="A.12.4.1",
            framework=ComplianceFramework.ISO27001,
            control_name="Event logging",
            description="Event logs recording user activities, exceptions, faults and information security events shall be produced, kept and regularly reviewed.",
            requirements=[
                "Comprehensive event logging",
                "Regular review of logs"
            ]
        )
    )
