"""
Tests for Chaos Engineering Module

Comprehensive test suite covering all chaos engineering functionality:
- Configuration and experiment management
- Chaos injectors and injection mechanisms
- System evaluation and monitoring
- Emergency controls and safety features
- Integration with observability and error handling
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from aiagentsuite.core.chaos_engineering import (
    ChaosConfiguration,
    ChaosExperiment,
    ChaosEvent,
    ChaosIntensity,
    ChaosInjector,
    DefaultChaosInjector,
    ChaosEvaluator,
    ChaosEngineeringManager,
    get_global_chaos_manager,
    set_global_chaos_manager,
    with_chaos_injection,
)


class TestChaosConfiguration:
    """Test ChaosConfiguration dataclass."""

    def test_default_configuration(self):
        """Test default chaos configuration values."""
        config = ChaosConfiguration()

        assert config.enabled is False
        assert config.intensity == ChaosIntensity.LOW
        assert config.experiment_duration == 300
        assert config.cooldown_period == 60
        assert config.target_services == {"*"}
        assert config.excluded_services == set()
        assert config.safe_mode is True

    def test_custom_configuration(self):
        """Test custom chaos configuration."""
        config = ChaosConfiguration(
            enabled=True,
            intensity=ChaosIntensity.HIGH,
            experiment_duration=600,
            cooldown_period=120,
            target_services={"service1", "service2"},
            excluded_services={"service3"},
            safe_mode=False,
        )

        assert config.enabled is True
        assert config.intensity == ChaosIntensity.HIGH
        assert config.experiment_duration == 600
        assert config.cooldown_period == 120
        assert config.target_services == {"service1", "service2"}
        assert config.excluded_services == {"service3"}
        assert config.safe_mode is False


class TestChaosExperiment:
    """Test ChaosExperiment dataclass."""

    def test_experiment_creation(self):
        """Test creating a chaos experiment."""
        experiment = ChaosExperiment(
            name="Test Experiment",
            description="A test chaos experiment",
            events=[ChaosEvent.LATENCY_INJECTION, ChaosEvent.EXCEPTION_INJECTION],
            intensity=ChaosIntensity.MEDIUM,
            duration=300,
        )

        assert experiment.name == "Test Experiment"
        assert experiment.description == "A test chaos experiment"
        assert experiment.events == [ChaosEvent.LATENCY_INJECTION, ChaosEvent.EXCEPTION_INJECTION]
        assert experiment.intensity == ChaosIntensity.MEDIUM
        assert experiment.duration == 300
        assert experiment.status == "pending"
        assert experiment.start_time is None
        assert experiment.end_time is None
        assert experiment.results == {}
        assert experiment.emergency_stop_triggered is False
        assert experiment.experiment_id.startswith("chaos_")

    def test_experiment_with_custom_id(self):
        """Test experiment with custom ID."""
        experiment = ChaosExperiment(
            name="Custom ID Experiment",
            description="Test custom ID",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=60,
            experiment_id="custom_123",
        )

        assert experiment.experiment_id == "custom_123"


class TestDefaultChaosInjector:
    """Test DefaultChaosInjector implementation."""

    def test_injector_initialization(self):
        """Test injector initialization."""
        injector = DefaultChaosInjector("test_service")

        assert injector.service_name == "test_service"
        assert injector.active_experiments == set()
        assert injector.failure_flags == {}
        assert injector.latency_injectors == {}

    @pytest.mark.asyncio
    async def test_inject_latency(self):
        """Test latency injection."""
        injector = DefaultChaosInjector("test_service")

        start_time = time.time()
        await injector.inject_latency(100, "test_correlation")
        end_time = time.time()

        # Should have injected at least 100ms (0.1 seconds) of latency
        assert end_time - start_time >= 0.09  # Allow small timing variance
        assert "test_correlation" in injector.latency_injectors
        assert injector.latency_injectors["test_correlation"] == 0.1

    @pytest.mark.asyncio
    async def test_inject_exception_value_error(self):
        """Test exception injection with ValueError."""
        injector = DefaultChaosInjector("test_service")

        with pytest.raises(ValueError, match=r"\[CHAOS INJECTION\] Test message"):
            await injector.inject_exception("ValueError", "Test message", "test_correlation")

    @pytest.mark.asyncio
    async def test_inject_exception_runtime_error(self):
        """Test exception injection with RuntimeError."""
        injector = DefaultChaosInjector("test_service")

        with pytest.raises(RuntimeError, match=r"\[CHAOS INJECTION\] Test message"):
            await injector.inject_exception("RuntimeError", "Test message", "test_correlation")

    @pytest.mark.asyncio
    async def test_inject_exception_unknown_type(self):
        """Test exception injection with unknown type defaults to RuntimeError."""
        injector = DefaultChaosInjector("test_service")

        with pytest.raises(RuntimeError, match=r"\[CHAOS INJECTION\] Test message"):
            await injector.inject_exception("UnknownError", "Test message", "test_correlation")

    @pytest.mark.asyncio
    async def test_exhaust_memory_resource(self):
        """Test memory resource exhaustion."""
        injector = DefaultChaosInjector("test_service")

        # This should not raise an exception, just simulate memory usage
        await injector.exhaust_resource("memory", 0.1, "test_correlation")

    @pytest.mark.asyncio
    async def test_exhaust_cpu_resource(self):
        """Test CPU resource exhaustion."""
        injector = DefaultChaosInjector("test_service")

        start_time = time.time()
        await injector.exhaust_resource("cpu", 0.01, "test_correlation")  # Very low percentage for quick test
        end_time = time.time()

        # Should have taken some time for CPU exhaustion simulation
        assert end_time - start_time >= 0.01

    @pytest.mark.asyncio
    async def test_exhaust_unknown_resource(self):
        """Test exhaustion of unknown resource type."""
        injector = DefaultChaosInjector("test_service")

        # Should not raise exception for unknown resource type
        await injector.exhaust_resource("unknown", 0.5, "test_correlation")

    @pytest.mark.asyncio
    async def test_simulate_service_failure(self):
        """Test service failure simulation."""
        injector = DefaultChaosInjector("test_service")

        # Start the failure simulation
        import asyncio
        task = asyncio.create_task(injector.simulate_service_failure("test_service", 0.1, "test_correlation"))
        
        # Check that flag is set during failure
        await asyncio.sleep(0.05)  # Halfway through
        assert injector.failure_flags["test_correlation"] is True
        
        # Wait for completion
        await task
        
        # Flag should be cleaned up
        assert "test_correlation" not in injector.failure_flags

    def test_is_experiment_active(self):
        """Test checking if experiment is active."""
        injector = DefaultChaosInjector("test_service")

        assert not injector.is_experiment_active("exp1")

        injector.active_experiments.add("exp1")
        assert injector.is_experiment_active("exp1")
        assert not injector.is_experiment_active("exp2")


class TestChaosEvaluator:
    """Test ChaosEvaluator functionality."""

    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        evaluator = ChaosEvaluator()

        assert evaluator.baseline_metrics == {}
        assert evaluator.experiment_metrics == {}
        assert "error_rate_increase" in evaluator.failure_thresholds
        assert "latency_increase" in evaluator.failure_thresholds
        assert "availability_decrease" in evaluator.failure_thresholds

    @pytest.mark.asyncio
    async def test_establish_baseline(self):
        """Test establishing baseline metrics."""
        evaluator = ChaosEvaluator()

        # Mock observability manager
        mock_observability = MagicMock()
        from aiagentsuite.core.observability import SystemMetrics, ApplicationMetrics
        mock_observability.metrics.collect_system_metrics = AsyncMock(return_value=SystemMetrics(
            cpu_percent=10.0, memory_percent=50.0, memory_used_gb=4.0, memory_total_gb=8.0,
            disk_usage_percent=30.0, network_bytes_sent=1000, network_bytes_recv=2000
        ))
        mock_observability.metrics.collect_application_metrics = AsyncMock(return_value=ApplicationMetrics(
            memory_usage_mb=100.0, uptime_seconds=3600.0
        ))

        await evaluator.establish_baseline(mock_observability, duration=1)  # Short duration for test

        assert "system_cpu_percent_avg" in evaluator.baseline_metrics
        assert "system_memory_percent_avg" in evaluator.baseline_metrics
        assert "app_memory_usage_mb_avg" in evaluator.baseline_metrics
        assert "app_uptime_seconds_avg" in evaluator.baseline_metrics

    @pytest.mark.asyncio
    async def test_monitor_during_experiment(self):
        """Test monitoring during experiment."""
        evaluator = ChaosEvaluator()

        # Set up baseline
        evaluator.baseline_metrics = {
            "system_cpu_percent_avg": 10.0,
            "system_memory_percent_avg": 50.0,
        }

        # Create experiment
        experiment = ChaosExperiment(
            name="Test Monitor",
            description="Test monitoring",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=1,  # Short duration
        )

        # Mock observability
        mock_observability = MagicMock()
        from aiagentsuite.core.observability import SystemMetrics, ApplicationMetrics
        mock_observability.metrics.collect_system_metrics = AsyncMock(return_value=SystemMetrics(
            cpu_percent=15.0, memory_percent=55.0, memory_used_gb=4.4, memory_total_gb=8.0,
            disk_usage_percent=65.0, network_bytes_sent=1500, network_bytes_recv=2500
        ))
        mock_observability.metrics.collect_application_metrics = AsyncMock(return_value=ApplicationMetrics(
            memory_usage_mb=110.0, uptime_seconds=3600.0
        ))

        await evaluator.monitor_during_experiment(experiment, mock_observability)

        assert experiment.status == "completed"
        assert experiment.start_time is not None
        assert experiment.end_time is not None
        assert "duration_actual" in experiment.results
        assert "stability_score" in experiment.results

    def test_calculate_averages_empty(self):
        """Test calculating averages with empty data."""
        evaluator = ChaosEvaluator()

        result = evaluator._calculate_averages([])
        assert result == {}

    def test_calculate_averages_with_data(self):
        """Test calculating averages with sample data."""
        from aiagentsuite.core.observability import SystemMetrics, ApplicationMetrics
        evaluator = ChaosEvaluator()

        samples = [
            {
                "system": SystemMetrics(
                    cpu_percent=10.0, memory_percent=50.0, memory_used_gb=4.0, memory_total_gb=8.0,
                    disk_usage_percent=30.0, network_bytes_sent=1000, network_bytes_recv=2000
                ),
                "application": ApplicationMetrics(
                    memory_usage_mb=100.0, uptime_seconds=3600.0
                ),
            },
            {
                "system": SystemMetrics(
                    cpu_percent=20.0, memory_percent=60.0, memory_used_gb=4.8, memory_total_gb=8.0,
                    disk_usage_percent=40.0, network_bytes_sent=2000, network_bytes_recv=3000
                ),
                "application": ApplicationMetrics(
                    memory_usage_mb=120.0, uptime_seconds=3700.0
                ),
            },
        ]

        result = evaluator._calculate_averages(samples)

        assert result["system_cpu_percent_avg"] == 15.0
        assert result["system_memory_percent_avg"] == 55.0
        assert result["app_memory_usage_mb_avg"] == 110.0
        assert result["app_uptime_seconds_avg"] == 3650.0

    def test_compare_with_baseline_no_baseline(self):
        """Test comparison when no baseline exists."""
        evaluator = ChaosEvaluator()

        result = evaluator._compare_with_baseline([])
        assert result == {"error": "no_baseline"}

    def test_calculate_stability_score_insufficient_data(self):
        """Test stability score with insufficient data."""
        evaluator = ChaosEvaluator()

        score = evaluator._calculate_stability_score([{}, {}, {}])  # Less than 5 samples
        assert score == 0.5

    def test_calculate_variance(self):
        """Test variance calculation."""
        evaluator = ChaosEvaluator()

        # Test with identical values (zero variance)
        variance = evaluator._calculate_variance([10.0, 10.0, 10.0])
        assert variance == 0.0

        # Test with varying values
        variance = evaluator._calculate_variance([1.0, 3.0, 5.0])
        assert variance > 0


class TestChaosEngineeringManager:
    """Test ChaosEngineeringManager functionality."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = ChaosEngineeringManager()

        assert isinstance(manager.configuration, ChaosConfiguration)
        assert manager.injectors == {}
        assert isinstance(manager.evaluator, ChaosEvaluator)
        assert manager.experiments == {}
        assert manager._experiment_task is None
        assert manager._running is False

    @pytest.mark.asyncio
    async def test_manager_lifecycle(self):
        """Test manager initialization and shutdown."""
        manager = ChaosEngineeringManager()
        assert manager._running is False

        await manager.initialize()
        assert manager._running is True

        await manager.shutdown()
        assert manager._running is False

    def test_register_injector(self):
        """Test registering chaos injectors."""
        manager = ChaosEngineeringManager()
        injector = DefaultChaosInjector("test_service")
        manager.register_injector(injector)

        assert "test_service" in manager.injectors
        assert manager.injectors["test_service"] is injector

    def test_configure(self):
        """Test updating manager configuration."""
        manager = ChaosEngineeringManager()
        config = ChaosConfiguration(enabled=True, intensity=ChaosIntensity.HIGH)
        manager.configure(config)

        assert manager.configuration.enabled is True
        assert manager.configuration.intensity == ChaosIntensity.HIGH

    @pytest.mark.asyncio
    async def test_run_experiment_disabled(self):
        """Test running experiment when chaos is disabled."""
        manager = ChaosEngineeringManager()
        experiment = ChaosExperiment(
            name="Disabled Test",
            description="Test disabled chaos",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=60,
        )

        result = await manager.run_experiment(experiment)

        assert result.status == "cancelled"

    @pytest.mark.asyncio
    async def test_run_experiment_intensity_too_high(self):
        """Test running experiment with intensity above configured limit."""
        manager = ChaosEngineeringManager()
        manager.configure(ChaosConfiguration(enabled=True, intensity=ChaosIntensity.LOW))

        experiment = ChaosExperiment(
            name="High Intensity Test",
            description="Test high intensity",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.HIGH,  # Higher than configured LOW
            duration=60,
        )

        result = await manager.run_experiment(experiment)

        assert result.status == "cancelled"

    @pytest.mark.asyncio
    async def test_run_experiment_success(self):
        """Test successful experiment execution."""
        # Mock observability before creating manager
        with patch('aiagentsuite.core.chaos_engineering.get_global_observability_manager') as mock_get_obs:
            mock_obs = MagicMock()
            from aiagentsuite.core.observability import SystemMetrics, ApplicationMetrics
            mock_obs.metrics.collect_system_metrics = AsyncMock(return_value=SystemMetrics(
                cpu_percent=10.0, memory_percent=50.0, memory_used_gb=4.0, memory_total_gb=8.0,
                disk_usage_percent=60.0, network_bytes_sent=1000, network_bytes_recv=2000
            ))
            mock_obs.metrics.collect_application_metrics = AsyncMock(return_value=ApplicationMetrics(
                memory_usage_mb=100.0, uptime_seconds=3600.0
            ))
            mock_obs.record_business_event = AsyncMock()
            mock_get_obs.return_value = mock_obs

            manager = ChaosEngineeringManager()
            await manager.initialize()
            manager.configure(ChaosConfiguration(enabled=True, intensity=ChaosIntensity.LOW))

            # Register injector
            injector = DefaultChaosInjector("test_service")
            manager.register_injector(injector)

            experiment = ChaosExperiment(
                name="Success Test",
                description="Test successful experiment",
                events=[ChaosEvent.LATENCY_INJECTION],
                intensity=ChaosIntensity.MINIMAL,  # Minimal for quick test
                duration=1,  # Very short duration
            )

            result = await manager.run_experiment(experiment)

            assert result.status in ["completed", "emergency_stopped"]
            assert result.start_time is not None
            assert result.end_time is not None
            assert "duration_actual" in result.results

        await manager.shutdown()

        await manager.shutdown()

    def test_get_experiment_status(self):
        """Test getting experiment status."""
        manager = ChaosEngineeringManager()
        experiment = ChaosExperiment(
            name="Status Test",
            description="Test status retrieval",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=60,
        )

        # Experiment not found
        assert manager.get_experiment_status("nonexistent") is None

        # Add experiment manually
        manager.experiments[experiment.experiment_id] = experiment
        assert manager.get_experiment_status(experiment.experiment_id) is experiment

    def test_get_all_experiments(self):
        """Test getting all experiments."""
        manager = ChaosEngineeringManager()
        experiment1 = ChaosExperiment(
            name="Test 1",
            description="First test",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=60,
        )
        experiment2 = ChaosExperiment(
            name="Test 2",
            description="Second test",
            events=[ChaosEvent.EXCEPTION_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=60,
        )

        manager.experiments[experiment1.experiment_id] = experiment1
        manager.experiments[experiment2.experiment_id] = experiment2

        all_experiments = manager.get_all_experiments()
        assert len(all_experiments) == 2
        assert experiment1.experiment_id in all_experiments
        assert experiment2.experiment_id in all_experiments

    @pytest.mark.asyncio
    async def test_emergency_stop_all(self):
        """Test emergency stop functionality."""
        manager = ChaosEngineeringManager()
        experiment1 = ChaosExperiment(
            name="Emergency Test 1",
            description="First emergency test",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=300,
        )
        experiment2 = ChaosExperiment(
            name="Emergency Test 2",
            description="Second emergency test",
            events=[ChaosEvent.EXCEPTION_INJECTION],
            intensity=ChaosIntensity.LOW,
            duration=300,
        )

        manager.experiments[experiment1.experiment_id] = experiment1
        manager.experiments[experiment2.experiment_id] = experiment2

        await manager.emergency_stop_all()

        assert experiment1.emergency_stop_triggered is True
        assert experiment2.emergency_stop_triggered is True
        assert len(manager.experiments) == 0

    def test_generate_experiment_preset(self):
        """Test generating experiment presets."""
        manager = ChaosEngineeringManager()
        # Test basic latency preset
        preset = manager.generate_experiment_preset("basic_latency")
        assert preset.name == "Basic Latency Injection"
        assert preset.events == [ChaosEvent.LATENCY_INJECTION]
        assert preset.intensity == ChaosIntensity.LOW
        assert preset.duration == 300

        # Test service failures preset
        preset = manager.generate_experiment_preset("service_failures")
        assert preset.name == "Service Failure Simulation"
        assert preset.events == [ChaosEvent.SERVICE_UNAVAILABLE]
        assert preset.intensity == ChaosIntensity.MEDIUM
        assert preset.duration == 600

        # Test complete chaos preset
        preset = manager.generate_experiment_preset("complete_chaos")
        assert preset.name == "Full System Chaos"
        assert len(preset.events) == 4  # All event types
        assert preset.intensity == ChaosIntensity.HIGH
        assert preset.duration == 900

        # Test unknown preset (should return basic_latency)
        preset = manager.generate_experiment_preset("unknown")
        assert preset.name == "Basic Latency Injection"


class TestGlobalManager:
    """Test global chaos manager functions."""

    def test_get_global_chaos_manager(self):
        """Test getting global chaos manager."""
        # Reset global state
        from aiagentsuite.core import chaos_engineering
        chaos_engineering._chaos_manager = None

        manager = get_global_chaos_manager()
        assert isinstance(manager, ChaosEngineeringManager)

        # Should return the same instance
        manager2 = get_global_chaos_manager()
        assert manager is manager2

    def test_set_global_chaos_manager(self):
        """Test setting global chaos manager."""
        # Reset global state
        from aiagentsuite.core import chaos_engineering
        chaos_engineering._chaos_manager = None

        custom_manager = ChaosEngineeringManager()
        set_global_chaos_manager(custom_manager)

        retrieved_manager = get_global_chaos_manager()
        assert retrieved_manager is custom_manager


class TestChaosInjectionDecorator:
    """Test chaos injection decorator."""

    @pytest.mark.asyncio
    async def test_decorator_no_injection(self):
        """Test decorator when chaos injection is disabled."""
        call_count = 0

        @with_chaos_injection(ChaosEvent.LATENCY_INJECTION, probability=1.0)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        # Reset global manager
        from aiagentsuite.core import chaos_engineering
        chaos_engineering._chaos_manager = None

        result = await test_function()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_decorator_with_injection(self):
        """Test decorator when chaos injection is enabled."""
        call_count = 0

        @with_chaos_injection(ChaosEvent.LATENCY_INJECTION, probability=1.0)
        async def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        # Set up manager with chaos enabled
        manager = ChaosEngineeringManager()
        manager.configuration.enabled = True
        injector = DefaultChaosInjector("test_service")
        manager.injectors["test_service"] = injector

        # Set global manager
        set_global_chaos_manager(manager)

        # Mock random to always trigger injection
        with patch('aiagentsuite.core.chaos_engineering.random.random', return_value=0.0):
            result = await test_function()
            assert result == "success"
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_decorator_exception_injection(self):
        """Test decorator with exception injection."""
        @with_chaos_injection(ChaosEvent.EXCEPTION_INJECTION, probability=1.0)
        async def failing_function():
            return "should not reach here"

        # Set up manager with chaos enabled
        manager = ChaosEngineeringManager()
        manager.configuration.enabled = True
        injector = DefaultChaosInjector("test_service")
        injector.active_experiments.add("global_test")  # Make experiment active
        manager.injectors["test_service"] = injector

        set_global_chaos_manager(manager)

        # Mock random to always trigger injection
        with patch('aiagentsuite.core.chaos_engineering.random.random', return_value=0.0):
            with pytest.raises(RuntimeError, match=r"\[CHAOS INJECTION\]"):
                await failing_function()


class TestIntegration:
    """Integration tests for chaos engineering components."""

    @pytest.mark.asyncio
    async def test_full_experiment_workflow(self):
        """Test complete experiment workflow from setup to completion."""
        # Create manager
        manager = ChaosEngineeringManager()
        await manager.initialize()

        # Configure chaos
        config = ChaosConfiguration(
            enabled=True,
            intensity=ChaosIntensity.LOW,
            experiment_duration=60,
        )
        manager.configure(config)

        # Register injector
        injector = DefaultChaosInjector("integration_test")
        manager.register_injector(injector)

        # Create experiment
        experiment = ChaosExperiment(
            name="Integration Test",
            description="Full workflow integration test",
            events=[ChaosEvent.LATENCY_INJECTION],
            intensity=ChaosIntensity.LOW,  # Match config intensity
            duration=1,
        )

        # Mock observability
        with patch('aiagentsuite.core.chaos_engineering.get_global_observability_manager') as mock_get_obs:
            mock_obs = MagicMock()
            from aiagentsuite.core.observability import SystemMetrics, ApplicationMetrics
            mock_obs.metrics.collect_system_metrics = AsyncMock(return_value=SystemMetrics(
                cpu_percent=10.0, memory_percent=50.0, memory_used_gb=4.0, memory_total_gb=8.0,
                disk_usage_percent=60.0, network_bytes_sent=1000, network_bytes_recv=2000
            ))
            mock_obs.metrics.collect_application_metrics = AsyncMock(return_value=ApplicationMetrics(
                memory_usage_mb=100.0, uptime_seconds=3600.0
            ))
            mock_obs.record_business_event = AsyncMock()
            mock_get_obs.return_value = mock_obs

            # Run experiment
            result = await manager.run_experiment(experiment)

            # Verify results
            assert result.status in ["completed", "emergency_stopped"]
            assert result.start_time is not None
            assert result.end_time is not None
            assert isinstance(result.results, dict)
            assert "duration_actual" in result.results

        # Cleanup
        await manager.shutdown()