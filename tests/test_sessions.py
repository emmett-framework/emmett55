import pytest

from emmett55 import App, request, response, session
from emmett55.sessions import SessionManager


@pytest.fixture(scope="function")
def app():
    app = App(__name__)
    sessions = SessionManager.cookies("test")
    app.pipeline = [sessions]

    @app.route()
    async def set():
        response.status = 201
        data = await request.body
        session.data = data.decode("utf8")
        return ""

    @app.route()
    async def get():
        return session.data

    return app


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


def test_session_flow(client):
    req = client.post("/set", data=b"test")
    assert req.status == 201

    res = client.get("/get")
    assert res.status == 200
    assert res.data == "test"
