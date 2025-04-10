import pytest

from app.db.models.users import UserModel


@pytest.mark.asyncio(loop_scope="session")
async def test_save_user(user_repository, users_create_data):
    users = [UserModel(**user_data) for user_data in users_create_data]
    saved_user = [await user_repository.save_user(user) for user in users]

    assert saved_user[0].email == users_create_data[0]["email"]
    assert saved_user[1].email == users_create_data[1]["email"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_users_count(user_repository, users_create_data):
    users_count = await user_repository.get_users_count()
    assert users_count == len(users_create_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_users(user_repository, users_create_data):
    users_list = await user_repository.get_users(0, 10)
    assert [user.email for user in users_list] == [
        user_data["email"] for user_data in users_create_data
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id(user_repository, users_create_data):
    user1_email = users_create_data[0]["email"]
    user2_email = users_create_data[1]["email"]
    user1 = await user_repository.get_user_by_email(user1_email)
    user1_id = user1.id
    user2 = await user_repository.get_user_by_email(user2_email)
    user2_id = user2.id
    test_user1 = await user_repository.get_user_by_id(user1_id)
    test_user2 = await user_repository.get_user_by_id(user2_id)
    assert test_user1.email == user1_email
    assert test_user2.email == user2_email


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_email(user_repository, users_create_data):
    email1 = users_create_data[0]["email"]
    email2 = users_create_data[1]["email"]
    user1 = await user_repository.get_user_by_email(email1)
    user2 = await user_repository.get_user_by_email(email2)
    assert user1.email == email1
    assert user2.email == email2


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(user_repository, clear_user_table):
    user_data = {"email": "test3@mail.com", "hashed_password": "test12345"}
    user = UserModel(**user_data)
    db_user = await user_repository.save_user(user)
    await user_repository.delete_user(user)
    deleted_user = await user_repository.get_user_by_id(db_user.id)
    assert deleted_user is None
