"""
AOS System Monitor

Provides system monitoring, metrics collection, and telemetry for AOS.
"""

import logging
import asyncio
import time
import psutil
from typing import Dict, Any, List
from datetime import datetime, timezone
from ..core.config import MonitoringConfig


class SystemMonitor:
    """
    System monitor for AOS providing metrics and telemetry.
    
    Monitors:
    - System resources (CPU, memory, disk)
    - Agent performance and health
    - Message bus metrics
    - Workflow execution metrics
    - Custom application metrics
    """
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logger = logging.getLogger("AOS.SystemMonitor")
        
        # Metrics storage
        self.metrics = {}
        self.metric_history = []
        
        # Monitoring state
        self.is_running = False
        self.monitoring_task = None
        self.start_time = None
        
        # Performance counters
        self.counters = {
            "messages_sent": 0,
            "messages_received": 0,
            "workflows_started": 0,
            "workflows_completed": 0,
            "decisions_made": 0,
            "errors_occurred": 0
        }
    
    async def start(self):
        """Start the system monitor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        
        if self.config.enable_metrics:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("SystemMonitor started")
    
    async def stop(self):
        """Stop the system monitor"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("SystemMonitor stopped")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        current_time = datetime.now(timezone.utc)
        
        # System metrics
        system_metrics = await self._collect_system_metrics()
        
        # AOS metrics
        aos_metrics = {
            "uptime_seconds": (current_time - self.start_time).total_seconds() if self.start_time else 0,
            "counters": self.counters.copy(),
            "custom_metrics": self.metrics.copy()
        }
        
        return {
            "timestamp": current_time.isoformat(),
            "system": system_metrics,
            "aos": aos_metrics
        }
    
    async def record_metric(self, name: str, value: Any, tags: Dict[str, str] = None):
        """Record a custom metric"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        self.metrics[name] = {
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        }
        
        # Add to history
        self.metric_history.append({
            "name": name,
            "value": value,
            "timestamp": timestamp,
            "tags": tags or {}
        })
        
        # Limit history size
        if len(self.metric_history) > 10000:
            self.metric_history = self.metric_history[-10000:]
        
        self.logger.debug(f"Recorded metric {name}: {value}")
    
    def increment_counter(self, counter_name: str, increment: int = 1):
        """Increment a performance counter"""
        if counter_name in self.counters:
            self.counters[counter_name] += increment
        else:
            self.counters[counter_name] = increment
    
    def set_gauge(self, gauge_name: str, value: float):
        """Set a gauge metric"""
        asyncio.create_task(
            self.record_metric(f"gauge.{gauge_name}", value)
        )
    
    async def record_timing(self, operation_name: str, duration_seconds: float):
        """Record operation timing"""
        await self.record_metric(
            f"timing.{operation_name}", 
            duration_seconds, 
            {"unit": "seconds"}
        )
    
    async def get_metric_history(self, name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metric history"""
        history = self.metric_history
        
        if name:
            history = [m for m in history if m["name"] == name]
        
        return history[-limit:]
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_running:
            try:
                # Collect and store metrics
                metrics = await self.get_metrics()
                
                # Log metrics if configured
                if self.config.enable_logging:
                    self.logger.debug(f"System metrics: {metrics}")
                
                # Send telemetry if configured
                if self.config.enable_telemetry and self.config.telemetry_endpoint:
                    await self._send_telemetry(metrics)
                
                # Wait for next collection interval
                await asyncio.sleep(self.config.metrics_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system resource metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (basic)
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_bytes": disk.total,
                    "used_bytes": disk.used,
                    "free_bytes": disk.free,
                    "usage_percent": (disk.used / disk.total * 100) if disk.total > 0 else 0
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_received": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_received": network.packets_recv
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {"error": str(e)}
    
    async def _send_telemetry(self, metrics: Dict[str, Any]):
        """Send telemetry to configured endpoint"""
        try:
            # This would integrate with actual telemetry systems
            # (Application Insights, Prometheus, etc.)
            self.logger.debug(f"Would send telemetry to {self.config.telemetry_endpoint}")
            
        except Exception as e:
            self.logger.error(f"Error sending telemetry: {e}")


class MetricsCollector:
    """Helper class for collecting and aggregating metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation_name: str):
        """Start timing an operation"""
        self.start_times[operation_name] = time.time()
    
    def end_timer(self, operation_name: str) -> float:
        """End timing an operation and return duration"""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            del self.start_times[operation_name]
            return duration
        return 0.0
    
    def record_value(self, metric_name: str, value: float):
        """Record a metric value"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": time.time()
        })
    
    def get_average(self, metric_name: str, window_seconds: int = 300) -> float:
        """Get average value for a metric within time window"""
        if metric_name not in self.metrics:
            return 0.0
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        values = [
            m["value"] for m in self.metrics[metric_name]
            if m["timestamp"] >= window_start
        ]
        
        return sum(values) / len(values) if values else 0.0