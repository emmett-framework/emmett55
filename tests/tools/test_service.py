import json

import pytest

from emmett55 import App, request
from emmett55.tools import ServicePipe, service


@pytest.fixture(scope="function")
def app():
    app = App(__name__)

    @app.route()
    @service.json
    async def d():
        params = await request.body_params
        return {"msg": params.msg}

    @app.route(pipeline=[ServicePipe("json")])
    async def p():
        params = await request.body_params
        return {"msg": params.msg}

    return app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def test_service_deco(client):
    res = client.post("/d", data=json.dumps({"msg": "hello"}), headers=[("content-type", "application/json")])
    assert res.status == 200
    assert res.json() == {"msg": "hello"}


def test_service_pipe(client):
    res = client.post("/p", data=json.dumps({"msg": "hello"}), headers=[("content-type", "application/json")])
    assert res.status == 200
    assert res.json() == {"msg": "hello"}
