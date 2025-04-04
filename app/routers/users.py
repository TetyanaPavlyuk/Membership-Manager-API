from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.users import get_user_service
from app.services.users import UserService
from app.schemas.auth import RegisterSchema
from app.schemas.users import (
    UserListSchema,
    UserDetailSchema,
    UserUpdateSchema,
)


user_router = APIRouter(prefix="/users")


@user_router.get("/", response_model=UserListSchema)
async def get_users(
    page: int = 1,
    size: int = 10,
    user_service: UserService = Depends(get_user_service),
) -> UserListSchema:
    return await user_service.get_users(page, size)


@user_router.get("/{id}/", response_model=UserDetailSchema)
async def get_user(
    id: int, user_service: UserService = Depends(get_user_service)
) -> UserDetailSchema:
    return await user_service.get_user(id)


@user_router.post("/", response_model=UserDetailSchema)
async def create_user(
    user: RegisterSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    return await user_service.create_user(user)


@user_router.patch("/{id}/update/", response_model=UserDetailSchema)
async def update_user(
    id: int,
    update_data: UserUpdateSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    return await user_service.update_user(id, update_data)


@user_router.delete("/{id}/delete/")
async def delete_user(
    id: int, user_service: UserService = Depends(get_user_service)
) -> JSONResponse:
    result = await user_service.delete_user(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)
