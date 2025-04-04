from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.params import Header

from app.dependencies.auth import get_auth_service
from app.schemas.auth import (
    RegisterSchema,
    LoginSchema,
    RegisterResponseSchema,
    LoginResponseSchema,
)
from app.schemas.users import UserDetailSchema
from app.services.auth import AuthService
from app.utils.logger import async_log

auth_router = APIRouter()


@auth_router.post("/registration", response_model=RegisterResponseSchema)
async def registration(
    user_data: RegisterSchema, auth_service: AuthService = Depends(get_auth_service)
) -> RegisterResponseSchema:
    return await auth_service.registration(user_data)


@auth_router.post("/login", response_model=LoginResponseSchema)
async def login(
    user_data: LoginSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponseSchema:
    return await auth_service.login(user_data, response)


@auth_router.post("/login-social", response_model=LoginResponseSchema)
async def login_social(
    auth0_token: str,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponseSchema:
    result = await auth_service.login_social(auth0_token, response)
    return result


@auth_router.post("/logout")
async def logout(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    return await auth_service.logout(authorization)


@auth_router.get("/me", response_model=UserDetailSchema)
async def get_current_user(
    request: Request,
    response: Response,
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDetailSchema:
    return await auth_service.get_current_user(authorization, request, response)
