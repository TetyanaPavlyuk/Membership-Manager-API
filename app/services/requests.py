from app.db.enums import StatusEnum
from app.db.models import RequestModel
from app.schemas.requests import (
    RequestDetailSchema,
    RequestListSchema,
)
from app.services.memberships import MembershipService
from app.utils.logger import async_log
from app.repository import RequestRepository, InvitationRepository
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


class RequestService:
    def __init__(
        self,
        request_repository: RequestRepository,
        invitation_repository: InvitationRepository,
        membership_service: MembershipService,
    ):
        self.request_repository = request_repository
        self.invitation_repository = invitation_repository
        self.membership_service = membership_service

    async def get_requests_for_company(self, company_id: str) -> RequestListSchema:
        try:
            requests = await self.request_repository.get_requests_for_company(
                company_id
            )
            await async_log("Geting requests list was successful.")
            requests_detail_schema = [
                RequestDetailSchema.model_validate(request) for request in requests
            ]

            return RequestListSchema(
                requests=requests_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get requests list: {e}")
            raise ItemsListException("Requests", e)

    async def get_requests_from_user(self, user_id: str) -> RequestListSchema:
        try:
            requests = await self.request_repository.get_requests_from_user(user_id)
            await async_log("Geting requests list was successful.")
            requests_detail_schema = [
                RequestDetailSchema.model_validate(request) for request in requests
            ]

            return RequestListSchema(
                requests=requests_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get requests list: {e}")
            raise ItemsListException("Requests", e)

    async def get_request(self, request_id) -> RequestDetailSchema:
        try:
            db_request = await self.request_repository.get_request_by_id(request_id)
            if not db_request:
                await async_log("Request not found.")
                raise ItemNotFoundException("Request")
            await async_log(f"Getting request (ID {request_id}) was successful.")
            return RequestDetailSchema.model_validate(db_request)
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to get request (ID {request_id}): {e}")
            raise ItemDetailException("Request", request_id, e)

    async def create_request(
        self, company_id: str, user_id: str
    ) -> RequestDetailSchema:
        try:
            existing_request = (
                await self.request_repository.get_request_by_company_and_user_id(
                    company_id, user_id
                )
            )
            if existing_request:
                await async_log(f"Request for company {company_id} is already exist.")
                raise ItemAlreadyExistException(
                    item_type="Request",
                    unique_field_name="company_id",
                    unique_field_value=company_id,
                )

            existing_invitation = (
                await self.invitation_repository.get_invitation_by_company_and_user_id(
                    company_id, user_id
                )
            )
            if existing_invitation:
                await async_log(
                    f"Invitation from company {company_id} is already exist."
                )
                raise ItemAlreadyExistException(
                    item_type="Invitation",
                    unique_field_name="company_id",
                    unique_field_value=company_id,
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

            request_model = RequestModel(company_id=company_id, user_id=user_id)
            db_request = await self.request_repository.save_request(request_model)
            await async_log(
                f"Creating request from {db_request.user_id} to {db_request.company_id} was successful."
            )
            return RequestDetailSchema.model_validate(db_request)
        except ItemAlreadyExistException:
            raise
        except Exception as e:
            await async_log(f"Failed to create request: {e}")
            raise ItemCreateException("Request", e)

    async def delete_request(self, request_id: str):
        try:
            db_request = await self.request_repository.get_request_by_id(request_id)

            if not db_request:
                await async_log("Request with that id is not exist.")
                raise ItemNotFoundException("Request")

            await self.request_repository.delete_request(db_request)
            await async_log(f"Request (ID {request_id}) has been deleted.")
            return {"message": f"Request (ID {request_id}) has been deleted."}
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to delete request: {e}")
            raise ItemDeleteException("Request", request_id, e)

    async def change_request_status(self, request_id: str, new_status: StatusEnum):
        try:
            db_request = await self.request_repository.get_request_by_id(request_id)
            if not db_request:
                await async_log("No such request exists.")
                raise ItemNotFoundException("Request")

            if new_status == StatusEnum.ACCEPTED:
                await self.membership_service.create_membership(
                    db_request.company_id, db_request.user_id
                )
                await self.invitation_repository.delete_invitation(db_request)
                await async_log(f"Request accepted and membership created.")
                return {"message": "Request accepted and membership created."}

            else:
                db_request.status = new_status
                db_request = await self.request_repository.save_request(db_request)
                await async_log(
                    f"Updating request status (ID {db_request.id}) to {new_status} was successful."
                )
            return {
                "message": f"Updating request status (ID {db_request.id}) to {new_status} was successful."
            }
        except (ItemNotFoundException, ForbiddenException):
            raise
        except Exception as e:
            await async_log(f"Failed to update request: {e}")
            raise ItemUpdateException("Request", request_id, e)
