import pytest

from emmett55 import App, abort, request
from emmett55.pipeline import RequirePipe
from emmett55.tools import requires


@pytest.fixture(scope="function")
def app():
    app = App(__name__)

    @app.route()
    @requires(lambda: request.query_params.foo == "bar", lambda: abort(401))
    async def d():
        return "ok"

    @app.route(pipeline=[RequirePipe(lambda: request.query_params.foo == "bar", lambda: abort(401))])
    async def p():
        return "ok"

    return app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def test_requires_deco(client):
    res = client.get("/d")
    assert res.status == 401

    res = client.get("/d?foo=bar")
    assert res.data == "ok"


def test_requires_pipe(client):
    res = client.get("/p")
    assert res.status == 401

    res = client.get("/p?foo=bar")
    assert res.data == "ok"
