from fastapi import APIRouter, Depends

from app.dependencies.users import get_user_service
from app.services.users import UserService
from app.schemas.users import UserBaseSchema, UserListSchema, UserDetailSchema, UserSignUpSchema, UserSignInSchema, UserUpdateSchema


class UserRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/users")

        self.router.add_api_route("/", self.get_users, methods=["GET"], response_model=UserListSchema)
        self.router.add_api_route("/{id}/", self.get_user, methods=["GET"], response_model=UserDetailSchema)
        self.router.add_api_route("/", self.create_user, methods=["POST"], response_model=UserDetailSchema)
        self.router.add_api_route("/update/", self.update_user, methods=["PATCH"], response_model=UserDetailSchema)
        self.router.add_api_route("/delete/", self.delete_user, methods=["DELETE"])


    async def get_users(self, page: int = 1, size: int = 10, user_service: UserService = Depends(get_user_service)):
        response = await user_service.get_users(page, size)
        users = [UserBaseSchema.model_validate(user.__dict__) for user in response.get("users")]
        return UserListSchema(
            prev_page=f"/users/?page={page - 1}&size={size}" if page > 1 else None,
            next_page=f"/users/?page={page + 1}&size={size}" if page < response.get("pages_count") else None,
            pages_count=response.get("pages_count"),
            users_count=response.get("users_count"),
            users=users
        )

    async def get_user(self, id: int, user_service: UserService = Depends(get_user_service)):
        return await user_service.get_user(id)

    async def create_user(self, user: UserSignUpSchema, user_service: UserService = Depends(get_user_service)):
        return await user_service.create_user(user)

    async def update_user(self, id: int, update_data: UserUpdateSchema, user_service: UserService = Depends(get_user_service)):
        return await user_service.update_user(id, update_data)

    async def delete_user(self, id: int, user_service: UserService = Depends(get_user_service)):
        return await user_service.delete_user(id)


user_router = UserRouter().router
