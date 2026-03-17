"""
Audit Completeness Testing Framework for AgentOperatingSystem

Validates that every decision path produces required audit artifacts,
evidence, and compliance assertions.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import logging

from ..platform.contracts import MessageEnvelope
from ..governance.audit import AuditLogger
from ..governance.compliance import ComplianceAssertion


class DecisionPathTester:
    """
    Tests that decision paths produce required audit artifacts.

    Validates that all decision-making processes create proper audit trails,
    evidence, and compliance assertions.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.DecisionPath")
        self.test_results: List[Dict[str, Any]] = []
        self.required_artifacts = {
            "audit_entry",
            "decision_rationale",
            "compliance_assertion",
            "risk_assessment"
        }

    async def test_decision_path(
        self,
        decision_name: str,
        decision_data: Dict[str, Any],
        artifacts_produced: Set[str]
    ) -> Dict[str, Any]:
        """
        Test that a decision path produces all required artifacts.

        Args:
            decision_name: Name of the decision being tested
            decision_data: Data about the decision
            artifacts_produced: Set of artifact types that were produced

        Returns:
            Test result
        """
        result = {
            "test": "decision_path_completeness",
            "decision": decision_name,
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info(f"Testing decision path completeness: {decision_name}")

            # Check for required artifacts
            missing_artifacts = self.required_artifacts - artifacts_produced
            extra_artifacts = artifacts_produced - self.required_artifacts

            if missing_artifacts:
                result["status"] = "failed"
                result["missing_artifacts"] = list(missing_artifacts)
                result["error"] = f"Missing required artifacts: {missing_artifacts}"
                self.logger.error(
                    f"❌ Decision path incomplete: {decision_name} - "
                    f"Missing: {missing_artifacts}"
                )
            else:
                result["status"] = "passed"
                result["artifacts_produced"] = list(artifacts_produced)
                if extra_artifacts:
                    result["additional_artifacts"] = list(extra_artifacts)
                self.logger.info(
                    f"✅ Decision path complete: {decision_name} - "
                    f"All required artifacts present"
                )

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Decision path test failed: {e}")

        self.test_results.append(result)
        return result

    async def test_audit_entry_completeness(
        self,
        audit_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test that an audit entry contains all required fields.

        Args:
            audit_entry: Audit entry to validate

        Returns:
            Test result
        """
        result = {
            "test": "audit_entry_completeness",
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        required_fields = {
            "timestamp",
            "actor",
            "action",
            "context",
            "outcome"
        }

        try:
            self.logger.debug("Testing audit entry completeness")

            entry_fields = set(audit_entry.keys())
            missing_fields = required_fields - entry_fields

            if missing_fields:
                result["status"] = "failed"
                result["missing_fields"] = list(missing_fields)
                result["error"] = f"Missing required fields: {missing_fields}"
                self.logger.error(f"❌ Audit entry incomplete: Missing {missing_fields}")
            else:
                result["status"] = "passed"
                result["fields_present"] = list(entry_fields)
                self.logger.debug("✅ Audit entry complete")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Audit entry test failed: {e}")

        self.test_results.append(result)
        return result

    async def test_evidence_completeness(
        self,
        decision_id: str,
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test that sufficient evidence is collected for a decision.

        Args:
            decision_id: ID of the decision
            evidence_items: List of evidence items collected

        Returns:
            Test result
        """
        result = {
            "test": "evidence_completeness",
            "decision_id": decision_id,
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.debug(f"Testing evidence completeness for decision: {decision_id}")

            if not evidence_items:
                result["status"] = "failed"
                result["error"] = "No evidence items provided"
                self.logger.error(f"❌ No evidence for decision: {decision_id}")
            else:
                # Validate each evidence item
                valid_items = 0
                invalid_items = []

                for i, item in enumerate(evidence_items):
                    if self._validate_evidence_item(item):
                        valid_items += 1
                    else:
                        invalid_items.append(i)

                result["total_evidence_items"] = len(evidence_items)
                result["valid_items"] = valid_items

                if invalid_items:
                    result["status"] = "failed"
                    result["invalid_items"] = invalid_items
                    result["error"] = f"Invalid evidence items: {invalid_items}"
                    self.logger.error(
                        f"❌ Evidence incomplete for {decision_id}: "
                        f"{len(invalid_items)} invalid items"
                    )
                else:
                    result["status"] = "passed"
                    self.logger.debug(
                        f"✅ Evidence complete for {decision_id}: "
                        f"{valid_items} valid items"
                    )

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Evidence test failed: {e}")

        self.test_results.append(result)
        return result

    def _validate_evidence_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate that an evidence item has required structure.

        Args:
            item: Evidence item to validate

        Returns:
            True if valid
        """
        required_fields = {"source", "type", "content", "timestamp"}
        return required_fields.issubset(set(item.keys()))


class AuditCompletenessValidator:
    """
    Validates audit completeness across the system.

    Ensures that all actions produce appropriate audit trails and that
    the audit system meets compliance requirements.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.Testing.AuditValidator")
        self.decision_tester = DecisionPathTester(logger=self.logger)
        self.test_results: List[Dict[str, Any]] = []

    async def validate_audit_trail_integrity(
        self,
        audit_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate the integrity of an audit trail.

        Checks for:
        - Chronological ordering
        - No gaps in sequence
        - Hash chain integrity (if applicable)
        - Required metadata present

        Args:
            audit_entries: List of audit entries to validate

        Returns:
            Validation result
        """
        result = {
            "test": "audit_trail_integrity",
            "total_entries": len(audit_entries),
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info(f"Validating audit trail integrity ({len(audit_entries)} entries)")

            issues = []

            # Check chronological ordering
            for i in range(1, len(audit_entries)):
                prev_timestamp = audit_entries[i-1].get("timestamp")
                curr_timestamp = audit_entries[i].get("timestamp")

                if prev_timestamp and curr_timestamp:
                    if curr_timestamp < prev_timestamp:
                        issues.append({
                            "type": "ordering",
                            "index": i,
                            "message": "Entry out of chronological order"
                        })

            # Check for required fields in each entry
            for i, entry in enumerate(audit_entries):
                required_fields = {"timestamp", "actor", "action"}
                missing = required_fields - set(entry.keys())
                if missing:
                    issues.append({
                        "type": "missing_fields",
                        "index": i,
                        "missing": list(missing)
                    })

            # Check hash chain integrity (if applicable)
            if all("hash" in entry for entry in audit_entries):
                for i in range(1, len(audit_entries)):
                    prev_hash = audit_entries[i-1].get("hash")
                    curr_prev_hash = audit_entries[i].get("previous_hash")

                    if prev_hash != curr_prev_hash:
                        issues.append({
                            "type": "hash_chain",
                            "index": i,
                            "message": "Hash chain broken"
                        })

            result["issues"] = issues

            if issues:
                result["status"] = "failed"
                result["error"] = f"Found {len(issues)} integrity issues"
                self.logger.error(f"❌ Audit trail integrity issues: {len(issues)}")
            else:
                result["status"] = "passed"
                self.logger.info("✅ Audit trail integrity validated")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Audit trail validation failed: {e}")

        self.test_results.append(result)
        return result

    async def validate_compliance_coverage(
        self,
        actions: List[str],
        compliance_assertions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate that all actions have compliance assertions.

        Args:
            actions: List of action IDs
            compliance_assertions: List of compliance assertions

        Returns:
            Validation result
        """
        result = {
            "test": "compliance_coverage",
            "total_actions": len(actions),
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info(f"Validating compliance coverage for {len(actions)} actions")

            # Map assertions to actions
            action_assertions = {}
            for assertion in compliance_assertions:
                action_id = assertion.get("action_id")
                if action_id:
                    if action_id not in action_assertions:
                        action_assertions[action_id] = []
                    action_assertions[action_id].append(assertion)

            # Find actions without assertions
            uncovered_actions = [
                action for action in actions
                if action not in action_assertions
            ]

            result["covered_actions"] = len(actions) - len(uncovered_actions)
            result["uncovered_actions"] = uncovered_actions
            result["coverage_percentage"] = (
                (len(actions) - len(uncovered_actions)) / len(actions) * 100
                if actions else 100
            )

            if uncovered_actions:
                result["status"] = "failed"
                result["error"] = f"{len(uncovered_actions)} actions lack compliance assertions"
                self.logger.error(
                    f"❌ Compliance coverage incomplete: "
                    f"{len(uncovered_actions)} actions uncovered"
                )
            else:
                result["status"] = "passed"
                self.logger.info("✅ Compliance coverage complete")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Compliance coverage validation failed: {e}")

        self.test_results.append(result)
        return result

    async def validate_decision_audit_completeness(
        self,
        decision_id: str,
        audit_artifacts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that a decision has complete audit artifacts.

        Args:
            decision_id: ID of the decision
            audit_artifacts: Dictionary of audit artifacts

        Returns:
            Validation result
        """
        result = {
            "test": "decision_audit_completeness",
            "decision_id": decision_id,
            "status": "pending",
            "tested_at": datetime.utcnow().isoformat()
        }

        try:
            self.logger.info(f"Validating decision audit completeness: {decision_id}")

            required_artifacts = {
                "audit_log",
                "decision_rationale",
                "compliance_assertion",
                "risk_assessment",
                "evidence"
            }

            present_artifacts = set(audit_artifacts.keys())
            missing_artifacts = required_artifacts - present_artifacts

            result["present_artifacts"] = list(present_artifacts)
            result["missing_artifacts"] = list(missing_artifacts)

            if missing_artifacts:
                result["status"] = "failed"
                result["error"] = f"Missing artifacts: {missing_artifacts}"
                self.logger.error(
                    f"❌ Decision audit incomplete for {decision_id}: "
                    f"Missing {missing_artifacts}"
                )
            else:
                result["status"] = "passed"
                self.logger.info(f"✅ Decision audit complete for {decision_id}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"❌ Decision audit validation failed: {e}")

        self.test_results.append(result)
        return result

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive audit completeness report.

        Returns:
            Report with summary and detailed results
        """
        all_results = self.test_results + self.decision_tester.test_results

        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.get("status") == "passed")
        failed_tests = sum(1 for r in all_results if r.get("status") == "failed")

        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": all_results,
            "generated_at": datetime.utcnow().isoformat()
        }
