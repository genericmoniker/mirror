import json
import logging
from asyncio import CancelledError, Queue
from dataclasses import dataclass
from typing import *

_logger = logging.getLogger(__name__)

# Event bus backing storage:
_queue = None

_TERMINATE_SENTINEL = "__exit__"


@dataclass
class Event:
    """An event that can be sent from the server."""

    name: str
    data: dict

    def as_sse_dict(self):
        return {
            "event": self.name,
            "data": json.dumps(self.data),
        }


class EventBus:
    """Bus for posting events and streaming them to listeners."""

    def __init__(self) -> None:
        self._listener_queues: List[Queue] = []
        self._cached_events: Dict[str, Event] = {}

    async def shutdown(self) -> None:
        for queue in self._listener_queues:
            await queue.put(_TERMINATE_SENTINEL)

    async def post(self, event: Event) -> None:
        """Post an event to the bus."""
        # Cache the most recent event.
        self._cached_events[event.name] = event

        # Post to each active queue.
        for queue in self._listener_queues:
            await queue.put(event)

    async def listen_for_events(self):
        """A generator that yields events (as dicts) from the bus."""
        queue = Queue(maxsize=50)

        # Queue the most recent events.
        for _, event in self._cached_events.items():
            await queue.put(event)

        # Subscribe to future events.
        self._listener_queues.append(queue)

        try:
            while True:
                event = await queue.get()
                if event == _TERMINATE_SENTINEL:
                    return
                yield event.as_sse_dict()
        finally:
            self._listener_queues.remove(queue)
