from math import ceil

from app.db.models.users import UserModel
from app.schemas.auth import RegistrationSchema
from app.schemas.users import (
    UserUpdateSchema,
    UserListSchema,
    UserBaseSchema,
    UserDetailSchema,
)
from app.core.security import hash_password
from app.utils.logger import async_log
from app.repository.users import UserRepository
from app.exceptions.exceptions import (
    ItemsListException,
    ItemNotFoundException,
    ItemDetailException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemUpdateException,
    ItemDeleteException,
)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_users(self, page: int = 1, limit: int = 10) -> UserListSchema:
        try:
            users_count = await self.user_repository.get_users_count()
            pages_count = ceil(users_count / limit)
            page = max(1, min(pages_count, page))
            limit = max(1, limit)
            first_user = (page - 1) * limit

            users = await self.user_repository.get_users(first_user, limit)
            await async_log("Geting users list was successful.")
            users_schema = [UserBaseSchema.model_validate(user) for user in users]

            return UserListSchema(
                pages_count=pages_count,
                users_count=users_count,
                users=users_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get users list: {e}")
            raise ItemsListException("Users", e)

    async def get_user(self, user_id: str) -> UserDetailSchema:
        try:
            db_user = await self.user_repository.get_user_by_id(user_id)
            if not db_user:
                await async_log(f"User (ID {user_id}) not found.")
                raise ItemNotFoundException("User")
            await async_log(f"Getting user (ID {user_id}) was successful.")
            return UserDetailSchema.model_validate(db_user)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to get user (ID {user_id}): {e}")
            raise ItemDetailException("User", user_id, e)

    async def create_user(self, user: RegistrationSchema) -> UserDetailSchema:
        try:
            hashed_password = hash_password(user.password)
            created_user = UserModel(
                email=str(user.email),
                hashed_password=hashed_password,
                full_name=user.full_name,
            )

            existing_user = await self.user_repository.get_user_by_email(user.email)
            if existing_user:
                await async_log(f"User with email {user.email} is already registered.")
                raise ItemAlreadyExistException(
                    item_type="User",
                    unique_field_name="email",
                    unique_field_value=str(user.email),
                )

            db_user = await self.user_repository.save_user(created_user)

            await async_log(
                f"Creating user {db_user.email} (ID {db_user.id}) was successful."
            )
            return UserDetailSchema.model_validate(db_user)
        except ItemAlreadyExistException:
            raise
        except Exception as e:
            await async_log(f"Failed to create user {user.email}: {e}")
            raise ItemCreateException("User", e)

    async def update_user(
        self, user_id: str, update_data: UserUpdateSchema
    ) -> UserDetailSchema:
        try:
            db_user = await self.user_repository.get_user_by_id(user_id)

            if not db_user:
                await async_log("User with that id is not registered.")
                raise ItemNotFoundException("User")

            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(db_user, key, value)

            db_user = await self.user_repository.save_user(db_user)
            await async_log(
                f"Updating user {db_user.email} (ID {db_user.id}) was successful."
            )
            return UserDetailSchema.model_validate(db_user)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to update user: {e}")
            raise ItemUpdateException("User", user_id, e)

    async def delete_user(self, user_id: str):
        try:
            db_user = await self.user_repository.get_user_by_id(user_id)

            if not db_user:
                await async_log("User with that id is not registered.")
                raise ItemNotFoundException("User")

            deleted_user = await self.user_repository.delete_user(db_user)
            await async_log(
                f"User {deleted_user.email} (ID {user_id}) has been deleted."
            )
            return {
                "message": f"User {deleted_user.email} (ID {user_id}) has been deleted."
            }
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to delete user: {e}")
            raise ItemDeleteException("User", user_id, e)
