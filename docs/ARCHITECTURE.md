# AI Agent Suite - Architecture Documentation

Automatically generated from AST analysis.

Analysis Date: The current date is: Sat 10/11/2025 
Enter the new date: (mm-dd-yy)

Total Modules: 14
Total Classes: 111
Total Functions: 196
Total Integrations: 22

## 📦 Module Overview

### src.aiagentsuite.cli.main

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\cli\main.py`

**Functions:**
- `main(ctx, workspace)` 🟢 (complexity: 1)
  > AI Agent Suite CLI - Development/Debugging Tool (LSP/MCP handles automation).
- `init(ctx)` 🟢 (complexity: 1)
  > Initialize the AI Agent Suite (for development/testing).
- `constitution(ctx)` 🟢 (complexity: 1)
  > Display the AI agent constitution (for reference/verification).
- `protocols(ctx)` 🟢 (complexity: 2)
  > List available protocols (for development reference).
- `execute(ctx, protocol_name, context)` 🟢 (complexity: 4)
  > Execute a protocol manually (for testing/debugging).
- `memory(ctx, context_type)` 🟢 (complexity: 1)
  > Inspect memory bank context (for debugging/verification).
- `log_decision(ctx, decision, rationale, context)` 🟢 (complexity: 2)
  > Log a decision manually (for development/testing).

**Dependencies:**
- src.aiagentsuite.core.architecture_analyzer

### src.aiagentsuite.core.architecture_analyzer

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\architecture_analyzer.py`

**Classes:**
- `ClassInfo` (0 methods, 10 properties)
  > Information about a class.
- `FunctionInfo` (0 methods, 8 properties)
  > Information about a function.
- `ModuleInfo` (0 methods, 7 properties)
  > Information about a module.
- `IntegrationInfo` (0 methods, 6 properties)
  > Information about integrations between components.
- `ASTVisitor` (10 methods, 10 properties)
  > Custom AST visitor for code analysis.
  > Inherits: ast.NodeVisitor
- `ComplexityVisitor` (8 methods, 0 properties)
  > Inherits: ast.NodeVisitor
- `ArchitectureAnalyzer` (13 methods, 33 properties)
  > Main architecture analyzer using AST.

**Functions:**
- `__init__(self, project_root)` 🟢 (complexity: 2)
- `visit_Import(self, node)` 🟢 (complexity: 2)
  > Handle import statements.
- `visit_ImportFrom(self, node)` 🟢 (complexity: 2)
  > Handle from import statements.
- `visit_ClassDef(self, node)` 🟢 (complexity: 5)
  > Handle class definitions.
- `visit_FunctionDef(self, node)` 🟢 (complexity: 4)
  > Handle function definitions.
- `visit_Call(self, node)` 🟢 (complexity: 4)
  > Handle function/method calls.
- `visit_AnnAssign(self, node)` 🟢 (complexity: 3)
  > Handle annotated assignments (properties).
- `visit_Assign(self, node)` 🟢 (complexity: 5)
  > Handle assignments.
- `_get_decorator_name(self, decorator)` 🟡 (complexity: 6)
  > Extract decorator name from AST node.
- `_calculate_complexity(self, node)` 🟢 (complexity: 1)
  > Calculate cyclomatic complexity for a function.
- `visit_If(self, node)` 🟢 (complexity: 1)
- `visit_For(self, node)` 🟢 (complexity: 1)
- `visit_While(self, node)` 🟢 (complexity: 1)
- `visit_With(self, node)` 🟢 (complexity: 1)
- `visit_Try(self, node)` 🟢 (complexity: 1)
- `visit_And(self, node)` 🟢 (complexity: 1)
- `visit_Or(self, node)` 🟢 (complexity: 1)
- `analyze_project(self, source_path)` 🟡 (complexity: 6)
  > Analyze the entire project using AST.
- `analyze_file(self, file_path)` 🟡 (complexity: 8)
  > Analyze a single Python file.
- `_get_module_name(self, file_path)` 🟢 (complexity: 3)
  > Get module name from file path.
- `_build_integrations(self)` 🔴 (complexity: 13)
  > Build integration map between components.
- `_analyze_dependencies(self)` 🟡 (complexity: 9)
  > Analyze module dependencies.
- `_get_module_by_file(self, file_path)` 🟢 (complexity: 3)
  > Get module name by file path.
- `generate_documentation(self, output_path)` 🔴 (complexity: 13)
  > Generate comprehensive architecture documentation.
- `generate_mermaid_diagrams(self, output_dir)` 🟢 (complexity: 1)
  > Generate Mermaid diagrams for architecture visualization.
- `_generate_module_dependency_diagram(self, output_path)` 🟡 (complexity: 7)
  > Generate module dependency diagram.
- `_generate_class_inheritance_diagram(self, output_path)` 🟡 (complexity: 9)
  > Generate class inheritance diagram.
- `_generate_integration_flow_diagram(self, output_path)` 🟡 (complexity: 6)
  > Generate integration flow diagram.
- `_generate_architecture_overview_diagram(self, output_path)` 🟢 (complexity: 2)
  > Generate high-level architecture overview.
- `main()` 🟢 (complexity: 3)
  > CLI entry point for architecture analysis.

**Dependencies:**
- src.aiagentsuite.core.architecture_analyzer
- src.aiagentsuite.core.chaos_engineering

### src.aiagentsuite.core.cache

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\cache.py`

**Classes:**
- `CacheEntry` (5 methods, 0 properties)
  > Represents a cache entry with metadata.
- `CacheStrategy` (1 methods, 0 properties)
  > Abstract base class for cache strategies.
  > Inherits: ABC
- `MemoryCache` (2 methods, 3 properties)
  > In-memory cache implementation.
  > Inherits: CacheStrategy
- `RedisCache` (2 methods, 8 properties)
  > Redis cache implementation.
  > Inherits: CacheStrategy
- `MultiLevelCache` (4 methods, 11 properties)
  > Multi-level caching with L1 (memory) and L2 (Redis) layers.
  > Inherits: CacheStrategy
- `CacheManager` (4 methods, 24 properties)
  > Central cache management system.

**Functions:**
- `__init__(self)` 🟢 (complexity: 1)
- `is_expired(self)` 🟢 (complexity: 2)
  > Check if entry is expired.
- `access(self)` 🟢 (complexity: 1)
  > Record access to this entry.
- `to_dict(self)` 🟢 (complexity: 1)
  > Convert to dictionary for serialization.
- `from_dict(cls, data)` 🟢 (complexity: 1)
  > Create from dictionary.
- `get_stats(self)` 🟢 (complexity: 2)
  > Get multi-level cache statistics.
- `set_read_through(self, enabled)` 🟢 (complexity: 1)
  > Enable/disable read-through caching.
- `set_write_through(self, enabled)` 🟢 (complexity: 1)
  > Enable/disable write-through caching.
- `get_cache(self, cache_type)` 🟢 (complexity: 1)
  > Get cache instance by type.
- `cached(self, cache_type, key_template, ttl)` 🟡 (complexity: 6)
  > Decorator for caching function results.
- `decorator(func)` 🟢 (complexity: 1)
- `get_global_cache_manager()` 🟢 (complexity: 2)
  > Get the global cache manager instance.
- `set_global_cache_manager(manager)` 🟢 (complexity: 1)
  > Set the global cache manager instance.
- `cached_framework(ttl)` 🟢 (complexity: 1)
  > Decorator for framework-related caching.
- `cached_protocol(ttl)` 🟢 (complexity: 1)
  > Decorator for protocol-related caching.
- `cached_memory(ttl)` 🟢 (complexity: 1)
  > Decorator for memory bank caching.
- `cached_conversation(ttl)` 🟢 (complexity: 1)
  > Decorator for conversation caching.

**Dependencies:**
- src.aiagentsuite.core.cache
- src.aiagentsuite.core.config
- src.aiagentsuite.core.errors
- src.aiagentsuite.core.observability

### src.aiagentsuite.core.chaos_engineering

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\chaos_engineering.py`

**Classes:**
- `ChaosEvent` (0 methods, 8 properties)
  > Types of chaos events that can be injected.
  > Inherits: Enum
- `ChaosIntensity` (0 methods, 5 properties)
  > Intensity levels for chaos experiments.
  > Inherits: Enum
- `ChaosConfiguration` (0 methods, 7 properties)
  > Configuration for chaos engineering experiments.
- `ChaosExperiment` (0 methods, 11 properties)
  > Represents a single chaos engineering experiment.
- `ChaosInjector` (2 methods, 0 properties)
  > Abstract base class for chaos injectors.
  > Inherits: ABC
- `DefaultChaosInjector` (1 methods, 4 properties)
  > Default implementation for chaos injection.
  > Inherits: ChaosInjector
- `ChaosEvaluator` (5 methods, 26 properties)
  > Evaluates system behavior during chaos experiments.
- `ChaosEngineeringManager` (6 methods, 25 properties)
  > Central manager for chaos engineering experiments.

**Functions:**
- `__init__(self)` 🟢 (complexity: 1)
- `is_experiment_active(self, experiment_id)` 🟢 (complexity: 1)
  > Check if experiment is active.
- `_calculate_averages(self, metrics_samples)` 🟢 (complexity: 4)
  > Calculate average metrics from samples.
- `_compare_with_baseline(self, metrics_samples)` 🟢 (complexity: 4)
  > Compare experiment metrics with baseline.
- `_calculate_stability_score(self, metrics_samples)` 🟢 (complexity: 2)
  > Calculate system stability score during experiment.
- `_calculate_variance(self, values)` 🟢 (complexity: 2)
  > Calculate variance of a list of values.
- `register_injector(self, injector)` 🟢 (complexity: 1)
  > Register a chaos injector for a service.
- `configure(self, config)` 🟢 (complexity: 1)
  > Update chaos configuration.
- `get_experiment_status(self, experiment_id)` 🟢 (complexity: 1)
  > Get status of a running experiment.
- `get_all_experiments(self)` 🟢 (complexity: 1)
  > Get all experiments.
- `generate_experiment_preset(self, preset_name)` 🟢 (complexity: 1)
  > Generate a pre-configured experiment.
- `get_global_chaos_manager()` 🟢 (complexity: 2)
  > Get the global chaos engineering manager instance.
- `set_global_chaos_manager(manager)` 🟢 (complexity: 1)
  > Set the global chaos engineering manager instance.
- `with_chaos_injection(chaos_type, probability)` 🟡 (complexity: 7)
  > Decorator to inject chaos into functions during experiments.
- `decorator(func)` 🟡 (complexity: 7)

**Dependencies:**
- src.aiagentsuite.core.chaos_engineering
- src.aiagentsuite.core.errors
- src.aiagentsuite.core.observability

### src.aiagentsuite.core.config

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\config.py`

**Classes:**
- `Environment` (0 methods, 5 properties)
  > Deployment environments.
  > Inherits: Enum
- `ConfigSource` (0 methods, 8 properties)
  > Configuration source types.
  > Inherits: Enum
- `ConfigurationChangeEvent` (0 methods, 6 properties)
  > Event representing a configuration change.
- `ConfigurationUpdateCallback` (0 methods, 0 properties)
  > Abstract base class for configuration update callbacks.
  > Inherits: ABC
- `AppSettings` (3 methods, 40 properties)
  > Core application settings with Pydantic validation.
  > Inherits: BaseSettings
- `ComponentConfiguration` (0 methods, 6 properties)
  > Configuration for individual components.
  > Inherits: BaseModel
- `Config` (0 methods, 1 properties)
- `ConfigurationSource` (2 methods, 2 properties)
  > Abstract base class for configuration sources.
  > Inherits: ABC
- `EnvironmentSource` (2 methods, 2 properties)
  > Configuration source from environment variables.
  > Inherits: ConfigurationSource
- `FileSource` (4 methods, 6 properties)
  > Configuration source from files.
  > Inherits: ConfigurationSource
- `CacheConfiguration` (1 methods, 0 properties)
  > Caching layer for configuration.
- `ConfigurationManager` (9 methods, 14 properties)
  > Central configuration management system.

**Functions:**
- `validate_environment(cls, v)` 🟢 (complexity: 3)
  > Validate environment value.
- `validate_log_level(cls, v)` 🟢 (complexity: 2)
  > Validate log level.
- `validate_environmental_dependencies(self)` 🟢 (complexity: 5)
  > Validate environment-specific dependencies.
- `__init__(self)` 🟢 (complexity: 1)
- `is_expired(self, ttl_seconds)` 🟢 (complexity: 2)
  > Check if configuration is expired.
- `_parse_value(self, value)` 🟢 (complexity: 4)
  > Parse string value.
- `_parse_content(self, content)` 🔴 (complexity: 11)
  > Parse file content based on format.
- `_serialize_content(self, config)` 🟡 (complexity: 8)
  > Serialize configuration to content.
- `add_source(self, source)` 🟢 (complexity: 1)
  > Add a configuration source.
- `remove_source(self, source_name)` 🟢 (complexity: 1)
  > Remove a configuration source.
- `add_change_callback(self, callback)` 🟢 (complexity: 1)
  > Add configuration change callback.
- `remove_change_callback(self, callback)` 🟢 (complexity: 1)
  > Remove configuration change callback.
- `add_validation_schema(self, key, schema)` 🟢 (complexity: 1)
  > Add validation schema for configuration key.
- `get_component_config(self, component_name)` 🟢 (complexity: 1)
  > Get component configuration.
- `set_component_config(self, component_name, config)` 🟢 (complexity: 1)
  > Set component configuration.
- `_get_version(self)` 🟢 (complexity: 3)
  > Get application version.
- `get_global_config_manager()` 🟢 (complexity: 2)
  > Get the global configuration manager instance.
- `set_global_config_manager(manager)` 🟢 (complexity: 1)
  > Set the global configuration manager instance.
- `require_config()` 🟢 (complexity: 3)
  > Decorator to require specific configuration keys.
- `decorator(func)` 🟢 (complexity: 4)
- `config_aware(param_name, default_value)` 🟢 (complexity: 4)
  > Decorator to inject configuration values as function parameters.

**Dependencies:**
- src.aiagentsuite.core.chaos_engineering
- src.aiagentsuite.core.config
- src.aiagentsuite.core.errors
- src.aiagentsuite.core.security

### src.aiagentsuite.core.errors

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py`

**Classes:**
- `AIAgentSuiteError` (4 methods, 0 properties)
  > Base exception for AI Agent Suite errors.
  > Inherits: Exception
- `FrameworkError` (0 methods, 0 properties)
  > Errors related to framework operations.
  > Inherits: AIAgentSuiteError
- `ProtocolError` (0 methods, 0 properties)
  > Errors related to protocol execution.
  > Inherits: AIAgentSuiteError
- `ValidationError` (0 methods, 0 properties)
  > Errors related to data validation.
  > Inherits: AIAgentSuiteError
- `SecurityError` (0 methods, 0 properties)
  > Errors related to security violations.
  > Inherits: AIAgentSuiteError
- `ConfigurationError` (0 methods, 0 properties)
  > Errors related to configuration issues.
  > Inherits: AIAgentSuiteError
- `ResourceError` (0 methods, 0 properties)
  > Errors related to resource exhaustion or unavailability.
  > Inherits: AIAgentSuiteError
- `CircuitBreakerState` (0 methods, 3 properties)
  > Circuit breaker states.
  > Inherits: Enum
- `CircuitBreakerConfig` (0 methods, 4 properties)
  > Configuration for circuit breaker.
- `CircuitBreakerStats` (0 methods, 7 properties)
  > Circuit breaker statistics.
- `CircuitBreaker` (2 methods, 1 properties)
  > Circuit breaker implementation.
- `ErrorHandler` (4 methods, 8 properties)
  > Central error handling and resilience manager.
- `ErrorBoundary` (3 methods, 0 properties)
  > Error boundary that catches and handles errors in async contexts.
- `Bulkhead` (2 methods, 0 properties)
  > Bulkhead pattern for limiting concurrent operations.

**Functions:**
- `__init__(self, max_concurrent, name)` 🟢 (complexity: 1)
- `_get_error_code(self)` 🟢 (complexity: 1)
  > Get error code from class name.
- `_get_component_name(self)` 🟢 (complexity: 1)
  > Get component name from class hierarchy.
- `to_dict(self)` 🟢 (complexity: 1)
  > Convert error to dictionary for logging/serialization.
- `get_stats(self)` 🟢 (complexity: 1)
  > Get bulkhead statistics.
- `register_circuit_breaker(self, name, config)` 🟢 (complexity: 1)
  > Register a circuit breaker.
- `register_error_handler(self, error_type, handler)` 🟢 (complexity: 1)
  > Register an error handler for specific error types.
- `register_recovery_strategy(self, operation_name, strategy)` 🟢 (complexity: 1)
  > Register a recovery strategy for specific operations.
- `with_resilience(error_handler, circuit_breaker, max_retries, backoff_factor, operation_name)` 🟡 (complexity: 7)
  > Decorator for adding resilience to functions.
- `decorator(func)` 🟡 (complexity: 7)
- `has_errors(self)` 🟢 (complexity: 1)
  > Check if any errors occurred.
- `get_errors(self)` 🟢 (complexity: 1)
  > Get all captured errors.
- `get_global_error_handler()` 🟢 (complexity: 2)
  > Get the global error handler instance.
- `set_global_error_handler(handler)` 🟢 (complexity: 1)
  > Set the global error handler instance.

**Dependencies:**
- src.aiagentsuite.core.errors
- src.aiagentsuite.memory_bank.manager

### src.aiagentsuite.core.event_sourcing

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py`

**Classes:**
- `EventType` (0 methods, 8 properties)
  > Types of domain events.
  > Inherits: Enum
- `DomainEvent` (1 methods, 8 properties)
  > Domain event representing business facts.
- `AggregateState` (0 methods, 6 properties)
  > Current state of an aggregate root.
- `EventStore` (0 methods, 0 properties)
  > Abstract event store interface.
  > Inherits: ABC
- `InMemoryEventStore` (1 methods, 2 properties)
  > In-memory event store implementation.
  > Inherits: EventStore
- `AggregateRoot` (6 methods, 2 properties)
  > Base class for aggregate roots in event sourcing.
  > Inherits: ABC
- `EventSourcedRepository` (1 methods, 3 properties)
  > Repository for event-sourced aggregates.
- `CommandHandler` (0 methods, 0 properties)
  > Handles commands and produces events.
  > Inherits: ABC
- `EventHandler` (0 methods, 0 properties)
  > Handles events for projections and side effects.
  > Inherits: ABC
- `CQRSReadModel` (0 methods, 0 properties)
  > Read model for CQRS pattern.
  > Inherits: ABC
- `EventBus` (1 methods, 3 properties)
  > In-memory event bus for event sourcing.
- `UserAggregate` (1 methods, 0 properties)
  > Example aggregate for users.
  > Inherits: AggregateRoot
- `UserReadModel` (1 methods, 1 properties)
  > Read model for users.
  > Inherits: CQRSReadModel
- `CreateUserCommand` (1 methods, 0 properties)
  > Command to create a user.
- `UpdateUserCommand` (1 methods, 0 properties)
  > Command to update a user.
- `UserCommandHandler` (1 methods, 3 properties)
  > Handles user commands.
  > Inherits: CommandHandler
- `UserEventHandler` (1 methods, 0 properties)
  > Handles user events for projections.
  > Inherits: EventHandler
- `EventSourcingManager` (2 methods, 14 properties)
  > Central manager for event sourcing architecture.

**Functions:**
- `event_name(self)` 🟢 (complexity: 1)
- `__init__(self, event_store)` 🟢 (complexity: 2)
- `apply_event(self, event)` 🟢 (complexity: 4)
  > Apply event to user aggregate.
- `raise_event(self, event_type, data, metadata)` 🟢 (complexity: 3)
  > Raise a new domain event.
- `get_uncommitted_events(self)` 🟢 (complexity: 1)
  > Get all uncommitted events.
- `commit_events(self)` 🟢 (complexity: 1)
  > Commit events and return them.
- `load_from_events(self, events)` 🟢 (complexity: 2)
  > Load aggregate state from historical events.
- `_setup_example_domain(self)` 🟢 (complexity: 2)
  > Set up the user domain example.
- `get_global_event_sourcing_manager()` 🟢 (complexity: 2)
  > Get the global event sourcing manager instance.
- `set_global_event_sourcing_manager(manager)` 🟢 (complexity: 1)
  > Set the global event sourcing manager instance.

**Dependencies:**
- src.aiagentsuite.core.event_sourcing

### src.aiagentsuite.core.formal_verification

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\formal_verification.py`

**Classes:**
- `VerificationResult` (0 methods, 5 properties)
  > Result of a verification check.
  > Inherits: Enum
- `PropertyType` (0 methods, 6 properties)
  > Types of properties to verify.
  > Inherits: Enum
- `VerificationProperty` (0 methods, 8 properties)
  > A property to be verified.
- `VerificationAttempt` (0 methods, 8 properties)
  > Result of a verification attempt.
- `VerificationModel` (0 methods, 7 properties)
  > Mathematical model of system behavior.
- `ModelChecker` (1 methods, 0 properties)
  > Abstract base class for model checking algorithms.
  > Inherits: ABC
- `BasicModelChecker` (1 methods, 22 properties)
  > Basic model checker implementation using state space exploration.
  > Inherits: ModelChecker
- `TheoremProver` (0 methods, 0 properties)
  > Abstract base class for theorem provers.
  > Inherits: ABC
- `BasicTheoremProver` (0 methods, 4 properties)
  > Basic theorem prover for simple mathematical proofs.
  > Inherits: TheoremProver
- `ContractVerifier` (0 methods, 11 properties)
  > Verify software contracts and interface obligations.
- `RuntimeVerifier` (2 methods, 11 properties)
  > Runtime verification and monitoring.
- `FormalVerificationManager` (6 methods, 19 properties)
  > Central manager for formal verification activities.

**Functions:**
- `supports_property_type(self, property_type)` 🟢 (complexity: 1)
  > Support basic safety and liveness properties.
- `__init__(self)` 🟢 (complexity: 1)
- `add_runtime_property(self, property, callback)` 🟢 (complexity: 2)
  > Add a property to verify at runtime.
- `add_property(self, property)` 🟢 (complexity: 1)
  > Add a verification property.
- `add_model(self, model)` 🟢 (complexity: 1)
  > Add a verification model.
- `add_model_checker(self, name, checker)` 🟢 (complexity: 1)
  > Add a model checker.
- `add_theorem_prover(self, prover)` 🟢 (complexity: 1)
  > Add a theorem prover.
- `create_security_model(self, system_name)` 🟢 (complexity: 1)
  > Create a basic security model for the system.
- `get_global_verification_manager()` 🟢 (complexity: 2)
  > Get the global formal verification manager instance.
- `set_global_verification_manager(manager)` 🟢 (complexity: 1)
  > Set the global formal verification manager instance.
- `verified_property(property_type, description)` 🟢 (complexity: 2)
  > Decorator to mark methods that have verified properties.
- `decorator(func)` 🟡 (complexity: 7)
- `enforces_contract(preconditions, postconditions, invariants)` 🟡 (complexity: 7)
  > Decorator to specify method contracts.

**Dependencies:**
- src.aiagentsuite.core.errors
- src.aiagentsuite.core.formal_verification
- src.aiagentsuite.core.observability
- src.aiagentsuite.core.security

### src.aiagentsuite.core.observability

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\observability.py`

**Classes:**
- `HealthStatus` (0 methods, 3 properties)
  > Health check status.
  > Inherits: Enum
- `HealthCheckResult` (1 methods, 6 properties)
  > Result of a health check.
- `SystemMetrics` (0 methods, 8 properties)
  > System performance metrics.
- `ApplicationMetrics` (0 methods, 8 properties)
  > Application-specific metrics.
- `HealthCheck` (1 methods, 0 properties)
  > Abstract base class for health checks.
  > Inherits: ABC
- `DatabaseHealthCheck` (1 methods, 3 properties)
  > Health check for database connectivity.
  > Inherits: HealthCheck
- `ExternalServiceHealthCheck` (1 methods, 4 properties)
  > Health check for external service availability.
  > Inherits: HealthCheck
- `ComponentHealthCheck` (1 methods, 4 properties)
  > Health check for internal components.
  > Inherits: HealthCheck
- `MetricsCollector` (8 methods, 9 properties)
  > Collects and exposes system and application metrics.
- `ApplicationInsights` (4 methods, 3 properties)
  > Application insights and business metrics.
- `TracingManager` (3 methods, 4 properties)
  > Distributed tracing manager.
- `StructuredLogger` (3 methods, 0 properties)
  > Enhanced structured logging.
- `SecurityMonitoring` (2 methods, 1 properties)
  > Security event monitoring and alerting.
- `ObservabilityManager` (6 methods, 17 properties)
  > Central observability manager coordinating all monitoring components.

**Functions:**
- `is_healthy(self)` 🟢 (complexity: 1)
  > Check if the result indicates a healthy state.
- `__init__(self)` 🟢 (complexity: 1)
- `collect_system_metrics(self)` 🟢 (complexity: 1)
  > Collect current system metrics.
- `collect_application_metrics(self)` 🟢 (complexity: 1)
  > Collect current application metrics.
- `record_request(self, method, endpoint, duration, status_code)` 🟢 (complexity: 2)
  > Record an HTTP request.
- `record_protocol_execution(self, protocol_name, status, duration)` 🟢 (complexity: 1)
  > Record a protocol execution.
- `record_framework_operation(self, operation, status)` 🟢 (complexity: 1)
  > Record a framework operation.
- `record_security_event(self, event_type, severity)` 🟢 (complexity: 1)
  > Record a security event.
- `get_prometheus_metrics(self)` 🟢 (complexity: 1)
  > Get metrics in Prometheus format.
- `record_protocol_usage(self, protocol_name, user_id)` 🟢 (complexity: 3)
  > Record protocol usage for insights.
- `get_popular_protocols(self, limit)` 🟢 (complexity: 1)
  > Get most popular protocols.
- `get_user_engagement(self)` 🟢 (complexity: 1)
  > Get user engagement metrics.
- `initialize(self, jaeger_endpoint)` 🟢 (complexity: 2)
  > Initialize distributed tracing.
- `get_tracer(self)` 🟢 (complexity: 2)
  > Get the current tracer.
- `setup_structlog(self, log_level)` 🟢 (complexity: 1)
  > Setup structured logging configuration.
- `get_logger(self, name)` 🟢 (complexity: 1)
  > Get a structured logger instance.
- `add_alert_callback(self, callback)` 🟢 (complexity: 1)
  > Add a callback for security alerts.
- `_get_sentry_dsn(self)` 🟢 (complexity: 1)
  > Get Sentry DSN from environment configuration.
- `_setup_default_health_checks(self)` 🟢 (complexity: 1)
  > Setup default health checks.
- `add_health_check(self, health_check)` 🟢 (complexity: 1)
  > Add a health check.
- `instrument_function(self, name)` 🟢 (complexity: 4)
  > Decorator to instrument functions with monitoring.
- `decorator(func)` 🟢 (complexity: 4)
- `get_global_observability_manager()` 🟢 (complexity: 2)
  > Get the global observability manager instance.
- `set_global_observability_manager(manager)` 🟢 (complexity: 1)
  > Set the global observability manager instance.

**Dependencies:**
- src.aiagentsuite.core.errors
- src.aiagentsuite.core.observability
- src.aiagentsuite.core.security

### src.aiagentsuite.core.security

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\security.py`

**Classes:**
- `SecurityLevel` (0 methods, 4 properties)
  > Security levels for operations.
  > Inherits: Enum
- `Permission` (0 methods, 15 properties)
  > System permissions.
  > Inherits: Enum
- `User` (0 methods, 9 properties)
  > User entity.
- `SecurityContext` (0 methods, 8 properties)
  > Security context for operations.
- `AuditEvent` (0 methods, 13 properties)
  > Audit event for logging.
- `EncryptionManager` (7 methods, 4 properties)
  > Manages encryption and decryption operations.
- `InputValidator` (6 methods, 6 properties)
  > Comprehensive input validation.
- `AuthorizationManager` (8 methods, 4 properties)
  > Manages permissions and authorization.
- `AuditLogger` (2 methods, 3 properties)
  > Comprehensive audit logging system.
- `RateLimiter` (4 methods, 2 properties)
  > Rate limiting for API endpoints and operations.
- `SecurityManager` (9 methods, 11 properties)
  > Central security manager coordinating all security components.

**Functions:**
- `__init__(self, memory_bank)` 🟢 (complexity: 1)
- `encrypt(self, data)` 🟢 (complexity: 3)
  > Encrypt data.
- `decrypt(self, encrypted_data)` 🟢 (complexity: 3)
  > Decrypt data.
- `hash_password(self, password)` 🟢 (complexity: 1)
  > Hash a password using bcrypt.
- `verify_password(self, password, hashed)` 🟢 (complexity: 1)
  > Verify a password against its hash.
- `generate_token(self, data, expires_in)` 🟢 (complexity: 1)
  > Generate a JWT token.
- `verify_token(self, token)` 🟢 (complexity: 3)
  > Verify and decode a JWT token.
- `validate_email(email)` 🟢 (complexity: 1)
  > Validate email format.
- `validate_username(username)` 🟢 (complexity: 1)
  > Validate username format.
- `sanitize_string(input_str, max_length)` 🟢 (complexity: 4)
  > Sanitize string input.
- `validate_protocol_name(name)` 🟢 (complexity: 4)
  > Validate protocol name.
- `validate_context_data(data, max_depth)` 🟡 (complexity: 10)
  > Recursively validate context data structures.
- `_validate_recursive(obj, depth)` 🟡 (complexity: 10)
- `assign_role_permissions(self, role, permissions)` 🟢 (complexity: 1)
  > Assign permissions to a role.
- `assign_user_permissions(self, user_id, permissions)` 🟢 (complexity: 1)
  > Assign direct permissions to a user.
- `check_permission(self, context, permission, resource)` 🟡 (complexity: 6)
  > Check if the context has the required permission.
- `require_permission(self, permission, resource)` 🟢 (complexity: 3)
  > Decorator to require a specific permission.
- `decorator(func)` 🟡 (complexity: 8)
- `create_resource_policy(self, resource_pattern, policy)` 🟢 (complexity: 1)
  > Create a resource access policy.
- `evaluate_resource_policy(self, resource, context)` 🟡 (complexity: 8)
  > Evaluate if access is allowed based on resource policies.
- `create_audit_event(self, event_type, resource, action, result, context, details, risk_score)` 🟢 (complexity: 3)
  > Create an audit event.
- `set_limit(self, key, max_requests, window_seconds)` 🟢 (complexity: 1)
  > Set rate limiting for a key.
- `is_allowed(self, key)` 🟢 (complexity: 4)
  > Check if request is allowed under rate limits.
- `get_remaining(self, key)` 🟢 (complexity: 3)
  > Get remaining requests for a key.
- `_setup_default_policies(self)` 🟢 (complexity: 1)
  > Setup default security policies.
- `_setup_rate_limits(self)` 🟢 (complexity: 1)
  > Setup default rate limits.
- `_determine_security_level(self, user)` 🟢 (complexity: 4)
  > Determine security level for a user.
- `_collect_user_permissions(self, user)` 🟢 (complexity: 2)
  > Collect all permissions for a user.
- `secure_operation(self, permission, security_level, audit_event)` 🟡 (complexity: 8)
  > Decorator for securing operations.
- `create_user(self, username, email, password, roles)` 🟢 (complexity: 5)
  > Create a new user with validation.
- `authenticate_user(self, username, password, stored_hash)` 🟢 (complexity: 1)
  > Authenticate a user.
- `get_global_security_manager()` 🟢 (complexity: 2)
  > Get the global security manager instance.
- `set_global_security_manager(manager)` 🟢 (complexity: 1)
  > Set the global security manager instance.

**Dependencies:**
- src.aiagentsuite.core.architecture_analyzer
- src.aiagentsuite.core.errors
- src.aiagentsuite.memory_bank.manager

### src.aiagentsuite.core.suite

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\suite.py`

**Classes:**
- `AIAgentSuite` (1 methods, 0 properties)
  > Main AI Agent Suite class providing unified access to all framework components.

**Functions:**
- `__init__(self, workspace_path)` 🟢 (complexity: 2)
  > Initialize the AI Agent Suite.

**Dependencies:**
- src.aiagentsuite.framework.manager
- src.aiagentsuite.memory_bank.manager
- src.aiagentsuite.protocols.executor

### src.aiagentsuite.framework.manager

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\framework\manager.py`

**Classes:**
- `FrameworkManager` (1 methods, 9 properties)
  > Manages framework components including constitution, principles, and project context.

**Functions:**
- `__init__(self, workspace_path)` 🟢 (complexity: 1)

### src.aiagentsuite.memory_bank.manager

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\memory_bank\manager.py`

**Classes:**
- `MemoryBank` (1 methods, 15 properties)
  > Manages persistent memory for context, decisions, and progress tracking.

**Functions:**
- `__init__(self, workspace_path)` 🟢 (complexity: 1)

### src.aiagentsuite.protocols.executor

**File:** `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\protocols\executor.py`

**Classes:**
- `ProtocolExecutionStatus` (0 methods, 5 properties)
  > Status of protocol execution.
  > Inherits: Enum
- `ProtocolPhaseStatus` (0 methods, 5 properties)
  > Status of individual protocol phases.
  > Inherits: Enum
- `ProtocolExecutionContext` (1 methods, 9 properties)
  > Context for protocol execution.
- `ProtocolPhase` (2 methods, 20 properties)
  > Represents a single protocol phase with execution capabilities.
- `ProtocolDSLInterpreter` (2 methods, 8 properties)
  > Interprets protocol DSL for advanced execution.
- `ProtocolExecutor` (6 methods, 34 properties)
  > Executes framework protocols and manages protocol lifecycle.

**Functions:**
- `duration(self)` 🟢 (complexity: 1)
  > Get execution duration in seconds.
- `__init__(self, workspace_path)` 🟢 (complexity: 1)
- `_parse_actions(self)` 🟡 (complexity: 8)
  > Parse executable actions from phase content.
- `_parse_dsl_commands(self, dsl_content)` 🟢 (complexity: 4)
  > Parse DSL commands from content.
- `_extract_protocol_name(self, filename)` 🟢 (complexity: 1)
  > Extract protocol name from filename.
- `_parse_protocol_phases(self, content)` 🟢 (complexity: 2)
  > Parse protocol phases from markdown content.
- `_extract_dsl_blocks(self, content)` 🟢 (complexity: 1)
  > Extract DSL blocks from protocol content.
- `_extract_metadata(self, content)` 🟢 (complexity: 4)
  > Extract metadata from protocol content.
- `_extract_protocol_description(self, content)` 🟢 (complexity: 5)
  > Extract protocol objective/description.

**Dependencies:**
- src.aiagentsuite.core.architecture_analyzer

## 🔗 Component Integrations

- **inheritance**: `src.aiagentsuite.core.cache.MemoryCache` → `src.aiagentsuite.core.cache.CacheStrategy`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\cache.py:122`
  - Context: MemoryCache extends CacheStrategy

- **inheritance**: `src.aiagentsuite.core.cache.RedisCache` → `src.aiagentsuite.core.cache.CacheStrategy`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\cache.py:197`
  - Context: RedisCache extends CacheStrategy

- **inheritance**: `src.aiagentsuite.core.cache.MultiLevelCache` → `src.aiagentsuite.core.cache.CacheStrategy`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\cache.py:322`
  - Context: MultiLevelCache extends CacheStrategy

- **inheritance**: `src.aiagentsuite.core.chaos_engineering.DefaultChaosInjector` → `src.aiagentsuite.core.chaos_engineering.ChaosInjector`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\chaos_engineering.py:108`
  - Context: DefaultChaosInjector extends ChaosInjector

- **inheritance**: `src.aiagentsuite.core.config.EnvironmentSource` → `src.aiagentsuite.core.config.ConfigurationSource`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\config.py:234`
  - Context: EnvironmentSource extends ConfigurationSource

- **inheritance**: `src.aiagentsuite.core.config.FileSource` → `src.aiagentsuite.core.config.ConfigurationSource`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\config.py:276`
  - Context: FileSource extends ConfigurationSource

- **inheritance**: `src.aiagentsuite.core.errors.FrameworkError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:58`
  - Context: FrameworkError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.errors.ProtocolError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:63`
  - Context: ProtocolError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.errors.ValidationError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:68`
  - Context: ValidationError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.errors.SecurityError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:73`
  - Context: SecurityError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.errors.ConfigurationError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:78`
  - Context: ConfigurationError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.errors.ResourceError` → `src.aiagentsuite.core.errors.AIAgentSuiteError`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\errors.py:83`
  - Context: ResourceError extends AIAgentSuiteError

- **inheritance**: `src.aiagentsuite.core.event_sourcing.InMemoryEventStore` → `src.aiagentsuite.core.event_sourcing.EventStore`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py:81`
  - Context: InMemoryEventStore extends EventStore

- **inheritance**: `src.aiagentsuite.core.event_sourcing.UserAggregate` → `src.aiagentsuite.core.event_sourcing.AggregateRoot`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py:260`
  - Context: UserAggregate extends AggregateRoot

- **inheritance**: `src.aiagentsuite.core.event_sourcing.UserReadModel` → `src.aiagentsuite.core.event_sourcing.CQRSReadModel`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py:281`
  - Context: UserReadModel extends CQRSReadModel

- **inheritance**: `src.aiagentsuite.core.event_sourcing.UserCommandHandler` → `src.aiagentsuite.core.event_sourcing.CommandHandler`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py:335`
  - Context: UserCommandHandler extends CommandHandler

- **inheritance**: `src.aiagentsuite.core.event_sourcing.UserEventHandler` → `src.aiagentsuite.core.event_sourcing.EventHandler`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\event_sourcing.py:380`
  - Context: UserEventHandler extends EventHandler

- **inheritance**: `src.aiagentsuite.core.formal_verification.BasicModelChecker` → `src.aiagentsuite.core.formal_verification.ModelChecker`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\formal_verification.py:101`
  - Context: BasicModelChecker extends ModelChecker

- **inheritance**: `src.aiagentsuite.core.formal_verification.BasicTheoremProver` → `src.aiagentsuite.core.formal_verification.TheoremProver`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\formal_verification.py:303`
  - Context: BasicTheoremProver extends TheoremProver

- **inheritance**: `src.aiagentsuite.core.observability.DatabaseHealthCheck` → `src.aiagentsuite.core.observability.HealthCheck`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\observability.py:100`
  - Context: DatabaseHealthCheck extends HealthCheck

- **inheritance**: `src.aiagentsuite.core.observability.ExternalServiceHealthCheck` → `src.aiagentsuite.core.observability.HealthCheck`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\observability.py:144`
  - Context: ExternalServiceHealthCheck extends HealthCheck

- **inheritance**: `src.aiagentsuite.core.observability.ComponentHealthCheck` → `src.aiagentsuite.core.observability.HealthCheck`
  - File: `C:\Users\jimmy\.cursor\.aiagentsuite\src\aiagentsuite\core\observability.py:193`
  - Context: ComponentHealthCheck extends HealthCheck

