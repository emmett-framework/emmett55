from __future__ import annotations

import os
from typing import Optional

import click
from emmett_core._internal import create_missing_app_folders, get_root_path
from emmett_core.app import App as _App, AppModule as AppModule
from emmett_core.protocols.asgi.handlers import HTTPHandler as ASGIHTTPHandler, WSHandler as ASGIWSHandler
from emmett_core.protocols.rsgi.handlers import HTTPHandler as RSGIHTTPHandler, WSHandler as RSGIWSHandler

from .ctx import current
from .routing.router import HTTPRouter, WebsocketRouter
from .testing import Emmett55TestClient


class App(_App):
    __slots__ = ["cli"]

    test_client_class = Emmett55TestClient

    def __init__(self, import_name: str, root_path: Optional[str] = None, url_prefix: Optional[str] = None, **opts):
        super().__init__(import_name, root_path, url_prefix, **opts)
        self.cli = click.Group(self.import_name)

    def _configure_paths(self, root_path, opts):
        if root_path is None:
            root_path = get_root_path(self.import_name)
        self.root_path = root_path
        self.static_path = os.path.join(self.root_path, "static")
        create_missing_app_folders(self, ["logs", "static"])

    def _init_routers(self, url_prefix):
        self._router_http = HTTPRouter(self, current, url_prefix=url_prefix)
        self._router_ws = WebsocketRouter(self, current, url_prefix=url_prefix)

    def _init_handlers(self):
        self._asgi_handlers["http"] = ASGIHTTPHandler(self, current)
        self._asgi_handlers["ws"] = ASGIWSHandler(self, current)
        self._rsgi_handlers["http"] = RSGIHTTPHandler(self, current)
        self._rsgi_handlers["ws"] = RSGIWSHandler(self, current)

    def _register_with_ctx(self):
        current.app = self

    @property
    def command(self):
        return self.cli.command

    @property
    def command_group(self):
        return self.cli.group

    def make_shell_context(self, context):
        context["app"] = self
        return context
