import asyncio

import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.db.session_postgresql import engine
from app.db.models.users import UserModel
from app.main import server
from app.dependencies.users import get_async_db


TEST_DB: str = "test_db"


@pytest_asyncio.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(autouse=True)
async def set_testing_env():
    origin_env = settings.ENVIRONMENT
    settings.ENVIRONMENT = "testing"
    yield
    settings.ENVIRONMENT = origin_env


@pytest_asyncio.fixture(scope="session")
def test_db_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DB}"
    )


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_db_url):
    return create_async_engine(test_db_url, future=True, echo=True)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db(test_engine):
    # create test DB
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB}"))
    # create test tables
    async with test_engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
    yield
    # drop all tables and delete test DB
    async with test_engine.begin() as conn:
        await conn.run_sync(UserModel.metadata.drop_all)
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB}' AND pid <> pg_backend_pid();"
            )
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))


@pytest_asyncio.fixture()
async def get_test_db(test_engine) -> AsyncSession:
    test_session_local = sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with test_session_local() as session:
        yield session


@pytest_asyncio.fixture()
async def clear_user_table(get_test_db):
    yield
    async with get_test_db as session:
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        await session.commit()


@pytest_asyncio.fixture()
async def test_client():

    async def override_get_db():
        async with get_test_db() as session:
            yield session

    server.app.dependency_overrides[get_async_db()] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=server.app), base_url="http://"
    ) as cl:
        yield cl

    server.app.dependency_overrides.clear()
