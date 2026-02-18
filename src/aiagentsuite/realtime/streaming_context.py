"""
Streaming Context Processor Module

Real-time context processing for handling continuous
context updates without restarts.
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json
from collections import deque


class ContextPriority(Enum):
    """Priority levels for context updates."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContextUpdate:
    """A single context update."""
    id: str
    key: str
    value: Any
    priority: ContextPriority = ContextPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = f"ctx_{self.timestamp.timestamp()}_{self.key}"


@dataclass
class ContextSnapshot:
    """A snapshot of the current context."""
    timestamp: datetime
    data: dict[str, Any]
    sources: dict[str, datetime]
    version: int


class StreamingContextProcessor:
    """
    Streaming context processor for real-time context updates.

    Provides:
    - Non-blocking context updates
    - Priority-based processing
    - Context buffering and batching
    - Change detection
    - Context history
    """

    def __init__(
        self,
        buffer_size: int = 100,
        batch_size: int = 10,
        flush_interval: float = 1.0,  # seconds
        max_history: int = 100,
    ):
        """
        Initialize streaming context processor.

        Args:
            buffer_size: Maximum updates to buffer
            batch_size: Number of updates to batch together
            flush_interval: Seconds between automatic flushes
            max_history: Maximum context snapshots to keep
        """
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_history = max_history

        self._context: dict[str, Any] = {}
        self._sources: dict[str, datetime] = {}
        self._version: int = 0
        self._buffer: deque[ContextUpdate] = deque(maxlen=buffer_size)
        self._history: deque[ContextSnapshot] = deque(maxlen=max_history)
        
        # Callbacks
        self._change_callbacks: list[Callable[[str, Any, Any], None]] = []
        self._flush_callbacks: list[Callable[[dict], None]] = []
        
        # Processing state
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the streaming context processor."""
        if self._running:
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_loop())

    async def stop(self) -> None:
        """Stop the streaming context processor."""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining buffer
        await self.flush()

    def update(
        self,
        key: str,
        value: Any,
        priority: ContextPriority = ContextPriority.NORMAL,
        source: str = "unknown",
    ) -> None:
        """
        Queue a context update for processing.

        Args:
            key: Context key to update
            value: New value
            priority: Update priority
            source: Source of the update
        """
        update = ContextUpdate(
            id="",
            key=key,
            value=value,
            priority=priority,
            source=source,
        )
        
        self._buffer.append(update)

    async def flush(self) -> None:
        """Process all buffered updates immediately."""
        if not self._buffer:
            return

        # Sort by priority (highest first)
        updates = sorted(self._buffer, key=lambda u: u.priority.value, reverse=True)
        self._buffer.clear()

        # Track changes for callbacks
        changes = {}

        for update in updates:
            old_value = self._context.get(update.key)
            
            # Skip if value hasn't changed
            if old_value == update.value:
                continue

            # Apply update
            self._context[update.key] = update.value
            self._sources[update.source] = update.timestamp
            self._version += 1
            
            changes[update.key] = (old_value, update.value)

        # Take snapshot
        snapshot = ContextSnapshot(
            timestamp=datetime.now(),
            data=self._context.copy(),
            sources=self._sources.copy(),
            version=self._version,
        )
        self._history.append(snapshot)

        # Trigger callbacks
        for key, (old, new) in changes.items():
            for callback in self._change_callbacks:
                try:
                    callback(key, old, new)
                except Exception:
                    pass

        for callback in self._flush_callbacks:
            try:
                callback(changes)
            except Exception:
                pass

    async def _process_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                
                if len(self._buffer) >= self.batch_size:
                    await self.flush()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self._context.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Get all current context."""
        return self._context.copy()

    def get_snapshot(self) -> ContextSnapshot:
        """Get current context snapshot."""
        return ContextSnapshot(
            timestamp=datetime.now(),
            data=self._context.copy(),
            sources=self._sources.copy(),
            version=self._version,
        )

    def get_history(self, limit: int = 10) -> list[ContextSnapshot]:
        """Get recent context history."""
        return list(self._history)[-limit:]

    def register_change_callback(
        self,
        callback: Callable[[str, Any, Any], None],
    ) -> None:
        """Register callback for context changes."""
        self._change_callbacks.append(callback)

    def register_flush_callback(
        self,
        callback: Callable[[dict], None],
    ) -> None:
        """Register callback for context flushes."""
        self._flush_callbacks.append(callback)

    def get_statistics(self) -> dict[str, Any]:
        """Get processor statistics."""
        return {
            "buffered_updates": len(self._buffer),
            "context_keys": len(self._context),
            "version": self._version,
            "history_size": len(self._history),
            "running": self._running,
        }

    def export_context(self) -> str:
        """Export current context as JSON."""
        return json.dumps({
            "version": self._version,
            "data": self._context,
            "sources": {
                k: v.isoformat() for k, v in self._sources.items()
            },
            "timestamp": datetime.now().isoformat(),
        }, indent=2)

    def import_context(self, json_data: str) -> None:
        """Import context from JSON."""
        data = json.loads(json_data)
        self._version = data.get("version", 0)
        self._context = data.get("data", {})
        self._sources = {
            k: datetime.fromisoformat(v) 
            for k, v in data.get("sources", {}).items()
        }


class AsyncStreamingContextProcessor(StreamingContextProcessor):
    """
    Async version of StreamingContextProcessor with additional
    async features like async generators for context streams.
    """

    async def stream_updates(self):
        """Yield context updates as they occur."""
        last_version = self._version
        
        while self._running:
            if self._version > last_version:
                # Get changes since last check
                snapshot = self.get_snapshot()
                yield snapshot
                last_version = self._version
            
            await asyncio.sleep(0.1)  # Poll every 100ms

    async def wait_for_key(
        self,
        key: str,
        timeout: Optional[float] = None,
    ) -> Any:
        """Wait for a specific key to appear in context."""
        if key in self._context:
            return self._context[key]
        
        future = asyncio.Future()
        
        def callback(k: str, old: Any, new: Any):
            if k == key and not future.done():
                future.set_result(new)
        
        self.register_change_callback(callback)
        
        try:
            if timeout:
                return await asyncio.wait_for(future, timeout)
            return await future
        finally:
            # Note: In production, you'd want to remove the callback
            pass
