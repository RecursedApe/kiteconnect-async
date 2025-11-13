from dataclasses import dataclass
from typing import NamedTuple, Optional, Literal

Method = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]

class Route(NamedTuple):
    method: Method
    path: str
    # stable: bool = True
    # version: Optional[str] = None

API_TOKEN_CREATE = Route("POST", "/session/token")
API_TOKEN_INVALIDATE = Route("DELETE", "/session/token")