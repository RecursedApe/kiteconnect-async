import hashlib
import httpx

from .__version__ import __version__, __title__
from kiteconnect_async.routes import Route
import routes as APIRoutes


class Kite:
    """
    The Kite Connect API wrapper class.
    In production, you may initialise a single instance of this class per `api_key`.
    """

    # Default root API endpoint. It's possible to
    # override this by passing the `root` parameter during initialisation.
    _base_url = "https://api.kite.trade"
    _login_url = "https://kite.zerodha.com/connect/login"
    _default_timeout = 7  # In seconds

    # Kite connect header version
    kite_header_version = "3"

    access_token: str | None

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

        default_headers = {
            "X-Kite-Version": self.kite_header_version,
            "User-Agent": self._user_agent(),
        }
        self.session = httpx.Client(
            base_url=self._base_url,
            headers=default_headers,
            timeout=self._default_timeout,
        )

    def get_login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s&v=%s" % (
            self._base_url,
            self.api_key,
            self.kite_header_version,
        )

    def generate_session(self, request_token: str):
        h = hashlib.sha256(
            self.api_key.encode("utf-8")
            + request_token.encode("utf-8")
            + self.api_secret.encode("utf-8")
        )
        checksum = h.hexdigest()

        resp = self._request(
            APIRoutes.API_TOKEN,
            query_params={
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum,
            },
        )

        if "access_token" in resp:
            self.set_access_token()

        return resp

    def set_access_token(self, access_token: str):
        self.access_token = access_token

    def _request(
        self,
        route: Route,
        query_params: dict = None,
        payload: dict = None,
        is_json: bool = False,
    ):
        pass

    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__
