# Class Inheritance

```mermaid
graph TD
    src_aiagentsuite_core_architecture_analyzer_ClassInfo("ClassInfo<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_FunctionInfo("FunctionInfo<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_ModuleInfo("ModuleInfo<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_IntegrationInfo("IntegrationInfo<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_ASTVisitor("ASTVisitor<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_ComplexityVisitor("ComplexityVisitor<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_architecture_analyzer_ArchitectureAnalyzer("ArchitectureAnalyzer<br/><small>src.aiagentsuite.core.architecture_analyzer</small>")
    src_aiagentsuite_core_cache_CacheEntry("CacheEntry<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_cache_CacheStrategy("CacheStrategy<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_cache_MemoryCache("MemoryCache<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_cache_RedisCache("RedisCache<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_cache_MultiLevelCache("MultiLevelCache<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_cache_CacheManager("CacheManager<br/><small>src.aiagentsuite.core.cache</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosEvent("ChaosEvent<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosIntensity("ChaosIntensity<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosConfiguration("ChaosConfiguration<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosExperiment("ChaosExperiment<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosInjector("ChaosInjector<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_DefaultChaosInjector("DefaultChaosInjector<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosEvaluator("ChaosEvaluator<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_chaos_engineering_ChaosEngineeringManager("ChaosEngineeringManager<br/><small>src.aiagentsuite.core.chaos_engineering</small>")
    src_aiagentsuite_core_config_Environment("Environment<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ConfigSource("ConfigSource<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ConfigurationChangeEvent("ConfigurationChangeEvent<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ConfigurationUpdateCallback("ConfigurationUpdateCallback<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_AppSettings("AppSettings<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ComponentConfiguration("ComponentConfiguration<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_Config("Config<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ConfigurationSource("ConfigurationSource<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_EnvironmentSource("EnvironmentSource<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_FileSource("FileSource<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_CacheConfiguration("CacheConfiguration<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_config_ConfigurationManager("ConfigurationManager<br/><small>src.aiagentsuite.core.config</small>")
    src_aiagentsuite_core_errors_AIAgentSuiteError("AIAgentSuiteError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_FrameworkError("FrameworkError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ProtocolError("ProtocolError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ValidationError("ValidationError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_SecurityError("SecurityError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ConfigurationError("ConfigurationError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ResourceError("ResourceError<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_CircuitBreakerState("CircuitBreakerState<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_CircuitBreakerConfig("CircuitBreakerConfig<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_CircuitBreakerStats("CircuitBreakerStats<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_CircuitBreaker("CircuitBreaker<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ErrorHandler("ErrorHandler<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_ErrorBoundary("ErrorBoundary<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_errors_Bulkhead("Bulkhead<br/><small>src.aiagentsuite.core.errors</small>")
    src_aiagentsuite_core_event_sourcing_EventType("EventType<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_DomainEvent("DomainEvent<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_AggregateState("AggregateState<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_EventStore("EventStore<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_InMemoryEventStore("InMemoryEventStore<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_AggregateRoot("AggregateRoot<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_EventSourcedRepository("EventSourcedRepository<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_CommandHandler("CommandHandler<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_EventHandler("EventHandler<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_CQRSReadModel("CQRSReadModel<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_EventBus("EventBus<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_UserAggregate("UserAggregate<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_UserReadModel("UserReadModel<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_CreateUserCommand("CreateUserCommand<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_UpdateUserCommand("UpdateUserCommand<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_UserCommandHandler("UserCommandHandler<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_UserEventHandler("UserEventHandler<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_event_sourcing_EventSourcingManager("EventSourcingManager<br/><small>src.aiagentsuite.core.event_sourcing</small>")
    src_aiagentsuite_core_formal_verification_VerificationResult("VerificationResult<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_PropertyType("PropertyType<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_VerificationProperty("VerificationProperty<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_VerificationAttempt("VerificationAttempt<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_VerificationModel("VerificationModel<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_ModelChecker("ModelChecker<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_BasicModelChecker("BasicModelChecker<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_TheoremProver("TheoremProver<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_BasicTheoremProver("BasicTheoremProver<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_ContractVerifier("ContractVerifier<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_RuntimeVerifier("RuntimeVerifier<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_formal_verification_FormalVerificationManager("FormalVerificationManager<br/><small>src.aiagentsuite.core.formal_verification</small>")
    src_aiagentsuite_core_observability_HealthStatus("HealthStatus<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_HealthCheckResult("HealthCheckResult<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_SystemMetrics("SystemMetrics<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_ApplicationMetrics("ApplicationMetrics<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_HealthCheck("HealthCheck<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_DatabaseHealthCheck("DatabaseHealthCheck<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_ExternalServiceHealthCheck("ExternalServiceHealthCheck<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_ComponentHealthCheck("ComponentHealthCheck<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_MetricsCollector("MetricsCollector<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_ApplicationInsights("ApplicationInsights<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_TracingManager("TracingManager<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_StructuredLogger("StructuredLogger<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_SecurityMonitoring("SecurityMonitoring<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_observability_ObservabilityManager("ObservabilityManager<br/><small>src.aiagentsuite.core.observability</small>")
    src_aiagentsuite_core_security_SecurityLevel("SecurityLevel<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_Permission("Permission<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_User("User<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_SecurityContext("SecurityContext<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_AuditEvent("AuditEvent<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_EncryptionManager("EncryptionManager<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_InputValidator("InputValidator<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_AuthorizationManager("AuthorizationManager<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_AuditLogger("AuditLogger<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_RateLimiter("RateLimiter<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_security_SecurityManager("SecurityManager<br/><small>src.aiagentsuite.core.security</small>")
    src_aiagentsuite_core_suite_AIAgentSuite("AIAgentSuite<br/><small>src.aiagentsuite.core.suite</small>")
    src_aiagentsuite_framework_manager_FrameworkManager("FrameworkManager<br/><small>src.aiagentsuite.framework.manager</small>")
    src_aiagentsuite_memory_bank_manager_MemoryBank("MemoryBank<br/><small>src.aiagentsuite.memory_bank.manager</small>")
    src_aiagentsuite_protocols_executor_ProtocolExecutionStatus("ProtocolExecutionStatus<br/><small>src.aiagentsuite.protocols.executor</small>")
    src_aiagentsuite_protocols_executor_ProtocolPhaseStatus("ProtocolPhaseStatus<br/><small>src.aiagentsuite.protocols.executor</small>")
    src_aiagentsuite_protocols_executor_ProtocolExecutionContext("ProtocolExecutionContext<br/><small>src.aiagentsuite.protocols.executor</small>")
    src_aiagentsuite_protocols_executor_ProtocolPhase("ProtocolPhase<br/><small>src.aiagentsuite.protocols.executor</small>")
    src_aiagentsuite_protocols_executor_ProtocolDSLInterpreter("ProtocolDSLInterpreter<br/><small>src.aiagentsuite.protocols.executor</small>")
    src_aiagentsuite_protocols_executor_ProtocolExecutor("ProtocolExecutor<br/><small>src.aiagentsuite.protocols.executor</small>")

    src_aiagentsuite_core_cache_MemoryCache --> src_aiagentsuite_core_cache_CacheStrategy
    src_aiagentsuite_core_cache_RedisCache --> src_aiagentsuite_core_cache_CacheStrategy
    src_aiagentsuite_core_cache_MultiLevelCache --> src_aiagentsuite_core_cache_CacheStrategy
    src_aiagentsuite_core_chaos_engineering_DefaultChaosInjector --> src_aiagentsuite_core_chaos_engineering_ChaosInjector
    src_aiagentsuite_core_config_EnvironmentSource --> src_aiagentsuite_core_config_ConfigurationSource
    src_aiagentsuite_core_config_FileSource --> src_aiagentsuite_core_config_ConfigurationSource
    src_aiagentsuite_core_errors_FrameworkError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_errors_ProtocolError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_errors_ValidationError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_errors_SecurityError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_errors_ConfigurationError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_errors_ResourceError --> src_aiagentsuite_core_errors_AIAgentSuiteError
    src_aiagentsuite_core_event_sourcing_InMemoryEventStore --> src_aiagentsuite_core_event_sourcing_EventStore
    src_aiagentsuite_core_event_sourcing_UserAggregate --> src_aiagentsuite_core_event_sourcing_AggregateRoot
    src_aiagentsuite_core_event_sourcing_UserReadModel --> src_aiagentsuite_core_event_sourcing_CQRSReadModel
    src_aiagentsuite_core_event_sourcing_UserCommandHandler --> src_aiagentsuite_core_event_sourcing_CommandHandler
    src_aiagentsuite_core_event_sourcing_UserEventHandler --> src_aiagentsuite_core_event_sourcing_EventHandler
    src_aiagentsuite_core_formal_verification_BasicModelChecker --> src_aiagentsuite_core_formal_verification_ModelChecker
    src_aiagentsuite_core_formal_verification_BasicTheoremProver --> src_aiagentsuite_core_formal_verification_TheoremProver
    src_aiagentsuite_core_observability_DatabaseHealthCheck --> src_aiagentsuite_core_observability_HealthCheck
    src_aiagentsuite_core_observability_ExternalServiceHealthCheck --> src_aiagentsuite_core_observability_HealthCheck
    src_aiagentsuite_core_observability_ComponentHealthCheck --> src_aiagentsuite_core_observability_HealthCheck
```
