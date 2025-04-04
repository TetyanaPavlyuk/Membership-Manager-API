from fastapi import Depends

from app.dependencies.tokens import get_token_service
from app.dependencies.users import get_user_service
from app.services.auth import AuthService
from app.services.tokens import TokenService
from app.services.users import UserService


async def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
):
    return AuthService(user_service, token_service)
