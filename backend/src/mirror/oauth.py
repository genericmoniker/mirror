"""Simple OAuth 2.0 helper library."""
import logging
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Queue
from threading import Thread
from time import sleep
from urllib.parse import parse_qs, urlparse

from authlib.integrations.httpx_client import OAuth2Client

logger = logging.getLogger(__name__)


def authorize(
    auth_url: str,
    client_id: str,
    client_secret: str,
    scope: str,
    redirect_uri: str,
    **kwargs: dict,
) -> tuple[str, str]:
    """Interactively prompt the user for access to protected resources.

    Uses an OAuth 2.0 authorization code flow, which requires a browser and user input.

    The return value is a tuple of:
    - The path and query string values sent to the redirect URI
    - The authorization code state (used internally for CSRF checks)

    If this succeeds, an access token can be retrieved by calling `fetch_token`
    including the return values of `authorize` as `auth_response` and `state`.

    :return: tuple of (auth_response, state)
    """
    auth_client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        redirect_uri=redirect_uri,
    )
    url, state = auth_client.create_authorization_url(auth_url, **kwargs)

    server = _AuthHTTPServer(redirect_uri)
    server.start()

    # Give the server a moment to start.
    # More elegant would be to wait until it responds to a liveness check.
    sleep(3)

    print("Launching your browser to continue authorization...")
    webbrowser.open(url)

    response = server.wait_for_auth_redirect()
    error = _get_authorize_response_error(response)
    if error:
        msg = f"Authorization failed: {error}"
        raise AuthError(msg)

    return response, state


class AuthError(Exception):
    """An error occurred during authorization."""


def fetch_token(  # noqa: PLR0913
    token_url: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    auth_response: str,
    state: str,
) -> dict:
    """Fetch an access token.

    The access token can then be used to access protected resources.

    :return: dict of token values, such as "access_token", "refresh_token",
        "expires_at", etc.
    """
    auth_client = OAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        state=state,
    )

    return auth_client.fetch_token(token_url, authorization_response=auth_response)


def _get_authorize_response_error(response: str) -> list[str] | None:
    """Get the authorization error from a redirect URI, if any.

    When the authorization server redirects to the redirect URI, it will either include
    the auth code that can be exchanged for an access token or an error. For example:

    /auth?error=access_denied&state=abc123
    """
    result = urlparse(response)
    query = parse_qs(result.query)
    return query.get("error")


class _AuthHTTPServer:
    """Simple HTTP server to handle authorization redirects.

    Note that on Windows this will trigger a "Windows Security Alert" and
    prompt the user to allow access through the firewall.
    """

    class _AuthServerHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()
            if _get_authorize_response_error(self.path):  # path includes query string
                self.wfile.write(ERROR_HTML)
            else:
                self.wfile.write(SUCCESS_HTML)
            logger.debug("Queueing %s", self.path)
            self.server.queue.put(self.path)  # type: ignore

    def __init__(self, url: str) -> None:
        self.url = urlparse(url)
        self.queue: Queue = Queue()
        self.server: HTTPServer | None = None

    def start(self) -> None:
        """Start the server."""
        thread = Thread(target=self._run_server, name="HTTPServer")
        thread.start()

    def wait_for_auth_redirect(self) -> str:
        """Wait for the authorization redirect.

        :return: the path + query string of the redirect URI from the auth server.
            This will include the auth code or an error in the query string.
        """
        path = ""
        while self.url.path not in path:
            path = self.queue.get()
            logger.debug("Received %s", path)
        logger.debug("Matched expected redirect; stopping server.")
        assert self.server  # noqa: S101
        self.server.shutdown()
        return path

    def _run_server(self) -> None:
        address = ("", self.url.port or 80)
        self.server = HTTPServer(address, _AuthHTTPServer._AuthServerHandler)
        self.server.queue = self.queue  # type: ignore
        self.server.serve_forever()


SUCCESS_HTML = b"""
    <!doctype html>
    <html lang=en>
    <head>
    <meta charset=utf-8>
    <title>Success</title>
    </head>
    <body>
    <h1>Successfully Authorized</h1>
    <p>Feel free to close this window/tab now.</p>
    </body>
    </html>
"""

ERROR_HTML = b"""
    <!doctype html>
    <html lang=en>
    <head>
    <meta charset=utf-8>
    <title>Failed</title>
    </head>
    <body>
    <h1>Authorization Failed</h1>
    <p>Feel free to close this window/tab now.</p>
    </body>
    </html>
"""
