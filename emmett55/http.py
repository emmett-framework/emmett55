from emmett_core.http.helpers import abort as _abort, redirect as _redirect

from .ctx import current


def abort(code: int, body: str = ""):
    _abort(current, code, body)


def redirect(location: str, status_code: int = 303):
    _redirect(current, location, status_code)
