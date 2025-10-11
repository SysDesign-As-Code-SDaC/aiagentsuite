"""
AI Agent Suite Configuration Management

Provides comprehensive configuration management including environment handling,
settings validation, dynamic configuration, and configuration sources.
"""

import os
import json
import yaml
import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Type, TypeVar
from functools import wraps
import logging

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import aiocache
from aiocache import Cache

from .errors import ConfigurationError, ValidationError, get_global_error_handler
from .security import get_global_security_manager, SecurityLevel

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Environment(Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class ConfigSource(Enum):
    """Configuration source types."""
    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    KUBERNETES = "kubernetes"
    AWS_SECRETS = "aws_secrets"
    AZURE_KEYVAULT = "azure_keyvault"
    CONSUL = "consul"
    ETCD = "etcd"


@dataclass
class ConfigurationChangeEvent:
    """Event representing a configuration change."""
    key: str
    old_value: Any
    new_value: Any
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    user: Optional[str] = None


class ConfigurationUpdateCallback(ABC):
    """Abstract base class for configuration update callbacks."""

    @abstractmethod
    async def on_configuration_change(self, event: ConfigurationChangeEvent) -> None:
        """Called when configuration changes."""
        pass


class AppSettings(BaseSettings):
    """Core application settings with Pydantic validation."""

    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Security
    secret_key: str = Field(default_factory=lambda: os.urandom(32).hex())
    jwt_secret_key: str = Field(default_factory=lambda: os.urandom(32).hex())
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)
    bcrypt_rounds: int = Field(default=12)

    # Database
    database_url: Optional[str] = Field(default=None)
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)
    database_pool_timeout: float = Field(default=30.0)

    # Redis/Caching
    redis_url: Optional[str] = Field(default=None)
    cache_ttl: int = Field(default=3600)  # 1 hour
    enable_cache: bool = Field(default=True)

    # External Services
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    sentry_dsn: Optional[str] = Field(default=None)
    jaeger_endpoint: Optional[str] = Field(default=None)

    # Framework
    framework_data_path: str = Field(default="./framework/data")
    protocols_path: str = Field(default="./protocols")
    memory_bank_path: str = Field(default="./memory-bank")

    # Security
    enable_rate_limiting: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)
    enable_audit_logging: bool = Field(default=True)
    audit_log_retention_days: int = Field(default=90)

    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    health_check_interval: int = Field(default=30)

    # Resiliency
    circuit_breaker_failure_threshold: int = Field(default=5)
    circuit_breaker_timeout: float = Field(default=60.0)
    retry_max_attempts: int = Field(default=3)
    retry_backoff_factor: float = Field(default=1.0)

    # Observability
    enable_structured_logging: bool = Field(default=True)
    enable_tracing: bool = Field(default=True)
    trace_sample_rate: float = Field(default=1.0)

    model_config = SettingsConfigDict(
        env_prefix="AAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True
    )

    @field_validator('environment', mode='before')
    @classmethod
    def validate_environment(cls, v: Any) -> Environment:
        """Validate environment value."""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f"Invalid environment: {v}")
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()

    @model_validator(mode='after')
    def validate_environmental_dependencies(self) -> 'AppSettings':
        """Validate environment-specific dependencies."""
        env = self.environment

        if env == Environment.PRODUCTION:
            # Production requires certain settings
            if not self.database_url:
                raise ValueError("Database URL required in production")
            if not self.redis_url:
                logger.warning("Redis URL not set in production - using in-memory cache")
            if not self.secret_key:
                raise ValueError("Secret key required in production")

        return self


class ComponentConfiguration(BaseModel):
    """Configuration for individual components."""

    name: str
    enabled: bool = Field(default=True)
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    health_check_enabled: bool = Field(default=True)
    monitoring_enabled: bool = Field(default=True)

    class Config:
        arbitrary_types_allowed = True


class ConfigurationSource(ABC):
    """Abstract base class for configuration sources."""

    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority
        self._last_load = None
        self._cache: Dict[str, Any] = {}
        self.enabled = True

    @abstractmethod
    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from this source."""
        pass

    @abstractmethod
    async def save_configuration(self, key: str, value: Any) -> bool:
        """Save configuration to this source."""
        pass

    async def get_value(self, key: str) -> Optional[Any]:
        """Get a configuration value."""
        config = await self.load_configuration()
        return config.get(key)

    async def set_value(self, key: str, value: Any) -> bool:
        """Set a configuration value."""
        success = await self.save_configuration(key, value)
        if success:
            self._cache[key] = value
        return success

    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """Check if configuration is expired."""
        if not self._last_load:
            return True
        return (datetime.now() - self._last_load).total_seconds() > ttl_seconds


class EnvironmentSource(ConfigurationSource):
    """Configuration source from environment variables."""

    def __init__(self, prefix: str = "AAI_"):
        super().__init__("environment", priority=10)
        self.prefix = prefix

    async def load_configuration(self) -> Dict[str, Any]:
        """Load environment variable configuration."""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower()
                config[config_key] = self._parse_value(value)
        return config

    async def save_configuration(self, key: str, value: Any) -> bool:
        """Environment variables cannot be saved."""
        return False

    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value


class FileSource(ConfigurationSource):
    """Configuration source from files."""

    def __init__(self, path: Union[str, Path], format_type: str = "auto"):
        super().__init__(f"file:{Path(path).name}", priority=20)
        self.path = Path(path)
        self.format_type = format_type

    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.path.exists():
            return {}

        content = await self._read_file()
        return self._parse_content(content)

    async def save_configuration(self, key: str, value: Any) -> bool:
        """Save configuration to file."""
        try:
            config = await self.load_configuration()
            config[key] = value
            content = self._serialize_content(config)
            await self._write_file(content)
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.path}: {e}")
            return False

    async def _read_file(self) -> str:
        """Read file content."""
        import aiofiles
        async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
            return await f.read()

    async def _write_file(self, content: str) -> None:
        """Write content to file."""
        import aiofiles
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
            await f.write(content)

    def _parse_content(self, content: str) -> Dict[str, Any]:
        """Parse file content based on format."""
        if self.format_type == "json" or (self.format_type == "auto" and self.path.suffix == ".json"):
            return json.loads(content)
        elif self.format_type == "yaml" or (self.format_type == "auto" and self.path.suffix in (".yaml", ".yml")):
            return yaml.safe_load(content)
        else:
            # Simple key-value format
            config = {}
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = self._parse_value(value.strip())
            return config

    def _serialize_content(self, config: Dict[str, Any]) -> str:
        """Serialize configuration to content."""
        if self.format_type == "json" or (self.format_type == "auto" and self.path.suffix == ".json"):
            return json.dumps(config, indent=2, default=str)
        elif self.format_type == "yaml" or (self.format_type == "auto" and self.path.suffix in (".yaml", ".yml")):
            return yaml.dump(config, default_flow_style=False)
        else:
            # Simple key-value format
            lines = []
            for key, value in config.items():
                lines.append(f"{key}={value}")
            return "\n".join(lines)

    def _parse_value(self, value: str) -> Any:
        """Parse string value."""
        # Same logic as EnvironmentSource
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value


class CacheConfiguration:
    """Caching layer for configuration."""

    def __init__(self, cache: Optional[Cache] = None):
        self.cache = cache or Cache(Cache.MEMORY)

    async def get(self, key: str) -> Optional[Any]:
        """Get cached configuration value."""
        return await self.cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached configuration value."""
        await self.cache.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        """Delete cached configuration value."""
        await self.cache.delete(key)

    async def clear(self) -> None:
        """Clear all cached configuration."""
        await self.cache.clear()


class ConfigurationManager:
    """Central configuration management system."""

    def __init__(self) -> None:
        self.sources: List[ConfigurationSource] = []
        self.cache = CacheConfiguration()
        self.settings = AppSettings()
        self.component_configs: Dict[str, ComponentConfiguration] = {}
        self.change_callbacks: Dict[int, ConfigurationUpdateCallback] = {}
        self.validation_schemas: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self._config_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize configuration manager."""
        if self._initialized:
            return

        # Setup default configuration sources
        await self._setup_default_sources()

        # Load initial configuration
        await self._load_initial_configuration()

        # Validate configuration
        await self._validate_configuration()

        self._initialized = True
        logger.info("Configuration manager initialized")

    async def _setup_default_sources(self) -> None:
        """Setup default configuration sources."""
        # Environment variables (highest priority)
        self.add_source(EnvironmentSource())

        # Configuration file
        config_file = Path(".env")
        if config_file.exists():
            self.add_source(FileSource(config_file))

        # Local development overrides
        dev_config = Path("config.local.yaml")
        if dev_config.exists():
            self.add_source(FileSource(dev_config))

    async def _load_initial_configuration(self) -> None:
        """Load initial configuration from all sources."""
        config_data = await self._merge_configuration_sources()

        # Update settings
        try:
            self.settings = AppSettings(**config_data)
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

        # Load component configurations
        await self._load_component_configurations()

    async def _merge_configuration_sources(self) -> Dict[str, Any]:
        """Merge configuration from all sources by priority."""
        merged_config = {}

        # Sort sources by priority (lower number = higher priority)
        sorted_sources = sorted(self.sources, key=lambda s: s.priority)

        for source in sorted_sources:
            if not source.enabled:
                continue

            try:
                source_config = await source.load_configuration()
                merged_config.update(source_config)
            except Exception as e:
                logger.warning(f"Failed to load configuration from {source.name}: {e}")

        return merged_config

    async def _load_component_configurations(self) -> None:
        """Load component-specific configurations."""
        # Default component configurations
        components: Dict[str, Dict[str, Any]] = {
            "lsp": {"enabled": True, "dependencies": []},
            "mcp": {"enabled": True, "dependencies": []},
            "protocols": {"enabled": True, "dependencies": ["framework", "memory_bank"]},
            "framework": {"enabled": True, "dependencies": []},
            "memory_bank": {"enabled": True, "dependencies": []},
            "security": {"enabled": True, "dependencies": []},
            "observability": {"enabled": True, "dependencies": []},
        }

        for component_name, config in components.items():
            self.component_configs[component_name] = ComponentConfiguration(
                name=component_name,
                **config
            )

    async def _validate_configuration(self) -> None:
        """Validate loaded configuration."""
        # Check required dependencies
        for component_name, component_config in self.component_configs.items():
            for dep in component_config.dependencies:
                if dep not in self.component_configs or not self.component_configs[dep].enabled:
                    logger.warning(f"Component {component_name} requires {dep} but it's not enabled")

        # Validate security settings
        if self.settings.environment == Environment.PRODUCTION:
            if not self.settings.secret_key or self.settings.secret_key == os.urandom(32).hex():
                raise ConfigurationError("Production environment requires a proper secret key")

    def add_source(self, source: ConfigurationSource) -> None:
        """Add a configuration source."""
        self.sources.append(source)
        logger.info(f"Added configuration source: {source.name} (priority: {source.priority})")

    def remove_source(self, source_name: str) -> None:
        """Remove a configuration source."""
        self.sources = [s for s in self.sources if s.name != source_name]
        logger.info(f"Removed configuration source: {source_name}")

    async def get_value(self, key: str, use_cache: bool = True) -> Optional[Any]:
        """Get configuration value."""
        if not self._initialized:
            await self.initialize()

        # Check cache first
        if use_cache:
            cached_value = await self.cache.get(key)
            if cached_value is not None:
                return cached_value

        # Load from sources
        async with self._config_lock:
            merged_config = await self._merge_configuration_sources()

        value = merged_config.get(key)

        # Cache the value
        if use_cache and value is not None:
            await self.cache.set(key, value, ttl=self.settings.cache_ttl)

        return value

    async def set_value(self, key: str, value: Any, source_name: str = "dynamic") -> bool:
        """Set configuration value."""
        if not self._initialized:
            await self.initialize()

        old_value = await self.get_value(key, use_cache=False)

        # Find writable source with highest priority
        for source in sorted(self.sources, key=lambda s: s.priority):
            if await source.set_value(key, value):
                # Update cache
                await self.cache.set(key, value, ttl=self.settings.cache_ttl)

                # Notify change listeners
                await self._notify_change_listeners(
                    ConfigurationChangeEvent(
                        key=key,
                        old_value=old_value,
                        new_value=value,
                        source=source_name
                    )
                )
                return True

        return False

    def add_change_callback(self, callback: ConfigurationUpdateCallback) -> None:
        """Add configuration change callback."""
        self.change_callbacks[id(callback)] = callback

    def remove_change_callback(self, callback: ConfigurationUpdateCallback) -> None:
        """Remove configuration change callback."""
        self.change_callbacks.pop(id(callback), None)

    async def _notify_change_listeners(self, event: ConfigurationChangeEvent) -> None:
        """Notify all change listeners."""
        for callback in self.change_callbacks.values():
            try:
                await callback.on_configuration_change(event)
            except Exception as e:
                logger.error(f"Configuration change callback failed: {e}")

    def add_validation_schema(self, key: str, schema: Dict[str, Any]) -> None:
        """Add validation schema for configuration key."""
        self.validation_schemas[key] = schema

    async def reload_configuration(self) -> None:
        """Reload configuration from all sources."""
        logger.info("Reloading configuration")
        await self.cache.clear()
        await self._load_initial_configuration()
        await self._validate_configuration()
        logger.info("Configuration reloaded")

    def get_component_config(self, component_name: str) -> Optional[ComponentConfiguration]:
        """Get component configuration."""
        return self.component_configs.get(component_name)

    def set_component_config(self, component_name: str, config: ComponentConfiguration) -> None:
        """Set component configuration."""
        self.component_configs[component_name] = config

    async def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "environment": self.settings.environment.value,
            "debug": self.settings.debug,
            "version": self._get_version(),
            "config_sources": [s.name for s in self.sources if s.enabled],
            "components": {
                name: {
                    "enabled": config.enabled,
                    "dependencies": config.dependencies
                }
                for name, config in self.component_configs.items()
            }
        }

    def _get_version(self) -> str:
        """Get application version."""
        # Placeholder - would read from version file or package
        try:
            with open("pyproject.toml", "r") as f:
                import tomllib
                data = tomllib.load(f)
                version = data.get("tool", {}).get("poetry", {}).get("version", "0.1.0")
                return str(version)
        except:
            return "0.1.0"

    async def export_configuration(self, format_type: str = "json") -> str:
        """Export current configuration."""
        config = {
            "settings": self.settings.dict(),
            "components": {
                name: config.dict() for name, config in self.component_configs.items()
            },
            "sources": [s.name for s in self.sources if s.enabled]
        }

        if format_type == "json":
            return str(json.dumps(config, indent=2, default=str))
        elif format_type == "yaml":
            return str(yaml.dump(config, default_flow_style=False))

        raise ValueError(f"Unsupported format: {format_type}")


# Global configuration manager instance
_configuration_manager = None

def get_global_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _configuration_manager
    if _configuration_manager is None:
        _configuration_manager = ConfigurationManager()
    return _configuration_manager

def set_global_config_manager(manager: ConfigurationManager) -> None:
    """Set the global configuration manager instance."""
    global _configuration_manager
    _configuration_manager = manager


# Configuration decorators
def require_config(*required_keys: str) -> Callable:
    """Decorator to require specific configuration keys."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            config_manager = get_global_config_manager()

            for key in required_keys:
                if await config_manager.get_value(key) is None:
                    raise ConfigurationError(f"Required configuration key missing: {key}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def config_aware(param_name: str, default_value: Any = None) -> Callable:
    """Decorator to inject configuration values as function parameters."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if param_name not in kwargs:
                config_manager = get_global_config_manager()
                config_value = await config_manager.get_value(param_name)
                if config_value is not None:
                    kwargs[param_name] = config_value
                elif default_value is not None:
                    kwargs[param_name] = default_value

            return await func(*args, **kwargs)
        return wrapper
    return decorator
