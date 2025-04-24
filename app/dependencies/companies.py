from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session_postgresql import get_async_db
from app.repository.companies import CompanyRepository
from app.services.companies import CompanyService


async def get_company_service(
    db: AsyncSession = Depends(get_async_db),
) -> CompanyService:
    company_repository = CompanyRepository(db)
    return CompanyService(company_repository)
