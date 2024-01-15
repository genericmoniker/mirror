"""Context given to plugins."""
import json
import logging
from datetime import datetime

from cryptography.fernet import Fernet
from sqlitedict import SqliteDict

from mirror.event_bus import Event, EventBus
from mirror.paths import INSTANCE_DIR
from mirror.plugin import Plugin

_logger = logging.getLogger(__name__)


class PluginContext:
    """Services provided to plugins.

    Plugins are provided with an instance of this class and do not create one
    themselves.
    """

    def __init__(self, plugin: Plugin, event_bus: EventBus) -> None:
        """Initialize the plugin context."""
        self._plugin = plugin
        self._event_bus = event_bus
        self.db = PluginDatabase(self.plugin_name)

    @property
    def plugin_name(self) -> str:
        """Get the plugin's name."""
        return self._plugin.name

    async def widget_updated(self, data: dict, widget_name: str | None = None) -> None:
        """Indicate that a widget has been updated.

        If appropriate, the widget will be refreshed via a server-sent event (SSE).

        :param data: Data to pass as the widget's template context.
        :param widget_name: Name of the widget to refresh, defaults to the plugin name.
        """
        event_name = self.plugin_name
        if widget_name:
            event_name += f".{widget_name}"
        event_name += ".refresh"

        event_data = self._plugin.render(context=data, widget=widget_name)

        await self._event_bus.post(Event(name=event_name, data=event_data))

    async def post_event(self, name: str, data: dict) -> None:  # noqa: ARG002
        """Post an event that is available to client-side JavaScript.

        :param name: Name of the event (see notes below).
        :param data: Data sent with the event. Send "" if there is no data.

        The plugin name is automatically used to namespace all events as they appear on
        the client side. For example, if the plugin name is `myplugin` and the event
        name is `myeventname`, the event name on the client side will be:

        `myplugin.myeventname`

        Some metadata keys are also automatically added to the event data:

        _source: The name of the plugin
        _time: When the event was raised
        """
        _logger.warning("post_event is deprecated; use widget_updated() instead")

    _connectivity_score = 0

    @property
    def is_connected(self) -> bool:
        """Whether the network is connected."""
        return PluginContext._connectivity_score >= 0

    def vote_connected(self) -> None:
        """Allow a plugin to vote that the network is connected."""
        score = min(PluginContext._connectivity_score + 1, 10)
        PluginContext._connectivity_score = score
        _logger.info(
            "%s votes connected; score: %s",
            self.plugin_name,
            score,
        )

    def vote_disconnected(self, cause: Exception) -> None:
        """Allow a plugin to vote that the network is disconnected."""
        score = max(PluginContext._connectivity_score - 1, -10)
        PluginContext._connectivity_score = score
        _logger.info(
            "%s votes disconnected because of %s; score: %s",
            self.plugin_name,
            cause,
            score,
        )


class PluginDatabase(SqliteDict):
    """Database for persistent plug-in data.

    The database exposes a dict-like interface, and can be used in either async or sync
    code without blocking I/O (since the underlying SqliteDict queues database
    operations to be handled on a separate thread).
    """

    _data_dir = INSTANCE_DIR
    _key = None

    def __init__(self, plugin_name: str, filename: str | None = None) -> None:
        """Initialize the database."""
        self._init_key()
        assert self._key is not None  # noqa: S101
        self._fernet: Fernet = Fernet(self._key)
        super().__init__(
            filename=filename or self._data_dir / "mirror.db",
            tablename=plugin_name,
            autocommit=True,
            encode=self._encrypted_json_encoder,
            decode=self._encrypted_json_decoder,
        )

    @staticmethod
    def _init_key() -> None:
        if PluginDatabase._key:
            return
        key_path = PluginDatabase._data_dir / "mirror.key"
        if not key_path.exists():
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            PluginDatabase._key = key
            _logger.debug("New database key created at %s", key_path.absolute())
        else:
            PluginDatabase._key = key_path.read_bytes()
            _logger.debug("Existing database key used at %s", key_path.absolute())

    def _encrypted_json_encoder(self, obj: object) -> bytes:
        return self._fernet.encrypt(json.dumps(obj, cls=_ExtendedEncoder).encode())

    def _encrypted_json_decoder(self, data: bytes) -> object:
        return json.loads(self._fernet.decrypt(data), cls=_ExtendedDecoder)


class _ExtendedEncoder(json.JSONEncoder):
    """JSON encoder that handles additional object types."""

    def default(self, o: object) -> object:
        if hasattr(o, "isoformat"):
            return {"_dt_": o.isoformat()}

        return json.JSONEncoder.default(self, o)


class _ExtendedDecoder(json.JSONDecoder):
    """JSON decoder that handles additional object types."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs["object_hook"] = self._object_hook
        super().__init__(*args, **kwargs)

    @staticmethod
    def _object_hook(obj: dict) -> object:
        if "_dt_" in obj:
            try:
                return datetime.fromisoformat(obj["_dt_"])
            except ValueError:
                pass
        return obj
