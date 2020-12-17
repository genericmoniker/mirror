import json
from asyncio import CancelledError, Queue
from dataclasses import dataclass
import logging

_logger = logging.getLogger(__name__)

# Event bus backing storage:
_queue = None

_TERMINATE_SENTINEL = '__exit__'


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


async def start():
    """Initialize the event bus."""
    _logger.debug('Event bus starting')
    global _queue  # pylint:disable=global-statement
    _queue = Queue(maxsize=20)


async def shutdown():
    """Terminate the event bus."""
    if not _queue:
        raise Exception('Call `start()` first.')
    _logger.debug('Event bus shutting down')
    await _queue.put(_TERMINATE_SENTINEL)


async def post(event: Event):
    """Post an event to the bus."""
    if not _queue:
        raise Exception('Call `start()` first.')
    await _queue.put(event)


async def event_generator(request):
    """A generator that yields events (as dicts) from the bus."""
    if not _queue:
        raise Exception('Call `start()` first.')
    try:
        while True:
            disconnected = await request.is_disconnected()
            if disconnected:
                _logger.debug("Disconnecting client %s", request.client)
                return
            event = await _queue.get()
            if event == _TERMINATE_SENTINEL:
                return
            yield event.as_sse_dict()
    except CancelledError as ex:
        _logger.debug("Disconnected from client (via refresh/close) %s", request.client)
        raise ex
