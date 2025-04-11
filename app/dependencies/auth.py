from fastapi import Depends

from app.dependencies.users import get_user_service
from app.services.auth import AuthService
from app.services.users import UserService


async def get_auth_service(
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(user_service)
