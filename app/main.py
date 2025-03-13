import asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.exceptions import ConnectionError

from app.config.settings import settings
from app.db.session_postgresql import get_db
from app.db.session_redis import set_redis_value, get_redis_value
from app.utils.logger import async_log


class Server:
    def __init__(self):
        self.app = FastAPI()

        origins = settings.parse_origins
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            await async_log("Root endpoint accessed.")
            return {"status_code": 200, "detail": "ok", "result": "working"}

        @self.app.get("/check-db")
        async def check_db(db: AsyncSession = Depends(get_db)):
            try:
                await async_log("Checking PostgreSQL connection.")
                result = await db.execute(text("SELECT 1"))
                await async_log("PostgreSQL connection is successful.")
                return {"message": "Postgres is connected", "result": result}
            except SQLAlchemyError as e:
                await async_log(f"PostgreSQL connection failed: {e}")
                raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


        @self.app.get("/check-redis")
        async def check_redis():
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


server = Server()
