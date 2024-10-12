from emmett_core.sessions import SessionManager as _SessionManager

from .ctx import current


class SessionManager(_SessionManager):
    @classmethod
    def _build_pipe(cls, handler_cls, *args, **kwargs):
        cls._pipe = handler_cls(current, *args, **kwargs)
        return cls._pipe
