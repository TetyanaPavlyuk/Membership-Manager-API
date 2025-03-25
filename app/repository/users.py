from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.db.models.users import UserModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users_count(self):
        try:
            users_count = await self.db.execute(
                select(func.count()).select_from(UserModel)
            )
            return users_count.scalar() or 0
        except SQLAlchemyError as e:
            await async_log(f"Failed to get users count from DB: {e}")
            raise DatabaseError(e)

    async def get_users(self, offset: int, limit: int):
        try:
            result = await self.db.scalars(
                select(UserModel).offset(offset).limit(limit)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get users list from DB: {e}")
            raise DatabaseError(e)

    async def get_user_by_id(self, id: int):
        try:
            return await self.db.get(UserModel, id)
        except SQLAlchemyError as e:
            await async_log(f"Failed to get user (ID {id}) from DB: {e}")
            raise DatabaseError(e)

    async def get_user_by_email(self, email: str):
        try:
            return await self.db.scalar(
                select(UserModel).filter(UserModel.email == email)
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get user with email {email} from DB: {e}")
            raise DatabaseError(e)

    async def save_user(self, user: UserModel):
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving user {user.email}: {e}")
            raise DatabaseError(e)

    async def delete_user(self, user: UserModel):
        try:
            await self.db.delete(user)
            await self.db.commit()

            return user
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete user (ID {user.id}) from DB.: {e}")
            raise DatabaseError(e)
