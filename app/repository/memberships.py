from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.db.models import MembershipModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class MembershipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_memberships_count_for_company(self, company_id: str):
        try:
            memberships_count = await self.db.execute(
                select(func.count())
                .select_from(MembershipModel)
                .filter(
                    MembershipModel.company_id == company_id,
                )
            )
            return memberships_count.scalar() or 0
        except SQLAlchemyError as e:
            await async_log(f"Failed to get memberships count from DB: {e}")
            raise DatabaseError(e)

    async def get_memberships_count_for_user(self, user_id: str):
        try:
            memberships_count = await self.db.execute(
                select(func.count())
                .select_from(MembershipModel)
                .filter(
                    MembershipModel.user_id == user_id,
                )
            )
            return memberships_count.scalar() or 0
        except SQLAlchemyError as e:
            await async_log(f"Failed to get memberships count from DB: {e}")
            raise DatabaseError(e)

    async def get_memberships_for_company(
        self, offset: int, limit: int, company_id: str
    ):
        try:
            result = await self.db.scalars(
                select(MembershipModel)
                .filter(MembershipModel.company_id == company_id)
                .offset(offset)
                .limit(limit)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get memberships list from DB: {e}")
            raise DatabaseError(e)

    async def get_memberships_for_user(self, offset: int, limit: int, user_id: str):
        try:
            result = await self.db.scalars(
                select(MembershipModel)
                .filter(MembershipModel.user_id == user_id)
                .offset(offset)
                .limit(limit)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get memberships list from DB: {e}")
            raise DatabaseError(e)

    async def get_membership_by_id(self, membership_id: str):
        try:
            return await self.db.get(MembershipModel, membership_id)
        except SQLAlchemyError as e:
            await async_log(
                f"Failed to get membership (ID {membership_id}) from DB: {e}"
            )
            raise DatabaseError(e)

    async def get_membership_by_company_and_user_id(
        self, company_id: str, user_id: str
    ):
        try:
            return await self.db.scalar(
                select(MembershipModel).where(
                    MembershipModel.company_id == company_id,
                    MembershipModel.user_id == user_id,
                )
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get membership from DB: {e}")
            raise DatabaseError(e)

    async def save_membership(self, membership: MembershipModel):
        try:
            self.db.add(membership)
            await self.db.commit()
            await self.db.refresh(membership)
            return membership
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving membership: {e}")
            raise DatabaseError(e)

    async def delete_membership(self, membership: MembershipModel):
        try:
            await self.db.delete(membership)
            await self.db.commit()

            return membership
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete membership from DB.: {e}")
            raise DatabaseError(e)
