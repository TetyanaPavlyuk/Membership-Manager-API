from math import ceil

from app.db.models import MembershipModel
from app.schemas.memberships import (
    MembershipDetailSchema,
    MembershipsListSchema,
)
from app.utils.logger import async_log
from app.repository import MembershipRepository
from app.exceptions.exceptions import (
    ItemsListException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemNotFoundException,
    ItemDeleteException,
)


class MembershipService:
    def __init__(self, membership_repository: MembershipRepository):
        self.membership_repository = membership_repository

    async def create_membership(
        self, company_id: str, user_id: str
    ) -> MembershipDetailSchema:
        try:
            existing_membership = (
                await self.membership_repository.get_membership_by_company_and_user_id(
                    company_id, user_id
                )
            )
            if existing_membership:
                await async_log("Membership is already exist.")
                raise ItemAlreadyExistException(
                    item_type="Membership",
                    unique_field_name="[company_id, user_id]",
                    unique_field_value=f"[{company_id}, {user_id}]",
                )

            membership_model = MembershipModel(company_id=company_id, user_id=user_id)
            db_membership = await self.membership_repository.save_membership(
                membership_model
            )

            await async_log(
                f"Creating membership between {db_membership.company_id} and {db_membership.user_id} was successful."
            )
            return MembershipDetailSchema.model_validate(db_membership)
        except ItemAlreadyExistException:
            raise
        except Exception as e:
            await async_log(f"Failed to create membership: {e}")
            raise ItemCreateException("Membership", e)

    async def get_memberships_for_company(
        self, company_id: str, page: int = 1, limit: int = 10
    ) -> MembershipsListSchema:
        try:
            memberships_count = (
                await self.membership_repository.get_memberships_count_for_company(
                    company_id
                )
            )
            pages_count = ceil(memberships_count / limit)
            page = max(1, min(pages_count, page))
            limit = max(1, limit)
            first_membership = (page - 1) * limit

            memberships_for_company = (
                await self.membership_repository.get_memberships_for_company(
                    first_membership, limit, company_id
                )
            )
            await async_log("Geting membeships list was successful.")
            memberships_detail_schema = [
                MembershipDetailSchema.model_validate(membership)
                for membership in memberships_for_company
            ]

            return MembershipsListSchema(
                pages_count=pages_count,
                memberships_count=memberships_count,
                memberships=memberships_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get memberships list: {e}")
            raise ItemsListException("Memberships", e)

    async def get_memberships_for_user(
        self, user_id: str, page: int = 1, limit: int = 10
    ) -> MembershipsListSchema:
        try:
            memberships_count = (
                await self.membership_repository.get_memberships_count_for_user(user_id)
            )
            pages_count = ceil(memberships_count / limit)
            page = max(1, min(pages_count, page))
            limit = max(1, limit)
            first_membership = (page - 1) * limit

            memberships_for_user = (
                await self.membership_repository.get_memberships_for_user(
                    first_membership, limit, user_id
                )
            )
            await async_log("Geting membeships list was successful.")
            memberships_detail_schema = [
                MembershipDetailSchema.model_validate(membership)
                for membership in memberships_for_user
            ]

            return MembershipsListSchema(
                pages_count=pages_count,
                memberships_count=memberships_count,
                memberships=memberships_detail_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get memberships list: {e}")
            raise ItemsListException("Memberships", e)

    async def delete_membership(self, membership_id: str):
        try:
            db_membership = await self.membership_repository.get_membership_by_id(
                membership_id
            )

            if not db_membership:
                await async_log("Membership with that id is not exist.")
                raise ItemNotFoundException("Membership")

            await self.membership_repository.delete_membership(db_membership)
            await async_log(f"Membership (ID {membership_id}) has been deleted.")
            return {"message": f"Membership (ID {membership_id}) has been deleted."}
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to delete membership: {e}")
            raise ItemDeleteException("Membership", membership_id, e)
