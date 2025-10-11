# 🚀 AI Agent Suite - LLM Bootstrap Installation Guide

## Quick Start (Copy-Paste for LLM)

**For team members:** Simply copy and paste this entire section to an LLM to set up the AI Agent Suite framework.

```
I need help installing and setting up the AI Agent Suite framework. Please follow these steps:

1. Clone the repository:
   git clone <repository-url>
   cd aiagentsuite

2. Create a virtual environment:
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate

3. Install dependencies:
   pip install -e .

4. Verify installation:
   python -c "from src.aiagentsuite import __version__; print(f'AI Agent Suite v{__version__} installed successfully!')"

5. Run comprehensive tests to verify everything works:
   python -m pytest tests/test_comprehensive.py -v

6. Initialize the framework for your project:
   python -c "
   import asyncio
   from src.aiagentsuite.core import initialize_framework
   
   async def setup():
       print('🔧 Initializing AI Agent Suite...')
       await initialize_framework()
       print('✅ Framework initialized successfully!')
       print('📖 See README.md for usage examples')
   
   asyncio.run(setup())
   "

The framework is now ready to use!
```

## What You Get

The AI Agent Suite provides enterprise-grade components:

### 🏗️ Core Enterprise Patterns
- **Event Sourcing & CQRS** - Domain-driven design with complete audit trails
- **Chaos Engineering** - Systematic resilience testing and failure injection
- **Formal Verification** - Mathematical proofs and property verification
- **Protocol Execution** - ContextGuard security protocols and DSL

### 🔐 Security & Observability
- **Multi-layered Security** - Encryption, authorization, audit logging
- **Comprehensive Monitoring** - System metrics, application metrics, tracing
- **Configuration Management** - Hot-reload, environment-specific settings
- **Intelligent Caching** - Multi-tier caching with Redis support

### 🤖 AI Integration
- **LSP Server** - Language Server Protocol for IDE integration
- **MCP Server** - Model Context Protocol for AI tools
- **Framework Manager** - AI coding principles and best practices
- **Memory Bank** - Context-aware development assistance

## Quick Usage Examples

### Event Sourcing (CQRS Pattern)

```python
import asyncio
from src.aiagentsuite.core.event_sourcing import (
    get_global_event_sourcing_manager,
    CreateUserCommand,
    UpdateUserCommand
)

async def demo_event_sourcing():
    # Get the event sourcing manager
    manager = get_global_event_sourcing_manager()
    
    # Create a user (command)
    create_cmd = CreateUserCommand(
        user_id="user123",
        name="John Doe",
        email="john@example.com",
        role="developer"
    )
    user_id = await manager.execute_command(create_cmd)
    
    # Query the read model
    user = await manager.query_read_model("users", {"user_id": user_id})
    print(f"User created: {user}")
    
    # Update user
    update_cmd = UpdateUserCommand(
        user_id="user123",
        updates={"email": "john.doe@example.com"}
    )
    await manager.execute_command(update_cmd)
    
    # Get complete event history
    events = await manager.get_event_history("user123")
    print(f"Event history: {len(events)} events")

asyncio.run(demo_event_sourcing())
```

### Chaos Engineering

```python
import asyncio
from src.aiagentsuite.core.chaos_engineering import (
    get_global_chaos_manager,
    ChaosExperiment,
    ChaosEvent,
    ChaosIntensity,
    ChaosConfiguration
)

async def demo_chaos():
    # Initialize chaos manager
    chaos = get_global_chaos_manager()
    await chaos.initialize()
    
    # Configure chaos engineering
    config = ChaosConfiguration(
        enabled=True,
        intensity=ChaosIntensity.MEDIUM,
        safe_mode=True  # Emergency stop enabled
    )
    chaos.configure(config)
    
    # Create experiment
    experiment = ChaosExperiment(
        name="Latency Test",
        description="Test system resilience under latency",
        events=[ChaosEvent.LATENCY_INJECTION],
        intensity=ChaosIntensity.LOW,
        duration=30  # 30 seconds
    )
    
    # Run experiment
    result = await chaos.run_experiment(experiment)
    print(f"Experiment status: {result.status}")
    print(f"Stability score: {result.results.get('stability_score', 'N/A')}")

asyncio.run(demo_chaos())
```

### Formal Verification

```python
import asyncio
from src.aiagentsuite.core.formal_verification import (
    get_global_verification_manager,
    VerificationProperty,
    PropertyType
)

async def demo_verification():
    # Get verification manager
    verifier = get_global_verification_manager()
    await verifier.initialize()
    
    # Define security property
    property = VerificationProperty(
        property_id="auth_security",
        name="Authentication Security",
        description="Verify authentication always requires valid credentials",
        property_type=PropertyType.SECURITY,
        expression="auth_requires_credentials"
    )
    
    # Verify property
    result = await verifier.verify_property(property)
    print(f"Verification result: {result.result}")
    print(f"Confidence: {result.confidence_score}")
    
    # Get verification stats
    stats = await verifier.get_verification_status()
    print(f"Total verifications: {stats['total_verifications']}")

asyncio.run(demo_verification())
```

### Protocol Execution

```python
import asyncio
from pathlib import Path
from src.aiagentsuite.protocols.executor import ProtocolExecutor

async def demo_protocols():
    # Initialize protocol executor
    workspace = Path.cwd()
    executor = ProtocolExecutor(workspace)
    await executor.initialize()
    
    # List available protocols
    protocols = await executor.list_protocols()
    print(f"Available protocols: {list(protocols.keys())}")
    
    # Execute a protocol
    context = {
        "security_level": "high",
        "audit_mode": True
    }
    
    result = await executor.execute_protocol(
        "Secure Code Implementation",
        context
    )
    print(f"Protocol completed in {result['duration']:.2f}s")
    print(f"Phases completed: {result['phases_completed']}")

asyncio.run(demo_protocols())
```

## Advanced Features

### Security Management

```python
from src.aiagentsuite.core.security import (
    get_global_security_manager,
    SecurityLevel
)

# Set security level
security = get_global_security_manager()
await security.set_security_level(SecurityLevel.CRITICAL)

# Current level
print(f"Security level: {security.current_security_level}")
```

### Observability & Monitoring

```python
from src.aiagentsuite.core.observability import get_global_observability_manager

# Initialize monitoring
obs = get_global_observability_manager()
await obs.initialize()

# Collect metrics
system_metrics = await obs.metrics.collect_system_metrics()
app_metrics = await obs.metrics.collect_application_metrics()

print(f"CPU: {system_metrics.cpu_percent}%")
print(f"Memory: {system_metrics.memory_percent}%")
print(f"Error rate: {app_metrics.error_rate}")
```

### Configuration Management

```python
from src.aiagentsuite.core.config import get_global_config_manager

# Get configuration
config = get_global_config_manager()
await config.initialize()

# Reload configuration (hot-reload)
await config.reload_configuration()

# Get settings
print(f"Environment: {config.settings.environment}")
print(f"Debug mode: {config.settings.debug}")
```

### Caching

```python
from src.aiagentsuite.core.cache import get_global_cache_manager

# Initialize cache
cache = get_global_cache_manager()
await cache.initialize()

# Cache operations
await cache.cache.set("key", {"data": "value"}, ttl=300)
value = await cache.cache.get("key")
exists = await cache.cache.exists("key")
await cache.cache.delete("key")
```

## Testing Your Integration

Run the comprehensive test suite to verify everything works:

```bash
# Run all tests
python -m pytest tests/test_comprehensive.py -v

# Run specific test categories
python -m pytest tests/test_comprehensive.py::TestComprehensiveSuite -v
python -m pytest tests/test_comprehensive.py::TestContractVerification -v
python -m pytest tests/test_comprehensive.py::TestE2EWorkflows -v

# Run with coverage
python -m pytest tests/ --cov=src/aiagentsuite --cov-report=html
```

## Architecture Overview

```
AI Agent Suite
├── Core Components
│   ├── Event Sourcing (CQRS)
│   ├── Chaos Engineering
│   ├── Formal Verification
│   ├── Security Manager
│   ├── Observability
│   ├── Configuration
│   ├── Cache Manager
│   └── Error Handler
├── Protocol Engine
│   └── ContextGuard Protocols
├── AI Integration
│   ├── LSP Server
│   ├── MCP Server
│   └── Framework Manager
└── Memory Bank
    ├── Context Management
    ├── Decision Logging
    └── Progress Tracking
```

## 20 Software Engineering Principles

This framework implements 20 advanced software engineering principles:

1. **Event Sourcing** - Immutable event streams
2. **CQRS** - Command Query Responsibility Segregation
3. **Domain-Driven Design** - Aggregates, entities, value objects
4. **Chaos Engineering** - Systematic failure testing
5. **Formal Verification** - Mathematical correctness proofs
6. **Security by Design** - Multi-layered security architecture
7. **Observability** - Comprehensive monitoring and metrics
8. **Configuration as Code** - Dynamic configuration management
9. **Caching Strategies** - Multi-tier intelligent caching
10. **Protocol-Driven Development** - Executable specifications
11. **Contract Testing** - Interface verification
12. **Error Handling** - Comprehensive error management
13. **Async/Await Patterns** - Modern asynchronous programming
14. **Dependency Injection** - Loose coupling architecture
15. **Factory Patterns** - Object creation abstraction
16. **Repository Pattern** - Data access abstraction
17. **Strategy Pattern** - Algorithm selection
18. **Observer Pattern** - Event notification
19. **Decorator Pattern** - Behavior extension
20. **Singleton Pattern** - Global state management

## Troubleshooting

### Import Errors

If you get import errors, ensure you installed in editable mode:
```bash
pip install -e .
```

### Test Failures

If tests fail, check that all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Performance Issues

For production deployments, ensure Redis is configured for caching:
```python
# In your config
REDIS_URL = "redis://localhost:6379"
ENABLE_CACHE = True
```

## Support & Documentation

- **Full Documentation**: See `README.md` in the repository root
- **Architecture Docs**: Check `docs/ARCHITECTURE.md`
- **API Reference**: Generated from docstrings
- **Contributing**: See `Contributing to the .aiagentsuite Framework.md`

## License

See LICENSE file in the repository.

---

**Ready to build enterprise-grade AI applications!** 🚀

For questions or issues, consult the main README or contact the development team.
