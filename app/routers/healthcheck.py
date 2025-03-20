from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.exceptions import ConnectionError

from app.db.session_postgresql import get_async_db
from app.db.session_redis import set_redis_value, get_redis_value
from app.utils.logger import async_log


class HealthCheckRouter:
    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route("/", self.root, methods=["GET"])
        self.router.add_api_route("/check-db", self.check_db, methods=["GET"])
        self.router.add_api_route("/check-redis", self.check_redis, methods=["GET"])

    async def root(self):
        await async_log("Root endpoint accessed.")
        return {"status_code": 200, "detail": "ok", "result": "working"}

    async def check_db(self, db: AsyncSession = Depends(get_async_db)):
        try:
            await async_log("Checking PostgreSQL connection.")
            result = await db.execute(text("SELECT 1"))
            await async_log("PostgreSQL connection is successful.")
            return {"message": "Postgres is connected", "result": result}
        except SQLAlchemyError as e:
            await async_log(f"PostgreSQL connection failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Database connection failed: {e}"
            )

    async def check_redis(self):
        try:
            await async_log("Checking Redis connection.")
            await set_redis_value("some_key", "correct_value")
            result = await get_redis_value("some_key")

            if result == "correct_value":
                await async_log("Redis connection is successful.")
                return {"message": "Redis is connected", "result": result}
            else:
                await async_log("Redis is not behaving as expected.")
                raise HTTPException(
                    status_code=500, detail="Redis is not behaving as expected."
                )
        except ConnectionError as e:
            await async_log(f"Redis connection failed: {e}")
            raise HTTPException(status_code=500, detail=f"Redis connection failed: {e}")


healthcheck_router = HealthCheckRouter().router
