import asyncio
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path
from sqlitedict import SqliteDict
from cryptography.fernet import Fernet
from mirror.event_bus import Event, post

_logger = logging.getLogger(__name__)


class PluginContext:
    """Services provided to plugins.

    Plugins are provided with an instance of this class and do not create one
    themselves.
    """

    def __init__(self, plugin_name) -> None:
        self.plugin_name = plugin_name
        self.db = PluginDatabase(plugin_name)

    def create_periodic_task(self, coro, interval: timedelta) -> None:
        """Wrap a coroutine in a task and schedule it every `interval`.

        :param coro: Coroutine to wrap.
        :param interval: Interval between executions.

        The task is scheduled to be run immediately, and rescheduled for the `interval`
        after the task completes.
        """
        task = asyncio.create_task(self._periodic_wrapper(coro, interval))
        task.set_name(f"{self.plugin_name}:{coro.__name__}")

    async def post_event(self, name: str, data: dict) -> None:
        """Post an event that is available to client-side JavaScript.

        :param name: Name of the event (see notes below).
        :param data: Data sent with the event.

        The plugin name is automatically used to namespace all events as they appear on
        the client side. For example:

        `myplugin:myeventname`
        """
        full_name = f"{self.plugin_name}:{name}"
        await post(Event(name=full_name, data=data))

    async def _periodic_wrapper(self, coro, interval: timedelta):
        while True:
            await coro(self)
            await asyncio.sleep(interval.total_seconds())


class PluginDatabase(SqliteDict):
    """Database for persistent plug-in data.

    The database exposes a dict-like interface, and can be used in either async or sync
    code without blocking I/O (since the underlying SqliteDict queues database
    operations to be handled on a separate thread).
    """
    _data_dir = Path(__file__).parent.parent.parent / 'instance'
    _key = None

    def __init__(self, plugin_name, filename=None):
        self._init_key()
        self._fernet = Fernet(self._key)
        super().__init__(
            filename=filename or self._data_dir / 'mirror.db',
            tablename=plugin_name,
            autocommit=True,
            encode=self._encrypted_json_encoder,
            decode=self._encrypted_json_decoder,
        )

    @staticmethod
    def _init_key():
        if PluginDatabase._key:
            return
        key_path = PluginDatabase._data_dir / 'mirror.key'
        if not key_path.exists():
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            PluginDatabase._key = key
            _logger.debug("New database key created at %s", key_path.absolute())
        else:
            PluginDatabase._key = key_path.read_bytes()
            _logger.debug("Existing database key used at %s", key_path.absolute())

    def _encrypted_json_encoder(self, obj: object):
        return self._fernet.encrypt(json.dumps(obj, cls=_ExtendedEncoder).encode())

    def _encrypted_json_decoder(self, data: bytes) -> object:
        return json.loads(self._fernet.decrypt(data), cls=_ExtendedDecoder)


class _ExtendedEncoder(json.JSONEncoder):
    """JSON encoder that handles additional object types."""

    def default(self, o):
        if hasattr(o, "isoformat"):
            return {"_dt_": o.isoformat()}

        return json.JSONEncoder.default(self, o)


class _ExtendedDecoder(json.JSONDecoder):
    """JSON decoder that handles additional object types."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs['object_hook'] = self._object_hook
        super().__init__(*args, **kwargs)

    @staticmethod
    def _object_hook(obj):
        if "_dt_" in obj:
            try:
                return datetime.fromisoformat(obj["_dt_"])
            except ValueError:
                pass
        return obj
