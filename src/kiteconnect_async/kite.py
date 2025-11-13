import hashlib
import httpx

from .__version__ import __version__, __title__
from kiteconnect_async.routes import Route
from . import routes as APIRoutes, exceptions as ex


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

    api_key: str
    access_token: str
    client: httpx.Client

    def __init__(self, api_key: str, api_secret: str, access_token: str = None):
        self.api_key = api_key
        self.api_secret = api_secret

        default_headers = {
            "X-Kite-Version": self.kite_header_version,
            "User-Agent": self._user_agent(),
        }

        self.client = httpx.Client(
            base_url=self._base_url,
            headers=default_headers,
            timeout=self._default_timeout,
            follow_redirects=True,
        )

        if access_token is not None:
            self.access_token = access_token
            self.set_auth_header()

    def get_login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s&v=%s" % (
            self._login_url,
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
            APIRoutes.API_TOKEN_CREATE,
            request_data={
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum,
            },
        )

        if "access_token" in resp:
            self.set_access_token(resp["access_token"])

        return resp

    def invalidate_access_token(self, access_token=None):
        """
        Kill the session by invalidating the access token.

        - `access_token` to invalidate. Default is the active `access_token`.
        """
        access_token = access_token or self.access_token
        return self._delete(
            APIRoutes.API_TOKEN_INVALIDATE,
            params={"api_key": self.api_key, "access_token": access_token},
        )

    def _request(
        self,
        route: Route,
        query_params: dict | None = None,
        request_data: dict | None = None,
        json_payload: dict | None = None,
    ):
        req = self.client.build_request(
            route.method,
            route.path,
            params=query_params,
            data=request_data,
            json=json_payload,
        )

        try:
            resp = self.client.send(req)
        except Exception as e:
            raise e

        if resp.headers.get("content-type") == "application/json":
            try:
                data = resp.json()
            except ValueError:
                raise ex.DataException(
                    "Couldn't parse the JSON response received from the server: {content}".format(
                        content=resp.content
                    )
                )
            # api error
            if data.get("status") == "error" or data.get("error_type"):
                if resp.status_code == 403 and data["error_type"] == "TokenException":
                    pass

                # native Kite errors
                exp = getattr(ex, data.get("error_type"), ex.GeneralException)
                raise exp(data["message"], code=resp.status_code)

            return data["data"]
        elif "csv" in resp.headers["content-type"]:
            return resp.content
        else:
            raise ex.DataException(
                "Unknown Content-Type ({content_type}) with response: ({content})".format(
                    content_type=resp.headers["content-type"], content=resp.content
                )
            )

    def set_auth_header(self):
        auth_token = ":".join([self.api_key, self.access_token])
        self.client.headers.update(
            {"Authorization": "token {}".format(auth_token)}
        )

    def set_access_token(self, access_token: str):
        self.access_token = access_token
        self.set_auth_header()

    def _user_agent(self):
        return (__title__ + "-python/").capitalize() + __version__
