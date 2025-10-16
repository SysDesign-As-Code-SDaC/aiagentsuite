"""
AI Agent Suite Observability Module

Provides comprehensive monitoring, metrics collection, distributed tracing,
logging, and health checks for enterprise-grade observability.
"""

import asyncio
import logging
import time
import json
import psutil
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable, AsyncGenerator
from functools import wraps

import structlog
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry, generate_latest
import sentry_sdk
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
except ImportError:
    JaegerExporter = None
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from .errors import get_global_error_handler
from .security import get_global_security_manager, SecurityLevel

logger = structlog.get_logger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0

    @property
    def is_healthy(self) -> bool:
        """Check if the result indicates a healthy state."""
        return self.status == HealthStatus.HEALTHY


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    active_connections: int = 0
    total_requests: int = 0
    active_requests: int = 0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    uptime_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class HealthCheck(ABC):
    """Abstract base class for health checks."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description or f"Health check for {name}"

    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""
        pass


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""

    def __init__(self, connection_string: str, name: str = "database"):
        super().__init__(name, "Database connectivity check")
        self.connection_string = connection_string

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Placeholder for actual database connection check
            # In production, this would test actual connectivity
            await asyncio.sleep(0.1)  # Simulate connection test
            duration = time.time() - start_time

            if duration < 1.0:  # Success if under 1 second
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    duration=duration,
                    details={"connection_time": f"{duration:.3f}s"}
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.DEGRADED,
                    message="Database connection slow",
                    duration=duration,
                    details={"connection_time": f"{duration:.3f}s"}
                )

        except Exception as e:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                duration=duration,
                details={"error": str(e)}
            )


class ExternalServiceHealthCheck(HealthCheck):
    """Health check for external service availability."""

    def __init__(self, service_name: str, url: str, timeout: float = 5.0):
        super().__init__(service_name, f"External service {service_name} availability check")
        self.url = url
        self.timeout = timeout

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            # Placeholder for HTTP health check
            # In production, this would make actual HTTP requests
            import aiohttp

            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.url}/health") as response:
                    duration = time.time() - start_time

                    if response.status == 200:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"Service {self.name} is healthy",
                            duration=duration,
                            details={"status_code": response.status}
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"Service {self.name} returned status {response.status}",
                            duration=duration,
                            details={"status_code": response.status}
                        )

        except Exception as e:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Service {self.name} unavailable: {str(e)}",
                duration=duration,
                details={"error": str(e)}
            )


class ComponentHealthCheck(HealthCheck):
    """Health check for internal components."""

    def __init__(self, component_name: str, health_func: Callable[[], Awaitable[bool]]):
        super().__init__(component_name, f"Component {component_name} health check")
        self.health_func = health_func

    async def check(self) -> HealthCheckResult:
        start_time = time.time()

        try:
            healthy = await self.health_func()
            duration = time.time() - start_time

            if healthy:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message=f"Component {self.name} is healthy",
                    duration=duration
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Component {self.name} is unhealthy",
                    duration=duration
                )

        except Exception as e:
            duration = time.time() - start_time
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Component {self.name} check failed: {str(e)}",
                duration=duration,
                details={"error": str(e)}
            )


class MetricsCollector:
    """Collects and exposes system and application metrics."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()

        # System metrics
        self.cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage', registry=self.registry)
        self.memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage', registry=self.registry)
        self.disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage', registry=self.registry)

        # Application metrics
        self.requests_total = Counter('requests_total', 'Total number of requests', ['method', 'endpoint'], registry=self.registry)
        self.requests_active = Gauge('requests_active', 'Number of active requests', registry=self.registry)
        self.request_duration = Histogram('request_duration_seconds', 'Request duration', ['method', 'endpoint'], registry=self.registry)
        self.errors_total = Counter('errors_total', 'Total number of errors', ['type', 'component'], registry=self.registry)

        # Protocol metrics
        self.protocol_executions = Counter('protocol_executions_total', 'Total protocol executions', ['protocol_name', 'status'], registry=self.registry)
        self.protocol_duration = Histogram('protocol_execution_duration_seconds', 'Protocol execution duration', ['protocol_name'], registry=self.registry)

        # Framework metrics
        self.framework_operations = Counter('framework_operations_total', 'Framework operations', ['operation', 'status'], registry=self.registry)

        # Security metrics
        self.security_events = Counter('security_events_total', 'Security events', ['event_type', 'severity'], registry=self.registry)

        self.start_time = time.time()

    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        metrics = SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_total_gb=memory.total / (1024**3),
            disk_usage_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv
        )

        # Update Prometheus metrics
        self.cpu_usage.set(cpu_percent)
        self.memory_usage.set(memory.percent)
        self.disk_usage.set(disk.percent)

        return metrics

    async def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect current application metrics."""
        process = psutil.Process()
        memory_info = process.memory_info()

        metrics = ApplicationMetrics(
            uptime_seconds=time.time() - self.start_time,
            memory_usage_mb=memory_info.rss / (1024**2)
        )

        return metrics

    def record_request(self, method: str, endpoint: str, duration: float, status_code: int = 200) -> None:
        """Record an HTTP request."""
        self.requests_total.labels(method=method, endpoint=endpoint).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            self.errors_total.labels(type=error_type, component="http").inc()

    def record_protocol_execution(self, protocol_name: str, status: str, duration: float) -> None:
        """Record a protocol execution."""
        self.protocol_executions.labels(protocol_name=protocol_name, status=status).inc()
        self.protocol_duration.labels(protocol_name=protocol_name).observe(duration)

    def record_framework_operation(self, operation: str, status: str) -> None:
        """Record a framework operation."""
        self.framework_operations.labels(operation=operation, status=status).inc()

    def record_security_event(self, event_type: str, severity: str) -> None:
        """Record a security event."""
        self.security_events.labels(event_type=event_type, severity=severity).inc()

    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode('utf-8')


class ApplicationInsights:
    """Application insights and business metrics."""

    def __init__(self) -> None:
        self.protocol_usage: Dict[str, int] = {}  # protocol_name -> usage_count
        self.user_activity: Dict[str, Dict[str, Any]] = {}  # user_id -> activity_metrics
        self.performance_trends: List[Dict[str, Any]] = []  # time-series performance data
        self.error_patterns: Dict[str, int] = {}  # error_type -> occurrences

    def record_protocol_usage(self, protocol_name: str, user_id: Optional[str] = None) -> None:
        """Record protocol usage for insights."""
        self.protocol_usage[protocol_name] = self.protocol_usage.get(protocol_name, 0) + 1

        if user_id:
            if user_id not in self.user_activity:
                self.user_activity[user_id] = {"protocols_executed": 0, "last_activity": time.time()}
            self.user_activity[user_id]["protocols_executed"] += 1
            self.user_activity[user_id]["last_activity"] = time.time()

    def get_popular_protocols(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular protocols."""
        sorted_protocols = sorted(
            self.protocol_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [{"protocol": name, "usage": count} for name, count in sorted_protocols[:limit]]

    def get_user_engagement(self) -> Dict[str, Any]:
        """Get user engagement metrics."""
        active_users = len([u for u in self.user_activity.values() if u["last_activity"] > time.time() - 86400])  # Last 24h
        total_executions = sum(u["protocols_executed"] for u in self.user_activity.values())

        return {
            "active_users_24h": active_users,
            "total_users": len(self.user_activity),
            "total_protocol_executions": total_executions,
            "avg_executions_per_user": total_executions / len(self.user_activity) if self.user_activity else 0
        }


class TracingManager:
    """Distributed tracing manager."""

    def __init__(self, service_name: str = "aiagentsuite"):
        self.service_name = service_name
        self.tracer = None
        self.resource = Resource.create({ResourceAttributes.SERVICE_NAME: service_name})

    def initialize(self, jaeger_endpoint: Optional[str] = None) -> None:
        """Initialize distributed tracing."""
        trace.set_tracer_provider(TracerProvider(resource=self.resource))

        # Console exporter for development
        console_processor = BatchSpanProcessor(ConsoleSpanExporter())
        trace.get_tracer_provider().add_span_processor(console_processor)

        # Jaeger exporter for production (if configured)
        if jaeger_endpoint:
            jaeger_processor = BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=jaeger_endpoint.split(':')[0],
                    agent_port=int(jaeger_endpoint.split(':')[1])
                )
            )
            trace.get_tracer_provider().add_span_processor(jaeger_processor)

        self.tracer = trace.get_tracer(__name__)
        logger.info("Distributed tracing initialized", service_name=self.service_name)

    def get_tracer(self) -> Any:
        """Get the current tracer."""
        return self.tracer or trace.get_tracer(__name__)

    @asynccontextmanager
    async def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Any, None]:
        """Context manager for tracing operations."""
        if not self.tracer:
            async with self._dummy_context():
                yield
            return

        with self.tracer.start_span(operation_name, attributes=attributes or {}) as span:
            start_time = time.time()
            try:
                yield span
                span.set_attribute("operation.success", True)
            except Exception as e:
                span.set_attribute("operation.success", False)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("operation.duration", duration)

    @asynccontextmanager
    async def _dummy_context(self) -> AsyncGenerator[None, None]:
        """Dummy context manager when tracing is not available."""
        yield None


class StructuredLogger:
    """Enhanced structured logging."""

    def __init__(self, log_level: str = "INFO"):
        self.setup_structlog(log_level)

    def setup_structlog(self, log_level: str) -> None:
        """Setup structured logging configuration."""
        import logging.config

        # Setup standard Python logging
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.WriteLoggerFactory(),
                }
            },
            "handlers": {
                "json": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": logging.sys.stdout,
                }
            },
            "loggers": {
                "": {
                    "handlers": ["json"],
                    "level": log_level,
                }
            }
        })

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.WriteLoggerFactory(),
            wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(log_level))
        )

    def get_logger(self, name: str) -> Any:
        """Get a structured logger instance."""
        return structlog.get_logger(name)


class SecurityMonitoring:
    """Security event monitoring and alerting."""

    def __init__(self, alert_thresholds: Optional[Dict[str, int]] = None) -> None:
        self.failed_auth_attempts: Dict[str, int] = {}  # ip -> count
        self.suspicious_activities: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> activities
        self.alert_thresholds = alert_thresholds or {
            "failed_auth_per_ip": 5,
            "suspicious_activities_per_user": 10,
            "rate_limit_violations": 50
        }
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], Awaitable[None]]] = []

    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None]]) -> None:
        """Add a callback for security alerts."""
        self.alert_callbacks.append(callback)

    async def record_failed_auth(self, ip_address: str, username: str) -> None:
        """Record a failed authentication attempt."""
        self.failed_auth_attempts[ip_address] = self.failed_auth_attempts.get(ip_address, 0) + 1

        if self.failed_auth_attempts[ip_address] >= self.alert_thresholds["failed_auth_per_ip"]:
            await self._trigger_alert("multiple_failed_auth", {
                "ip_address": ip_address,
                "username": username,
                "attempt_count": self.failed_auth_attempts[ip_address]
            })

    async def record_suspicious_activity(self, user_id: str, activity_type: str, details: Dict[str, Any]) -> None:
        """Record suspicious user activity."""
        if user_id not in self.suspicious_activities:
            self.suspicious_activities[user_id] = []

        self.suspicious_activities[user_id].append({
            "activity_type": activity_type,
            "details": details,
            "timestamp": time.time()
        })

        # Keep only recent activities (last 24 hours)
        cutoff = time.time() - 86400
        self.suspicious_activities[user_id] = [
            activity for activity in self.suspicious_activities[user_id]
            if activity["timestamp"] > cutoff
        ]

        if len(self.suspicious_activities[user_id]) >= self.alert_thresholds["suspicious_activities_per_user"]:
            await self._trigger_alert("suspicious_user_activity", {
                "user_id": user_id,
                "activity_count": len(self.suspicious_activities[user_id]),
                "activities": self.suspicious_activities[user_id]
            })

    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger security alert to all registered callbacks."""
        for callback in self.alert_callbacks:
            try:
                await callback(alert_type, data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}", alert_type=alert_type)


class ObservabilityManager:
    """Central observability manager coordinating all monitoring components."""

    def __init__(self) -> None:
        self.metrics = MetricsCollector()
        self.health_checks: List[HealthCheck] = []
        self.insights = ApplicationInsights()
        self.tracing = TracingManager()
        self.security_monitoring = SecurityMonitoring()
        self.logger = StructuredLogger()
        self.error_handler = get_global_error_handler()
        self.security_manager = get_global_security_manager()

        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_interval = 30  # seconds

    async def initialize(self, jaeger_endpoint: Optional[str] = None) -> None:
        """Initialize observability manager."""
        # Initialize tracing
        self.tracing.initialize(jaeger_endpoint)

        # Setup default health checks
        self._setup_default_health_checks()

        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        # Setup Sentry (if configured)
        if sentry_dsn := self._get_sentry_dsn():
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[],
                environment="production"
            )

        logger.info("Observability manager initialized")

    async def shutdown(self) -> None:
        """Shutdown observability manager."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

    def _get_sentry_dsn(self) -> Optional[str]:
        """Get Sentry DSN from environment configuration."""
        # Placeholder - would read from environment
        return None

    def _setup_default_health_checks(self) -> None:
        """Setup default health checks."""
        # Add framework component health checks
        self.add_health_check(ComponentHealthCheck(
            "framework_manager",
            lambda: self._check_framework_health()
        ))

        self.add_health_check(ComponentHealthCheck(
            "protocol_executor",
            lambda: self._check_protocol_health()
        ))

        self.add_health_check(ComponentHealthCheck(
            "memory_bank",
            lambda: self._check_memory_bank_health()
        ))

    def add_health_check(self, health_check: HealthCheck) -> None:
        """Add a health check."""
        self.health_checks.append(health_check)

    async def run_health_checks(self) -> List[HealthCheckResult]:
        """Run all health checks."""
        results = []

        for check in self.health_checks:
            try:
                result = await check.check()
                results.append(result)

                # Record health check metrics
                status = 1 if result.is_healthy else 0
                self.metrics.errors_total.labels(
                    type="health_check_failure",
                    component=check.name
                ).inc(1 - status)  # Increment if unhealthy

            except Exception as e:
                logger.error(f"Health check {check.name} failed: {e}")
                results.append(HealthCheckResult(
                    name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check execution failed: {str(e)}"
                ))

        return results

    async def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        results = await self.run_health_checks()

        healthy_count = sum(1 for r in results if r.is_healthy)
        total_count = len(results)

        # Determine overall status
        if healthy_count == total_count:
            overall_status = HealthStatus.HEALTHY
        elif healthy_count >= total_count * 0.5:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY

        return {
            "status": overall_status.value,
            "healthy_components": healthy_count,
            "total_components": total_count,
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration": r.duration
                }
                for r in results
            ],
            "timestamp": datetime.now().isoformat()
        }

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        try:
            while True:
                try:
                    # Collect metrics
                    system_metrics = self.metrics.collect_system_metrics()
                    app_metrics = self.metrics.collect_application_metrics()

                    # Log performance data periodically
                    logger.info("System metrics collected",
                              cpu_percent=system_metrics.cpu_percent,
                              memory_percent=system_metrics.memory_percent,
                              memory_used_gb=system_metrics.memory_used_gb)

                except Exception as e:
                    logger.error(f"Metrics collection failed: {e}")
                    await self.error_handler.handle_error(e)

                await asyncio.sleep(self._metrics_interval)

        except asyncio.CancelledError:
            logger.info("Monitoring loop stopped")

    async def _check_framework_health(self) -> bool:
        """Check framework component health."""
        # Placeholder - would check actual framework status
        return True

    async def _check_protocol_health(self) -> bool:
        """Check protocol executor health."""
        # Placeholder - would check protocol execution capability
        return True

    async def _check_memory_bank_health(self) -> bool:
        """Check memory bank health."""
        # Placeholder - would check memory bank connectivity
        return True

    def instrument_function(self, name: Optional[str] = None) -> Callable:
        """Decorator to instrument functions with monitoring."""
        def decorator(func: Callable) -> Callable:
            operation_name = name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.tracing.get_tracer().start_span(operation_name) as span:
                    start_time = time.time()
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("operation.success", True)
                        return result
                    except Exception as e:
                        span.set_attribute("operation.success", False)
                        span.record_exception(e)
                        raise
                    finally:
                        duration = time.time() - start_time
                        span.set_attribute("operation.duration", duration)
                        self.metrics.request_duration.labels(
                            method="function", endpoint=operation_name
                        ).observe(duration)

            return wrapper
        return decorator

    async def record_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record business-level events for monitoring."""
        logger.info(f"Business event: {event_type}", **data)

        # Update insights
        if event_type == "protocol_executed":
            protocol_name = data.get("protocol_name")
            user_id = data.get("user_id")
            if protocol_name:
                self.insights.record_protocol_usage(protocol_name, user_id)


# Global observability manager instance
_observability_manager = None

def get_global_observability_manager() -> ObservabilityManager:
    """Get the global observability manager instance."""
    global _observability_manager
    if _observability_manager is None:
        _observability_manager = ObservabilityManager()
    return _observability_manager

def set_global_observability_manager(manager: ObservabilityManager) -> None:
    """Set the global observability manager instance."""
    global _observability_manager
    _observability_manager = manager
