import os

from emmett_core.pipeline.dyn import PipeBuilder
from emmett_core.routing.router import RouterMixin

from .extensions import Extension
from .locals import response
from .pipeline import Pipe


class TemplatePipe(Pipe):
    output = "str"

    def __init__(self, templater, template):
        self.templater = templater
        self.template = template

    async def pipe(self, next_pipe, **kwargs):
        ctx = await super().pipe(next_pipe, **kwargs)
        response.content_type = "text/html; charset=utf-8"
        return self.templater.render(self.template, ctx)


class TemplatePipeBuilder(PipeBuilder):
    pipe_cls = TemplatePipe

    def __init__(self, templater, template):
        self.templater = templater
        self.template = template

    def __call__(self, func):
        obj = RouterMixin.exposing()
        obj.pipeline.append(self.build_pipe(func))
        return func

    def build_pipe(self, func):
        if not self.template:
            self.template = func.__name__ + self.templater.config.file_extension
        return self.pipe_cls(self.templater, self.template)


class AbstractTemplater(Extension):
    namespace = "templates"
    default_config = {"folder": "templates", "file_extension": ".html"}
    pipe_builder = TemplatePipeBuilder

    def on_load(self):
        self.config.path = self.config.path or os.path.join(self.app.root_path, self.config.folder)

    def __call__(self, name=None):
        return self.pipe_builder(self, name)

    def render(self, template, ctx):
        raise NotImplementedError
