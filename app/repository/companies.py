from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.db.models.companies import CompanyModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_companies_count(self, owner_id: str):
        try:
            companies_count = await self.db.execute(
                select(func.count())
                .select_from(CompanyModel)
                .filter(
                    or_(
                        CompanyModel.owner_id == owner_id,
                        CompanyModel.is_visible == True,
                    )
                )
            )
            return companies_count.scalar() or 0
        except SQLAlchemyError as e:
            await async_log(f"Failed to get companies count from DB: {e}")
            raise DatabaseError(e)

    async def get_companies(self, offset: int, limit: int, owner_id: str):
        try:
            result = await self.db.scalars(
                select(CompanyModel)
                .filter(
                    or_(
                        CompanyModel.owner_id == owner_id,
                        CompanyModel.is_visible == True,
                    )
                )
                .offset(offset)
                .limit(limit)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get companies list from DB: {e}")
            raise DatabaseError(e)

    async def get_company_by_id(self, company_id: str):
        try:
            return await self.db.get(CompanyModel, company_id)
        except SQLAlchemyError as e:
            await async_log(f"Failed to get company (ID {company_id}) from DB: {e}")
            raise DatabaseError(e)

    async def get_company_by_name(self, name: str):
        try:
            return await self.db.scalar(
                select(CompanyModel).filter(CompanyModel.name == name)
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get company with name {name} from DB: {e}")
            raise DatabaseError(e)

    async def save_company(self, company: CompanyModel):
        try:
            self.db.add(company)
            await self.db.commit()
            await self.db.refresh(company)
            return company
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving company {company.name}: {e}")
            raise DatabaseError(e)

    async def delete_company(self, company: CompanyModel):
        try:
            await self.db.delete(company)
            await self.db.commit()

            return company
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete company (ID {company.id}) from DB.: {e}")
            raise DatabaseError(e)
