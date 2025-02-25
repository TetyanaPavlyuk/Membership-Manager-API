import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_root():
    """
    Test that the `/` endpoint returns a 200 code and a success info.
    """
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status_code"] == 200
    assert data["detail"] == "ok"
    assert data["result"] == "working"
