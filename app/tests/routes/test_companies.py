import pytest

from fastapi import status

from app.db.models import CompanyModel, UserModel


@pytest.mark.asyncio(loop_scope="session")
async def test_user_get_own_and_visible_companies(
    test_client, access_token, user_id, company_repository, user_repository
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    visible_other = CompanyModel(
        name="Visible Other Company", is_visible=True, owner_id=other_user_db.id
    )
    invisible_other = CompanyModel(
        name="Invisible Other Company", is_visible=False, owner_id=other_user_db.id
    )

    for company in [own_company, visible_other, invisible_other]:
        await company_repository.save_company(company)

    response = await test_client.get(
        f"/companies/",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["companies"]
    names = [company["name"] for company in data]
    assert own_company.name in names
    assert visible_other.name in names
    assert invisible_other.name not in names

    for company in [own_company, visible_other, invisible_other]:
        await company_repository.delete_company(company)
    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_update_own_company(
    test_client, access_token, user_id, company_repository
):
    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    db_company = await company_repository.save_company(own_company)

    response = await test_client.patch(
        f"/companies/{db_company.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "New name",
            "description": "Some Description",
            "is_visible": "True",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "New name"
    assert response.json()["description"] == "Some Description"
    assert response.json()["is_visible"] is True

    await company_repository.delete_company(db_company)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_cannot_update_other_company(
    test_client, access_token, user_id, company_repository, user_repository
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    other_company = CompanyModel(
        name="Visible Other Company", is_visible=True, owner_id=other_user_db.id
    )
    db_company = await company_repository.save_company(other_company)

    response = await test_client.patch(
        f"/companies/{db_company.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": "New name",
            "description": "Some Description",
            "is_visible": "True",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await company_repository.delete_company(db_company)
    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_delete_own_company(
    test_client, access_token, user_id, company_repository
):
    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    db_company = await company_repository.save_company(own_company)

    response = await test_client.delete(
        f"/companies/{db_company.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio(loop_scope="session")
async def test_user_cannot_delete_other_company(
    test_client, access_token, user_id, company_repository, user_repository
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    other_company = CompanyModel(
        name="Visible Other Company", is_visible=True, owner_id=other_user_db.id
    )
    db_company = await company_repository.save_company(other_company)

    response = await test_client.delete(
        f"/companies/{db_company.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await company_repository.delete_company(db_company)
    await user_repository.delete_user(other_user)
