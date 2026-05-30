import pytest

from mirror.plugins.calendars.common import USER_CREDENTIALS
from mirrortests.doubles.plugin_context import PluginContext


@pytest.fixture
def context() -> PluginContext:
    context = PluginContext()
    context.db[USER_CREDENTIALS] = "fake user creds"
    context.config["client_id"] = "fake_client_id"
    context.config["client_secret"] = "fake_client_secret"
    return context
