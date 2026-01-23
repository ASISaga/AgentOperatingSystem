"""
Alerting system for AgentOperatingSystem

Threshold monitoring on key SLOs with routing and playbook attachments.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    """Individual alert"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    threshold_value: float
    actual_value: float
    owner: Optional[str] = None
    playbook_url: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertRule(BaseModel):
    """Rule for generating alerts"""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    metric_name: str
    condition: str  # e.g., "greater_than", "less_than"
    threshold: float
    severity: AlertSeverity
    owner: str
    playbook_url: Optional[str] = None
    enabled: bool = True


class AlertingSystem:
    """
    System for monitoring SLOs and generating alerts.

    Monitors thresholds and routes alerts to appropriate owners.
    """

    def __init__(self):
        """Initialize alerting system"""
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: List[Alert] = []
        self._alert_handlers: List[Callable[[Alert], None]] = []

    def add_rule(
        self,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        severity: AlertSeverity,
        owner: str,
        playbook_url: Optional[str] = None
    ) -> AlertRule:
        """
        Add an alert rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            condition: Condition to check
            threshold: Threshold value
            severity: Alert severity
            owner: Alert owner
            playbook_url: Optional playbook URL

        Returns:
            Created rule
        """
        rule = AlertRule(
            name=name,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            severity=severity,
            owner=owner,
            playbook_url=playbook_url
        )

        self._rules[rule.rule_id] = rule
        return rule

    def check_metric(self, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None):
        """
        Check a metric value against all rules.

        Args:
            metric_name: Metric name
            value: Current value
            context: Additional context
        """
        for rule in self._rules.values():
            if not rule.enabled or rule.metric_name != metric_name:
                continue

            should_alert = self._evaluate_condition(value, rule.condition, rule.threshold)

            if should_alert:
                self._create_alert(rule, value, context or {})

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate if condition is met"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return value == threshold
        elif condition == "not_equals":
            return value != threshold
        elif condition == "greater_than_or_equal":
            return value >= threshold
        elif condition == "less_than_or_equal":
            return value <= threshold
        return False

    def _create_alert(self, rule: AlertRule, actual_value: float, context: Dict[str, Any]):
        """Create and dispatch an alert"""
        alert = Alert(
            severity=rule.severity,
            title=f"Alert: {rule.name}",
            description=f"Metric {rule.metric_name} triggered alert (condition: {rule.condition}, threshold: {rule.threshold}, actual: {actual_value})",
            metric_name=rule.metric_name,
            threshold_value=rule.threshold,
            actual_value=actual_value,
            owner=rule.owner,
            playbook_url=rule.playbook_url,
            context=context
        )

        self._alerts.append(alert)

        # Dispatch to handlers
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                print(f"Error in alert handler: {e}")

    def register_handler(self, handler: Callable[[Alert], None]):
        """Register an alert handler"""
        self._alert_handlers.append(handler)

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                break

    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                break

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [a for a in self._alerts if not a.resolved]

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity"""
        return [a for a in self._alerts if a.severity == severity and not a.resolved]
