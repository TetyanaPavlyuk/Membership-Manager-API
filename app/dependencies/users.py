from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.repository.users import UserRepository
from app.services.users import UserService


async def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    user_repository = UserRepository(db)
    return UserService(user_repository)
