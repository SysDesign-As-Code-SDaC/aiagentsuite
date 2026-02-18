"""
Real-time Monitoring Module

Real-time system monitoring for tracking metrics,
performance, and health.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
import threading
import psutil
import json
from collections import deque


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Time-based measurement


class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """A metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """A health check result."""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class RealtimeMonitor:
    """
    Real-time monitoring system for tracking metrics and health.

    Provides:
    - Real-time metric collection
    - Health checks
    - Metric history and aggregation
    - Alerting callbacks
    - System resource monitoring
    """

    def __init__(
        self,
        max_metric_history: int = 10000,
        collection_interval: float = 1.0,
    ):
        """
        Initialize real-time monitor.

        Args:
            max_metric_history: Maximum metric history to keep
            collection_interval: Seconds between collections
        """
        self.max_metric_history = max_metric_history
        self.collection_interval = collection_interval

        # Metrics storage
        self._metrics: Dict[str, deque] = {}
        
        # Health checks
        self._health_checks: Dict[str, Callable[[], HealthCheck]] = {}
        self._last_health_status: Dict[str, HealthCheck] = {}
        
        # Monitoring state
        self._running = False
        self._monitor_task: Optional[threading.Thread] = None
        
        # Callbacks
        self._alert_callbacks: List[Callable[[str, float, float], None]] = []
        self._health_callbacks: List[Callable[[HealthCheck], None]] = []

        # System metrics collection
        self._collect_system_metrics = True
        self._process = psutil.Process()

    def start(self) -> None:
        """Start the monitoring system."""
        if self._running:
            return
        
        self._running = True
        self._monitor_task = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_task.start()

    def stop(self) -> None:
        """Stop the monitoring system."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.join(timeout=2)

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                if self._collect_system_metrics:
                    self._collect_system_metrics_internal()
                
                # Run health checks
                self._run_health_checks()
                
                time.sleep(self.collection_interval)
            except Exception:
                pass

    def _collect_system_metrics_internal(self) -> None:
        """Collect system metrics."""
        try:
            # CPU
            self.record_gauge(
                "system.cpu.percent",
                psutil.cpu_percent(interval=0.1),
            )
            
            # Memory
            mem = psutil.virtual_memory()
            self.record_gauge(
                "system.memory.percent",
                mem.percent,
            )
            self.record_gauge(
                "system.memory.available",
                mem.available / (1024 ** 3),  # GB
            )
            
            # Disk
            disk = psutil.disk_usage('/')
            self.record_gauge(
                "system.disk.percent",
                disk.percent,
            )
            
            # Process-specific
            self.record_gauge(
                "process.cpu.percent",
                self._process.cpu_percent(),
            )
            self.record_gauge(
                "process.memory.percent",
                self._process.memory_percent(),
            )
            self.record_gauge(
                "process.threads",
                self._process.num_threads(),
            )
        except Exception:
            pass

    def _run_health_checks(self) -> None:
        """Run all registered health checks."""
        for name, check_fn in self._health_checks.items():
            try:
                result = check_fn()
                self._last_health_status[name] = result
                
                # Trigger callbacks for status changes
                if result.status != HealthStatus.HEALTHY:
                    for callback in self._health_callbacks:
                        try:
                            callback(result)
                        except Exception:
                            pass
            except Exception:
                pass

    # Metric Recording Methods

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a counter metric."""
        self._record_metric(name, value, MetricType.COUNTER, labels)

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a gauge metric."""
        self._record_metric(name, value, MetricType.GAUGE, labels)

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram metric."""
        self._record_metric(name, value, MetricType.HISTOGRAM, labels)

    def record_timer(
        self,
        name: str,
        duration_ms: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a timer metric."""
        self._record_metric(name, duration_ms, MetricType.TIMER, labels)

    def _record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        labels: Optional[Dict[str, str]],
    ) -> None:
        """Record a metric."""
        if name not in self._metrics:
            self._metrics[name] = deque(maxlen=self.max_metric_history)

        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            labels=labels or {},
        )
        
        self._metrics[name].append(metric)

    # Metric Retrieval Methods

    def get_current(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Optional[float]:
        """Get current value for a metric."""
        if name not in self._metrics:
            return None
        
        metrics = list(self._metrics[name])
        
        if labels:
            # Filter by labels
            for metric in reversed(metrics):
                if metric.labels == labels:
                    return metric.value
            return None
        
        # Return latest
        return metrics[-1].value if metrics else None

    def get_history(
        self,
        name: str,
        duration: Optional[timedelta] = None,
        limit: int = 100,
    ) -> List[Metric]:
        """Get metric history."""
        if name not in self._metrics:
            return []
        
        metrics = list(self._metrics[name])
        
        if duration:
            cutoff = datetime.now() - duration
            metrics = [m for m in metrics if m.timestamp >= cutoff]
        
        return metrics[-limit:]

    def get_aggregated(
        self,
        name: str,
        duration: timedelta = timedelta(minutes=5),
    ) -> Dict[str, float]:
        """Get aggregated metrics."""
        history = self.get_history(name, duration=duration, limit=1000)
        
        if not history:
            return {}
        
        values = [m.value for m in history]
        
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
        }

    # Health Check Methods

    def register_health_check(
        self,
        name: str,
        check_fn: Callable[[], HealthCheck],
    ) -> None:
        """Register a health check."""
        self._health_checks[name] = check_fn

    def get_health_status(self) -> Dict[str, HealthCheck]:
        """Get current health status of all checks."""
        return self._last_health_status.copy()

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health."""
        if not self._last_health_status:
            return HealthStatus.UNKNOWN
        
        statuses = [h.status for h in self._last_health_status.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED

    # Callback Methods

    def register_alert_callback(
        self,
        callback: Callable[[str, float, float], None],
    ) -> None:
        """Register callback for alerts (metric_name, threshold, value)."""
        self._alert_callbacks.append(callback)

    def register_health_callback(
        self,
        callback: Callable[[HealthCheck], None],
    ) -> None:
        """Register callback for health changes."""
        self._health_callbacks.append(callback)

    # Utility Methods

    def check_threshold(
        self,
        name: str,
        threshold: float,
        operator: str = ">",
    ) -> bool:
        """Check if metric exceeds threshold."""
        current = self.get_current(name)
        if current is None:
            return False
        
        if operator == ">":
            return current > threshold
        elif operator == "<":
            return current < threshold
        elif operator == ">=":
            return current >= threshold
        elif operator == "<=":
            return current <= threshold
        elif operator == "==":
            return current == threshold
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "tracked_metrics": len(self._metrics),
            "total_data_points": sum(len(m) for m in self._metrics.values()),
            "health_checks": len(self._health_checks),
            "overall_health": self.get_overall_health().value,
            "running": self._running,
        }

    def export_metrics(self, name: Optional[str] = None) -> str:
        """Export metrics as JSON."""
        if name:
            metrics = self.get_history(name, limit=1000)
            data = {
                name: [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "labels": m.labels,
                    }
                    for m in metrics
                ]
            }
        else:
            data = {
                metric_name: [
                    {
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "labels": m.labels,
                    }
                    for m in metrics
                ]
                for metric_name, metrics in self._metrics.items()
            }
        
        return json.dumps(data, indent=2)

    def clear_metrics(self, name: Optional[str] = None) -> None:
        """Clear metrics."""
        if name and name in self._metrics:
            self._metrics[name].clear()
        elif not name:
            self._metrics.clear()


class Timer:
    """Context manager for timing operations."""

    def __init__(self, monitor: RealtimeMonitor, name: str, labels: Optional[Dict[str, str]] = None):
        self.monitor = monitor
        self.name = name
        self.labels = labels
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        self.monitor.record_timer(self.name, duration_ms, self.labels)
