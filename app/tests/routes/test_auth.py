import pytest

from fastapi import status

from app.tests.conftest import user_token_id_func


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_update_self(test_client, access_token, user_id):
    response = await test_client.patch(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "New name"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "New name"


@pytest.mark.asyncio(loop_scope="session")
async def test_user_cannot_update_email(test_client, access_token, user_id):
    response = await test_client.patch(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": "other@mail.com"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_delete_self(test_client, access_token, user_id):
    response = await test_client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_user_cannot_edit_other(test_client, access_token, user_id):
    other_user_id, other_user_token = await user_token_id_func(test_client)

    response = await test_client.patch(
        f"/users/{other_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "Hacked"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio(loop_scope="session")
async def test_user_cannot_delete_other(test_client, access_token, user_id):
    other_user_id, other_user_token = await user_token_id_func(test_client)

    response = await test_client.delete(
        f"/users/{other_user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
