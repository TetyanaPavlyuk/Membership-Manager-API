from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from app.db.models import RequestModel
from app.utils.logger import async_log
from app.exceptions.exceptions import DatabaseError


class RequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_requests_for_company(self, company_id: str):
        try:
            result = await self.db.scalars(
                select(RequestModel).filter(RequestModel.company_id == company_id)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get requests list from DB: {e}")
            raise DatabaseError(e)

    async def get_requests_from_user(self, user_id: str):
        try:
            result = await self.db.scalars(
                select(RequestModel).filter(RequestModel.user_id == user_id)
            )
            return result.all()
        except SQLAlchemyError as e:
            await async_log(f"Failed to get requests list from DB: {e}")
            raise DatabaseError(e)

    async def get_request_by_id(self, request_id: str):
        try:
            return await self.db.get(RequestModel, request_id)
        except SQLAlchemyError as e:
            await async_log(f"Failed to get request (ID {request_id}) from DB: {e}")
            raise DatabaseError(e)

    async def get_request_by_company_and_user_id(self, company_id: str, user_id: str):
        try:
            return await self.db.scalar(
                select(RequestModel).where(
                    RequestModel.company_id == company_id,
                    RequestModel.user_id == user_id,
                )
            )
        except SQLAlchemyError as e:
            await async_log(f"Failed to get request from DB: {e}")
            raise DatabaseError(e)

    async def save_request(self, request: RequestModel):
        try:
            self.db.add(request)
            await self.db.commit()
            await self.db.refresh(request)
            return request
        except SQLAlchemyError as e:
            await async_log(f"DB error while saving request: {e}")
            raise DatabaseError(e)

    async def delete_request(self, request: RequestModel):
        try:
            await self.db.delete(request)
            await self.db.commit()

            return request
        except SQLAlchemyError as e:
            await async_log(f"Failed to delete request from DB.: {e}")
            raise DatabaseError(e)
