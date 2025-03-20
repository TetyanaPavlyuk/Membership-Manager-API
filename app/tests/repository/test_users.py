import pytest

from app.db.models.users import UserModel
from app.repository.users import UserRepository

@pytest.fixture
def users_data():
    return [
        {"email": "test1@mail.com", "hashed_password": "test12345"},
        {"email": "test2@mail.com", "hashed_password": "test12345"}
    ]

@pytest.fixture
async def user_repository(get_test_db):
    return UserRepository(get_test_db)


@pytest.mark.asyncio(loop_scope="session")
async def test_save_user(user_repository, users_data):
    users = [UserModel(**user_data) for user_data in users_data]
    saved_user = [await user_repository.save_user(user) for user in users]

    assert saved_user[0].id == 1
    assert saved_user[1].id == 2
    assert saved_user[0].email == users_data[0]["email"]
    assert saved_user[1].email == users_data[1]["email"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_users_count(user_repository, users_data):
    users_count = await user_repository.get_users_count()
    assert users_count == len(users_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_users(user_repository, users_data):
    users_list = await user_repository.get_users(1, 10)
    assert [user.email for user in users_list] == [
        user_data["email"] for user_data in users_data
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id(user_repository, users_data):
    user1 = await user_repository.get_user_by_id(1)
    user2 = await user_repository.get_user_by_id(2)
    assert user1.email == users_data[0]["email"]
    assert user2.email == users_data[1]["email"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_email(user_repository, users_data):
    email1 = users_data[0]["email"]
    email2 = users_data[1]["email"]
    user1 = await user_repository.get_user_by_email(email1)
    user2 = await user_repository.get_user_by_email(email2)
    assert user1.id == 1
    assert user2.id == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(user_repository, clear_user_table):
    user_data = {"email": "test3@mail.com", "hashed_password": "test12345"}
    user = UserModel(**user_data)
    db_user = await user_repository.save_user(user)
    await user_repository.delete_user(user)
    deleted_user = await user_repository.get_user_by_id(db_user.id)
    assert deleted_user is None
