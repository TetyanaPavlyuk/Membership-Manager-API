from fastapi import Depends, Path

from app.exceptions.exceptions import ForbiddenException
from app.routers.auth import get_current_user
from app.schemas.users import UserDetailSchema
from app.utils.logger import async_log


async def can_modify_user(
    modify_user_id: str = Path(..., alias="user_id"),
    current_user: UserDetailSchema = Depends(get_current_user),
):
    if current_user.id != modify_user_id:
        await async_log("User does not have permission to access this resource")
        raise ForbiddenException
    return True
