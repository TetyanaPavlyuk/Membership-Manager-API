from math import ceil
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.core.security import hash_password
from app.db.models.users import UserModel
from app.schemas.auth import RegistrationSchema
from app.schemas.users import (
    UserShortSchema,
    UserDetailSchema,
    UserBaseSchema,
    UserListSchema,
)
from app.services.users import UserService
from app.exceptions.exceptions import (
    ItemCreateException,
    ItemDetailException,
    ItemsListException,
    ItemUpdateException,
    ItemDeleteException,
    ItemAlreadyExistException,
    ItemNotFoundException,
)


@pytest.mark.asyncio
async def test_create_user_success():
    mock_repository = AsyncMock()

    user_service = UserService(mock_repository)

    user_data = RegistrationSchema(
        email="test@mail.com", password="Test12345?", full_name="Test Name"
    )
    hashed_password = hash_password(user_data.password)
    saved_user = UserModel(
        id="3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        email=user_data.email,
        hashed_password=hashed_password,
        is_superuser=False,
        is_active=True,
        full_name=user_data.full_name,
    )

    mock_repository.get_user_by_email.return_value = None
    mock_repository.save_user.return_value = saved_user

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with patch(
            "app.services.users.hash_password", return_value=hashed_password
        ) as mock_hash_password:
            db_user = await user_service.create_user(user_data)

    assert isinstance(db_user, UserDetailSchema)
    assert db_user.id == saved_user.id
    assert db_user.email == user_data.email
    assert db_user.full_name == user_data.full_name
    mock_hash_password.assert_called_once_with(user_data.password)
    mock_repository.get_user_by_email.assert_called_once_with(user_data.email)
    mock_repository.save_user.assert_called_once()
    user_to_save = mock_repository.save_user.call_args.args[0]
    assert user_to_save.email == user_data.email
    assert user_to_save.hashed_password == hashed_password


@pytest.mark.asyncio
async def test_create_user_already_exist():
    mock_repository = AsyncMock()
    user_model_data = {
        "id": 1,
        "email": "test@mail.com",
        "hashed_password": "hashed_pass",
    }
    mock_repository.get_user_by_email.return_value = UserModel(**user_model_data)

    user_service = UserService(mock_repository)
    user_sign_up_data = {
        "email": "test@mail.com",
        "password": "Test12345?",
        "full_name": None,
    }
    test_user = RegistrationSchema(**user_sign_up_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemAlreadyExistException) as exc:
            await user_service.create_user(test_user)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exist" in exc.value.message
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_email.return_value = None
    mock_repository.save_user = Exception("DB Error")
    user_service = UserService(mock_repository)
    user_sign_up_data = {
        "email": "test@mail.com",
        "password": "Test12345?",
        "full_name": None,
    }
    test_user = RegistrationSchema(**user_sign_up_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemCreateException) as exc:
            await user_service.create_user(test_user)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()


@pytest.mark.parametrize(
    "password",
    ["short1A@", "nouppercase1@", "NOLOWERCASE1@", "NoNumber@", "NoSpecial1"],
)
@pytest.mark.asyncio
async def test_create_user_invalid_password(password):
    mock_repository = AsyncMock()
    mock_repository.get_user_by_email.return_value = None
    user_service = UserService(mock_repository)
    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemCreateException):
            test_user = RegistrationSchema(
                email="test@example.com", password=password, full_name="Test"
            )
            await user_service.create_user(test_user)


@pytest.mark.asyncio
async def test_get_users_success():
    users_data = [
        {"email": "test1@mail.com", "hashed_password": "hashed_pass"},
        {"email": "test2@mail.com", "hashed_password": "hashed_pass"},
    ]
    mock_repository = AsyncMock()
    users_count = len(users_data)
    mock_repository.get_users_count.return_value = users_count
    mock_repository.get_users.return_value = [
        UserModel(**user_data) for user_data in users_data
    ]
    user_service = UserService(mock_repository)
    page = 1
    size = 5

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        response = await user_service.get_users(page=page, size=size)

    assert isinstance(response, UserListSchema)
    assert len(response.users) == users_count
    assert response.users_count == users_count
    assert response.pages_count == ceil(users_count / size)
    for i, user in enumerate(response.users):
        assert isinstance(user, UserBaseSchema)
        assert user.email == users_data[i]["email"]
    mock_repository.get_users_count.assert_called_once()
    mock_repository.get_users.assert_called_once_with((page - 1) * size, size)


@pytest.mark.asyncio
async def test_get_users_exception():
    mock_repository = AsyncMock()
    mock_repository.get_users_count.side_effect = Exception("DB Error")
    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemsListException) as exc:
            await user_service.get_users(page=1, size=2)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_get_user_success():
    mock_repository = AsyncMock()
    user_data = {
        "id": "3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        "email": "test@mail.com",
        "hashed_password": "test12345",
        "is_active": True,
        "is_superuser": False,
    }
    mock_repository.get_user_by_id.return_value = UserModel(**user_data)
    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        user = await user_service.get_user(id=user_data["id"])

    assert isinstance(user, UserDetailSchema)
    assert user.id == user_data["id"]
    assert user.email == user_data["email"]
    mock_repository.get_user_by_id.assert_called_once_with(user_data["id"])


@pytest.mark.asyncio
async def test_get_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = None
    user_service = UserService(mock_repository)
    user_id = 5

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await user_service.get_user(user_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.get_user_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect = Exception("DB Error.")
    user_service = UserService(mock_repository)
    user_id = 1

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemDetailException) as exc:
            await user_service.get_user(user_id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in exc.value.message.lower()
    mock_repository.get_user_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_user_success():
    user_model_data = {
        "id": "3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        "email": "test@mail.com",
        "hashed_password": "test12345",
        "is_active": True,
        "is_superuser": False,
    }
    user_model = UserModel(**user_model_data)
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = user_model
    mock_repository.save_user = AsyncMock(side_effect=lambda user: user)

    user_service = UserService(mock_repository)

    user_update_data = {"email": "new@mail.com"}
    update_user = UserShortSchema(**user_update_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        db_user = await user_service.update_user(user_model_data["id"], update_user)

    assert db_user.email == user_update_data["email"]
    mock_repository.get_user_by_id.assert_called_once_with(user_model_data["id"])
    mock_repository.save_user.assert_called_once_with(user_model)


@pytest.mark.asyncio
async def test_update_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = None

    user_service = UserService(mock_repository)
    user_update_data = {"email": "new@mail.com"}
    update_user = UserShortSchema(**user_update_data)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await user_service.update_user(2, update_user)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect = Exception("DB Error.")
    user_service = UserService(mock_repository)
    user_update_data = {"email": "new@mail.com"}
    update_user = UserShortSchema(**user_update_data)
    user_id = 2

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemUpdateException) as exc:
            await user_service.update_user(user_id, update_user)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.save_user.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_success():
    user_model_data = {
        "id": 1,
        "email": "test@mail.com",
        "hashed_password": "test12345",
    }
    user_model = UserModel(**user_model_data)
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = user_model
    mock_repository.delete_user.return_value = user_model

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        response = await user_service.delete_user(user_model_data["id"])

    assert (
        response["message"]
        == f"User {user_model_data['email']} (ID {user_model_data['id']}) has been deleted."
    )
    mock_repository.get_user_by_id.assert_called_once_with(user_model_data["id"])
    mock_repository.delete_user.assert_called_once_with(user_model)


@pytest.mark.asyncio
async def test_delete_user_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = None
    user_id = 1

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await user_service.delete_user(user_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.delete_user.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_exception():
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.side_effect = Exception("DB Error.")
    user_id = 1

    user_service = UserService(mock_repository)

    with patch("app.services.users.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemDeleteException) as exc:
            await user_service.delete_user(user_id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed to delete" in exc.value.message.lower()
    mock_repository.get_user_by_id.assert_called_once_with(user_id)
    mock_repository.delete_user.assert_not_called()
