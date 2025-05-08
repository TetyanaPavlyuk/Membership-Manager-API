from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.repository import MembershipRepository
from app.services.memberships import MembershipService


async def get_membership_service(
    db: AsyncSession = Depends(get_async_db),
) -> MembershipService:
    membership_repository = MembershipRepository(db)
    return MembershipService(membership_repository)
