"""
AI Agent Suite Event Sourcing Architecture

Implements CQRS/Event Sourcing patterns for enterprise-grade 
data consistency and auditability.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Generic, TypeVar
from functools import wraps
import threading
import queue

T = TypeVar('T')


class EventType(Enum):
    """Types of domain events."""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    TASK_COMPLETED = "task_completed"
    SECURITY_VIOLATION = "security_violation"
    CONFIGURATION_CHANGED = "configuration_changed"


@dataclass
class DomainEvent:
    """Domain event representing business facts."""
    event_id: str = field(default_factory=lambda: f"evt_{int(datetime.now().timestamp() * 1000)}_{id(datetime.now())}")
    event_type: EventType = EventType.USER_CREATED
    aggregate_id: str = ""
    aggregate_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1

    @property
    def event_name(self) -> str:
        return self.event_type.value


@dataclass
class AggregateState:
    """Current state of an aggregate root."""
    aggregate_id: str
    aggregate_type: str
    version: int = 0
    state: Dict[str, Any] = field(default_factory=dict)
    applied_events: List[str] = field(default_factory=list)
    last_modified: datetime = field(default_factory=datetime.now)


class EventStore(ABC):
    """Abstract event store interface."""

    @abstractmethod
    async def save_event(self, event: DomainEvent) -> None:
        """Save an event to the store."""
        pass

    @abstractmethod
    async def get_events_for_aggregate(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Get all events for an aggregate."""
        pass

    @abstractmethod
    async def get_all_events(self, event_types: List[EventType] = None) -> List[DomainEvent]:
        """Get all events, optionally filtered by type."""
        pass


class InMemoryEventStore(EventStore):
    """In-memory event store implementation."""

    def __init__(self):
        self.events: Dict[str, List[DomainEvent]] = {}
        self._lock = asyncio.Lock()

    async def save_event(self, event: DomainEvent) -> None:
        """Save event to memory."""
        async with self._lock:
            if event.aggregate_id not in self.events:
                self.events[event.aggregate_id] = []

            self.events[event.aggregate_id].append(event)

    async def get_events_for_aggregate(self, aggregate_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Get events for aggregate."""
        async with self._lock:
            aggregate_events = self.events.get(aggregate_id, [])
            return [e for e in aggregate_events if e.version >= from_version]

    async def get_all_events(self, event_types: List[EventType] = None) -> List[DomainEvent]:
        """Get all events with optional filtering."""
        async with self._lock:
            all_events = []
            for aggregate_events in self.events.values():
                for event in aggregate_events:
                    if event_types is None or event.event_type in event_types:
                        all_events.append(event)

            # Sort by timestamp
            all_events.sort(key=lambda e: e.timestamp)
            return all_events


class AggregateRoot(ABC):
    """Base class for aggregate roots in event sourcing."""

    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self.uncommitted_events: List[DomainEvent] = []
        self.state: Dict[str, Any] = {}

    @abstractmethod
    def apply_event(self, event: DomainEvent) -> None:
        """Apply an event to update aggregate state."""
        pass

    def raise_event(self, event_type: EventType, data: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> None:
        """Raise a new domain event."""
        event = DomainEvent(
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            aggregate_type=self.__class__.__name__,
            data=data or {},
            metadata=metadata or {},
            version=self.version + 1
        )

        self.apply_event(event)
        self.uncommitted_events.append(event)
        self.version += 1

    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get all uncommitted events."""
        return self.uncommitted_events.copy()

    def commit_events(self) -> List[DomainEvent]:
        """Commit events and return them."""
        committed = self.uncommitted_events.copy()
        self.uncommitted_events.clear()
        return committed

    def load_from_events(self, events: List[DomainEvent]) -> None:
        """Load aggregate state from historical events."""
        for event in events:
            self.apply_event(event)
            self.version = max(self.version, event.version)


class EventSourcedRepository:
    """Repository for event-sourced aggregates."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    async def save(self, aggregate: AggregateRoot) -> None:
        """Save aggregate by persisting its events."""
        events = aggregate.get_uncommitted_events()
        if not events:
            return

        for event in events:
            await self.event_store.save_event(event)

        aggregate.commit_events()

    async def load(self, aggregate_class: type, aggregate_id: str) -> Optional[AggregateRoot]:
        """Load aggregate from its event history."""
        events = await self.event_store.get_events_for_aggregate(aggregate_id)

        if not events:
            return None

        aggregate = aggregate_class(aggregate_id)
        aggregate.load_from_events(events)
        return aggregate


class CommandHandler(ABC, Generic[T]):
    """Handles commands and produces events."""

    @abstractmethod
    async def handle(self, command: T) -> List[DomainEvent]:
        """Handle a command and return resulting events."""
        pass


class EventHandler(ABC):
    """Handles events for projections and side effects."""

    @abstractmethod
    async def handle_event(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        pass


class CQRSReadModel(ABC):
    """Read model for CQRS pattern."""

    @abstractmethod
    async def update_from_events(self, events: List[DomainEvent]) -> None:
        """Update read model from events."""
        pass

    @abstractmethod
    async def query(self, query: Dict[str, Any]) -> Any:
        """Query the read model."""
        pass


class EventBus:
    """In-memory event bus for event sourcing."""

    def __init__(self):
        self.handlers: Dict[EventType, List[EventHandler]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to an event type."""
        async with self._lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        async with self._lock:
            handlers = self.handlers.get(event.event_type, [])

            # Publish asynchronously
            publish_tasks = []
            for handler in handlers:
                task = asyncio.create_task(self._safe_handle_event(handler, event))
                publish_tasks.append(task)

            if publish_tasks:
                await asyncio.gather(*publish_tasks, return_exceptions=True)

    async def _safe_handle_event(self, handler: EventHandler, event: DomainEvent) -> None:
        """Handle event with error isolation."""
        try:
            await handler.handle_event(event)
        except Exception as e:
            # Log error but don't crash the system
            print(f"Event handler error: {e}")


class UserAggregate(AggregateRoot):
    """Example aggregate for users."""

    def apply_event(self, event: DomainEvent) -> None:
        """Apply event to user aggregate."""
        if event.event_type == EventType.USER_CREATED:
            self.state.update({
                "name": event.data.get("name", ""),
                "email": event.data.get("email", ""),
                "role": event.data.get("role", "user"),
                "created_at": event.timestamp.isoformat(),
                "active": True
            })
        elif event.event_type == EventType.USER_UPDATED:
            self.state.update(event.data)
            self.state["updated_at"] = event.timestamp.isoformat()
        elif event.event_type == EventType.USER_DELETED:
            self.state["active"] = False
            self.state["deleted_at"] = event.timestamp.isoformat()


class UserReadModel(CQRSReadModel):
    """Read model for users."""

    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}

    async def update_from_events(self, events: List[DomainEvent]) -> None:
        """Update user read model from events."""
        for event in events:
            if event.aggregate_type == "UserAggregate":
                if event.event_type == EventType.USER_CREATED:
                    self.users[event.aggregate_id] = {
                        "user_id": event.aggregate_id,
                        "name": event.data.get("name", ""),
                        "email": event.data.get("email", ""),
                        "role": event.data.get("role", "user"),
                        "active": True,
                        "created_at": event.timestamp.isoformat()
                    }
                elif event.event_type == EventType.USER_UPDATED:
                    if event.aggregate_id in self.users:
                        self.users[event.aggregate_id].update(event.data)
                        self.users[event.aggregate_id]["updated_at"] = event.timestamp.isoformat()
                elif event.event_type == EventType.USER_DELETED:
                    if event.aggregate_id in self.users:
                        self.users[event.aggregate_id]["active"] = False
                        self.users[event.aggregate_id]["deleted_at"] = event.timestamp.isoformat()

    async def query(self, query: Dict[str, Any]) -> Any:
        """Query the user read model."""
        user_id = query.get("user_id")
        if user_id:
            return self.users.get(user_id)

        # Return all active users
        return [user for user in self.users.values() if user.get("active", True)]


class CreateUserCommand:
    """Command to create a user."""
    def __init__(self, user_id: str, name: str, email: str, role: str = "user"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role


class UpdateUserCommand:
    """Command to update a user."""
    def __init__(self, user_id: str, updates: Dict[str, Any]):
        self.user_id = user_id
        self.updates = updates


class UserCommandHandler(CommandHandler):
    """Handles user commands."""

    def __init__(self, repository: EventSourcedRepository):
        self.repository = repository

    async def handle(self, command: Any) -> List[DomainEvent]:
        """Handle user commands."""
        if isinstance(command, CreateUserCommand):
            return await self._handle_create_user(command)
        elif isinstance(command, UpdateUserCommand):
            return await self._handle_update_user(command)
        else:
            raise ValueError(f"Unknown command type: {type(command)}")

    async def _handle_create_user(self, command: CreateUserCommand) -> List[DomainEvent]:
        """Handle user creation."""
        # Validate - check if user already exists
        existing = await self.repository.load(UserAggregate, command.user_id)
        if existing:
            raise ValueError(f"User {command.user_id} already exists")

        # Create new aggregate
        user = UserAggregate(command.user_id)
        user.raise_event(
            EventType.USER_CREATED,
            {
                "name": command.name,
                "email": command.email,
                "role": command.role
            }
        )

        return user.get_uncommitted_events()

    async def _handle_update_user(self, command: UpdateUserCommand) -> List[DomainEvent]:
        """Handle user update."""
        user = await self.repository.load(UserAggregate, command.user_id)
        if not user:
            raise ValueError(f"User {command.user_id} not found")

        user.raise_event(EventType.USER_UPDATED, command.updates)
        return user.get_uncommitted_events()


class UserEventHandler(EventHandler):
    """Handles user events for projections."""

    def __init__(self, read_model: UserReadModel):
        self.read_model = read_model

    async def handle_event(self, event: DomainEvent) -> None:
        """Handle user events."""
        await self.read_model.update_from_events([event])


class EventSourcingManager:
    """Central manager for event sourcing architecture."""

    def __init__(self, event_store: EventStore = None):
        self.event_store = event_store or InMemoryEventStore()
        self.repository = EventSourcedRepository(self.event_store)
        self.event_bus = EventBus()
        self.command_handlers: Dict[str, CommandHandler] = {}
        self.projections: Dict[str, CQRSReadModel] = {}

        # Set up example domain
        self._setup_example_domain()

    def _setup_example_domain(self) -> None:
        """Set up the user domain example."""
        # Create read model
        user_read_model = UserReadModel()
        self.projections["users"] = user_read_model

        # Create command handler
        user_command_handler = UserCommandHandler(self.repository)
        self.command_handlers["user"] = user_command_handler

        # Create event handler and subscribe
        user_event_handler = UserEventHandler(user_read_model)

        # Subscribe to user events synchronously
        for event_type in [EventType.USER_CREATED, EventType.USER_UPDATED, EventType.USER_DELETED]:
            if event_type not in self.event_bus.handlers:
                self.event_bus.handlers[event_type] = []
            self.event_bus.handlers[event_type].append(user_event_handler)

    async def execute_command(self, command: Any) -> str:
        """Execute a command and publish resulting events."""
        # Determine command type - group by domain entity
        command_class_name = command.__class__.__name__

        # Map command classes to handler keys
        if command_class_name in ['CreateUserCommand', 'UpdateUserCommand']:
            command_type = 'user'
        else:
            # Fallback to removing 'Command' suffix and lowercasing
            command_type = command_class_name.replace("Command", "").lower()

        handler = self.command_handlers.get(command_type)
        if not handler:
            raise ValueError(f"No handler for command type: {command_type}")

        # Handle command
        events = await handler.handle(command)

        # Save events
        aggregate_id = getattr(command, 'user_id', 'unknown')
        aggregate = await self.repository.load(UserAggregate, aggregate_id) or UserAggregate(aggregate_id)
        aggregate.uncommitted_events = events.copy()  # Make a copy to avoid clearing the original list
        await self.repository.save(aggregate)

        # Publish events
        for event in events:
            await self.event_bus.publish(event)

        return aggregate_id

    async def query_read_model(self, model_name: str, query: Dict[str, Any] = None) -> Any:
        """Query a read model."""
        model = self.projections.get(model_name)
        if not model:
            raise ValueError(f"No read model named: {model_name}")

        return await model.query(query or {})

    async def get_event_history(self, aggregate_id: str) -> List[DomainEvent]:
        """Get complete event history for an aggregate."""
        return await self.event_store.get_events_for_aggregate(aggregate_id)

    async def replay_events_to_projection(self, projection_name: str, from_time: datetime = None) -> None:
        """Replay all events to a projection."""
        events = await self.event_store.get_all_events()

        # Filter by time if specified
        if from_time:
            events = [e for e in events if e.timestamp >= from_time]

        if projection_name in self.projections:
            projection = self.projections[projection_name]
            await projection.update_from_events(events)

    async def get_aggregate_at_version(self, aggregate_id: str, version: int) -> Optional[AggregateRoot]:
        """Get aggregate state at a specific version."""
        events = await self.event_store.get_events_for_aggregate(aggregate_id, version)
        if not events:
            return None

        aggregate = UserAggregate(aggregate_id)
        aggregate.load_from_events(events)
        return aggregate


# Global event sourcing manager instance
_event_sourcing_manager = None

def get_global_event_sourcing_manager() -> EventSourcingManager:
    """Get the global event sourcing manager instance."""
    global _event_sourcing_manager
    if _event_sourcing_manager is None:
        _event_sourcing_manager = EventSourcingManager()
    return _event_sourcing_manager

def set_global_event_sourcing_manager(manager: EventSourcingManager) -> None:
    """Set the global event sourcing manager instance."""
    global _event_sourcing_manager
    _event_sourcing_manager = manager
