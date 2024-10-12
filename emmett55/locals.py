import datetime
from typing import Optional, cast

from emmett_core._internal import ContextVarProxy as _VProxy
from emmett_core.http.wrappers.request import Request
from emmett_core.http.wrappers.response import Response
from emmett_core.http.wrappers.websocket import Websocket

from .ctx import _ctxv, current
from .datastructures import sdict


request = cast(Request, _VProxy[Request](_ctxv, "request"))
response = cast(Response, _VProxy[Response](_ctxv, "response"))
session = cast(Optional[sdict], _VProxy[Optional[sdict]](_ctxv, "session"))
websocket = cast(Websocket, _VProxy[Websocket](_ctxv, "websocket"))


def now() -> datetime.datetime:
    return current.now
