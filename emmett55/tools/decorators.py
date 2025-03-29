from emmett_core.pipeline.dyn import requires as _requires, service as _service, sse as _sse, stream as _stream

from ..pipeline import RequirePipe
from .pipes import ServicePipeBuilder, SSEPipe, StreamPipe


class requires(_requires):
    _pipe_cls = RequirePipe


class service(_service):
    _inner_builder = ServicePipeBuilder()


class stream(_stream):
    _pipe_cls = StreamPipe


class sse(_sse):
    _pipe_cls = SSEPipe
