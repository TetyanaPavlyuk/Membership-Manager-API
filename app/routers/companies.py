from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.companies import get_company_service
from app.permissions.companies import can_modify_company
from app.routers.auth import get_current_user
from app.schemas.users import UserDetailSchema
from app.services.companies import CompanyService
from app.schemas.companies import (
    CompanyListSchema,
    CompanyDetailSchema,
    CompanyUpdateSchema,
    CompanyCreateSchema,
)


company_router = APIRouter(prefix="/companies")


@company_router.get("/", response_model=CompanyListSchema)
async def get_companies(
    page: int = 1,
    limit: int = 10,
    company_service: CompanyService = Depends(get_company_service),
    current_user: UserDetailSchema = Depends(get_current_user),
) -> CompanyListSchema:
    return await company_service.get_companies(current_user.id, page, limit)


@company_router.get("/{company_id}/", response_model=CompanyDetailSchema)
async def get_company(
    company_id: str,
    company_service: CompanyService = Depends(get_company_service),
    current_user: UserDetailSchema = Depends(get_current_user),
) -> CompanyDetailSchema:
    return await company_service.get_company(company_id, current_user.id)


@company_router.post("/", response_model=CompanyDetailSchema)
async def create_company(
    company: CompanyCreateSchema,
    company_service: CompanyService = Depends(get_company_service),
    current_user: UserDetailSchema = Depends(get_current_user),
) -> CompanyDetailSchema:
    return await company_service.create_company(company=company, user=current_user)


@company_router.patch(
    "/{company_id}/",
    response_model=CompanyDetailSchema,
    dependencies=[Depends(can_modify_company)],
)
async def update_company(
    company_id: str,
    update_data: CompanyUpdateSchema,
    company_service: CompanyService = Depends(get_company_service),
) -> CompanyDetailSchema:
    return await company_service.update_company(company_id, update_data)


@company_router.delete("/{company_id}/", dependencies=[Depends(can_modify_company)])
async def delete_company(
    company_id: str,
    company_service: CompanyService = Depends(get_company_service),
) -> JSONResponse:
    result = await company_service.delete_company(company_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)
