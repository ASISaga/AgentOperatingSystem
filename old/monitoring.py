"""
AOS System Monitoring

Provides system monitoring and telemetry for the Agent Operating System.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import psutil


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class SystemMonitor:
    """
    System monitor for AOS.
    
    Collects and tracks system metrics, performance data, and health status.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("AOS.SystemMonitor")
        
        # Metric storage (metric_name -> deque of MetricPoint)
        self.metrics: Dict[str, deque] = {}
        self.max_metric_points = 1000  # Keep last 1000 points per metric
        
        # Monitoring state
        self.is_running = False
        self.monitor_task = None
        
        # Component health status
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
    async def start(self):
        """Start system monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        
        if self.config.enable_metrics:
            self.monitor_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("System monitor started")
    
    async def stop(self):
        """Stop system monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("System monitor stopped")
    
    async def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        if not self.config.enable_metrics:
            return
        
        if name not in self.metrics:
            self.metrics[name] = deque(maxlen=self.max_metric_points)
        
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            tags=tags or {}
        )
        
        self.metrics[name].append(point)
    
    async def record_agent_metric(self, agent_id: str, metric_name: str, value: float):
        """Record an agent-specific metric"""
        full_name = f"agent.{metric_name}"
        tags = {"agent_id": agent_id}
        await self.record_metric(full_name, value, tags)
    
    async def record_workflow_metric(self, workflow_id: str, metric_name: str, value: float):
        """Record a workflow-specific metric"""
        full_name = f"workflow.{metric_name}"
        tags = {"workflow_id": workflow_id}
        await self.record_metric(full_name, value, tags)
    
    async def update_component_health(self, component: str, status: str, details: Dict[str, Any] = None):
        """Update health status of a system component"""
        self.component_health[component] = {
            "status": status,  # "healthy", "degraded", "unhealthy"
            "last_check": datetime.utcnow().isoformat(),
            "details": details or {}
        }
    
    async def get_metrics(self, metric_name: str = None, since: datetime = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics data"""
        result = {}
        
        metrics_to_include = [metric_name] if metric_name else list(self.metrics.keys())
        
        for name in metrics_to_include:
            if name not in self.metrics:
                continue
            
            points = []
            for point in self.metrics[name]:
                if since is None or point.timestamp >= since:
                    points.append({
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "tags": point.tags
                    })
            
            result[name] = points
        
        return result
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        # Calculate overall health based on component health
        healthy_components = sum(1 for health in self.component_health.values() if health["status"] == "healthy")
        total_components = len(self.component_health)
        
        if total_components == 0:
            overall_status = "unknown"
        elif healthy_components == total_components:
            overall_status = "healthy"
        elif healthy_components >= total_components * 0.7:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "components": self.component_health.copy(),
            "healthy_components": healthy_components,
            "total_components": total_components,
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {
            "system": await self._get_system_performance(),
            "aos": await self._get_aos_performance(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return summary
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.config.metrics_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric("system.cpu_usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric("system.memory_usage", memory.percent)
            await self.record_metric("system.memory_available", memory.available / (1024**3))  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.record_metric("system.disk_usage", (disk.used / disk.total) * 100)
            
            # Network I/O
            network = psutil.net_io_counters()
            if network:
                await self.record_metric("system.network_bytes_sent", network.bytes_sent)
                await self.record_metric("system.network_bytes_recv", network.bytes_recv)
            
            # Process count
            process_count = len(psutil.pids())
            await self.record_metric("system.process_count", process_count)
            
            # Load average (Unix systems)
            try:
                load_avg = psutil.getloadavg()
                await self.record_metric("system.load_avg_1m", load_avg[0])
                await self.record_metric("system.load_avg_5m", load_avg[1])
                await self.record_metric("system.load_avg_15m", load_avg[2])
            except AttributeError:
                # Not available on Windows
                pass
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    async def _get_system_performance(self) -> Dict[str, Any]:
        """Get current system performance data"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            self.logger.error(f"Error getting system performance: {e}")
            return {"error": str(e)}
    
    async def _get_aos_performance(self) -> Dict[str, Any]:
        """Get AOS-specific performance data"""
        # Calculate AOS metrics from stored metrics
        aos_metrics = {}
        
        # Get recent agent metrics
        agent_metrics = {}
        for metric_name, points in self.metrics.items():
            if metric_name.startswith("agent.") and points:
                # Get average value from last 10 points
                recent_points = list(points)[-10:]
                avg_value = sum(p.value for p in recent_points) / len(recent_points)
                agent_metrics[metric_name] = avg_value
        
        aos_metrics["agent_metrics"] = agent_metrics
        
        # Get workflow metrics
        workflow_metrics = {}
        for metric_name, points in self.metrics.items():
            if metric_name.startswith("workflow.") and points:
                recent_points = list(points)[-10:]
                avg_value = sum(p.value for p in recent_points) / len(recent_points)
                workflow_metrics[metric_name] = avg_value
        
        aos_metrics["workflow_metrics"] = workflow_metrics
        
        return aos_metrics
    
    def get_metric_statistics(self, metric_name: str, window_minutes: int = 60) -> Dict[str, float]:
        """Get statistics for a specific metric over a time window"""
        if metric_name not in self.metrics:
            return {}
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_points = [
            p for p in self.metrics[metric_name] 
            if p.timestamp >= cutoff_time
        ]
        
        if not recent_points:
            return {}
        
        values = [p.value for p in recent_points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "last": values[-1] if values else 0
        }