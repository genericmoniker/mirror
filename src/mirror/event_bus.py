"""Event support."""
import logging
from asyncio import Queue
from collections.abc import AsyncGenerator
from dataclasses import dataclass

_TERMINATE_SENTINEL = "__exit__"

_logger = logging.getLogger(__name__)


@dataclass
class Event:
    """An event that can be sent from the server."""

    name: str
    data: str

    def as_sse_dict(self) -> dict:
        """Get the event as a dict for SSE."""
        return {
            "event": self.name,
            "data": self.data,
        }


class EventBus:
    """Bus for posting events and streaming them to listeners."""

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._listener_queues: list[Queue] = []
        self._cached_events: dict[str, Event] = {}

    async def shutdown(self) -> None:
        """Shutdown the event bus."""
        for queue in self._listener_queues:
            _logger.info("queuing terminate sentinel")
            await queue.put(_TERMINATE_SENTINEL)

    async def post(self, event: Event) -> None:
        """Post an event to the bus.

        If the event is the same as the last event posted (not including data['_time'])
        then it will not be sent to clients.
        """
        _logger.debug("Event posted: %s", event)

        # Don't send if there's nothing new.
        cached = self._cached_events.get(event.name)
        if cached == event:
            return

        # Cache the most recent event.
        self._cached_events[event.name] = event

        # Post to each active queue.
        for queue in self._listener_queues:
            await queue.put(event)

    async def listen_for_events(self) -> AsyncGenerator:
        """Yield events (as dicts) from the bus."""
        queue: Queue = Queue(maxsize=50)

        # Queue the most recent events.
        for event in self._cached_events.values():
            await queue.put(event)

        # Subscribe to future events.
        self._listener_queues.append(queue)

        try:
            while True:
                event = await queue.get()
                if event == _TERMINATE_SENTINEL:
                    _logger.info("terminating event generator")
                    return
                yield event.as_sse_dict()
        finally:
            self._listener_queues.remove(queue)
