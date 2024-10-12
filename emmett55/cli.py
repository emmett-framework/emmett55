import code
import os
import re
import sys
import types

import click
from emmett_core._internal import get_app_module, locate_app
from emmett_core.log import LOG_LEVELS
from emmett_core.server import run as sgi_run

from .__version__ import __version__ as fw_version


def find_app_module():
    rv, files, dirs = None, [], []
    for path in os.listdir():
        if any(path.startswith(val) for val in [".", "test"]):
            continue
        if os.path.isdir(path):
            if not path.startswith("_"):
                dirs.append(path)
            continue
        _, ext = os.path.splitext(path)
        if ext == ".py":
            files.append(path)
    if "app.py" in files:
        rv = "app.py"
    elif "app" in dirs:
        rv = "app"
    elif "__init__.py" in files:
        rv = "__init__.py"
    elif len(files) == 1:
        rv = files[0]
    elif len(dirs) == 1:
        rv = dirs[0]
    else:
        modules = []
        for path in dirs:
            if os.path.exists(os.path.join(path, "__init__.py")):
                modules.append(path)
        if len(modules) == 1:
            rv = modules[0]
    return rv


def get_import_components(path):
    return (re.split(r":(?![\\/])", path, 1) + [None])[:2]


def prepare_import(path):
    #: Given a path this will try to calculate the python path, add it
    #  to the search path and return the actual module name that is expected.
    path = os.path.realpath(path)

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        path = fname
    if os.path.basename(path) == "__init__":
        path = os.path.dirname(path)

    module_name = []

    #: move up untile outside package
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, "__init__.py")):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return ".".join(module_name[::-1])


class ScriptInfo(object):
    def __init__(self, app_import_path=None, debug=None):
        #: The application import path
        self.app_import_path = app_import_path or os.environ.get("EMMETT55_APP")
        #: The debug flag. If this is not None, the application will
        #  automatically have it's debug flag overridden with this value.
        self.debug = debug
        #: A dictionary with arbitrary data that can be associated with
        #  this script info.
        self.data = {}
        self._loaded_app = None
        self._loaded_ctx = None
        self.db_var_name = None

    def _get_import_name(self):
        if self.app_import_path:
            path, name = get_import_components(self.app_import_path)
        else:
            path, name = (find_app_module(), None)
        return prepare_import(path) if path else None, name

    def load_app(self):
        if self._loaded_app is not None:
            return self._loaded_app

        from .app import App

        import_name, app_name = self._get_import_name()
        app = locate_app(App, import_name, app_name) if import_name else None

        if app is None:
            raise RuntimeError("Could not locate an Emmett55 application.")

        if self.debug is not None:
            app.debug = self.debug

        self._loaded_app = app
        return app

    def load_appctx(self):
        ctx = {}
        import_name, _ = self._get_import_name()
        mod = get_app_module(import_name)

        for key in set(mod.__dict__.keys()) - {"__builtins__"}:
            value = mod.__dict__[key]
            if isinstance(value, types.FunctionType):
                continue
            ctx[key] = value

        self._loaded_ctx = ctx
        return ctx


pass_script_info = click.make_pass_decorator(ScriptInfo)


def set_app_value(ctx, param, value):
    ctx.ensure_object(ScriptInfo).app_import_path = value


app_option = click.Option(["-a", "--app"], help="The application to run", callback=set_app_value, is_eager=True)


class Emmett55Group(click.Group):
    def __init__(self, add_default_commands=True, add_app_option=True, add_debug_option=True, **extra):
        params = list(extra.pop("params", None) or ())
        if add_app_option:
            params.append(app_option)
        # if add_debug_option:
        #    params.append(debug_option)

        click.Group.__init__(self, params=params, **extra)

        if add_default_commands:
            self.add_command(develop_command)
            self.add_command(shell_command)
            self.add_command(routes_command)
            self.add_command(serve_command)

    def list_commands(self, ctx):
        rv = super(Emmett55Group, self).list_commands(ctx)
        info = ctx.ensure_object(ScriptInfo)
        try:
            rv = rv + info.load_app().cli.list_commands(ctx)
        except Exception:
            pass
        return rv

    def get_command(self, ctx, name):
        # We load built-in commands first as these should always be the
        # same no matter what the app does.  If the app does want to
        # override this it needs to make a custom instance of this group
        # and not attach the default commands.
        #
        # This also means that the script stays functional in case the
        # application completely fails.
        rv = click.Group.get_command(self, ctx, name)
        if rv is not None:
            return rv

        info = ctx.ensure_object(ScriptInfo)
        try:
            rv = info.load_app().cli.get_command(ctx, name)
            if rv is not None:
                return rv
        except Exception:
            pass

    def main(self, *args, **kwargs):
        obj = kwargs.get("obj")
        if obj is None:
            obj = ScriptInfo()
        kwargs["obj"] = obj
        return super().main(*args, **kwargs)


@click.command("develop", short_help="Runs a development server.")
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", type=int, default=8000, help="The port to bind to.")
@click.option("--interface", type=click.Choice(["rsgi", "asgi"]), default="rsgi", help="Application interface.")
@click.option(
    "--loop", type=click.Choice(["auto", "asyncio", "uvloop"]), default="auto", help="Event loop implementation."
)
@click.option("--ssl-certfile", type=str, default=None, help="SSL certificate file")
@click.option("--ssl-keyfile", type=str, default=None, help="SSL key file")
@click.option("--reloader/--no-reloader", is_flag=True, default=True, help="Runs with reloader.")
@pass_script_info
def develop_command(info, host, port, interface, loop, ssl_certfile, ssl_keyfile, reloader):
    os.environ["EMMETT55_RUN_ENV"] = "true"
    app_target = info._get_import_name()

    click.echo(
        " ".join(["> Starting Emmett55 development server on app", click.style(app_target[0], fg="cyan", bold=True)])
    )
    click.echo(
        " ".join(
            [
                click.style("> Emmett55 application", fg="green"),
                click.style(app_target[0], fg="cyan", bold=True),
                click.style("running on", fg="green"),
                click.style(f"http://{host}:{port}", fg="cyan"),
                click.style("(press CTRL+C to quit)", fg="green"),
            ]
        )
    )

    sgi_run(
        interface,
        app_target,
        host=host,
        port=port,
        loop=loop,
        log_level="debug",
        log_access=True,
        threading_mode="workers",
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        reload=reloader,
    )


@click.command("serve", short_help="Serve the app.")
@click.option("--host", "-h", default="0.0.0.0", help="The interface to bind to.")
@click.option("--port", "-p", type=int, default=8000, help="The port to bind to.")
@click.option("--workers", "-w", type=int, default=1, help="Number of worker processes. Defaults to 1.")
@click.option("--threads", type=int, default=1, help="Number of worker threads.")
@click.option(
    "--threading-mode", type=click.Choice(["runtime", "workers"]), default="workers", help="Server threading mode."
)
@click.option("--interface", type=click.Choice(["rsgi", "asgi"]), default="rsgi", help="Application interface.")
@click.option("--http", type=click.Choice(["auto", "1", "2"]), default="auto", help="HTTP version.")
@click.option("--ws/--no-ws", is_flag=True, default=True, help="Enable websockets support.")
@click.option(
    "--loop", type=click.Choice(["auto", "asyncio", "uvloop"]), default="auto", help="Event loop implementation."
)
@click.option("--opt/--no-opt", is_flag=True, default=False, help="Enable loop optimizations.")
@click.option("--log-level", type=click.Choice(LOG_LEVELS.keys()), default="info", help="Logging level.")
@click.option("--access-log/--no-access-log", is_flag=True, default=False, help="Enable access log.")
@click.option("--backlog", type=int, default=2048, help="Maximum number of connections to hold in backlog")
@click.option("--backpressure", type=int, help="Maximum number of requests to process concurrently (per worker)")
@click.option("--ssl-certfile", type=str, default=None, help="SSL certificate file")
@click.option("--ssl-keyfile", type=str, default=None, help="SSL key file")
@pass_script_info
def serve_command(
    info,
    host,
    port,
    workers,
    threads,
    threading_mode,
    interface,
    http,
    ws,
    loop,
    opt,
    log_level,
    access_log,
    backlog,
    backpressure,
    ssl_certfile,
    ssl_keyfile,
):
    app_target = info._get_import_name()
    sgi_run(
        interface,
        app_target,
        host=host,
        port=port,
        loop=loop,
        loop_opt=opt,
        log_level=log_level,
        log_access=access_log,
        workers=workers,
        threads=threads,
        threading_mode=threading_mode,
        backlog=backlog,
        backpressure=backpressure,
        http=http,
        enable_websockets=ws,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )


@click.command("shell", short_help="Runs a shell in the app context.")
@pass_script_info
def shell_command(info):
    os.environ["EMMETT55_CLI_ENV"] = "true"
    ctx = info.load_appctx()
    app = info.load_app()
    banner = "Python %s on %s\nEmmett55 %s shell on app: %s" % (sys.version, sys.platform, fw_version, app.import_name)
    code.interact(banner=banner, local=app.make_shell_context(ctx))


@click.command("routes", short_help="Display the app routing table.")
@pass_script_info
def routes_command(info):
    app = info.load_app()
    click.echo(
        "".join(["> Routing table for Emmett55 application ", click.style(app.import_name, fg="cyan", bold=True), ":"])
    )
    for route in app._router_http._routes_str.values():
        click.echo(route)
    for route in app._router_ws._routes_str.values():
        click.echo(route)


cli = Emmett55Group(help="")


def main(as_module=False):
    cli.main(prog_name="python -m emmett55" if as_module else None)


if __name__ == "__main__":
    main(as_module=True)
