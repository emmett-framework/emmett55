from emmett_core.pipeline.extras import RequirePipe as _RequirePipe
from emmett_core.pipeline.pipe import Pipe as Pipe

from .ctx import current


class RequirePipe(_RequirePipe):
    __slots__ = []
    _current = current
