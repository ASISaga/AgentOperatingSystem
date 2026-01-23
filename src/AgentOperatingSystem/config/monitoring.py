import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MonitoringConfig:
    """Configuration for AOS monitoring"""
    enable_metrics: bool = True
    metrics_interval_seconds: int = 60
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_telemetry: bool = True
    telemetry_endpoint: Optional[str] = None

    @classmethod
    def from_env(cls):
        return cls(
            enable_metrics=os.getenv("AOS_ENABLE_METRICS", "true").lower() == "true",
            metrics_interval_seconds=int(os.getenv("AOS_METRICS_INTERVAL", "60")),
            enable_logging=os.getenv("AOS_ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv("AOS_LOG_LEVEL", "INFO"),
            enable_telemetry=os.getenv("AOS_ENABLE_TELEMETRY", "true").lower() == "true",
            telemetry_endpoint=os.getenv("AOS_TELEMETRY_ENDPOINT")
        )
