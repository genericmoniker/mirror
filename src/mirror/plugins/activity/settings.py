"""Settings page for the activity plugin.

Part of the settings page's functionality is to set up the OAuth2 credentials for the
plugin, which are then stored in the database under a key that is the person's name.
After initial setup, the data for a person (e.g. db["Joe"]) has:

{
    "client_id": "<client_id>",
    "client_secret": "<client_secret>",
}

With this data, the authorization flow can be started. The user is redirected to the
Fitbit authorization page, where they log in and authorize the app. The Fitbit API then
redirects the user back to the plugin's redirect URI with an authorization code. The
plugin then exchanges this code for an access token and refresh token and stores them in
the database under the person's name. The database would then look like this:

{
    "client_id": "<client_id>",
    "client_secret": "<client_secret>",
    "access_token": "<access_token>",
    "refresh_token": "<refresh_token>",
}

The fitbit.py module uses these credentials to make requests to the Fitbit API. It uses
the access token to authenticate the requests and the refresh token to get a new access
token when the current one expires.
"""

import logging
from pathlib import Path

import httpx
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugins.activity.fitbit import get_access_token
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

_logger = logging.getLogger(__name__)


def create_settings_application(
    base_template_dir: Path,
    config_context: PluginConfigureContext,
) -> Starlette:
    """Create the settings application for the plugin."""
    template_dir = Path(__file__).parent
    app = Starlette()
    app.state.templates = Jinja2Templates(directory=[base_template_dir, template_dir])
    app.state.config_context = config_context
    app.add_route("/auth", auth, name="redirect_uri")
    app.add_route("/", settings, methods=["GET"])
    return app


async def settings(request: Request) -> Response:
    """Handle the settings page for the plugin."""
    db = request.app.state.config_context.db
    context = {
        "db": db,
        "redirect_uri": str(request.url_for("redirect_uri")),
    }
    templates = request.app.state.templates
    return templates.TemplateResponse(request, "activity-settings.html", context)


async def auth(request: Request) -> Response:
    """Handle the authorization callback to the redirect URI for the plugin.

    Extract the authorization code from the query parameters and exchange it for an
    access token and refresh token. Store these tokens in the database.
    """
    authorization_code = request.query_params["code"]
    person_name = request.query_params["state"]
    db = request.app.state.config_context.db
    creds = db[person_name]
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            access_token, refresh_token = await get_access_token(
                client,
                authorization_code,
                client_id,
                client_secret,
                str(request.url_for("redirect_uri")),
            )
        creds["access_token"] = access_token
        creds["refresh_token"] = refresh_token
        db[person_name] = creds  # Assign all at once so the DB detects the change.
        _logger.info(
            "Authorization successful for %s.\n%s\n%s",
            person_name,
            access_token,
            refresh_token,
        )
        return Response("Authorization successful.")
    except Exception as ex:
        _logger.exception("Error handling authorization response.")
        return Response(f"Error: {ex}", status_code=500)
