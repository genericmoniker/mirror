import pytest
from mirror.plugins.calendars.common import (
    CLIENT_CREDENTIALS,
    USER_CREDENTIALS,
)

from mirrortests.doubles.plugin_context import PluginContext


@pytest.fixture()
def context() -> PluginContext:
    context = PluginContext()
    context.db[USER_CREDENTIALS] = "fake user creds"
    context.db[CLIENT_CREDENTIALS] = "fake client creds"
    return context
