from unittest.mock import patch

import pytest
from jwt import decode, encode, PyJWKClientError
from datetime import datetime, timedelta

from app.exceptions.exceptions import (
    ExpiredTokenException,
    InvalidTokenException,
    InvalidTokenFormatException,
    UnauthorizedException,
)
from app.schemas.auth import LoginResponseSchema
from app.services.auth import AuthService
from app.config.settings import settings


async def test_create_access_token_success(test_email):
    token = await AuthService.create_access_token(test_email)
    payload = decode(
        jwt=token, key=settings.ACCESS_TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert payload["sub"] == test_email
    assert "exp" in payload
    assert datetime.utcfromtimestamp(payload["exp"]) > datetime.utcnow()


async def test_verify_access_token_success(test_email):
    token = await AuthService.create_access_token(test_email)
    payload = await AuthService.verify_access_token(token)

    assert payload["sub"] == test_email


async def test_verify_access_token_expired(test_email):
    past_time = datetime.utcnow() - timedelta(minutes=1)
    payload = {"sub": test_email, "exp": past_time}
    token = encode(
        payload=payload,
        key=settings.ACCESS_TOKEN_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(ExpiredTokenException):
        await AuthService.verify_access_token(token)


async def test_verify_access_token_invalid(test_email):
    token = await AuthService.create_access_token(test_email)
    invalid_token = token[:-1]

    with pytest.raises(InvalidTokenException):
        await AuthService.verify_access_token(invalid_token)


async def test_extract_bearer_token_success():
    token1 = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBtYWlsLmNvbSIsImV4cCI6MTc0NDAwOTU0My4xMTcwNDR9.kP6mW3Vsi3ml5G5eJ7PrsAYiToeiP8JAKkzFCWpIem4"
    token2 = "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QG1haWwuY29tIiwiZXhwIjoxNzQ0MjIwMzg2LjQ3NTM5NH0.odX0k7IIxaWWY9u0SsCXSDWVRfTro6PkwItEuNEqdiQ"
    extract_token1 = await AuthService.extract_bearer_token(token1)
    extract_token2 = await AuthService.extract_bearer_token(token2)

    assert (
        extract_token1
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBtYWlsLmNvbSIsImV4cCI6MTc0NDAwOTU0My4xMTcwNDR9.kP6mW3Vsi3ml5G5eJ7PrsAYiToeiP8JAKkzFCWpIem4"
    )
    assert (
        extract_token2
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QG1haWwuY29tIiwiZXhwIjoxNzQ0MjIwMzg2LjQ3NTM5NH0.odX0k7IIxaWWY9u0SsCXSDWVRfTro6PkwItEuNEqdiQ"
    )


async def test_extract_bearer_token_exception():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBtYWlsLmNvbSIsImV4cCI6MTc0NDAwOTU0My4xMTcwNDR9.kP6mW3Vsi3ml5G5eJ7PrsAYiToeiP8JAKkzFCWpIem4"

    with pytest.raises(InvalidTokenFormatException):
        await AuthService.extract_bearer_token(token)


async def test_login_success(auth_service, login_data, mock_user_service):

    with (
        patch("app.services.auth.verify_password", return_value=True),
        patch.object(auth_service, "create_access_token", return_value="test_token"),
    ):
        result = await auth_service.login(login_data)

    assert isinstance(result, LoginResponseSchema)
    assert result.access_token == "test_token"
    assert result.token_type == "bearer"
    mock_user_service.user_repository.get_user_by_email.assert_awaited_once_with(
        login_data.email
    )


async def test_login_not_found(mock_user_service, auth_service, login_data):
    mock_user_service.user_repository.get_user_by_email.return_value = None

    with pytest.raises(UnauthorizedException):
        await auth_service.login(login_data)


async def test_login_wrong_password(auth_service, login_data):
    with patch("app.services.auth.verify_password", return_value=False):
        with pytest.raises(UnauthorizedException):
            await auth_service.login(login_data)


async def test_get_current_user_via_auth0_success(auth_service, db_user):
    auth0_token = "auth0_token"
    with (
        patch(
            "app.services.auth.AuthService.extract_bearer_token",
            return_value=auth0_token,
        ),
        patch(
            "app.services.auth.AuthService.verify_auth0_token",
            return_value={"email": db_user.email},
        ),
    ):
        user = await auth_service.get_current_user(f"Bearer {auth0_token}")

        assert user.email == db_user.email


async def test_get_current_user_creates_new_user_via_auth0(
    auth_service, mock_user_service, db_user
):
    auth0_token = "auth0_token"
    email = db_user.email
    with (
        patch(
            "app.services.auth.AuthService.extract_bearer_token",
            return_value=auth0_token,
        ),
        patch(
            "app.services.auth.AuthService.verify_auth0_token",
            return_value={"email": email},
        ),
        patch.object(
            mock_user_service.user_repository, "get_user_by_email", return_value=None
        ),
        patch.object(mock_user_service, "create_user", return_value=db_user),
    ):

        user = await auth_service.get_current_user(f"Bearer {auth0_token}")

        assert user.email == email


async def test_get_current_user_via_local_jwt(auth_service, db_user):
    token = "access_token"
    with (
        patch("app.services.auth.AuthService.extract_bearer_token", return_value=token),
        patch(
            "app.services.auth.AuthService.verify_auth0_token",
            side_effect=PyJWKClientError("Auth0 decode error"),
        ),
        patch(
            "app.services.auth.AuthService.verify_access_token",
            return_value={"sub": db_user.email},
        ),
    ):

        user = await auth_service.get_current_user(f"Bearer {token}")
        assert user.email == db_user.email


async def test_get_current_user_invalid_token(auth_service):
    token = "invalid_token"
    with (
        patch("app.services.auth.AuthService.extract_bearer_token", return_value=token),
        patch(
            "app.services.auth.AuthService.verify_auth0_token",
            side_effect=PyJWKClientError("mock error"),
        ),
        patch(
            "app.services.auth.AuthService.verify_access_token",
            side_effect=InvalidTokenException("invalid"),
        ),
    ):

        with pytest.raises(InvalidTokenException):
            await auth_service.get_current_user(f"Bearer {token}")


async def test_get_current_user_expired_token(auth_service):
    token = "expired_token"
    with (
        patch("app.services.auth.AuthService.extract_bearer_token", return_value=token),
        patch(
            "app.services.auth.AuthService.verify_auth0_token",
            side_effect=PyJWKClientError("mock error"),
        ),
        patch(
            "app.services.auth.AuthService.verify_access_token",
            side_effect=ExpiredTokenException("expired"),
        ),
    ):

        with pytest.raises(ExpiredTokenException):
            await auth_service.get_current_user(f"Bearer {token}")
