from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.memberships import get_membership_service
from app.permissions.companies import can_modify_company
from app.permissions.users import can_modify_user
from app.routers.auth import get_current_user
from app.services.memberships import MembershipService
from app.schemas.memberships import MembershipsListSchema


membership_router = APIRouter(dependencies=[Depends(get_current_user)])


@membership_router.get(
    "/companies/{company_id}/memberships/",
    response_model=MembershipsListSchema,
    dependencies=[Depends(can_modify_company)],
)
async def get_memberships_for_company(
    company_id: str,
    page: int = 1,
    limit: int = 10,
    membership_service: MembershipService = Depends(get_membership_service),
) -> MembershipsListSchema:
    return await membership_service.get_memberships_for_company(company_id, page, limit)


@membership_router.get(
    "/users/{user_id}/memberships/",
    response_model=MembershipsListSchema,
    dependencies=[Depends(can_modify_user)],
)
async def get_memberships_for_user(
    user_id: str,
    page: int = 1,
    limit: int = 10,
    membership_service: MembershipService = Depends(get_membership_service),
) -> MembershipsListSchema:
    return await membership_service.get_memberships_for_user(user_id, page, limit)


@membership_router.delete(
    "/companies/{company_id}/memberships/{membership_id}/",
    dependencies=[Depends(can_modify_company)],
)
async def delete_membership_for_company(
    membership_id: str,
    membership_service: MembershipService = Depends(get_membership_service),
) -> JSONResponse:
    result = await membership_service.delete_membership(membership_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)


@membership_router.delete(
    "/users/{user_id}/memberships/{membership_id}/",
    dependencies=[Depends(can_modify_user)],
)
async def delete_membership_for_user(
    membership_id: str,
    membership_service: MembershipService = Depends(get_membership_service),
) -> JSONResponse:
    result = await membership_service.delete_membership(membership_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)
