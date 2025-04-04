from datetime import datetime, timedelta

import jwt
from fastapi import Response
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError, PyJWKClient

from app.config.settings import settings
from app.db.models.refresh_tokens import RefreshTokenModel
from app.exceptions.exceptions import (
    ItemNotFoundException,
    ItemException,
    ExpiredTokenException,
    InvalidTokenException,
    InvalidTokenFormatException,
)
from app.repository.refresh_tokens import RefreshTokenRepository
from app.schemas.tokens import RefreshTokenResponseSchema
from app.utils.logger import async_log


class TokenService:
    def __init__(self, refresh_token_repository: RefreshTokenRepository):
        self.refresh_token_repository = refresh_token_repository

    async def create_refresh_token(self, email: str) -> RefreshTokenResponseSchema:
        try:
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            payload = {"sub": email, "exp": expires_at.timestamp()}
            refresh_token = encode(
                payload=payload,
                key=settings.REFRESH_TOKEN_SECRET_KEY,
                algorithm=settings.ALGORITHM,
            )

            db_token = await self.refresh_token_repository.get_token_by_email(email)
            if db_token:
                db_token.token = refresh_token
                db_token.created_at = created_at
                db_token.expires_at = expires_at
                db_token.revoked = False
            else:
                db_token = RefreshTokenModel(
                    email=email,
                    token=refresh_token,
                    created_at=created_at,
                    expires_at=expires_at,
                    revoked=False,
                )
            saved_token = await self.refresh_token_repository.save_token(db_token)

            return RefreshTokenResponseSchema.model_validate(saved_token)
        except Exception as e:
            await async_log(f"Failed to create refresh token: {e}")
            raise ItemException(e)

    async def revoke_refresh_token(self, token: str):
        try:
            token = token.replace("Bearer ", "").replace("bearer", "")
            db_token = await self.refresh_token_repository.get_token_by_value(token)
            if not db_token:
                raise ItemNotFoundException("Refresh token")
            db_token.revoked = True
            return await self.refresh_token_repository.save_token(db_token)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to revoke refresh token: {e}")
            raise ItemException(e)

    async def verify_access_token(self, token: str):
        payload = await self.decode_token(token, settings.ACCESS_TOKEN_SECRET_KEY)
        return payload

    async def verify_refresh_token(self, token: str):
        token_db = await self.refresh_token_repository.get_token_by_value(token)
        is_expire = token_db.expires_at < datetime.utcnow()
        if is_expire or token_db.revoked:
            raise ExpiredTokenException("Refresh token is expired")
        return await self.decode_token(token, settings.REFRESH_TOKEN_SECRET_KEY)

    async def verify_auth0_token(self, auth0_token: str) -> dict:
        try:
            public_key = await self.get_auth0_public_key(auth0_token)
            payload = jwt.decode(
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

    async def get_refresh_token_by_email(
        self, email: str
    ) -> RefreshTokenResponseSchema:
        try:
            db_token = await self.refresh_token_repository.get_token_by_email(email)
            if not db_token:
                await async_log(f"Refresh token for user {email} not found.")
                raise ItemNotFoundException("Refresh Token")
            return RefreshTokenResponseSchema.model_validate(db_token)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to get refresh token for user {email}: {e}")
            raise ItemException(e)

    async def get_refresh_token(self, token: str) -> RefreshTokenResponseSchema:
        try:
            db_token = await self.refresh_token_repository.get_token_by_value(token)
            if not db_token:
                await async_log(f"Refresh token not found.")
                raise ItemNotFoundException("Refresh Token")
            return RefreshTokenResponseSchema.model_validate(db_token)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to get refresh token: {e}")
            raise ItemException(e)

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
            raise ItemException(e)

    @staticmethod
    async def decode_token(token: str, secret_key: str) -> dict:
        try:
            payload = decode(jwt=token, key=secret_key, algorithms=[settings.ALGORITHM])
            return payload
        except ExpiredSignatureError as e:
            raise ExpiredTokenException(e)
        except InvalidTokenError as e:
            raise InvalidTokenException(e)

    @staticmethod
    async def get_auth0_public_key(auth0_token: str) -> str:
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(auth0_token)
        return signing_key

    @staticmethod
    async def set_token_to_cookies(
        token_key: str, token_value: str, response: Response
    ) -> None:
        response.set_cookie(
            token_key,
            f"Bearer {token_value}",
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=5 * 24 * 60 * 60,
        )

    @staticmethod
    async def extract_bearer_token(bearer_token: str) -> str:
        if not bearer_token or not bearer_token.lower().startswith("bearer "):
            await async_log(f"Invalid access token format")
            raise InvalidTokenFormatException
        return bearer_token.replace("Bearer ", "").replace("bearer ", "")
