from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.invitations import get_invitation_service
from app.permissions.companies import can_modify_company
from app.permissions.users import can_modify_user
from app.routers.auth import get_current_user
from app.schemas.users import UserDetailSchema
from app.services.invitations import InvitationService
from app.schemas.invitations import (
    InvitationDetailSchema,
    InvitationListSchema,
    InvitationCreateSchema,
    InvitationUpdateStatusSchema,
)


invitation_router = APIRouter(dependencies=[Depends(get_current_user)])


@invitation_router.get(
    "/companies/{company_id}/invitations/",
    response_model=InvitationListSchema,
    dependencies=[Depends(can_modify_company)],
)
async def get_invitations_from_company(
    company_id: str,
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> InvitationListSchema:
    return await invitation_service.get_invitations_from_company(company_id)


@invitation_router.get(
    "/users/{user_id}/invitations/",
    response_model=InvitationListSchema,
    dependencies=[Depends(can_modify_user)],
)
async def get_invitations_for_user(
    user_id: str,
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> InvitationListSchema:
    return await invitation_service.get_invitations_for_user(user_id)


@invitation_router.post(
    "/companies/{company_id}/invitations/",
    response_model=InvitationDetailSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(can_modify_company)],
)
async def create_invitation(
    company_id: str,
    payload: InvitationCreateSchema,
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> InvitationDetailSchema:
    return await invitation_service.create_invitation(company_id, payload.user_id)


@invitation_router.delete(
    "/companies/{company_id}/invitations/{invitation_id}/",
    dependencies=[Depends(can_modify_company)],
)
async def delete_invitation(
    invitation_id: str,
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> JSONResponse:
    result = await invitation_service.delete_invitation(invitation_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)


@invitation_router.patch("/users/{user_id}/invitations/{invitation_id}/")
async def accept_or_decline_invitation(
    invitation_id: str,
    new_status: InvitationUpdateStatusSchema,
    current_user: UserDetailSchema = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    return await invitation_service.change_invitation_status(
        invitation_id, new_status.status, current_user.id
    )
