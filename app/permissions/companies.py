from fastapi import Depends, Path

from app.dependencies.companies import get_company_service
from app.exceptions.exceptions import ForbiddenException
from app.routers.auth import get_current_user
from app.schemas.users import UserDetailSchema
from app.services.companies import CompanyService
from app.utils.logger import async_log


async def can_modify_company(
    company_id: str = Path(...),
    current_user: UserDetailSchema = Depends(get_current_user),
    company_service: CompanyService = Depends(get_company_service),
):

    company = await company_service.get_company(company_id, current_user.id)

    if company.owner_id != current_user.id:
        async_log("User does not have permission to access this resource")
        raise ForbiddenException
    return company
