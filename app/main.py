from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.exceptions import ConnectionError

from app.config.settings import settings
from app.db.session_postgresql import get_db
from app.db.session_redis import set_redis_value, get_redis_value


app = FastAPI()

origins = settings.parse_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@app.get("/check-db")
async def check_db(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"message": "Postgres is connected", "result": result}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")


@app.get("/check-redis")
async def check_redis():
    try:
        await set_redis_value("some_key", "correct_value")
        result = await get_redis_value("some_key")

        if result == "correct_value":
            return {"message": "Redis is connected", "result": result}
        else:
            raise HTTPException(
                status_code=500, detail="Redis is not behaving as expected."
            )
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {e}")
