from datetime import datetime, timedelta
from functools import partial
import json
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from cryptography.fernet import Fernet
from sqlitedict import SqliteDict


HERE = Path(__file__).parent


_scheduler = None


def start():
    """Initialize the plugin context module.

    Should be called once by the application before loading plugins.
    """
    global _scheduler
    _scheduler = BackgroundScheduler()
    _scheduler.start()


def stop():
    if _scheduler:
        _scheduler.shutdown()


class PluginContext:
    """Services provided to plugins.

    The context includes:
      db - A persistent dict. Values can be anything that is JSON serializable, and are
           highly obfuscated when stored (technically encrypted, but the key sits
           adjacent to the database file on disk).
      cache - An auto-refreshing dict. Plugins can add functions that do the appropriate
           refreshing on a regular interval.
    """

    _key = None

    def __init__(self, plugin_name) -> None:

        # db
        PluginContext._init_key()
        self._fernet = Fernet(PluginContext._key)
        filename = PluginContext._get_db_filename()
        self.db = SqliteDict(
            filename=filename,
            tablename=plugin_name,
            autocommit=True,
            encode=self._encrypted_json_encoder,
            decode=self._encrypted_json_decoder,
        )

        # cache
        self.cache = Cache(_scheduler, self.db)

    @staticmethod
    def _init_key():
        if PluginContext._key:
            return
        key_path = HERE / "instance" / "mirror.key"
        if not key_path.exists():
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            PluginContext._key = key
        else:
            PluginContext._key = key_path.read_bytes()

    @staticmethod
    def _get_db_filename():
        return str(HERE / "instance" / "mirror.db")

    def _encrypted_json_encoder(self, obj: object):
        return self._fernet.encrypt(json.dumps(obj, cls=ExtendedEncoder).encode())

    def _encrypted_json_decoder(self, data: bytes) -> object:
        return json.loads(self._fernet.decrypt(data), cls=ExtendedDecoder)


class ExtendedEncoder(json.JSONEncoder):
    """JSON encoder that handles additional object types."""

    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return {"_dt_": obj.isoformat()}

        return json.JSONEncoder.default(self, obj)


class ExtendedDecoder(json.JSONDecoder):
    """JSON decoder that handles additional object types."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, object_hook=self._object_hook)

    @staticmethod
    def _object_hook(obj):
        if "_dt_" in obj:
            try:
                return datetime.fromisoformat(obj["_dt_"])
            except ValueError:
                pass
        return obj


class Cache(dict):
    """A dict to which periodic refresh functions can be attached."""

    def __init__(self, scheduler, refresh_arg, **kwargs) -> None:
        """Create a new instance.

        :param scheduler: Scheduler instance for scheduling refreshes.
        :param refresh_arg: Argument to be passed to all refresh functions.
        """
        super().__init__(**kwargs)
        self._scheduler = scheduler
        self._refresh_arg = refresh_arg

    def add_refresh(self, key: str, interval: timedelta, refresh_func) -> None:
        """Add a refresh function to the cache.

        :param key: The key to be updated by the refresh function.
        :param interval: How often to call the refresh function.
        :param refresh_func: The function to be called to refresh the key's value.
            Receives the argument passed to Cache.__init__().
        """
        # Start with the initial value.
        refresh = partial(self._refresh, key, refresh_func)
        refresh()

        # Schedule updates.
        self._scheduler.add_job(
            refresh,
            "interval",
            name=f"Refresh {key}",
            seconds=interval.total_seconds(),
        )

    def _refresh(self, key: str, refresh_func) -> None:
        self[key] = refresh_func(self._refresh_arg)
