from math import ceil

import pytest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.db.models.users import UserModel
from app.schemas.users import UserSignUpSchema, UserUpdateSchema
from app.services.users import UserService


@pytest.mark.asyncio
async def test_create_user_success():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_email.return_value=None
    mock_repository.save_user=AsyncMock(side_effect=lambda user: user)

    user_service = UserService(mock_repository)

    user_data = {"email": "test@mail.com", "password": "test12345"}
    test_user = UserSignUpSchema(**user_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        db_user = await user_service.create_user(test_user)

    assert db_user.email == user_data["email"]
    assert db_user.hashed_password != user_data["password"]
    mock_repository.save_user.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_already_exist():
    mock_repository = AsyncMock()
    user_model_data = {"id": 1, "email": "test@mail.com", "hashed_password": "hashed_pass"}
    mock_repository.get_user_by_email.return_value=UserModel(**user_model_data)

    user_service = UserService(mock_repository)
    user_sign_up_data = {"email": "test@mail.com", "password": "test12345"}
    test_user = UserSignUpSchema(**user_sign_up_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.create_user(test_user)

    assert exc.value.status_code==400
    assert "already registered" in exc.value.detail
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_email.return_value=None
    mock_repository.save_user=Exception("DB Error")
    user_service = UserService(mock_repository)
    user_sign_up_data = {"email": "test@mail.com", "password": "test12345"}
    test_user = UserSignUpSchema(**user_sign_up_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.create_user(test_user)

    assert exc.value.status_code==400
    assert "Failed" in exc.value.detail


@pytest.mark.asyncio
async def test_get_users_success():
    users_data = [
        {"email": "test1@mail.com", "hashed_password": "hashed_pass"},
        {"email": "test2@mail.com", "hashed_password": "hashed_pass"}
    ]
    mock_repository = AsyncMock()
    users_count = 25
    mock_repository.get_users_count.return_value=users_count
    mock_repository.get_users.return_value=[
        UserModel(**user_data) for user_data in users_data
    ]
    user_service = UserService(mock_repository)
    page = 1
    size = 5

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        response = await user_service.get_users(page=page, size=size)

    assert response["users"] == mock_repository.get_users.return_value
    assert response["page"] == page
    assert response["size"] == size
    assert response["pages_count"] == ceil(users_count / size)
    assert response["users_count"] == users_count
    mock_repository.get_users_count.assert_called_once()
    mock_repository.get_users.assert_called_once_with(page - 1, size)


@pytest.mark.asyncio
async def test_get_users_exception():
    mock_repository = AsyncMock()
    mock_repository.get_users_count.side_effect=Exception("DB Error")
    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.get_users(page=1, size=2)

    assert exc.value.status_code==404
    assert "Failed" in exc.value.detail


@pytest.mark.asyncio
async def test_get_user_success():
    mock_repository = AsyncMock()
    user_data = {"id": 1, "email": "test@mail.com", "hashed_password": "test12345"}
    mock_repository.get_user_by_id.return_value = UserModel(**user_data)
    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        user = await user_service.get_user(id=user_data["id"])

    assert user.id == user_data["id"]
    assert user.email == user_data["email"]
    mock_repository.get_user_by_id.assert_called_once_with(user_data["id"])


@pytest.mark.asyncio
async def test_get_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value=None
    user_service = UserService(mock_repository)
    user_id = 5

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.get_user(user_id)

    assert exc.value.status_code == 404
    assert "Not found" in exc.value.detail
    mock_repository.get_user_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect=Exception("DB Error.")
    user_service = UserService(mock_repository)
    user_id = 1

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.get_user(user_id)

    assert exc.value.status_code == 404
    assert "Failed" in exc.value.detail
    mock_repository.get_user_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_user_success():
    user_model_data = {"id": 1, "email": "test@mail.com", "hashed_password": "test12345"}
    user_model = UserModel(**user_model_data)
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value=user_model
    mock_repository.save_user=AsyncMock(side_effect=lambda user: user)

    user_service = UserService(mock_repository)

    user_update_data = {"email": "new@mail.com"}
    update_user = UserUpdateSchema(**user_update_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        db_user = await user_service.update_user(user_model_data["id"], update_user)

    assert db_user.email == user_update_data["email"]
    mock_repository.get_user_by_id.assert_called_once_with(user_model_data["id"])
    mock_repository.save_user.assert_called_once_with(user_model)


@pytest.mark.asyncio
async def test_update_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value=None

    user_service = UserService(mock_repository)
    user_update_data = {"email": "new@mail.com"}
    update_user = UserUpdateSchema(**user_update_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.update_user(2, update_user)

    assert exc.value.status_code==404
    assert "not registered" in exc.value.detail
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect=Exception("DB Error.")
    user_service = UserService(mock_repository)
    user_update_data = {"email": "new@mail.com"}
    update_user = UserUpdateSchema(**user_update_data)
    user_id = 2

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.update_user(user_id, update_user)

    assert exc.value.status_code == 400
    assert "Failed" in exc.value.detail
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_success():
    user_model_data = {"id": 1, "email": "test@mail.com", "hashed_password": "test12345"}
    user_model = UserModel(**user_model_data)
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value=user_model
    mock_repository.delete_user.return_value=user_model

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        response = await user_service.delete_user(user_model_data["id"])

    assert response["message"] == f"User {user_model_data['email']} (ID {user_model_data['id']}) has been deleted."
    mock_repository.get_user_by_id.assert_called_once_with(user_model_data["id"])
    mock_repository.delete_user.assert_called_once_with(user_model)


@pytest.mark.asyncio
async def test_delete_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value=None
    user_id = 1

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.delete_user(user_id)

    assert exc.value.status_code == 404
    assert "not registered" in exc.value.detail
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.delete_user.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect = Exception("DB Error.")
    user_id = 1

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await user_service.delete_user(user_id)

    assert exc.value.status_code == 400
    assert "Failed to delete" in exc.value.detail
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.delete_user.assert_not_called()
