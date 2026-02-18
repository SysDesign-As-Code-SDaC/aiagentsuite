"""
Event Bus Module

Event-driven architecture for decoupled communication
between system components.
"""

from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import threading
import uuid
from collections import defaultdict
from weakref import WeakSet


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventType(Enum):
    """Predefined event types."""
    # Context events
    CONTEXT_UPDATED = "context.updated"
    CONTEXT_RESET = "context.reset"
    
    # Configuration events
    CONFIG_CHANGED = "config.changed"
    CONFIG_RESET = "config.reset"
    
    # Protocol events
    PROTOCOL_STARTED = "protocol.started"
    PROTOCOL_COMPLETED = "protocol.completed"
    PROTOCOL_FAILED = "protocol.failed"
    
    # Learning events
    PATTERN_DETECTED = "pattern.detected"
    LEARNING_GENERATED = "learning.generated"
    IMPROVEMENT_PROPOSED = "improvement.proposed"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"
    
    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """An event in the system."""
    id: str
    type: EventType
    data: dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    correlation_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


# Type alias for event handlers
EventHandler = Callable[[Event], Any]


@dataclass
class Subscription:
    """Event subscription."""
    id: str
    event_type: EventType
    handler: EventHandler
    priority: EventPriority
    filter_fn: Optional[Callable[[Event], bool]] = None
    persistent: bool = True


class EventBus:
    """
    Event bus for publish-subscribe messaging.

    Provides:
    - Decoupled event communication
    - Priority-based event handling
    - Event filtering
    - Async and sync handling
    - Event history
    """

    def __init__(
        self,
        async_mode: bool = False,
        max_history: int = 1000,
        enable_logging: bool = True,
    ):
        """
        Initialize event bus.

        Args:
            async_mode: Use async event handling
            max_history: Maximum events to keep in history
            enable_logging: Enable event logging
        """
        self.async_mode = async_mode
        self.max_history = max_history
        self.enable_logging = enable_logging

        # Subscriptions by event type
        self._subscriptions: Dict[EventType, List[Subscription]] = defaultdict(list)
        
        # Global subscriptions (receive all events)
        self._global_subscriptions: List[Subscription] = []
        
        # Event history
        self._history: List[Event] = []
        
        # Lock for thread safety
        self._lock = threading.RLock()
        
        # Async handling
        self._async_queue: Optional[asyncio.Queue] = None
        self._processor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start async event processing."""
        if not self.async_mode:
            return
        
        self._async_queue = asyncio.Queue()
        self._processor_task = asyncio.create_task(self._process_events())

    async def stop(self) -> None:
        """Stop async event processing."""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

    async def _process_events(self) -> None:
        """Process events from async queue."""
        while True:
            try:
                event = await self._async_queue.get()
                await self._dispatch_event(event)
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
        priority: EventPriority = EventPriority.NORMAL,
        filter_fn: Optional[Callable[[Event], bool]] = None,
        persistent: bool = True,
    ) -> str:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Handler function
            priority: Handler priority
            filter_fn: Optional filter function
            persistent: Whether subscription persists after one call

        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        subscription = Subscription(
            id=subscription_id,
            event_type=event_type,
            handler=handler,
            priority=priority,
            filter_fn=filter_fn,
            persistent=persistent,
        )

        with self._lock:
            self._subscriptions[event_type].append(subscription)
            # Sort by priority (highest first)
            self._subscriptions[event_type].sort(
                key=lambda s: s.priority.value, reverse=True
            )

        return subscription_id

    def subscribe_global(
        self,
        handler: EventHandler,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> str:
        """
        Subscribe to all events.

        Args:
            handler: Handler function
            priority: Handler priority

        Returns:
            Subscription ID
        """
        return self.subscribe(
            EventType.CUSTOM,  # Use CUSTOM as placeholder
            handler,
            priority,
            persistent=True,
        )

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: ID of subscription to remove

        Returns:
            True if unsubscribed successfully
        """
        with self._lock:
            # Check specific subscriptions
            for event_type, subs in self._subscriptions.items():
                for i, sub in enumerate(subs):
                    if sub.id == subscription_id:
                        subs.pop(i)
                        return True
            
            # Check global subscriptions
            for i, sub in enumerate(self._global_subscriptions):
                if sub.id == subscription_id:
                    self._global_subscriptions.pop(i)
                    return True

        return False

    def publish(
        self,
        event_type: EventType,
        data: Optional[dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        source: str = "unknown",
        correlation_id: Optional[str] = None,
    ) -> Event:
        """
        Publish an event.

        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority
            source: Event source
            correlation_id: Optional correlation ID

        Returns:
            The published event
        """
        event = Event(
            id="",
            type=event_type,
            data=data or {},
            priority=priority,
            source=source,
            correlation_id=correlation_id,
        )

        if self.async_mode and self._async_queue:
            # Queue for async processing
            self._async_queue.put_nowait(event)
        else:
            # Process synchronously
            self._dispatch_event(event)

        return event

    async def publish_async(
        self,
        event_type: EventType,
        data: Optional[dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        source: str = "unknown",
    ) -> Event:
        """Async version of publish."""
        return self.publish(event_type, data, priority, source)

    async def _dispatch_event(self, event: Event) -> None:
        """Dispatch event to handlers."""
        handlers_called = []

        with self._lock:
            # Add to history
            self._history.append(event)
            if len(self._history) > self.max_history:
                self._history = self._history[-self.max_history:]

            # Get subscriptions for this event type
            subscriptions = list(self._subscriptions.get(event.type, []))
            # Also get global subscriptions
            subscriptions.extend(self._global_subscriptions)

        # Call handlers
        for subscription in subscriptions:
            # Apply filter if present
            if subscription.filter_fn and not subscription.filter_fn(event):
                continue

            try:
                if asyncio.iscoroutinefunction(subscription.handler):
                    await subscription.handler(event)
                else:
                    subscription.handler(event)
                
                handlers_called.append(subscription.id)
            except Exception:
                pass  # Log errors in production

        # Remove non-persistent subscriptions
        if not subscription.persistent:
            self.unsubscribe(subscription.id)

        return event

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get event history.

        Args:
            event_type: Optional filter by event type
            limit: Maximum events to return

        Returns:
            List of events
        """
        with self._lock:
            if event_type:
                return [
                    e for e in self._history
                    if e.type == event_type
                ][-limit:]
            return self._history[-limit:]

    def get_subscriptions(
        self,
        event_type: Optional[EventType] = None,
    ) -> List[Subscription]:
        """Get active subscriptions."""
        with self._lock:
            if event_type:
                return list(self._subscriptions.get(event_type, []))
            return [
                sub for subs in self._subscriptions.values()
                for sub in subs
            ]

    def clear_subscriptions(
        self,
        event_type: Optional[EventType] = None,
    ) -> int:
        """
        Clear subscriptions.

        Args:
            event_type: Optional specific event type to clear

        Returns:
            Number of subscriptions cleared
        """
        with self._lock:
            if event_type:
                count = len(self._subscriptions.get(event_type, []))
                self._subscriptions[event_type] = []
                return count
            else:
                count = sum(len(subs) for subs in self._subscriptions.values())
                self._subscriptions.clear()
                self._global_subscriptions.clear()
                return count

    def get_statistics(self) -> dict[str, Any]:
        """Get event bus statistics."""
        with self._lock:
            event_counts = defaultdict(int)
            for event in self._history:
                event_counts[event.type.value] += 1

            return {
                "total_events": len(self._history),
                "event_counts": dict(event_counts),
                "active_subscriptions": sum(
                    len(subs) for subs in self._subscriptions.values()
                ),
                "global_subscriptions": len(self._global_subscriptions),
            }


class AsyncEventBus(EventBus):
    """
    Async-only event bus.
    """

    def __init__(self, *args, **kwargs):
        kwargs["async_mode"] = True
        super().__init__(*args, **kwargs)

    async def publish_and_wait(
        self,
        event_type: EventType,
        data: Optional[dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        source: str = "unknown",
        timeout: Optional[float] = None,
    ) -> Event:
        """
        Publish event and wait for handlers to complete.

        Args:
            event_type: Type of event
            data: Event data
            priority: Event priority
            source: Event source
            timeout: Optional timeout

        Returns:
            The published event
        """
        event = Event(
            id="",
            type=event_type,
            data=data or {},
            priority=priority,
            source=source,
        )

        if timeout:
            try:
                await asyncio.wait_for(
                    self._dispatch_event(event),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                pass
        else:
            await self._dispatch_event(event)

        return event
