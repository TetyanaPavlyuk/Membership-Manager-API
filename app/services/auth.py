from secrets import token_urlsafe
from datetime import datetime, timedelta
from jwt import (
    encode,
    decode,
    ExpiredSignatureError,
    InvalidTokenError,
    PyJWKClient,
    PyJWKClientError,
)

from app.exceptions.exceptions import (
    UnauthorizedException,
    RegisterException,
    LoginException,
    InvalidTokenFormatException,
    GetCurrentUserException,
    ExpiredTokenException,
    InvalidTokenException,
    ItemCreateException,
)
from app.schemas.auth import (
    RegistrationSchema,
    RegisterResponseSchema,
    LoginSchema,
    LoginResponseSchema,
)
from app.schemas.users import UserDetailSchema
from app.services.users import UserService
from app.config.settings import settings
from app.core.security import verify_password
from app.utils.logger import async_log


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @staticmethod
    async def create_access_token(email: str) -> str:
        try:
            expires_at = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            payload = {"sub": email, "exp": expires_at.timestamp()}
            return encode(
                payload=payload,
                key=settings.ACCESS_TOKEN_SECRET_KEY,
                algorithm=settings.ALGORITHM,
            )
        except Exception as e:
            await async_log(f"Failed to create access token: {e}")
            raise ItemCreateException("Access Token", e)

    @staticmethod
    async def verify_access_token(token: str):
        try:
            payload = decode(
                jwt=token,
                key=settings.ACCESS_TOKEN_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return payload
        except ExpiredSignatureError as e:
            raise ExpiredTokenException(e)
        except InvalidTokenError as e:
            raise InvalidTokenException(e)

    @staticmethod
    async def extract_bearer_token(bearer_token: str) -> str:
        if not bearer_token or not bearer_token.lower().startswith("bearer "):
            await async_log(f"Invalid access token format")
            raise InvalidTokenFormatException
        return bearer_token.replace("Bearer ", "").replace("bearer ", "")

    @staticmethod
    async def get_auth0_public_key(auth0_token: str) -> str:
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(auth0_token)
        return signing_key

    @staticmethod
    async def _handle_token_exception(e: Exception):
        if isinstance(e, ExpiredTokenException):
            await async_log(f"Token expiration error: {e}")
            raise e
        if isinstance(e, InvalidTokenException):
            await async_log(f"Failed to decode token: {e}")
            raise e
        await async_log(f"Failed to get current user data: {e}")
        raise GetCurrentUserException

    async def verify_auth0_token(self, auth0_token: str) -> dict:
        try:
            public_key = await self.get_auth0_public_key(auth0_token)
            payload = decode(
                jwt=auth0_token,
                key=public_key,
                algorithms=[settings.AUTH0_ALGORITHM],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f"https://{settings.AUTH0_DOMAIN}/",
            )
            return payload
        except ExpiredSignatureError as e:
            raise ExpiredTokenException(e)
        except InvalidTokenError as e:
            raise InvalidTokenException(e)

    async def registration(
        self, user_data: RegistrationSchema
    ) -> RegisterResponseSchema:
        try:
            created_user = await self.user_service.create_user(user_data)
            return RegisterResponseSchema(user=created_user)
        except Exception as e:
            await async_log(f"Failed to register: {e}")
            raise RegisterException(e)

    async def login(self, user_data: LoginSchema) -> LoginResponseSchema:
        try:
            db_user = await self.user_service.user_repository.get_user_by_email(
                user_data.email
            )
            if not db_user:
                raise UnauthorizedException
            is_auth = verify_password(user_data.password, db_user.hashed_password)
            if not is_auth:
                raise UnauthorizedException
            access_token = await self.create_access_token(db_user.email)
            return LoginResponseSchema(
                access_token=access_token,
                token_type="bearer",
            )
        except UnauthorizedException:
            raise
        except Exception as e:
            await async_log(f"Failed to login: {e}")
            raise LoginException(e)

    async def get_current_user(self, access_token: str) -> UserDetailSchema:
        try:
            access_token = await self.extract_bearer_token(access_token)
            payload = await self.verify_auth0_token(access_token)
            email = payload.get("email")
            db_user = await self.user_service.user_repository.get_user_by_email(email)
            if not db_user:
                random_password = token_urlsafe(16)
                user_data = RegistrationSchema(
                    email=email, password=random_password, full_name=None
                )
                db_user = await self.user_service.create_user(user_data)
            return UserDetailSchema.model_validate(db_user)
        except PyJWKClientError:
            try:
                payload = await self.verify_access_token(access_token)
                email = payload.get("sub")
                db_user = await self.user_service.user_repository.get_user_by_email(
                    email
                )
                return UserDetailSchema.model_validate(db_user)
            except Exception as e:
                await self._handle_token_exception(e)
        except Exception as e:
            await self._handle_token_exception(e)
