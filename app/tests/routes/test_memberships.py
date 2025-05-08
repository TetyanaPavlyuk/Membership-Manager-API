import pytest

from fastapi import status

from app.db.models import MembershipModel, UserModel, CompanyModel


@pytest.mark.asyncio(loop_scope="session")
async def test_owner_can_get_memberships_for_company(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    company_repository,
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    membership_user = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    membership_user_db = await user_repository.save_user(membership_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    other_company = CompanyModel(
        name="Visible Other Company", is_visible=True, owner_id=other_user_db.id
    )

    for company in [own_company, other_company]:
        await company_repository.save_company(company)

    own_membership = MembershipModel(
        company_id=own_company.id, user_id=membership_user_db.id
    )
    other_membership = MembershipModel(
        company_id=other_company.id, user_id=membership_user_db.id
    )

    for membership in [own_membership, other_membership]:
        await membership_repository.save_membership(membership)

    response = await test_client.get(
        f"/companies/{own_company.id}/memberships/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_memberships = response.json()["memberships"]
    company_ids = [invitation["company_id"] for invitation in response_memberships]
    assert own_company.id in company_ids
    assert other_company.id not in company_ids

    for membership in [own_membership, other_membership]:
        await membership_repository.delete_membership(membership)
    for company in [own_company, other_company]:
        await company_repository.delete_company(company)
    for user in [membership_user, other_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_get_memberships_for_company(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    setup_companies,
):
    membership_user = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    membership_user_db = await user_repository.save_user(membership_user)

    company = setup_companies[0]

    membership = MembershipModel(company_id=company.id, user_id=membership_user_db.id)
    await membership_repository.save_membership(membership)

    response = await test_client.get(
        f"/companies/{company.id}/memberships/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await membership_repository.delete_membership(membership)
    await user_repository.delete_user(membership_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_memberships_for_user(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    setup_companies,
):
    other_membership = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    other_membership_db = await user_repository.save_user(other_membership)

    company = setup_companies[0]

    membership_for_user = MembershipModel(company_id=company.id, user_id=user_id)
    membership_for_other_user = MembershipModel(
        company_id=company.id, user_id=other_membership_db.id
    )

    for membership in [membership_for_user, membership_for_other_user]:
        await membership_repository.save_membership(membership)

    response = await test_client.get(
        f"/users/{user_id}/memberships/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_memberships = response.json()["memberships"]
    users_ids = [membership["user_id"] for membership in response_memberships]
    assert user_id in users_ids
    assert other_membership_db.id not in users_ids

    for membership in [membership_for_user, membership_for_other_user]:
        await membership_repository.delete_membership(membership)
    await user_repository.delete_user(other_membership)


@pytest.mark.asyncio(loop_scope="session")
async def test_cannot_get_memberships_for_other_user(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    setup_companies,
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    company = setup_companies[0]

    membership = MembershipModel(company_id=company.id, user_id=other_user_db.id)
    await membership_repository.save_membership(membership)

    response = await test_client.get(
        f"/users/{other_user_db.id}/memberships/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await membership_repository.delete_membership(membership)
    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_owner_can_delete_membership_for_company(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    company_repository,
):
    membership_user = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    membership_user_db = await user_repository.save_user(membership_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    await company_repository.save_company(own_company)

    membership = MembershipModel(
        company_id=own_company.id, user_id=membership_user_db.id
    )
    await membership_repository.save_membership(membership)

    response = await test_client.delete(
        f"/companies/{own_company.id}/memberships/{membership.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response_data = response.json()["message"]
    assert "deleted" in response_data

    await company_repository.delete_company(own_company)
    await user_repository.delete_user(membership_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_delete_membership_for_company(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    company_repository,
):
    owner_by_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_by_company_db = await user_repository.save_user(owner_by_company)
    membership_user = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    membership_user_db = await user_repository.save_user(membership_user)

    company = CompanyModel(
        name="Company", is_visible=True, owner_id=owner_by_company_db.id
    )
    company_db = await company_repository.save_company(company)

    membership = MembershipModel(company_id=company.id, user_id=membership_user_db.id)
    membership_db = await membership_repository.save_membership(membership)

    response = await test_client.delete(
        f"/companies/{company_db.id}/memberships/{membership_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await membership_repository.delete_membership(membership)
    await company_repository.delete_company(company)
    for user in [owner_by_company, membership_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_delete_membership(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    setup_companies,
):
    company = setup_companies[0]

    membership = MembershipModel(company_id=company.id, user_id=user_id)
    await membership_repository.save_membership(membership)

    response = await test_client.delete(
        f"/users/{user_id}/memberships/{membership.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response_data = response.json()["message"]
    assert "deleted" in response_data


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_delete_membership(
    test_client,
    access_token,
    user_id,
    membership_repository,
    user_repository,
    setup_companies,
):
    membership_user = UserModel(
        email="membership@mail.com", hashed_password="test12345"
    )
    membership_user_db = await user_repository.save_user(membership_user)

    company = setup_companies[0]

    membership = MembershipModel(company_id=company.id, user_id=membership_user_db.id)
    membership_db = await membership_repository.save_membership(membership)

    response = await test_client.delete(
        f"/users/{membership_user_db.id}/memberships/{membership_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await membership_repository.delete_membership(membership)
    await user_repository.delete_user(membership_user)
