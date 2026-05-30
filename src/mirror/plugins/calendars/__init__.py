# ruff: noqa: F401
import logging

from mirror.errors import AuthError
from mirror.plugin_context import PluginContext

from .calendars import start_plugin, stop_plugin, wake_widgets
from .common import OAUTH_STATE_KEY, USER_CREDENTIALS
from .google_calendar import exchange_code_for_creds

_logger = logging.getLogger(__name__)


async def set_authorization_code(context: PluginContext, code: str, state: str) -> None:
    stored_state = context.db.get(OAUTH_STATE_KEY)
    if not stored_state or stored_state != state:
        raise AuthError("OAuth state mismatch for calendars.")
    user_creds = await exchange_code_for_creds(
        context.config["client_id"],
        context.config["client_secret"],
        code,
    )
    context.db[USER_CREDENTIALS] = user_creds
    del context.db[OAUTH_STATE_KEY]
    _logger.info("Calendar OAuth authorization successful.")
    wake_widgets()
