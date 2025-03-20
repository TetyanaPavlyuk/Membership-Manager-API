from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.db.models.users import UserModel
from app.utils.logger import async_log


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
            raise

    async def get_users(self, offset: int, limit: int):
        try:
            result = await self.db.execute(
                select(UserModel).offset(offset - 1).limit(limit)
            )
            users = result.scalars().all()
            return users
        except SQLAlchemyError as e:
            await async_log(f"Failed to get users list from DB: {e}")
            raise
        except Exception:
            raise

    async def get_user_by_id(self, id: int):
        try:
            result = await self.db.execute(select(UserModel).where(UserModel.id == id))
            return result.scalars().first()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get user (ID {id}) from DB: {e}")
            raise
        except Exception:
            raise

    async def get_user_by_email(self, email: str):
        try:
            result = await self.db.execute(
                select(UserModel).filter(UserModel.email == email)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get user with email {email} from DB: {e}")
            raise
        except Exception:
            raise

    async def save_user(self, user: UserModel):
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving user {user.email}: {e}")
            raise
        except Exception:
            raise

    async def delete_user(self, user: UserModel):
        try:
            await self.db.delete(user)
            await self.db.commit()

            return user
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete user (ID {user.id}) from DB.: {e}")
            raise
        except Exception:
            raise
