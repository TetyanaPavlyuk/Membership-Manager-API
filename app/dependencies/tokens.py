from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.repository.refresh_tokens import RefreshTokenRepository
from app.services.tokens import TokenService


async def get_token_service(db: AsyncSession = Depends(get_async_db)):
    token_repository = RefreshTokenRepository(db)
    return TokenService(token_repository)
