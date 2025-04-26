from app.db.enums import StatusEnum
from app.db.models import InvitationModel
from app.schemas.invitations import (
    InvitationDetailSchema,
    InvitationListSchema,
)
from app.utils.logger import async_log
from app.repository import InvitationRepository, RequestRepository
from app.services.memberships import MembershipService
from app.exceptions.exceptions import (
    ItemsListException,
    ItemNotFoundException,
    ItemDetailException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemDeleteException,
    ItemUpdateException,
    ForbiddenException,
)


class InvitationService:
    def __init__(
        self,
        invitation_repository: InvitationRepository,
        request_repository: RequestRepository,
        membership_service: MembershipService,
    ):
        self.invitation_repository = invitation_repository
        self.request_repository = request_repository
        self.membership_service = membership_service

    async def get_invitations_from_company(
        self, company_id: str
    ) -> InvitationListSchema:
        try:
            invitations = await self.invitation_repository.get_invitations_from_company(
                company_id
            )
            await async_log("Geting invitations list was successful.")
            invitations_detail_schema = [
                InvitationDetailSchema.model_validate(invitation)
                for invitation in invitations
            ]

            return InvitationListSchema(
                invitations=invitations_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get invitations list: {e}")
            raise ItemsListException("Invitations", e)

    async def get_invitations_for_user(self, user_id: str) -> InvitationListSchema:
        try:
            invitations = await self.invitation_repository.get_invitations_for_user(
                user_id
            )
            await async_log("Geting invitations list was successful.")
            invitations_detail_schema = [
                InvitationDetailSchema.model_validate(invitation)
                for invitation in invitations
            ]

            return InvitationListSchema(
                invitations=invitations_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get invitations list: {e}")
            raise ItemsListException("Invitations", e)

    async def get_invitation(self, invitation_id) -> InvitationDetailSchema:
        try:
            db_invitation = await self.invitation_repository.get_invitation_by_id(
                invitation_id
            )
            if not db_invitation:
                await async_log("Invitation not found.")
                raise ItemNotFoundException("Invitation")
            await async_log(f"Getting invitation (ID {invitation_id}) was successful.")
            return InvitationDetailSchema.model_validate(db_invitation)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to get invitation (ID {invitation_id}): {e}")
            raise ItemDetailException("Invitation", invitation_id, e)

    async def create_invitation(
        self, company_id: str, user_id: str
    ) -> InvitationDetailSchema:
        try:
            existing_invitation = (
                await self.invitation_repository.get_invitation_by_company_and_user_id(
                    company_id, user_id
                )
            )
            if existing_invitation:
                await async_log(f"Invitation for user {user_id} is already exist.")
                raise ItemAlreadyExistException(
                    item_type="Invitation",
                    unique_field_name="user_id",
                    unique_field_value=user_id,
                )

            existing_request = (
                await self.request_repository.get_request_by_company_and_user_id(
                    company_id, user_id
                )
            )
            if existing_request:
                await async_log(f"Request from user {user_id} is already exist.")
                raise ItemAlreadyExistException(
                    item_type="Request",
                    unique_field_name="user_id",
                    unique_field_value=user_id,
                )

            existing_membership = await self.membership_service.membership_repository.get_membership_by_company_and_user_id(
                company_id, user_id
            )
            if existing_membership:
                await async_log(
                    f"Membership between user {user_id} and company {company_id} is already exist."
                )
                raise ItemAlreadyExistException(
                    item_type="Membership",
                    unique_field_name="[company_id, user_id]",
                    unique_field_value=f"[{company_id}, {user_id}]",
                )

            invitation_model = InvitationModel(company_id=company_id, user_id=user_id)
            db_invitation = await self.invitation_repository.save_invitation(
                invitation_model
            )

            await async_log(
                f"Creating invitation from {db_invitation.company_id} to {db_invitation.user_id} was successful."
            )
            return InvitationDetailSchema.model_validate(db_invitation)
        except ItemAlreadyExistException:
            raise
        except Exception as e:
            await async_log(f"Failed to create invitation: {e}")
            raise ItemCreateException("Invitation", e)

    async def delete_invitation(self, invitation_id: str):
        try:
            db_invitation = await self.invitation_repository.get_invitation_by_id(
                invitation_id
            )

            if not db_invitation:
                await async_log("Invitation with that id is not exist.")
                raise ItemNotFoundException("Invitation")

            await self.invitation_repository.delete_invitation(db_invitation)
            await async_log(f"Invitation (ID {invitation_id}) has been deleted.")
            return {"message": f"Invitation (ID {invitation_id}) has been deleted."}
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to delete invitation: {e}")
            raise ItemDeleteException("Invitation", invitation_id, e)

    async def change_invitation_status(
        self, invitation_id: str, new_status: StatusEnum, current_user_id: str
    ):
        try:
            db_invitation = await self.invitation_repository.get_invitation_by_id(
                invitation_id
            )
            if not db_invitation:
                await async_log("No such invitation exists.")
                raise ItemNotFoundException("Invitation")

            if current_user_id != db_invitation.user_id:
                await async_log(
                    "User does not have permission to access this invitation"
                )
                raise ForbiddenException

            if new_status == StatusEnum.ACCEPTED:
                await self.membership_service.create_membership(
                    db_invitation.company_id, db_invitation.user_id
                )
                await self.invitation_repository.delete_invitation(db_invitation)
                await async_log(f"Invitation accepted and membership created.")
                return {"message": "Invitation accepted and membership created."}

            else:
                db_invitation.status = new_status
                db_invitation = await self.invitation_repository.save_invitation(
                    db_invitation
                )
                await async_log(
                    f"Updating invitation status (ID {db_invitation.id}) to {new_status} was successful."
                )
                return {
                    "message": f"Updating invitation status (ID {db_invitation.id}) to {new_status} was successful."
                }
        except (ItemNotFoundException, ForbiddenException):
            raise
        except Exception as e:
            await async_log(f"Failed to update invitation: {e}")
            raise ItemUpdateException("Invitation", invitation_id, e)
