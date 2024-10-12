from emmett_core.pipeline.dyn import requires as _requires, service as _service

from ..pipeline import RequirePipe
from .pipes import ServicePipeBuilder


class requires(_requires):
    _pipe_cls = RequirePipe


class service(_service):
    _inner_builder = ServicePipeBuilder()
