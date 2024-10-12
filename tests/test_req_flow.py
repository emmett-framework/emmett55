import pytest

from emmett55 import App, request, response


@pytest.fixture(scope="function")
def app():
    app = App(__name__)

    @app.route("/")
    async def index():
        return "hello world"

    @app.route(output="bytes")
    async def echo():
        response.status = 201
        return await request.body

    return app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def test_req_flow_get(client):
    res = client.get("/")
    assert res.status == 200
    assert res.data == "hello world"


def test_req_flow_post(client):
    res = client.post("/echo", data=b"test")
    assert res.status == 201
    assert res.data == "test"
