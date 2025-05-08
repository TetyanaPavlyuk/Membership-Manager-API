from math import ceil

from app.db.models.companies import CompanyModel
from app.schemas.companies import (
    CompanyUpdateSchema,
    CompanyListSchema,
    CompanyBaseSchema,
    CompanyDetailSchema,
    CompanyCreateSchema,
)
from app.schemas.users import UserDetailSchema
from app.utils.logger import async_log
from app.repository.companies import CompanyRepository
from app.exceptions.exceptions import (
    ItemsListException,
    ItemNotFoundException,
    ItemDetailException,
    ItemAlreadyExistException,
    ItemCreateException,
    ItemUpdateException,
    ItemDeleteException,
    ForbiddenException,
)


class CompanyService:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    async def get_companies(
        self, owner_id: str, page: int = 1, limit: int = 10
    ) -> CompanyListSchema:
        try:
            companies_count = await self.company_repository.get_companies_count(
                owner_id
            )
            pages_count = ceil(companies_count / limit)
            page = max(1, min(pages_count, page))
            limit = max(1, limit)
            first_company = (page - 1) * limit

            companies = await self.company_repository.get_companies(
                first_company, limit, owner_id
            )
            await async_log("Geting companies list was successful.")
            companies_schema = [
                CompanyBaseSchema.model_validate(company) for company in companies
            ]

            return CompanyListSchema(
                pages_count=pages_count,
                companies_count=companies_count,
                companies=companies_schema,
            )
        except Exception as e:
            await async_log(f"Failed to get companies list: {e}")
            raise ItemsListException("Companies", e)

    async def get_company(self, company_id: str, owner_id: str) -> CompanyDetailSchema:
        try:
            db_company = await self.company_repository.get_company_by_id(company_id)
            if not db_company:
                await async_log(f"Company (ID {company_id}) not found.")
                raise ItemNotFoundException("Company")
            if db_company.owner_id != owner_id and db_company.is_visible is False:
                await async_log("User does not have permission to access this company")
                raise ForbiddenException
            await async_log(f"Getting company (ID {company_id}) was successful.")
            return CompanyDetailSchema.model_validate(db_company)
        except (ItemNotFoundException, ForbiddenException):
            raise
        except Exception as e:
            await async_log(f"Failed to get company (ID {company_id}): {e}")
            raise ItemDetailException("Company", company_id, e)

    async def create_company(
        self, company: CompanyCreateSchema, user: UserDetailSchema
    ) -> CompanyDetailSchema:
        try:
            existing_company = await self.company_repository.get_company_by_name(
                company.name
            )
            if existing_company:
                await async_log(f"Company with name {company.name} is already exist.")
                raise ItemAlreadyExistException(
                    item_type="Company",
                    unique_field_name="name",
                    unique_field_value=company.name,
                )

            created_company = CompanyModel(
                name=company.name,
                description=company.description,
                is_visible=company.is_visible,
                owner_id=user.id,
            )

            db_company = await self.company_repository.save_company(created_company)

            await async_log(
                f"Creating company {db_company.name} (ID {db_company.id}) was successful."
            )
            return CompanyDetailSchema.model_validate(db_company)
        except ItemAlreadyExistException:
            raise
        except Exception as e:
            await async_log(f"Failed to create company {company.name}: {e}")
            raise ItemCreateException("Company", e)

    async def update_company(
        self, company_id: str, update_data: CompanyUpdateSchema
    ) -> CompanyDetailSchema:
        try:
            db_company = await self.company_repository.get_company_by_id(company_id)

            if not db_company:
                await async_log("Company with that id is not registered.")
                raise ItemNotFoundException("Company")

            existing_company = await self.company_repository.get_company_by_name(
                update_data.name
            )
            if existing_company and existing_company.id != db_company.id:
                await async_log(
                    f"Company with name {update_data.name} is already exist."
                )
                raise ItemAlreadyExistException(
                    item_type="Company",
                    unique_field_name="name",
                    unique_field_value=update_data.name,
                )

            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(db_company, key, value)

            db_company = await self.company_repository.save_company(db_company)
            await async_log(
                f"Updating company {db_company.name} (ID {db_company.id}) was successful."
            )
            return CompanyDetailSchema.model_validate(db_company)
        except (ItemNotFoundException, ItemAlreadyExistException):
            raise
        except Exception as e:
            await async_log(f"Failed to update company: {e}")
            raise ItemUpdateException("Company", company_id, e)

    async def delete_company(self, company_id: str):
        try:
            db_company = await self.company_repository.get_company_by_id(company_id)

            if not db_company:
                await async_log("Company with that id is not exist.")
                raise ItemNotFoundException("Company")

            deleted_company = await self.company_repository.delete_company(db_company)
            await async_log(
                f"Company {deleted_company.name} (ID {company_id}) has been deleted."
            )
            return {
                "message": f"Company {deleted_company.name} (ID {company_id}) has been deleted."
            }
        except ItemNotFoundException:
            raise
        except Exception as e:
            await async_log(f"Failed to delete company: {e}")
            raise ItemDeleteException("Company", company_id, e)
