from app.main import app
from fastapi.testclient import TestClient
from pytest_mock import mocker

client = TestClient(app)


