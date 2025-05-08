from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.dependencies.memberships import get_membership_service
from app.repository import RequestRepository, InvitationRepository
from app.services.memberships import MembershipService
from app.services.requests import RequestService


async def get_request_service(
    db: AsyncSession = Depends(get_async_db),
    membership_service: MembershipService = Depends(get_membership_service),
) -> RequestService:
    request_repository = RequestRepository(db)
    invitation_repository = InvitationRepository(db)
    return RequestService(request_repository, invitation_repository, membership_service)
