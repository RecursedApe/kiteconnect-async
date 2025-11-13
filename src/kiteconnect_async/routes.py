from dataclasses import dataclass
from typing import NamedTuple, Optional


@dataclass(frozen=True)
class Route(NamedTuple):
    method: str
    path: str
    # stable: bool = True
    # version: Optional[str] = None

API_TOKEN = Route("POST", "/session/token")
API_TOKEN_INVALIDATE = Route("", "/session/token")
