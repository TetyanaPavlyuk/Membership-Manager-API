from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.refresh_tokens import RefreshTokenModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_token_by_value(self, token: str):
        try:
            return await self.db.scalar(
                select(RefreshTokenModel).where(RefreshTokenModel.token == token)
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get refresh token from DB: {e}")
            raise DatabaseError(e)

    async def get_token_by_email(self, email: str):
        try:
            return await self.db.scalar(
                select(RefreshTokenModel).filter(RefreshTokenModel.email == email)
            )
        except SQLAlchemyError as e:
            await async_log(
                f"Failed to get refresh token for user {email} from DB: {e}"
            )
            raise DatabaseError(e)

    async def save_token(self, refresh_token: RefreshTokenModel):
        try:
            self.db.add(refresh_token)
            await self.db.commit()
            await self.db.refresh(refresh_token)
            return refresh_token
        except SQLAlchemyError as e:
            await async_log(
                f"DB error while saving token for user (ID {refresh_token.user_id}): {e}"
            )
            raise DatabaseError(e)
