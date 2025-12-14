"""
AI Agent Suite Chaos Engineering Module

Implements systematic failure injection and resilience testing to ensure
system reliability under adverse conditions. Based on principles from
Netflix, Amazon, and other chaos engineering practitioners.
"""

import asyncio
import random
import time
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Awaitable
from functools import wraps

from .errors import get_global_error_handler, ResourceError
from .observability import get_global_observability_manager

logger = logging.getLogger(__name__)


class ChaosEvent(Enum):
    """Types of chaos events that can be injected."""
    LATENCY_INJECTION = "latency_injection"
    EXCEPTION_INJECTION = "exception_injection"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    PROCESS_CRASH = "process_crash"
    DATA_CORRUPTION = "data_corruption"
    CONFIGURATION_DRIFT = "configuration_drift"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ChaosIntensity(Enum):
    """Intensity levels for chaos experiments."""
    MINIMAL = 1     # < 1% error rate
    LOW = 2         # 1-5% error rate
    MEDIUM = 3      # 5-15% error rate
    HIGH = 4        # 15-30% error rate
    EXTREME = 5     # > 30% error rate (highly destructive)


@dataclass
class ChaosConfiguration:
    """Configuration for chaos engineering experiments."""
    enabled: bool = False
    intensity: ChaosIntensity = ChaosIntensity.LOW
    experiment_duration: int = 300  # 5 minutes
    cooldown_period: int = 60      # 1 minute
    target_services: Set[str] = field(default_factory=lambda: {"*"})
    excluded_services: Set[str] = field(default_factory=set)
    safe_mode: bool = True         # Emergency stop capability


@dataclass
class ChaosExperiment:
    """Represents a single chaos engineering experiment."""
    name: str
    description: str
    events: List[ChaosEvent]
    intensity: ChaosIntensity
    duration: int
    experiment_id: str = field(default_factory=lambda: f"chaos_{int(time.time())}_{random.randint(1000, 9999)}")
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    emergency_stop_triggered: bool = False


class ChaosInjector(ABC):
    """Abstract base class for chaos injectors."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.active_experiments: Set[str] = set()

    @abstractmethod
    async def inject_latency(self, duration_ms: int, correlation_id: str) -> None:
        """Inject artificial latency."""
        pass

    @abstractmethod
    async def inject_exception(self, exception_type: str, message: str, correlation_id: str) -> None:
        """Inject artificial exceptions."""
        pass

    @abstractmethod
    async def exhaust_resource(self, resource_type: str, percentage: float, correlation_id: str) -> None:
        """Exhaust system resources."""
        pass

    @abstractmethod
    async def simulate_service_failure(self, service_name: str, duration: int, correlation_id: str) -> None:
        """Simulate service unavailability."""
        pass

    def is_experiment_active(self, experiment_id: str) -> bool:
        """Check if experiment is active."""
        return experiment_id in self.active_experiments


class DefaultChaosInjector(ChaosInjector):
    """Default implementation for chaos injection."""

    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.failure_flags: Dict[str, bool] = {}
        self.latency_injectors: Dict[str, float] = {}

    async def inject_latency(self, duration_ms: int, correlation_id: str) -> None:
        """Inject artificial latency."""
        self.latency_injectors[correlation_id] = duration_ms / 1000.0
        await asyncio.sleep(duration_ms / 1000.0)

    async def inject_exception(self, exception_type: str, message: str, correlation_id: str) -> None:
        """Inject artificial exceptions."""
        exception_classes = {
            "ValueError": ValueError,
            "RuntimeError": RuntimeError,
            "ConnectionError": ConnectionError,
            "ResourceError": ResourceError,
        }

        exception_class = exception_classes.get(exception_type, RuntimeError)
        raise exception_class(f"[CHAOS INJECTION] {message}")

    async def exhaust_resource(self, resource_type: str, percentage: float, correlation_id: str) -> None:
        """Exhaust system resources."""
        if resource_type == "memory":
            # Simulate memory exhaustion by allocating large amounts
            large_data = "x" * int(100 * 1024 * 1024 * percentage)  # percentage of 100MB
            await asyncio.sleep(1)  # Hold memory
            del large_data
        elif resource_type == "cpu":
            # Simulate CPU exhaustion with busy loop
            end_time = time.time() + (percentage * 10)  # Scale to 10 seconds max
            while time.time() < end_time:
                # Busy work
                [i ** 2 for i in range(1000)]

    async def simulate_service_failure(self, service_name: str, duration: int, correlation_id: str) -> None:
        """Simulate service unavailability."""
        self.failure_flags[correlation_id] = True
        await asyncio.sleep(duration)
        self.failure_flags.pop(correlation_id, None)


class ChaosEvaluator:
    """Evaluates system behavior during chaos experiments."""

    def __init__(self):
        self.baseline_metrics = {}
        self.experiment_metrics = {}
        self.failure_thresholds = {
            "error_rate_increase": 10.0,  # % increase in errors
            "latency_increase": 50.0,     # % increase in latency
            "availability_decrease": 5.0, # % decrease in availability
        }

    async def establish_baseline(self, observability: 'ObservabilityManager', duration: int = 60) -> None:
        """Establish baseline metrics before chaos injection."""
        logger.info("Establishing baseline metrics")

        baseline_start = time.time()
        metrics_snapshot = []

        while time.time() - baseline_start < duration:
            # Collect current metrics
            system_metrics = await observability.metrics.collect_system_metrics()
            app_metrics = await observability.metrics.collect_application_metrics()

            metrics_snapshot.append({
                "timestamp": datetime.now(),
                "system": system_metrics,
                "application": app_metrics
            })

            await asyncio.sleep(5)  # Sample every 5 seconds

        # Calculate baseline averages
        self.baseline_metrics = self._calculate_averages(metrics_snapshot)
        logger.info(f"Baseline metrics established: {self.baseline_metrics}")

    async def monitor_during_experiment(self, experiment: ChaosExperiment, observability: 'ObservabilityManager') -> None:
        """Monitor system during chaos experiment."""
        logger.info(f"Monitoring experiment {experiment.experiment_id}")

        experiment.start_time = datetime.now()
        experiment.status = "running"

        metrics_samples = []

        start_time = time.time()
        while time.time() - start_time < experiment.duration and not experiment.emergency_stop_triggered:
            system_metrics = await observability.metrics.collect_system_metrics()
            app_metrics = await observability.metrics.collect_application_metrics()

            metrics_samples.append({
                "timestamp": datetime.now(),
                "system": system_metrics,
                "application": app_metrics
            })

            # Check emergency conditions
            if await self._check_emergency_conditions(metrics_samples):
                experiment.emergency_stop_triggered = True
                logger.warning(f"Emergency stop triggered for experiment {experiment.experiment_id}")
                break

            await asyncio.sleep(5)  # Sample every 5 seconds

        experiment.end_time = datetime.now()
        experiment.status = "completed" if not experiment.emergency_stop_triggered else "emergency_stopped"

        # Analyze results
        experiment.results = {
            "duration_actual": (experiment.end_time - experiment.start_time).total_seconds(),
            "emergency_stop": experiment.emergency_stop_triggered,
            "metrics_comparison": self._compare_with_baseline(metrics_samples),
            "stability_score": self._calculate_stability_score(metrics_samples)
        }

        logger.info(f"Experiment {experiment.experiment_id} monitoring complete with results: {experiment.results}")

    async def _check_emergency_conditions(self, metrics_samples: List[Dict]) -> bool:
        """Check if emergency conditions are met."""
        if len(metrics_samples) < 3:
            return False

        # Check for rapid error rate increase
        recent_errors = [sample["application"].error_rate for sample in metrics_samples[-3:]]
        if all(error > 0.5 for error in recent_errors):  # >50% error rate
            return True

        # Check for memory exhaustion
        recent_memory = [sample["system"].memory_percent for sample in metrics_samples[-3:]]
        if all(memory > 95 for memory in recent_memory):  # >95% memory usage
            return True

        return False

    def _calculate_averages(self, metrics_samples: List[Dict]) -> Dict[str, Any]:
        """Calculate average metrics from samples."""
        if not metrics_samples:
            return {}

        system_keys = ["cpu_percent", "memory_percent", "disk_usage_percent"]
        app_keys = ["memory_usage_mb", "uptime_seconds"]

        averages = {}

        for key in system_keys:
            values = [getattr(sample["system"], key, 0) for sample in metrics_samples]
            averages[f"system_{key}_avg"] = sum(values) / len(values) if values else 0

        for key in app_keys:
            values = [getattr(sample["application"], key, 0) for sample in metrics_samples]
            averages[f"app_{key}_avg"] = sum(values) / len(values) if values else 0

        return averages

    def _compare_with_baseline(self, metrics_samples: List[Dict]) -> Dict[str, Any]:
        """Compare experiment metrics with baseline."""
        if not self.baseline_metrics:
            return {"error": "no_baseline"}

        comparison = self._calculate_averages(metrics_samples)

        differences = {}
        for key, experiment_value in comparison.items():
            baseline_value = self.baseline_metrics.get(key, experiment_value)
            if baseline_value != 0:
                difference_pct = ((experiment_value - baseline_value) / baseline_value) * 100
                differences[f"{key}_change_pct"] = difference_pct

        return differences

    def _calculate_stability_score(self, metrics_samples: List[Dict]) -> float:
        """Calculate system stability score during experiment."""
        if len(metrics_samples) < 5:
            return 0.5

        # Calculate variance in key metrics
        # SystemMetrics and ApplicationMetrics are Pydantic models, so we access attributes directly
        cpu_values = [getattr(sample["system"], "cpu_percent", 0) for sample in metrics_samples]
        memory_values = [getattr(sample["system"], "memory_percent", 0) for sample in metrics_samples]

        cpu_variance = self._calculate_variance(cpu_values)
        memory_variance = self._calculate_variance(memory_values)

        # Lower variance = higher stability
        stability_score = max(0, 1.0 - (cpu_variance + memory_variance) / 200)  # Normalize

        return stability_score

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance


class ChaosEngineeringManager:
    """Central manager for chaos engineering experiments."""

    def __init__(self):
        self.configuration = ChaosConfiguration()
        self.injectors: Dict[str, ChaosInjector] = {}
        self.evaluator = ChaosEvaluator()
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.observability = get_global_observability_manager()
        self.error_handler = get_global_error_handler()

        self._experiment_task: Optional[asyncio.Task] = None
        self._running = False

    async def initialize(self) -> None:
        """Initialize chaos engineering manager."""
        if self._running:
            return

        self._running = True
        logger.info("Chaos engineering manager initialized")

    async def shutdown(self) -> None:
        """Shutdown chaos engineering manager."""
        if self._experiment_task and not self._experiment_task.done():
            self._experiment_task.cancel()
            try:
                await self._experiment_task
            except asyncio.CancelledError:
                pass

        self._running = False
        logger.info("Chaos engineering manager shutdown")

    def register_injector(self, injector: ChaosInjector) -> None:
        """Register a chaos injector for a service."""
        self.injectors[injector.service_name] = injector
        logger.info(f"Registered chaos injector for {injector.service_name}")

    def configure(self, config: ChaosConfiguration) -> None:
        """Update chaos configuration."""
        self.configuration = config
        logger.info(f"Chaos configuration updated: enabled={config.enabled}, intensity={config.intensity}")

    async def run_experiment(self, experiment: ChaosExperiment) -> ChaosExperiment:
        """Run a chaos experiment."""
        if not self.configuration.enabled:
            logger.warning("Chaos engineering is disabled")
            experiment.status = "cancelled"
            return experiment

        if experiment.intensity.value > self.configuration.intensity.value:
            logger.warning(f"Experiment intensity {experiment.intensity} exceeds configured {self.configuration.intensity}")
            experiment.status = "cancelled"
            return experiment

        # Establish baseline if not already done
        if not self.evaluator.baseline_metrics:
            await self.evaluator.establish_baseline(self.observability)

        # Run experiment
        self.experiments[experiment.experiment_id] = experiment

        try:
            # Setup injectors
            for event in experiment.events:
                await self._schedule_chaos_event(event, experiment)

            # Monitor experiment
            await self.evaluator.monitor_during_experiment(experiment, self.observability)

        except Exception as e:
            logger.error(f"Experiment {experiment.experiment_id} failed: {e}")
            experiment.status = "failed"
            experiment.results["error"] = str(e)

        finally:
            # Cleanup
            await self._cleanup_experiment(experiment.experiment_id)

        # Log results
        await self.observability.record_business_event("chaos_experiment_completed", {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "status": experiment.status,
            "stability_score": experiment.results.get("stability_score", 0),
            "emergency_stop": experiment.emergency_stop_triggered
        })

        return experiment

    async def _schedule_chaos_event(self, event: ChaosEvent, experiment: ChaosExperiment) -> None:
        """Schedule a chaos event during the experiment."""
        # Calculate timing based on intensity
        if experiment.intensity == ChaosIntensity.MINIMAL:
            event_count = 1
            timing_distribution = lambda: random.uniform(60, experiment.duration - 60)
        elif experiment.intensity == ChaosIntensity.LOW:
            event_count = random.randint(2, 4)
            timing_distribution = lambda: random.uniform(30, experiment.duration - 30)
        elif experiment.intensity == ChaosIntensity.MEDIUM:
            event_count = random.randint(4, 8)
            timing_distribution = lambda: random.uniform(15, experiment.duration - 15)
        elif experiment.intensity == ChaosIntensity.HIGH:
            event_count = random.randint(8, 12)
            timing_distribution = lambda: random.uniform(5, experiment.duration - 5)
        else:  # EXTREME
            event_count = random.randint(12, 20)
            timing_distribution = lambda: random.uniform(1, experiment.duration - 1)

        # Schedule events
        for i in range(event_count):
            delay = timing_distribution() if i > 0 else random.uniform(10, 30)
            service = random.choice(list(self.injectors.keys())) if self.injectors else None

            if service and service in self.injectors:
                injector = self.injectors[service]
                correlation_id = f"{experiment.experiment_id}_{i}"

                asyncio.create_task(self._inject_at_time(
                    injector, event, correlation_id, delay
                ))

    async def _inject_at_time(self, injector: ChaosInjector, event: ChaosEvent,
                            correlation_id: str, delay: float) -> None:
        """Inject chaos at a specific time."""
        await asyncio.sleep(delay)

        try:
            if event == ChaosEvent.LATENCY_INJECTION:
                duration = random.randint(1000, 5000)  # 1-5 seconds
                await injector.inject_latency(duration, correlation_id)

            elif event == ChaosEvent.EXCEPTION_INJECTION:
                exception_types = ["ValueError", "RuntimeError", "ConnectionError", "ResourceError"]
                exc_type = random.choice(exception_types)
                message = f"Chaos engineering experiment {correlation_id}"
                await injector.inject_exception(exc_type, message, correlation_id)

            elif event == ChaosEvent.RESOURCE_EXHAUSTION:
                resource_types = ["memory", "cpu"]
                res_type = random.choice(resource_types)
                percentage = random.uniform(0.3, 0.7)  # 30-70% exhaustion
                await injector.exhaust_resource(res_type, percentage, correlation_id)

            elif event == ChaosEvent.SERVICE_UNAVAILABLE:
                duration = random.randint(10, 60)  # 10-60 seconds
                service_name = injector.service_name
                await injector.simulate_service_failure(service_name, duration, correlation_id)

            logger.info(f"Chaos event injected: {event.value} on {injector.service_name}")

        except Exception as e:
            logger.error(f"Chaos injection failed: {e}")

    async def _cleanup_experiment(self, experiment_id: str) -> None:
        """Clean up after experiment completion."""
        # Remove experiment from active list
        self.experiments.pop(experiment_id, None)

        # Notify injectors to stop any active injections
        for injector in self.injectors.values():
            injector.active_experiments.discard(experiment_id)

    def get_experiment_status(self, experiment_id: str) -> Optional[ChaosExperiment]:
        """Get status of a running experiment."""
        return self.experiments.get(experiment_id)

    def get_all_experiments(self) -> Dict[str, ChaosExperiment]:
        """Get all experiments."""
        return self.experiments.copy()

    async def emergency_stop_all(self) -> None:
        """Emergency stop all running experiments."""
        logger.warning("Emergency stop triggered for all experiments")

        for experiment_id in list(self.experiments.keys()):
            experiment = self.experiments[experiment_id]
            experiment.emergency_stop_triggered = True
            await self._cleanup_experiment(experiment_id)

    def generate_experiment_preset(self, preset_name: str) -> ChaosExperiment:
        """Generate a pre-configured experiment."""

        presets = {
            "basic_latency": ChaosExperiment(
                name="Basic Latency Injection",
                description="Test system response to artificial latency",
                events=[ChaosEvent.LATENCY_INJECTION],
                intensity=ChaosIntensity.LOW,
                duration=300
            ),

            "service_failures": ChaosExperiment(
                name="Service Failure Simulation",
                description="Simulate random service unavailabilities",
                events=[ChaosEvent.SERVICE_UNAVAILABLE],
                intensity=ChaosIntensity.MEDIUM,
                duration=600
            ),

            "resource_contention": ChaosExperiment(
                name="Resource Exhaustion Test",
                description="Test system under resource pressure",
                events=[ChaosEvent.RESOURCE_EXHAUSTION],
                intensity=ChaosIntensity.MEDIUM,
                duration=450
            ),

            "complete_chaos": ChaosExperiment(
                name="Full System Chaos",
                description="Comprehensive chaos testing across all dimensions",
                events=[
                    ChaosEvent.LATENCY_INJECTION,
                    ChaosEvent.EXCEPTION_INJECTION,
                    ChaosEvent.RESOURCE_EXHAUSTION,
                    ChaosEvent.SERVICE_UNAVAILABLE
                ],
                intensity=ChaosIntensity.HIGH,
                duration=900
            ),
        }

        return presets.get(preset_name, presets["basic_latency"])


# Global chaos engineering manager instance
_chaos_manager = None

def get_global_chaos_manager() -> ChaosEngineeringManager:
    """Get the global chaos engineering manager instance."""
    global _chaos_manager
    if _chaos_manager is None:
        _chaos_manager = ChaosEngineeringManager()
    return _chaos_manager

def set_global_chaos_manager(manager: ChaosEngineeringManager) -> None:
    """Set the global chaos engineering manager instance."""
    global _chaos_manager
    _chaos_manager = manager


# Decorators for chaos injection
def with_chaos_injection(chaos_type: ChaosEvent, probability: float = 0.1):
    """Decorator to inject chaos into functions during experiments."""
    def decorator(func: callable) -> callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            chaos_manager = get_global_chaos_manager()

            # Check if chaos injection should occur
            if random.random() < probability and chaos_manager.configuration.enabled:
                # Check if any injector is available
                for injector in chaos_manager.injectors.values():
                    if injector.is_experiment_active("global_test"):
                        if chaos_type == ChaosEvent.LATENCY_INJECTION:
                            await injector.inject_latency(1000, f"func_{func.__name__}")
                        elif chaos_type == ChaosEvent.EXCEPTION_INJECTION:
                            await injector.inject_exception("RuntimeError", f"Chaos in {func.__name__}", f"func_{func.__name__}")
                        break

            return await func(*args, **kwargs)
        return wrapper
    return decorator
