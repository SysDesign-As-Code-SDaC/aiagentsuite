"""
Interfaces and Contracts for AI Agent Suite
"""

from typing import Dict, Any, List, Optional, Protocol, runtime_checkable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


class ProtocolExecutionStatus(Enum):
    """Status of protocol execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProtocolPhaseStatus(Enum):
    """Status of individual protocol phases."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class ProtocolExecutionContextData:
    """Data object for protocol execution context."""
    protocol_name: str
    execution_id: str
    start_time: datetime
    status: ProtocolExecutionStatus
    current_phase: int
    phases: List[Dict[str, Any]]
    results: Dict[str, Any]
    errors: List[str]
    metadata: Dict[str, Any]


@runtime_checkable
class IProtocolPhase(Protocol):
    """Interface for a protocol phase."""

    number: int
    title: str
    content: str

    async def execute(self, context: Any) -> Dict[str, Any]:
        """Execute the phase."""
        ...


@runtime_checkable
class IProtocolExecutor(Protocol):
    """Interface for protocol executor."""

    async def initialize(self) -> None:
        """Initialize the executor."""
        ...

    async def list_protocols(self) -> Dict[str, Any]:
        """List available protocols."""
        ...

    async def execute_protocol(self, protocol_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a protocol."""
        ...


@runtime_checkable
class IMemoryBank(Protocol):
    """Interface for memory bank operations."""

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        """Get context from memory bank."""
        ...

    async def update_context(self, context_type: str, content: str) -> None:
        """Update context in memory bank."""
        ...

    async def log_decision(self, decision: str, rationale: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log a decision."""
        ...
