from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse

from app.dependencies.auth import get_auth_service
from app.schemas.auth import (
    RegistrationSchema,
    LoginSchema,
    LoginResponseSchema,
)
from app.schemas.users import UserDetailSchema
from app.services.auth import AuthService

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@auth_router.post("/registration")
async def registration(
    user_data: RegistrationSchema, auth_service: AuthService = Depends(get_auth_service)
) -> JSONResponse:
    result = await auth_service.registration(user_data)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


@auth_router.post("/login", response_model=LoginResponseSchema)
async def login(
    login_data: LoginSchema, auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponseSchema:
    return await auth_service.login(login_data)


@auth_router.get("/me", response_model=UserDetailSchema)
async def get_current_user(
    authorization: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDetailSchema:
    return await auth_service.get_current_user(authorization)
