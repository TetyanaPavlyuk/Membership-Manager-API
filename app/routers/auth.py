from fastapi import APIRouter, Depends, Response, Request
from fastapi.params import Header

from app.dependencies.auth import get_auth_service
from app.schemas.auth import (
    RegistrationSchema,
    LoginSchema,
    RegisterResponseSchema,
    LoginResponseSchema,
)
from app.schemas.users import UserDetailSchema
from app.services.auth import AuthService

auth_router = APIRouter()


@auth_router.post("/registration", response_model=RegisterResponseSchema)
async def registration(
    user_data: RegistrationSchema, auth_service: AuthService = Depends(get_auth_service)
) -> RegisterResponseSchema:
    return await auth_service.registration(user_data)


@auth_router.post("/login", response_model=LoginResponseSchema)
async def login(
    user_data: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponseSchema:
    return await auth_service.login(user_data)


@auth_router.get("/me", response_model=UserDetailSchema)
async def get_current_user(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDetailSchema:
    return await auth_service.get_current_user(authorization)
