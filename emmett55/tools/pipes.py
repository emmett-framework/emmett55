from emmett_core.pipeline.dyn import ServicePipeBuilder as _ServicePipeBuilder
from emmett_core.pipeline.extras import JSONPipe as _JSONPipe

from ..ctx import current


class JSONPipe(_JSONPipe):
    _current = current


class ServicePipeBuilder(_ServicePipeBuilder):
    _pipe_cls = {"json": JSONPipe}


ServicePipe = ServicePipeBuilder()
