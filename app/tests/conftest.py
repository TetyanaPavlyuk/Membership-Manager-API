import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest_asyncio

from fastapi import status
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.db.models import CompanyModel
from app.db.session_postgresql import engine
from app.db.models.users import UserModel
from app.main import server
from app.dependencies.users import get_async_db
from app.repository.companies import CompanyRepository
from app.repository.users import UserRepository
from app.schemas.auth import LoginSchema
from app.services.auth import AuthService

TEST_DB: str = "test_db"
TEST_DB_URL: str = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{TEST_DB}"
)
TEST_ENGINE = create_async_engine(TEST_DB_URL, future=True, echo=True)
TestSessionLocal = sessionmaker(
    bind=TEST_ENGINE, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def get_test_db() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(autouse=True)
async def set_testing_env():
    origin_env = settings.ENVIRONMENT
    settings.ENVIRONMENT = "testing"
    yield
    settings.ENVIRONMENT = origin_env


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # create test DB
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))
        await conn.execute(text(f"CREATE DATABASE {TEST_DB}"))
    # create test tables
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(UserModel.metadata.create_all)
    yield
    # drop all tables and delete test DB
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(UserModel.metadata.drop_all)
    async with engine.connect() as conn:
        conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(
            text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{TEST_DB}' AND pid <> pg_backend_pid();"
            )
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB}"))


@pytest_asyncio.fixture
async def user_repository():
    async with get_test_db() as session:
        yield UserRepository(session)


@pytest_asyncio.fixture
async def company_repository():
    async with get_test_db() as session:
        yield CompanyRepository(session)


@pytest_asyncio.fixture
def users_create_data():
    return [
        {"email": "test1@mail.com", "hashed_password": "test12345"},
        {"email": "test2@mail.com", "hashed_password": "test12345"},
    ]


@pytest_asyncio.fixture
async def companies_create_data(user_repository):
    return [
        {
            "name": "Some company",
            "description": "Some description",
            "is_visible": False,
        },
        {"name": "Other company", "description": None},
    ]


@pytest_asyncio.fixture
async def setup_users(user_repository, users_create_data):
    users = [UserModel(**user_data) for user_data in users_create_data]
    for user in users:
        await user_repository.save_user(user)
    yield users
    for user in users:
        await user_repository.delete_user(user)


@pytest_asyncio.fixture
async def setup_companies(company_repository, user_repository, companies_create_data):
    user = UserModel(email="test@mail.com", hashed_password="test12345")
    db_user = await user_repository.save_user(user)
    companies = [
        CompanyModel(owner_id=db_user.id, **company_data)
        for company_data in companies_create_data
    ]
    saved_companies = [
        await company_repository.save_company(company) for company in companies
    ]
    yield saved_companies
    for company in saved_companies:
        await company_repository.delete_company(company)
    await user_repository.delete_user(db_user)


@pytest_asyncio.fixture
async def test_email():
    return "test@mail.com"


@pytest_asyncio.fixture
async def login_data():
    return LoginSchema(email="test@mail.com", password="Test12345?")


@pytest_asyncio.fixture
async def db_user(login_data):
    return UserModel(
        id="3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        email=str(login_data.email),
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        full_name=None,
    )


@pytest_asyncio.fixture
async def mock_user_service(db_user):
    mock_repository = AsyncMock()
    mock_repository.get_user_by_email.return_value = db_user
    user_service = AsyncMock()
    user_service.user_repository = mock_repository
    user_service.create_user.return_value = db_user
    return user_service


@pytest_asyncio.fixture
async def auth_service(mock_user_service):
    return AuthService(mock_user_service)


@pytest_asyncio.fixture(scope="session")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncClient, None]:
        async with get_test_db() as session:
            yield session

    server.app.dependency_overrides[get_async_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=server.app), base_url="http://test"
    ) as client:
        yield client
    server.app.dependency_overrides.clear()


async def user_token_id_func(test_client: AsyncClient):
    email = f"user_{uuid.uuid4().hex[:8]}@mail.com"
    password = "Test12345?"

    registration_response = await test_client.post(
        "/registration",
        json={"email": email, "password": password, "full_name": "Full Name"},
    )

    assert registration_response.status_code == status.HTTP_201_CREATED

    login_response = await test_client.post(
        "/login", json={"email": email, "password": password}
    )

    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()["access_token"]

    get_user_response = await test_client.get(
        "/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert get_user_response.status_code == status.HTTP_200_OK
    user_id = get_user_response.json()["id"]

    return access_token, user_id


@pytest_asyncio.fixture
async def user_token_id(test_client):
    return await user_token_id_func(test_client)


@pytest_asyncio.fixture
async def access_token(user_token_id):
    return user_token_id[0]


@pytest_asyncio.fixture
async def user_id(user_token_id):
    return user_token_id[1]
