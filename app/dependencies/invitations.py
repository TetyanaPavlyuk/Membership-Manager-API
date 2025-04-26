from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.dependencies.memberships import get_membership_service
from app.repository import InvitationRepository, RequestRepository
from app.services.invitations import InvitationService
from app.services.memberships import MembershipService


async def get_invitation_service(
    db: AsyncSession = Depends(get_async_db),
    membership_service: MembershipService = Depends(get_membership_service),
) -> InvitationService:
    invitation_repository = InvitationRepository(db)
    request_repository = RequestRepository(db)
    return InvitationService(
        invitation_repository, request_repository, membership_service
    )
