import pytest


@pytest.mark.asyncio
async def test_get_root(test_client):
    """
    Test that the `/` endpoint returns a 200 code and a success info.
    """
    response = await test_client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["status_code"] == 200
    assert data["detail"] == "ok"
    assert data["result"] == "working"
