import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_get_root(test_client):
    """
    Test that the `/` endpoint returns a 200 code and a success info.
    """
    response = await test_client.get("/check-health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status_code"] == status.HTTP_200_OK
    assert data["detail"] == "ok"
    assert data["result"] == "working"
