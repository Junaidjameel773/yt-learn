from fastapi.testclient import TestClient

from yt_learn import __version__
from yt_learn.api import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
