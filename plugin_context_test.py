from datetime import datetime, timedelta
import threading
from unittest import mock

from cryptography.fernet import Fernet
import pytest

from plugin_context import PluginContext, start, stop


@pytest.fixture(autouse=True, scope="module")
def memory_db():
    """Memory-only database."""
    # Set the encryption key to avoid hitting the key file on disk.
    PluginContext._key = Fernet.generate_key()
    # Patch the database filename to use an in-memory db.
    mock_target = "plugin_context.PluginContext._get_db_filename"
    with mock.patch(mock_target, return_value=":memory:"):
        yield


@pytest.fixture(autouse=True, scope="function")
def start_and_stop():
    """Automatically start and stop the context module."""
    start()
    yield
    stop()


def test_db_round_trip():
    context = PluginContext("test_plugin")

    test_data = [
        # Some JSON serializable data:
        ("str", "Some text 🦸‍♀️"),
        ("list", [1, 2, 3, 4, 5, True, False]),
        ("dict", {"one": 1, "two": 2, "three": 3, "hero": "🦸‍♂️"}),
        # And special handling for datetime:
        ("now", datetime.now()),
    ]
    for key, item in test_data:
        context.db[key] = item

    for key, item in test_data:
        assert context.db[key] == item


def test_cache_populates_on_add_refresh():
    def refresh_fn(db):
        return "🐙"

    context = PluginContext("test_plugin")
    context.cache.add_refresh("test cache key", timedelta(seconds=10), refresh_fn)
    assert context.cache["test cache key"] == "🐙"


def test_cache_schedules_refresh():

    event = threading.Event()
    first_call = [True]

    def refresh_fn(db):
        if first_call[0]:
            first_call[0] = False
            return "🦈"

        event.set()
        return "🐙"

    context = PluginContext("test_plugin")
    context.cache.add_refresh("test cache key", timedelta(seconds=0.1), refresh_fn)
    assert event.wait(timeout=5), "Timed out waiting for call to refresh."
    assert context.cache["test cache key"] == "🐙"
