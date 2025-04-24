from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.users import get_user_service
from app.permissions.users import can_modify_user
from app.routers.auth import get_current_user
from app.services.users import UserService
from app.schemas.auth import RegistrationSchema
from app.schemas.users import (
    UserListSchema,
    UserDetailSchema,
    UserUpdateSchema,
)


user_router = APIRouter(prefix="/users", dependencies=[Depends(get_current_user)])


@user_router.get("/", response_model=UserListSchema)
async def get_users(
    page: int = 1,
    limit: int = 10,
    user_service: UserService = Depends(get_user_service),
) -> UserListSchema:
    return await user_service.get_users(page, limit)


@user_router.get("/{id}/", response_model=UserDetailSchema)
async def get_user(
    id: str, user_service: UserService = Depends(get_user_service)
) -> UserDetailSchema:
    return await user_service.get_user(id)


@user_router.post("/", response_model=UserDetailSchema)
async def create_user(
    user: RegistrationSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    return await user_service.create_user(user)


@user_router.patch(
    "/{id}/", response_model=UserDetailSchema, dependencies=[Depends(can_modify_user)]
)
async def update_user(
    id: str,
    update_data: UserUpdateSchema,
    user_service: UserService = Depends(get_user_service),
) -> UserDetailSchema:
    return await user_service.update_user(id, update_data)


@user_router.delete("/{id}/", dependencies=[Depends(can_modify_user)])
async def delete_user(
    id: str,
    user_service: UserService = Depends(get_user_service),
) -> JSONResponse:
    result = await user_service.delete_user(id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)
