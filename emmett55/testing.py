from emmett_core.protocols.rsgi.test_client.client import EmmettTestClient as _EmmettTestClient

from .ctx import current


class Emmett55TestClient(_EmmettTestClient):
    _current = current
