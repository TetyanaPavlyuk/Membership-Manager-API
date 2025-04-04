from fastapi import Response, Request
from secrets import token_urlsafe

from app.exceptions.exceptions import (
    UnauthorizedException,
    RegisterException,
    LoginException,
    LogoutException,
    ResetException,
    InvalidTokenFormatException,
    GetCurrentUserException,
    ExpiredTokenException,
)
from app.schemas.auth import (
    RegisterSchema,
    RegisterResponseSchema,
    LoginSchema,
    LoginResponseSchema,
)
from app.schemas.users import UserDetailSchema
from app.services.tokens import TokenService
from app.services.users import UserService
from app.core.security import verify_password
from app.utils.logger import async_log


class AuthService:
    def __init__(self, user_service: UserService, token_service: TokenService):
        self.user_service = user_service
        self.token_service = token_service

    async def registration(self, user_data: RegisterSchema) -> RegisterResponseSchema:
        try:
            created_user = await self.user_service.create_user(user_data)
            return RegisterResponseSchema(user=created_user)
        except Exception as e:
            await async_log(f"Failed to register: {e}")
            raise RegisterException(e)

    async def login(
        self, user_data: LoginSchema, response: Response
    ) -> LoginResponseSchema:
        try:
            db_user = await self.user_service.user_repository.get_user_by_email(
                user_data.email
            )
            if not db_user:
                raise UnauthorizedException
            is_auth = verify_password(user_data.password, db_user.hashed_password)
            if not is_auth:
                raise UnauthorizedException
            access_token = await self.token_service.create_access_token(db_user.email)
            await self.token_service.set_token_to_cookies(
                "access_token", access_token, response
            )
            refresh_token = await self.token_service.create_refresh_token(db_user.email)
            await self.token_service.set_token_to_cookies(
                "refresh_token", refresh_token, response
            )
            return LoginResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token.token,
                token_type="bearer",
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            await async_log(f"Failed to login: {e}")
            raise LoginException(e)

    async def login_social(
        self, auth0_token: str, response: Response
    ) -> LoginResponseSchema:
        try:
            payload = await self.token_service.verify_auth0_token(auth0_token)
            email = payload.get("email")
            db_user = await self.user_service.user_repository.get_user_by_email(email)
            if not db_user:
                random_password = token_urlsafe(16)
                user_data = RegisterSchema(
                    email=email, password=random_password, full_name=None
                )
                await self.user_service.create_user(user_data)
            access_token = await self.token_service.create_access_token(email)
            await self.token_service.set_token_to_cookies(
                "access_token", access_token, response
            )
            refresh_token = await self.token_service.create_refresh_token(email)
            await self.token_service.set_token_to_cookies(
                "refresh_token", refresh_token, response
            )
            return LoginResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token.token,
                token_type="bearer",
            )
        except Exception as e:
            await async_log(f"Failed to login: {e}")
            raise LoginException(e)

    async def logout(self, access_token: str) -> dict:
        try:
            access_token = await self.token_service.extract_bearer_token(access_token)
            payload = await self.token_service.verify_access_token(access_token)
            email = payload.get("sub")
            refresh_token_data = await self.token_service.get_refresh_token_by_email(
                email
            )
            refresh_token = refresh_token_data.token
            await self.token_service.revoke_refresh_token(refresh_token)
            return {"message": "User logged out successfully."}
        except InvalidTokenFormatException:
            raise
        except Exception as e:
            await async_log(f"Failed to logout: {e}")
            raise LogoutException(e)

    async def refresh(self, refresh_token: str, response: Response):
        try:
            refresh_token = await self.token_service.extract_bearer_token(refresh_token)
            payload = await self.token_service.verify_refresh_token(refresh_token)
            email = payload.get("sub")
            access_token = await self.token_service.create_access_token(email)
            await self.token_service.set_token_to_cookies(
                "access_token", access_token, response
            )
            refresh_token = await self.token_service.create_refresh_token(email)
            await self.token_service.set_token_to_cookies(
                "refresh_token", refresh_token, response
            )
            return LoginResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token.token,
                token_type="bearer",
            )
        except InvalidTokenFormatException:
            raise
        except Exception as e:
            await async_log(f"Failed to refresh tokens: {e}")
            raise ResetException(e)

    async def get_current_user(
        self, access_token: str, request: Request, response: Response
    ) -> UserDetailSchema:
        try:
            access_token = await self.token_service.extract_bearer_token(access_token)
            payload = await self.token_service.verify_access_token(access_token)
            email = payload.get("sub")
            user_db = await self.user_service.user_repository.get_user_by_email(email)
            return UserDetailSchema.model_validate(user_db)
        except ExpiredTokenException:
            try:
                refresh_token = request.cookies.get("refresh_token")
                await self.refresh(refresh_token, response)
            except ExpiredTokenException:
                raise
        except InvalidTokenFormatException:
            raise
        except Exception as e:
            await async_log(f"Failed to get current user data: {e}")
            raise GetCurrentUserException(e)
