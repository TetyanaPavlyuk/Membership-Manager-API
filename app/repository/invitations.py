from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.db.models import InvitationModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class InvitationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_invitations_from_company(self, company_id: str):
        try:
            result = await self.db.scalars(
                select(InvitationModel).filter(InvitationModel.company_id == company_id)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get invitations list from DB: {e}")
            raise DatabaseError(e)

    async def get_invitations_for_user(self, user_id: str):
        try:
            result = await self.db.scalars(
                select(InvitationModel).filter(InvitationModel.user_id == user_id)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get invitations list from DB: {e}")
            raise DatabaseError(e)

    async def get_invitation_by_id(self, invitation_id: str):
        try:
            return await self.db.get(InvitationModel, invitation_id)
        except SQLAlchemyError as e:
            await async_log(
                f"Failed to get invitation (ID {invitation_id}) from DB: {e}"
            )
            raise DatabaseError(e)

    async def get_invitation_by_company_and_user_id(
        self, company_id: str, user_id: str
    ):
        try:
            return await self.db.scalar(
                select(InvitationModel).where(
                    InvitationModel.company_id == company_id,
                    InvitationModel.user_id == user_id,
                )
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get invitation from DB: {e}")
            raise DatabaseError(e)

    async def save_invitation(self, invitation: InvitationModel):
        try:
            self.db.add(invitation)
            await self.db.commit()
            await self.db.refresh(invitation)
            return invitation
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving invitation: {e}")
            raise DatabaseError(e)

    async def delete_invitation(self, invitation: InvitationModel):
        try:
            await self.db.delete(invitation)
            await self.db.commit()

            return invitation
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete invitation from DB.: {e}")
            raise DatabaseError(e)
