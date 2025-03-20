from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.utils.logger import async_log

from app.config.settings import settings


POSTGRES_URL = settings.POSTGRES_URL

engine = create_async_engine(POSTGRES_URL)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        await async_log("Connecting to database")
        yield session
        await async_log("Database connection closed.")
