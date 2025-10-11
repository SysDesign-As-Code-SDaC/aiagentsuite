"""
AI Agent Suite Security Module

Provides comprehensive security boundaries including authentication, authorization,
input validation, encryption, and audit logging.
"""

import asyncio
import hashlib
import hmac
import json
import secrets
import time
import logging
import re
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable, AsyncGenerator
from functools import wraps

import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from .errors import SecurityError, ValidationError, get_global_error_handler
from ..memory_bank.manager import MemoryBank

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for operations."""
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


class Permission(Enum):
    """System permissions."""
    # Framework operations
    FRAMEWORK_READ = "framework:read"
    FRAMEWORK_WRITE = "framework:write"
    FRAMEWORK_ADMIN = "framework:admin"

    # Protocol operations
    PROTOCOL_EXECUTE = "protocol:execute"
    PROTOCOL_MANAGE = "protocol:manage"

    # Memory operations
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"

    # LSP operations
    LSP_COMPLETIONS = "lsp:completions"
    LSP_DIAGNOSTICS = "lsp:diagnostics"
    LSP_CODE_ACTIONS = "lsp:code_actions"

    # MCP operations
    MCP_TOOLS = "mcp:tools"
    MCP_RESOURCES = "mcp:resources"

    # Administrative
    ADMIN_USERS = "admin:users"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_SYSTEM = "admin:system"


@dataclass
class User:
    """User entity."""
    user_id: str
    username: str
    email: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityContext:
    """Security context for operations."""
    user: Optional[User] = None
    session_id: Optional[str] = None
    permissions: Set[Permission] = field(default_factory=set)
    security_level: SecurityLevel = SecurityLevel.PUBLIC
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEvent:
    """Audit event for logging."""
    event_type: str
    resource: str
    action: str
    result: str  # "success", "failure", "denied"
    event_id: str = field(default_factory=lambda: secrets.token_hex(16))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    risk_score: int = 0
    security_level: SecurityLevel = SecurityLevel.PUBLIC


class EncryptionManager:
    """Manages encryption and decryption operations."""

    def __init__(self, key: Optional[bytes] = None):
        self.key = key or Fernet.generate_key()
        self.fernet = Fernet(self.key)

    def encrypt(self, data: Union[str, bytes, Dict]) -> bytes:
        """Encrypt data."""
        if isinstance(data, dict):
            data = json.dumps(data, default=str).encode()
        elif isinstance(data, str):
            data = data.encode()

        return self.fernet.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> Union[str, Dict, bytes]:
        """Decrypt data."""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return decrypted.decode()
        except Exception as e:
            raise SecurityError(f"Decryption failed: {e}")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def generate_token(self, data: Dict[str, Any], expires_in: int = 3600) -> str:
        """Generate a JWT token."""
        payload = data.copy()
        payload.update({
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
            "iss": "aiagentsuite"
        })
        return jwt.encode(payload, self.key.decode(), algorithm="HS256")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            return jwt.decode(token, self.key.decode(), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class InputValidator:
    """Comprehensive input validation."""

    # Common validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,32}$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.@]+$')

    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        re.compile(r'<script', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<\s*/?\s*script\s*>', re.IGNORECASE),
        re.compile(r'exec\(', re.IGNORECASE),
        re.compile(r'eval\(', re.IGNORECASE),
        re.compile(r'__import__\(', re.IGNORECASE),
        re.compile(r'subprocess\.', re.IGNORECASE),
    ]

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        return bool(InputValidator.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        return bool(InputValidator.USERNAME_PATTERN.match(username))

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if len(input_str) > max_length:
            raise ValidationError(f"Input exceeds maximum length of {max_length}")

        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if pattern.search(input_str):
                raise SecurityError("Input contains dangerous content")

        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>]', '', input_str)

        return sanitized.strip()

    @staticmethod
    def validate_protocol_name(name: str) -> str:
        """Validate protocol name."""
        if not name or len(name) > 100:
            raise ValidationError("Invalid protocol name length")

        if not InputValidator.SAFE_STRING_PATTERN.match(name):
            raise ValidationError("Protocol name contains invalid characters")

        return name

    @staticmethod
    def validate_context_data(data: Any, max_depth: int = 5) -> Any:
        """Recursively validate context data structures."""
        def _validate_recursive(obj: Any, depth: int = 0) -> Any:
            if depth > max_depth:
                raise ValidationError("Context data structure too deep")

            if isinstance(obj, dict):
                validated = {}
                for k, v in obj.items():
                    if not isinstance(k, str) or len(k) > 100:
                        raise ValidationError("Invalid dictionary key")
                    validated[k] = _validate_recursive(v, depth + 1)
                return validated
            elif isinstance(obj, list):
                if len(obj) > 100:
                    raise ValidationError("List too long")
                return [_validate_recursive(item, depth + 1) for item in obj]
            elif isinstance(obj, str):
                return InputValidator.sanitize_string(obj, 10000)
            elif isinstance(obj, (int, float, bool, type(None))):
                return obj
            else:
                # Convert other types to strings and validate
                return InputValidator.sanitize_string(str(obj), 1000)

        return _validate_recursive(data)


class AuthorizationManager:
    """Manages permissions and authorization."""

    def __init__(self) -> None:
        self.role_permissions: Dict[str, Set[Permission]] = {}
        self.user_permissions: Dict[str, Set[Permission]] = {}
        self.resource_policies: Dict[str, Dict[str, Any]] = {}

    def assign_role_permissions(self, role: str, permissions: Set[Permission]) -> None:
        """Assign permissions to a role."""
        self.role_permissions[role] = permissions

    def assign_user_permissions(self, user_id: str, permissions: Set[Permission]) -> None:
        """Assign direct permissions to a user."""
        self.user_permissions[user_id] = permissions

    def check_permission(self, context: SecurityContext, permission: Permission,
                        resource: str = "*") -> bool:
        """Check if the context has the required permission."""
        if not context.user:
            # Anonymous users only get public permissions
            return permission in [
                Permission.LSP_COMPLETIONS,
                Permission.MCP_TOOLS
            ] and context.security_level == SecurityLevel.PUBLIC

        # Check direct user permissions
        if permission in self.user_permissions.get(context.user.user_id, set()):
            return True

        # Check role-based permissions
        for role in context.user.roles:
            if permission in self.role_permissions.get(role, set()):
                return True

        return False

    def require_permission(self, permission: Permission, resource: str = "*") -> Callable[[Callable], Callable]:
        """Decorator to require a specific permission."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                # Get security context (assuming it's passed or available)
                context = kwargs.get('security_context')
                if context and not self.check_permission(context, permission, resource):
                    raise SecurityError(
                        f"Permission denied: {permission.value} on {resource}",
                        error_code="PERMISSION_DENIED"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

    def create_resource_policy(self, resource_pattern: str, policy: Dict[str, Any]) -> None:
        """Create a resource access policy."""
        self.resource_policies[resource_pattern] = policy

    def evaluate_resource_policy(self, resource: str, context: SecurityContext) -> bool:
        """Evaluate if access is allowed based on resource policies."""
        for pattern, policy in self.resource_policies.items():
            if re.match(pattern, resource):
                # Simple policy evaluation (could be extended with more complex logic)
                required_role = policy.get('required_role')
                if required_role and required_role not in context.user.roles:
                    return False

                required_permission = policy.get('required_permission')
                if required_permission and not self.check_permission(context, required_permission, resource):
                    return False

                security_level = policy.get('min_security_level', SecurityLevel.PUBLIC)
                if context.security_level.value < security_level.value:
                    return False

        return True


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, memory_bank: Optional[MemoryBank] = None, log_file: Optional[Path] = None):
        self.memory_bank = memory_bank
        self.log_file = log_file or Path("logs/audit.log")
        self.log_file.parent.mkdir(exist_ok=True)

        # Setup rotating file handler would go here in production
        self._audit_queue: asyncio.Queue[AuditEvent] = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the audit logging system."""
        self._processing_task = asyncio.create_task(self._process_audit_events())

    async def stop(self) -> None:
        """Stop the audit logging system."""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

    async def log_event(self, event: AuditEvent) -> None:
        """Log an audit event."""
        await self._audit_queue.put(event)

    async def _process_audit_events(self) -> None:
        """Process audit events from the queue."""
        try:
            while True:
                event = await self._audit_queue.get()

                # Write to file
                await self._write_to_file(event)

                # Store in memory bank if configured
                if self.memory_bank and event.security_level in [SecurityLevel.SENSITIVE, SecurityLevel.CRITICAL]:
                    try:
                        await self.memory_bank.log_decision(
                            f"Audit Event: {event.event_type}",
                            f"Action: {event.action} on {event.resource} - Result: {event.result}",
                            {
                                "audit_event_id": event.event_id,
                                "security_level": event.security_level.value,
                                "risk_score": event.risk_score,
                                "user_id": event.user_id,
                                "session_id": event.session_id,
                                "ip_address": event.ip_address,
                                "details": event.details
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to store audit event in memory bank: {e}")

                # Log high-risk events immediately
                if event.risk_score >= 7:
                    logger.warning("High-risk audit event", extra=event.__dict__)

                self._audit_queue.task_done()

        except asyncio.CancelledError:
            # Process remaining events before shutdown
            while not self._audit_queue.empty():
                event = self._audit_queue.get_nowait()
                await self._write_to_file(event)

    async def _write_to_file(self, event: AuditEvent) -> None:
        """Write audit event to log file."""
        try:
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_id": event.event_id,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "resource": event.resource,
                "action": event.action,
                "result": event.result,
                "risk_score": event.risk_score,
                "security_level": event.security_level.value,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "details": event.details
            }

            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def create_audit_event(
        self,
        event_type: str,
        resource: str,
        action: str,
        result: str,
        context: Optional[SecurityContext] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_score: int = 0
    ) -> AuditEvent:
        """Create an audit event."""
        return AuditEvent(
            event_type=event_type,
            user_id=context.user.user_id if context and context.user else None,
            session_id=context.session_id if context else None,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            ip_address=context.ip_address if context else None,
            user_agent=context.user_agent if context else None,
            risk_score=risk_score,
            security_level=context.security_level if context else SecurityLevel.PUBLIC
        )

    async def query_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_risk_score: int = 0
    ) -> List[AuditEvent]:
        """Query audit events with filters."""
        # In production, this would query from database
        # For now, return empty list (file-based queries are complex)
        logger.warning("Audit event querying not implemented for file-based storage")
        return []


class RateLimiter:
    """Rate limiting for API endpoints and operations."""

    def __init__(self) -> None:
        self.requests: Dict[str, List[float]] = {}
        self.limits: Dict[str, Tuple[int, float]] = {}  # (max_requests, window_seconds)

    def set_limit(self, key: str, max_requests: int, window_seconds: float) -> None:
        """Set rate limiting for a key."""
        self.limits[key] = (max_requests, window_seconds)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limits."""
        if key not in self.limits:
            return True

        max_requests, window_seconds = self.limits[key]
        now = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]

        if len(self.requests[key]) >= max_requests:
            return False

        self.requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for a key."""
        if key not in self.limits:
            return -1  # Unlimited

        max_requests, window_seconds = self.limits[key]
        now = time.time()

        if key not in self.requests:
            return max_requests

        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]

        return max_requests - len(self.requests[key])


class SecurityManager:
    """Central security manager coordinating all security components."""

    def __init__(self, memory_bank: Optional[MemoryBank] = None):
        self.encryption = EncryptionManager()
        self.authorization = AuthorizationManager()
        self.audit_logger = AuditLogger(memory_bank)
        self.rate_limiter = RateLimiter()
        self.error_handler = get_global_error_handler()

        # Security contexts
        self._contexts: Dict[str, SecurityContext] = {}

    async def initialize(self) -> None:
        """Initialize security manager."""
        await self.audit_logger.start()

        # Setup default security policies
        self._setup_default_policies()

        # Setup rate limiting
        self._setup_rate_limits()

        logger.info("Security manager initialized")

    async def shutdown(self) -> None:
        """Shutdown security manager."""
        await self.audit_logger.stop()

    def _setup_default_policies(self) -> None:
        """Setup default security policies."""
        # User roles
        self.authorization.assign_role_permissions("admin", {
            Permission.FRAMEWORK_ADMIN,
            Permission.PROTOCOL_MANAGE,
            Permission.MEMORY_WRITE,
            Permission.ADMIN_USERS,
            Permission.ADMIN_AUDIT,
            Permission.ADMIN_SYSTEM
        })

        self.authorization.assign_role_permissions("developer", {
            Permission.FRAMEWORK_READ,
            Permission.FRAMEWORK_WRITE,
            Permission.PROTOCOL_EXECUTE,
            Permission.MEMORY_READ,
            Permission.LSP_COMPLETIONS,
            Permission.LSP_DIAGNOSTICS,
            Permission.MCP_TOOLS
        })

        self.authorization.assign_role_permissions("viewer", {
            Permission.FRAMEWORK_READ,
            Permission.MEMORY_READ,
            Permission.LSP_COMPLETIONS
        })

        # Resource policies
        self.authorization.create_resource_policy("framework://constitution", {
            "required_role": "developer",
            "min_security_level": SecurityLevel.INTERNAL
        })

        self.authorization.create_resource_policy("protocol://*", {
            "required_permission": Permission.PROTOCOL_EXECUTE,
            "min_security_level": SecurityLevel.INTERNAL
        })

    def _setup_rate_limits(self) -> None:
        """Setup default rate limits."""
        self.rate_limiter.set_limit("lsp_completions", 100, 60)  # 100 per minute
        self.rate_limiter.set_limit("protocol_execution", 10, 60)  # 10 per minute
        self.rate_limiter.set_limit("authentication", 5, 300)  # 5 per 5 minutes

        # Current security level
        self._current_security_level = SecurityLevel.INTERNAL

    async def set_security_level(self, level: SecurityLevel) -> None:
        """Set the current security level."""
        self._current_security_level = level
        await self.audit_logger.log_event(
            self.audit_logger.create_audit_event(
                "security_level_changed",
                f"level:{level.value}",
                "configuration",
                "success",
                None,
                {"new_level": level.value}
            )
        )

    @property
    def current_security_level(self) -> SecurityLevel:
        """Get the current security level."""
        return self._current_security_level

    @asynccontextmanager
    async def security_context(
        self,
        user: Optional[User] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AsyncGenerator[SecurityContext, None]:
        """Create and manage a security context."""
        context = SecurityContext(
            user=user,
            session_id=session_id,
            permissions=set(),
            security_level=self._determine_security_level(user),
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        if user:
            context.permissions = self._collect_user_permissions(user)

        context_id = secrets.token_hex(8)
        self._contexts[context_id] = context

        try:
            yield context
        finally:
            # Log security event
            await self.audit_logger.log_event(
                self.audit_logger.create_audit_event(
                    "session_end",
                    f"context:{context_id}",
                    "complete",
                    "success",
                    context
                )
            )
            del self._contexts[context_id]

    def _determine_security_level(self, user: Optional[User]) -> SecurityLevel:
        """Determine security level for a user."""
        if not user:
            return SecurityLevel.PUBLIC

        if "admin" in user.roles:
            return SecurityLevel.CRITICAL
        elif any(role in ["developer", "architect"] for role in user.roles):
            return SecurityLevel.SENSITIVE
        else:
            return SecurityLevel.INTERNAL

    def _collect_user_permissions(self, user: User) -> Set[Permission]:
        """Collect all permissions for a user."""
        permissions = user.permissions.copy()

        for role in user.roles:
            permissions.update(self.authorization.role_permissions.get(role, set()))

        return permissions

    def secure_operation(
        self,
        permission: Optional[Permission] = None,
        security_level: SecurityLevel = SecurityLevel.INTERNAL,
        audit_event: bool = True
    ) -> Callable[[Callable], Callable]:
        """Decorator for securing operations."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                context = kwargs.get('security_context')

                # Rate limiting check
                operation_key = f"{func.__module__}.{func.__name__}"
                if not self.rate_limiter.is_allowed(operation_key):
                    await self.audit_logger.log_event(
                        self.audit_logger.create_audit_event(
                            "rate_limit_exceeded",
                            operation_key,
                            "access",
                            "denied",
                            context,
                            risk_score=3
                        )
                    )
                    raise SecurityError("Rate limit exceeded")

                # Security level check
                if context and context.security_level.value < security_level.value:
                    await self.audit_logger.log_event(
                        self.audit_logger.create_audit_event(
                            "security_level_violation",
                            operation_key,
                            "access",
                            "denied",
                            context,
                            risk_score=8
                        )
                    )
                    raise SecurityError(f"Insufficient security level: requires {security_level.value}")

                # Permission check
                if permission and context and not self.authorization.check_permission(context, permission):
                    await self.audit_logger.log_event(
                        self.audit_logger.create_audit_event(
                            "permission_denied",
                            operation_key,
                            "access",
                            "denied",
                            context,
                            {"required_permission": permission.value},
                            risk_score=7
                        )
                    )
                    raise SecurityError(f"Permission denied: {permission.value}")

                # Execute with security monitoring
                try:
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    if audit_event:
                        await self.audit_logger.log_event(
                            self.audit_logger.create_audit_event(
                                "operation_success",
                                operation_key,
                                "execute",
                                "success",
                                context,
                                {"duration": duration}
                            )
                        )

                    return result

                except Exception as e:
                    # Log failure
                    await self.audit_logger.log_event(
                        self.audit_logger.create_audit_event(
                            "operation_failure",
                            operation_key,
                            str(e),
                            "failure",
                            context,
                            {"error_type": e.__class__.__name__},
                            risk_score=5 if isinstance(e, SecurityError) else 2
                        )
                    )
                    raise

            return wrapper
        return decorator

    async def validate_input(self, data: Any, operation: str) -> Any:
        """Validate and sanitize input data."""
        try:
            validated_data = InputValidator.validate_context_data(data)

            # Additional security checks based on operation
            if operation == "protocol_execution":
                if isinstance(validated_data, dict):
                    if "protocol_name" in validated_data:
                        validated_data["protocol_name"] = InputValidator.validate_protocol_name(
                            validated_data["protocol_name"]
                        )

            return validated_data

        except (ValidationError, SecurityError) as e:
            await self.audit_logger.log_event(
                self.audit_logger.create_audit_event(
                    "input_validation_failure",
                    f"operation:{operation}",
                    "validate",
                    "failure",
                    None,
                    {"error": str(e)},
                    risk_score=6
                )
            )
            raise

    def create_user(self, username: str, email: str, password: str, roles: Optional[List[str]] = None) -> User:
        """Create a new user with validation."""
        if not InputValidator.validate_username(username):
            raise ValidationError("Invalid username format")

        if not InputValidator.validate_email(email):
            raise ValidationError("Invalid email format")

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        hashed_password = self.encryption.hash_password(password)

        user = User(
            user_id=secrets.token_hex(16),
            username=username,
            email=email,
            roles=set(roles or []),
            metadata={"password_hash": hashed_password}
        )

        return user

    def authenticate_user(self, username: str, password: str, stored_hash: str) -> bool:
        """Authenticate a user."""
        return self.encryption.verify_password(password, stored_hash)


# Global security manager instance
_security_manager = None

def get_global_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

def set_global_security_manager(manager: SecurityManager) -> None:
    """Set the global security manager instance."""
    global _security_manager
    _security_manager = manager
