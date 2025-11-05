from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_rate_limit():
    for i in range(5):
        response = client.get("/")
        assert response.status_code == 200, f"Failed at {i + 1}"
    response = client.get("/")
    assert response.status_code == 429
