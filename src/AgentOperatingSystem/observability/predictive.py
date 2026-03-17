"""
Predictive Alerting

Provides ML-based predictive alerting and anomaly detection.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque


class AnomalyDetector:
    """
    Detects anomalies in metrics using statistical methods.

    Features:
    - Statistical anomaly detection
    - Trend analysis
    - Threshold-based alerts
    - Pattern recognition
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.AnomalyDetector")
        self.metric_history = {}
        self.baselines = {}
        self.max_history = 1000

    async def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        sensitivity: float = 3.0
    ) -> Dict[str, Any]:
        """
        Detect if a metric value is anomalous.

        Args:
            metric_name: Name of the metric
            value: Current metric value
            sensitivity: Sensitivity threshold (std deviations)

        Returns:
            Anomaly detection result
        """
        # Initialize history for new metrics
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = deque(maxlen=self.max_history)
            self.baselines[metric_name] = None

        # Add to history
        self.metric_history[metric_name].append({
            "value": value,
            "timestamp": datetime.utcnow()
        })

        # Need enough history for baseline
        if len(self.metric_history[metric_name]) < 30:
            return {
                "is_anomaly": False,
                "reason": "Insufficient history for baseline"
            }

        # Calculate baseline if not exists
        if self.baselines[metric_name] is None:
            await self._calculate_baseline(metric_name)

        baseline = self.baselines[metric_name]
        mean = baseline["mean"]
        std_dev = baseline["std_dev"]

        # Check if value is outside normal range
        lower_bound = mean - (sensitivity * std_dev)
        upper_bound = mean + (sensitivity * std_dev)

        is_anomaly = value < lower_bound or value > upper_bound

        if is_anomaly:
            self.logger.warning(
                f"Anomaly detected in {metric_name}: {value:.2f} "
                f"(baseline: {mean:.2f} ± {std_dev:.2f})"
            )

        return {
            "is_anomaly": is_anomaly,
            "value": value,
            "baseline_mean": mean,
            "baseline_std_dev": std_dev,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "severity": self._calculate_severity(value, mean, std_dev)
        }

    async def _calculate_baseline(self, metric_name: str):
        """Calculate baseline statistics for a metric"""
        history = list(self.metric_history[metric_name])
        values = [h["value"] for h in history]

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        self.baselines[metric_name] = {
            "mean": mean,
            "std_dev": std_dev,
            "calculated_at": datetime.utcnow()
        }

        self.logger.debug(
            f"Calculated baseline for {metric_name}: "
            f"mean={mean:.2f}, std_dev={std_dev:.2f}"
        )

    def _calculate_severity(
        self,
        value: float,
        mean: float,
        std_dev: float
    ) -> str:
        """Calculate anomaly severity"""
        deviation = abs(value - mean) / std_dev if std_dev > 0 else 0

        if deviation > 5:
            return "critical"
        elif deviation > 4:
            return "high"
        elif deviation > 3:
            return "medium"
        else:
            return "low"


class PredictiveAlerter:
    """
    Predicts future metric values and alerts before issues occur.

    Features:
    - Time series forecasting
    - Trend prediction
    - Proactive alerting
    - Capacity planning
    """

    def __init__(self):
        self.logger = logging.getLogger("AOS.PredictiveAlerter")
        self.anomaly_detector = AnomalyDetector()
        self.predictions = {}
        self.alert_rules = []

    async def predict_metric(
        self,
        metric_name: str,
        forecast_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Predict future metric values.

        Args:
            metric_name: Metric to predict
            forecast_minutes: How far ahead to forecast

        Returns:
            Prediction result
        """
        self.logger.info(
            f"Predicting {metric_name} for next {forecast_minutes} minutes"
        )

        # Get historical data
        history = self.anomaly_detector.metric_history.get(metric_name, [])

        if len(history) < 10:
            return {
                "success": False,
                "reason": "Insufficient history for prediction"
            }

        # Simple linear trend prediction
        # In production, would use more sophisticated models
        values = [h["value"] for h in list(history)[-100:]]
        timestamps = [h["timestamp"] for h in list(history)[-100:]]

        # Calculate trend
        trend = await self._calculate_trend(values)

        # Project forward
        current_value = values[-1]
        predicted_value = current_value + (trend * forecast_minutes)

        prediction = {
            "success": True,
            "metric_name": metric_name,
            "current_value": current_value,
            "predicted_value": predicted_value,
            "forecast_minutes": forecast_minutes,
            "trend": trend,
            "confidence": 0.7,  # Simplified confidence
            "predicted_at": datetime.utcnow()
        }

        self.predictions[metric_name] = prediction

        # Check if prediction triggers any alerts
        await self._check_predictive_alerts(prediction)

        return prediction

    async def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (change per minute)"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression
        n = len(values)
        x = list(range(n))
        y = values

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        # Check for division by zero
        denominator = (n * sum_x2) - (sum_x ** 2)
        if denominator == 0:
            return 0.0

        # Slope = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x^2)
        slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator

        return slope

    async def add_predictive_alert(
        self,
        metric_name: str,
        condition: str,
        threshold: float,
        forecast_minutes: int = 30,
        action: str = "notify"
    ):
        """
        Add a predictive alert rule.

        Args:
            metric_name: Metric to monitor
            condition: Condition ("greater_than", "less_than", etc.)
            threshold: Threshold value
            forecast_minutes: How far ahead to predict
            action: Action to take when triggered
        """
        rule = {
            "metric_name": metric_name,
            "condition": condition,
            "threshold": threshold,
            "forecast_minutes": forecast_minutes,
            "action": action,
            "created_at": datetime.utcnow()
        }

        self.alert_rules.append(rule)

        self.logger.info(
            f"Added predictive alert: {metric_name} {condition} {threshold} "
            f"in {forecast_minutes} minutes"
        )

    async def _check_predictive_alerts(self, prediction: Dict[str, Any]):
        """Check if prediction triggers any alert rules"""
        metric_name = prediction["metric_name"]
        predicted_value = prediction["predicted_value"]

        for rule in self.alert_rules:
            if rule["metric_name"] != metric_name:
                continue

            triggered = False
            condition = rule["condition"]
            threshold = rule["threshold"]

            if condition == "greater_than" and predicted_value > threshold:
                triggered = True
            elif condition == "less_than" and predicted_value < threshold:
                triggered = True

            if triggered:
                self.logger.warning(
                    f"Predictive alert triggered: {metric_name} predicted to be "
                    f"{predicted_value:.2f} ({condition} {threshold}) in "
                    f"{rule['forecast_minutes']} minutes"
                )

                await self._execute_alert_action(rule, prediction)

    async def _execute_alert_action(
        self,
        rule: Dict[str, Any],
        prediction: Dict[str, Any]
    ):
        """Execute action for triggered alert"""
        action = rule.get("action", "notify")

        if action == "notify":
            # Send notification
            self.logger.info(f"Sending predictive alert notification")
        elif action == "auto_scale":
            # Trigger auto-scaling
            self.logger.info(f"Triggering auto-scaling")
        elif action == "remediate":
            # Execute remediation
            self.logger.info(f"Executing remediation")


class CapacityPlanner:
    """
    Plans capacity based on metric trends and predictions.

    Features:
    - Resource usage forecasting
    - Capacity recommendations
    - Growth trend analysis
    - Cost optimization
    """

    def __init__(self, predictor: PredictiveAlerter):
        self.logger = logging.getLogger("AOS.CapacityPlanner")
        self.predictor = predictor

    async def forecast_capacity(
        self,
        resource: str,
        time_horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast capacity needs.

        Args:
            resource: Resource to forecast (cpu, memory, etc.)
            time_horizon_days: Forecast time horizon

        Returns:
            Capacity forecast
        """
        self.logger.info(
            f"Forecasting capacity for {resource} over {time_horizon_days} days"
        )

        # Predict usage
        prediction = await self.predictor.predict_metric(
            f"{resource}_usage",
            forecast_minutes=time_horizon_days * 24 * 60
        )

        if not prediction.get("success"):
            return prediction

        current_value = prediction["current_value"]
        predicted_value = prediction["predicted_value"]

        # Calculate required capacity
        # Assume 80% target utilization
        target_utilization = 0.8
        required_capacity = predicted_value / target_utilization

        # Current capacity (simplified)
        current_capacity = 100  # Would get from actual system

        forecast = {
            "resource": resource,
            "current_usage": current_value,
            "predicted_usage": predicted_value,
            "current_capacity": current_capacity,
            "required_capacity": required_capacity,
            "capacity_gap": required_capacity - current_capacity,
            "recommendation": self._generate_recommendation(
                current_capacity,
                required_capacity
            ),
            "time_horizon_days": time_horizon_days,
            "forecasted_at": datetime.utcnow()
        }

        return forecast

    def _generate_recommendation(
        self,
        current: float,
        required: float
    ) -> str:
        """Generate capacity recommendation"""
        gap_percent = ((required - current) / current) * 100

        if gap_percent > 50:
            return f"URGENT: Increase capacity by {gap_percent:.0f}%"
        elif gap_percent > 20:
            return f"RECOMMEND: Increase capacity by {gap_percent:.0f}%"
        elif gap_percent > 0:
            return f"MONITOR: May need {gap_percent:.0f}% more capacity soon"
        else:
            return "SUFFICIENT: Current capacity adequate"
