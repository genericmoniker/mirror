# ruff: noqa: ANN201
from datetime import datetime

from cryptography.fernet import Fernet

from mirror.plugin_context import PluginDatabase


def test_database_round_trip():
    PluginDatabase._key = Fernet.generate_key()  # noqa: SLF001

    db = PluginDatabase("test_plugin", ":memory:")

    test_data = [
        # Some JSON serializable data:
        ("str", "Some text 🦸‍♀️"),
        ("list", [1, 2, 3, 4, 5, True, False]),
        ("dict", {"one": 1, "two": 2, "three": 3, "hero": "🦸‍♂️"}),
        # And special handling for datetime:
        ("now", datetime.now().astimezone()),
    ]
    for key, item in test_data:
        db[key] = item

    for key, item in test_data:
        assert db[key] == item
