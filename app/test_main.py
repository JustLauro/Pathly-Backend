from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

def test_route_generation():
    response = client.post("api/generate-route")
    assert response.status_code == 200

