from fastapi import HTTPException
from math import ceil

from app.db.models.users import UserModel
from app.schemas.users import UserSignUpSchema, UserUpdateSchema
from app.core.security import hash_password
from app.utils.logger import async_log
from app.repository.users import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_users(self, page: int = 1, size: int = 10):
        try:
            users_count = await self.user_repository.get_users_count()
            pages_count = ceil(users_count / size)
            page = max(1, min(pages_count, page))
            size = max(1, size)
            first_user = (page - 1) * size

            users = await self.user_repository.get_users(first_user, size)
            await async_log("Geting users list was successful.")

            return {
                "users": users,
                "page": page,
                "size": size,
                "pages_count": pages_count,
                "users_count": users_count,
            }

        except Exception as e:
            await async_log(f"Failed to get users list: {e}")
            raise HTTPException(
                status_code=404, detail=f"Failed to get users list: {e}"
            )

    async def get_user(self, id: int):
        try:
            db_user = await self.user_repository.get_user_by_id(id)
            if not db_user:
                await async_log(f"User (ID {id}) not found.")
                raise HTTPException(status_code=404, detail=f"Not found user {id}.")
            await async_log(f"Getting user (ID {id}) was successful.")
            return db_user
        except HTTPException as httpe:
            raise httpe
        except Exception as e:
            await async_log(f"Failed to get user (ID {id}): {e}")
            raise HTTPException(status_code=404, detail=f"Failed to get user {id}: {e}")

    async def create_user(self, user: UserSignUpSchema):
        try:
            hashed_password = hash_password(user.password)
            created_user = UserModel(email=user.email, hashed_password=hashed_password)

            existing_user = await self.user_repository.get_user_by_email(user.email)
            if existing_user:
                await async_log(f"User with email {user.email} is already registered.")
                raise HTTPException(
                    status_code=400,
                    detail=f"User with email {user.email} is already registered.",
                )

            db_user = await self.user_repository.save_user(created_user)

            await async_log(
                f"Creating user {db_user.email} (ID {db_user.id}) was successful."
            )
            return db_user
        except Exception as e:
            await async_log(f"Failed to create user {user.email}: {e}")
            raise HTTPException(
                status_code=400, detail=f"Failed to create user {user.email}: {e}"
            )

    async def update_user(self, id: int, update_data: UserUpdateSchema):
        try:
            db_user = await self.user_repository.get_user_by_id(id)

            if not db_user:
                await async_log("User with that id is not registered.")
                raise HTTPException(
                    status_code=404, detail="User with that id is not registered."
                )

            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(db_user, key, value)

            db_user = await self.user_repository.save_user(db_user)
            await async_log(
                f"Updating user {db_user.email} (ID {db_user.id}) was successful."
            )
            return db_user
        except HTTPException as httpe:
            raise httpe
        except Exception as e:
            await async_log(f"Failed to update user: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to update user: {e}")

    async def delete_user(self, id: int):
        try:
            db_user = await self.user_repository.get_user_by_id(id)

            if not db_user:
                await async_log("User with that id is not registered.")
                raise HTTPException(
                    status_code=404, detail="User with that id is not registered."
                )

            deleted_user = await self.user_repository.delete_user(db_user)
            await async_log(f"User {deleted_user.email} (ID {id}) has been deleted.")
            return {"message": f"User {deleted_user.email} (ID {id}) has been deleted."}
        except HTTPException as httpe:
            raise httpe
        except Exception as e:
            await async_log(f"Failed to delete user: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to delete user: {e}")
