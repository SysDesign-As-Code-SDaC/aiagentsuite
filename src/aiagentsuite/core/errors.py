"""
AI Agent Suite Error Handling and Resilience

Provides comprehensive error handling, circuit breakers, retries, and resilience patterns.
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union, TypeVar, AsyncGenerator
from functools import wraps

import backoff
import structlog

from ..memory_bank.manager import MemoryBank

logger = structlog.get_logger(__name__)

T = TypeVar('T')


class AIAgentSuiteError(Exception):
    """Base exception for AI Agent Suite errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._get_error_code()
        self.details = details or {}
        self.timestamp = time.time()
        self.component = self._get_component_name()

    def _get_error_code(self) -> str:
        """Get error code from class name."""
        return self.__class__.__name__.replace('Error', '').upper()

    def _get_component_name(self) -> str:
        """Get component name from class hierarchy."""
        return self.__class__.__module__.split('.')[-2]

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "component": self.component,
            "timestamp": self.timestamp,
            "details": self.details
        }


class FrameworkError(AIAgentSuiteError):
    """Errors related to framework operations."""
    pass


class ProtocolError(AIAgentSuiteError):
    """Errors related to protocol execution."""
    pass


class ValidationError(AIAgentSuiteError):
    """Errors related to data validation."""
    pass


class SecurityError(AIAgentSuiteError):
    """Errors related to security violations."""
    pass


class ConfigurationError(AIAgentSuiteError):
    """Errors related to configuration issues."""
    pass


class ResourceError(AIAgentSuiteError):
    """Errors related to resource exhaustion or unavailability."""
    pass


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Number of successes needed to close
    timeout: float = 60.0       # Seconds to wait in open state
    name: str = "default"       # Circuit breaker name


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics."""
    total_requests: int = 0
    total_failures: int = 0
    total_successes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self._last_state_change = time.time()
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute function through circuit breaker."""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self._last_state_change >= self.config.timeout:
                    # Time to try again
                    self.state = CircuitBreakerState.HALF_OPEN
                    self._last_state_change = time.time()
                    logger.info(f"Circuit breaker {self.config.name} entering half-open state")
                else:
                    raise ResourceError(
                        f"Circuit breaker {self.config.name} is open",
                        error_code="CIRCUIT_BREAKER_OPEN",
                        details={"timeout_remaining": self.config.timeout - (time.time() - self._last_state_change)}
                    )

            self.stats.total_requests += 1

        try:
            result = await func(*args, **kwargs)

            async with self._lock:
                self.stats.total_successes += 1
                self.stats.consecutive_successes += 1
                self.stats.consecutive_failures = 0
                self.stats.last_success_time = time.time()

                if self.state == CircuitBreakerState.HALF_OPEN:
                    if self.stats.consecutive_successes >= self.config.success_threshold:
                        self.state = CircuitBreakerState.CLOSED
                        self._last_state_change = time.time()
                        logger.info(f"Circuit breaker {self.config.name} closed")
                elif self.state == CircuitBreakerState.OPEN:
                    # Should not happen, but just in case
                    self.state = CircuitBreakerState.CLOSED

            return result

        except Exception as e:
            async with self._lock:
                self.stats.total_failures += 1
                self.stats.consecutive_failures += 1
                self.stats.consecutive_successes = 0
                self.stats.last_failure_time = time.time()

                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.OPEN
                    self._last_state_change = time.time()
                    logger.warning(f"Circuit breaker {self.config.name} reopened due to failure in half-open state")
                elif (self.state == CircuitBreakerState.CLOSED and
                      self.stats.consecutive_failures >= self.config.failure_threshold):
                    self.state = CircuitBreakerState.OPEN
                    self._last_state_change = time.time()
                    logger.warning(f"Circuit breaker {self.config.name} opened due to {self.stats.consecutive_failures} consecutive failures")

            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            },
            "stats": {
                "total_requests": self.stats.total_requests,
                "total_failures": self.stats.total_failures,
                "total_successes": self.stats.total_successes,
                "consecutive_failures": self.stats.consecutive_failures,
                "consecutive_successes": self.stats.consecutive_successes,
                "last_failure_time": self.stats.last_failure_time,
                "last_success_time": self.stats.last_success_time
            },
            "time_since_last_state_change": time.time() - self._last_state_change
        }


class ErrorHandler:
    """Central error handling and resilience manager."""

    def __init__(self, memory_bank: Optional[MemoryBank] = None):
        self.memory_bank = memory_bank
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_handlers: Dict[str, Callable[[Exception], Awaitable[None]]] = {}
        self.recovery_strategies: Dict[str, Callable[[Exception], Awaitable[Any]]] = {}

    def register_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Register a circuit breaker."""
        cb = CircuitBreaker(config)
        self.circuit_breakers[name] = cb
        return cb

    def register_error_handler(self, error_type: str, handler: Callable[[Exception], Awaitable[None]]) -> None:
        """Register an error handler for specific error types."""
        self.error_handlers[error_type] = handler

    def register_recovery_strategy(self, operation_name: str, strategy: Callable[[Exception], Awaitable[Any]]) -> None:
        """Register a recovery strategy for specific operations."""
        self.recovery_strategies[operation_name] = strategy

    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Handle an error with appropriate logging, tracking, and recovery."""
        error_dict = error.to_dict() if hasattr(error, 'to_dict') else {
            "error_type": error.__class__.__name__,
            "message": str(error),
            "timestamp": time.time()
        }

        if context:
            error_dict["context"] = context

        # Log error
        logger.error("Error handled by error handler", **error_dict)

        # Store in memory bank if configured
        if self.memory_bank:
            try:
                await self.memory_bank.log_decision(
                    f"Error occurred: {error.__class__.__name__}",
                    f"Error: {str(error)}",
                    {
                        "error_details": error_dict,
                        "component": context.get("component", "unknown") if context else "unknown",
                        "operation": context.get("operation", "unknown") if context else "unknown"
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log error to memory bank: {e}")

        # Call registered error handler
        error_type = error.__class__.__name__
        if error_type in self.error_handlers:
            try:
                await self.error_handlers[error_type](error)
            except Exception as e:
                logger.error(f"Error handler for {error_type} failed: {e}")

    @asynccontextmanager
    async def resilient_operation(self, operation_name: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[None, None]:
        """Context manager for resilient operations with error handling."""
        start_time = time.time()

        try:
            yield
            duration = time.time() - start_time
            logger.info(f"Operation {operation_name} completed successfully", duration=duration)

        except Exception as e:
            duration = time.time() - start_time
            context = context or {}
            context.update({
                "operation": operation_name,
                "duration": duration,
                "start_time": start_time
            })

            await self.handle_error(e, context)

            # Try recovery strategy
            if operation_name in self.recovery_strategies:
                try:
                    logger.info(f"Attempting recovery for {operation_name}")
                    recovery_result = await self.recovery_strategies[operation_name](e)
                    logger.info(f"Recovery successful for {operation_name}", recovery_result=recovery_result)
                    return  # Recovery successful
                except Exception as recovery_error:
                    logger.error(f"Recovery failed for {operation_name}: {recovery_error}")
                    await self.handle_error(recovery_error, {
                        **context,
                        "recovery_attempt": True,
                        "original_error": str(e)
                    })

            # Re-raise the original error if recovery failed or not available
            raise


def with_resilience(
    error_handler: ErrorHandler,
    circuit_breaker: Optional[str] = None,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    operation_name: Optional[str] = None
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator for adding resilience to functions."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            op_name = operation_name or f"{func.__module__}.{func.__name__}"

            # Use circuit breaker if specified
            if circuit_breaker and circuit_breaker in error_handler.circuit_breakers:
                cb = error_handler.circuit_breakers[circuit_breaker]
                return await cb.call(func, *args, **kwargs)

            # Exponential backoff retry logic
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    async with error_handler.resilient_operation(op_name, {
                        "attempt": attempt + 1,
                        "max_attempts": max_retries + 1,
                        "args": str(args) if args else None,
                        "kwargs": str(kwargs) if kwargs else None
                    }):
                        return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed for {op_name}, retrying in {delay:.2f}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {op_name}")
                        break

            raise last_exception

        return wrapper
    return decorator


class ErrorBoundary:
    """Error boundary that catches and handles errors in async contexts."""

    def __init__(self, error_handler: ErrorHandler, operation_name: str):
        self.error_handler = error_handler
        self.operation_name = operation_name
        self.errors: List[Exception] = []

    async def execute(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> Optional[T]:
        """Execute function within error boundary."""
        try:
            async with self.error_handler.resilient_operation(self.operation_name):
                return await func(*args, **kwargs)
        except Exception as e:
            self.errors.append(e)
            await self.error_handler.handle_error(e, {
                "operation": self.operation_name,
                "error_boundary_caught": True
            })
            return None

    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0

    def get_errors(self) -> List[Exception]:
        """Get all captured errors."""
        return self.errors.copy()


class Bulkhead:
    """Bulkhead pattern for limiting concurrent operations."""

    def __init__(self, max_concurrent: int, name: str = "default"):
        self.max_concurrent = max_concurrent
        self.name = name
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_operations = 0

    @asynccontextmanager
    async def limit(self) -> AsyncGenerator[None, None]:
        """Context manager for limiting concurrent operations."""
        async with self.semaphore:
            self.active_operations += 1
            try:
                yield
            finally:
                self.active_operations -= 1

    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "active_operations": self.active_operations,
            "available_slots": self.max_concurrent - self.active_operations
        }


@backoff.on_exception(
    backoff.expo,
    (FrameworkError, ProtocolError, ResourceError),
    max_tries=3,
    max_time=30,
    logger=logger
)
async def resilient_call(func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
    """Generic resilient function call with exponential backoff."""
    return await func(*args, **kwargs)


async def graceful_shutdown(error_handler: ErrorHandler, timeout: float = 30.0) -> None:
    """Perform graceful shutdown with proper error handling."""
    logger.info("Initiating graceful shutdown")

    shutdown_tasks: List[Awaitable[None]] = []

    # Add cleanup tasks here
    # shutdown_tasks.append(cleanup_database())
    # shutdown_tasks.append(cleanup_network_connections())

    if shutdown_tasks:
        try:
            await asyncio.wait_for(asyncio.gather(*shutdown_tasks), timeout=timeout)
            logger.info("Graceful shutdown completed")
        except asyncio.TimeoutError:
            logger.error(f"Graceful shutdown timed out after {timeout}s")
        except Exception as e:
            await error_handler.handle_error(e, {"operation": "graceful_shutdown"})
    else:
        logger.info("No cleanup tasks, shutdown immediate")


# Global error handler instance
_error_handler = None

def get_global_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _error_handler
    _error_handler = handler
