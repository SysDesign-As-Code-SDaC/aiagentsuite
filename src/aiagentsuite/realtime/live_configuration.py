"""
Live Configuration Manager Module

Dynamic configuration management with hot-reload
capabilities for real-time configuration changes without restarts.
"""

from typing import Any, Callable, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
import threading
import asyncio


class ConfigScope(Enum):
    """Scope of configuration values."""
    GLOBAL = "global"
    PROJECT = "project"
    USER = "user"
    SESSION = "session"


class ConfigType(Enum):
    """Type of configuration value."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"


@dataclass
class ConfigValue:
    """A configuration value with metadata."""
    key: str
    value: Any
    config_type: ConfigType
    scope: ConfigScope
    default: Any
    description: str = ""
    validation_schema: Optional[dict] = None
    modified_at: datetime = field(default_factory=datetime.now)
    modified_by: str = "system"
    version: int = 1

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "type": self.config_type.value,
            "scope": self.scope.value,
            "default": self.default,
            "description": self.description,
            "modified_at": self.modified_at.isoformat(),
            "modified_by": self.modified_by,
            "version": self.version,
        }


@dataclass
class ConfigChange:
    """Record of a configuration change."""
    key: str
    old_value: Any
    new_value: Any
    scope: ConfigScope
    timestamp: datetime
    modified_by: str
    reason: str = ""


class LiveConfigurationManager:
    """
    Live configuration manager with hot-reload support.

    Provides:
    - Dynamic configuration updates without restarts
    - Configuration versioning and history
    - Scope-based configuration
    - Configuration validation
    - Change callbacks
    - Configuration persistence
    """

    def __init__(
        self,
        auto_persist: bool = True,
        persist_path: Optional[str] = None,
        max_history: int = 100,
    ):
        """
        Initialize live configuration manager.

        Args:
            auto_persist: Whether to auto-persist changes
            persist_path: Path for configuration persistence
            max_history: Maximum change history to keep
        """
        self.auto_persist = auto_persist
        self.persist_path = persist_path
        self.max_history = max_history

        self._config: dict[str, ConfigValue] = {}
        self._change_history: list[ConfigChange] = []
        self._lock = threading.RLock()
        
        # Callbacks
        self._change_callbacks: list[Callable[[ConfigChange], None]] = []
        self._validation_callbacks: list[Callable[[str, Any], bool]] = []

        # Default configurations
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Set up default configurations."""
        defaults = [
            ("debug", False, ConfigType.BOOLEAN, ConfigScope.GLOBAL, "Enable debug mode"),
            ("max_retries", 3, ConfigType.NUMBER, ConfigScope.GLOBAL, "Maximum retry attempts"),
            ("timeout", 30, ConfigType.NUMBER, ConfigScope.GLOBAL, "Default timeout in seconds"),
            ("cache_enabled", True, ConfigType.BOOLEAN, ConfigScope.GLOBAL, "Enable caching"),
            ("log_level", "INFO", ConfigType.STRING, ConfigScope.GLOBAL, "Logging level"),
            ("feature_flags", {}, ConfigType.OBJECT, ConfigScope.GLOBAL, "Feature flags"),
        ]

        for key, default, config_type, scope, description in defaults:
            self._config[key] = ConfigValue(
                key=key,
                value=default,
                config_type=config_type,
                scope=scope,
                default=default,
                description=description,
            )

    def get(
        self,
        key: str,
        default: Any = None,
        scope: Optional[ConfigScope] = None,
    ) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found
            scope: Optional scope filter

        Returns:
            Configuration value or default
        """
        with self._lock:
            config = self._config.get(key)
            if config is None:
                return default
            
            if scope and config.scope != scope:
                return default
            
            return config.value

    def set(
        self,
        key: str,
        value: Any,
        scope: ConfigScope = ConfigScope.GLOBAL,
        modified_by: str = "system",
        reason: str = "",
        validate: bool = True,
    ) -> bool:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: New value
            scope: Configuration scope
            modified_by: Who modified the value
            reason: Reason for change
            validate: Whether to validate the value

        Returns:
            True if set successfully, False otherwise
        """
        if validate and not self._validate_value(key, value):
            return False

        with self._lock:
            old_config = self._config.get(key)
            old_value = old_config.value if old_config else None
            
            # Determine type
            config_type = self._infer_type(value)
            
            # Create or update config
            if key in self._config:
                config = self._config[key]
                config.value = value
                config.modified_at = datetime.now()
                config.modified_by = modified_by
                config.version += 1
            else:
                self._config[key] = ConfigValue(
                    key=key,
                    value=value,
                    config_type=config_type,
                    scope=scope,
                    default=value,
                )

            # Record change
            change = ConfigChange(
                key=key,
                old_value=old_value,
                new_value=value,
                scope=scope,
                timestamp=datetime.now(),
                modified_by=modified_by,
                reason=reason,
            )
            self._change_history.append(change)
            
            # Trim history
            if len(self._change_history) > self.max_history:
                self._change_history = self._change_history[-self.max_history:]

            # Trigger callbacks
            for callback in self._change_callbacks:
                try:
                    callback(change)
                except Exception:
                    pass

            return True

    def _infer_type(self, value: Any) -> ConfigType:
        """Infer configuration type from value."""
        if isinstance(value, bool):
            return ConfigType.BOOLEAN
        elif isinstance(value, (int, float)):
            return ConfigType.NUMBER
        elif isinstance(value, dict):
            return ConfigType.OBJECT
        elif isinstance(value, list):
            return ConfigType.ARRAY
        else:
            return ConfigType.STRING

    def _validate_value(self, key: str, value: Any) -> bool:
        """Validate a configuration value."""
        # Run validation callbacks
        for callback in self._validation_callbacks:
            if not callback(key, value):
                return False
        
        # Get config if exists
        config = self._config.get(key)
        if config and config.validation_schema:
            return self._validate_schema(value, config.validation_schema)
        
        return True

    def _validate_schema(self, value: Any, schema: dict) -> bool:
        """Validate value against schema."""
        # Basic schema validation
        if "type" in schema:
            expected_type = schema["type"]
            type_map = {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "object": dict,
                "array": list,
            }
            
            expected = type_map.get(expected_type)
            if expected and not isinstance(value, expected):
                return False
        
        if "min" in schema and isinstance(value, (int, float)):
            if value < schema["min"]:
                return False
        
        if "max" in schema and isinstance(value, (int, float)):
            if value > schema["max"]:
                return False
        
        if "enum" in schema:
            if value not in schema["enum"]:
                return False
        
        return True

    def register_change_callback(
        self,
        callback: Callable[[ConfigChange], None],
    ) -> None:
        """Register callback for configuration changes."""
        self._change_callbacks.append(callback)

    def register_validation_callback(
        self,
        callback: Callable[[str, Any], bool],
    ) -> None:
        """Register callback for configuration validation."""
        self._validation_callbacks.append(callback)

    def get_all(
        self,
        scope: Optional[ConfigScope] = None,
    ) -> dict[str, Any]:
        """Get all configuration values."""
        with self._lock:
            if scope:
                return {
                    k: v.value for k, v in self._config.items()
                    if v.scope == scope
                }
            return {k: v.value for k, v in self._config.items()}

    def get_metadata(self, key: str) -> Optional[dict]:
        """Get configuration metadata."""
        config = self._config.get(key)
        return config.to_dict() if config else None

    def reset(self, key: str) -> bool:
        """Reset a configuration to its default value."""
        with self._lock:
            config = self._config.get(key)
            if not config:
                return False
            
            return self.set(
                key,
                config.default,
                modified_by="system",
                reason="Reset to default",
            )

    def reset_all(self) -> None:
        """Reset all configurations to defaults."""
        with self._lock:
            for key in list(self._config.keys()):
                self.reset(key)

    def get_changes(
        self,
        key: Optional[str] = None,
        limit: int = 10,
    ) -> list[ConfigChange]:
        """Get configuration change history."""
        if key:
            return [
                c for c in self._change_history
                if c.key == key
            ][-limit:]
        return self._change_history[-limit:]

    def export_config(self) -> str:
        """Export configuration as JSON."""
        with self._lock:
            data = {
                key: config.to_dict()
                for key, config in self._config.items()
            }
            return json.dumps(data, indent=2)

    def import_config(
        self,
        json_data: str,
        merge: bool = True,
    ) -> int:
        """Import configuration from JSON."""
        data = json.loads(json_data)
        imported = 0

        with self._lock:
            if not merge:
                self._config.clear()

            for key, config_data in data.items():
                self.set(
                    key=key,
                    value=config_data.get("value"),
                    scope=ConfigScope(config_data.get("scope", "global")),
                    modified_by=config_data.get("modified_by", "import"),
                    reason="Imported configuration",
                )
                imported += 1

        return imported

    def get_statistics(self) -> dict[str, Any]:
        """Get configuration statistics."""
        with self._lock:
            by_scope = {}
            for scope in ConfigScope:
                count = sum(
                    1 for c in self._config.values()
                    if c.scope == scope
                )
                by_scope[scope.value] = count

            return {
                "total_keys": len(self._config),
                "by_scope": by_scope,
                "total_changes": len(self._change_history),
            }


class AsyncLiveConfigurationManager(LiveConfigurationManager):
    """
    Async version of LiveConfigurationManager with additional
    async features.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_callbacks: list[Callable[[ConfigChange], None]] = []

    async def set_async(
        self,
        key: str,
        value: Any,
        scope: ConfigScope = ConfigScope.GLOBAL,
        modified_by: str = "system",
        reason: str = "",
    ) -> bool:
        """Async version of set with awaitable result."""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.set,
            key, value, scope, modified_by, reason
        )

    def register_async_callback(
        self,
        callback: Callable[[ConfigChange], None],
    ) -> None:
        """Register async callback for changes."""
        self._async_callbacks.append(callback)
