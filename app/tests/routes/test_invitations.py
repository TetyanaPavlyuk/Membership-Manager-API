import pytest

from fastapi import status

from app.db.models import InvitationModel, UserModel, CompanyModel


@pytest.mark.asyncio(loop_scope="session")
async def test_owner_can_create_invitation_from_company(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    await company_repository.save_company(own_company)

    response = await test_client.post(
        f"/companies/{own_company.id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"user_id": invited_user_db.id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_invitations = response.json()
    assert response_invitations["company_id"] == own_company.id
    assert response_invitations["user_id"] == invited_user_db.id

    invitation = await invitation_repository.get_invitation_by_company_and_user_id(
        company_id=own_company.id, user_id=invited_user_db.id
    )
    await invitation_repository.delete_invitation(invitation)
    await company_repository.delete_company(own_company)
    await user_repository.delete_user(invited_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_create_invitation_from_company(
    test_client, access_token, user_id, user_repository, company_repository
):
    owner_by_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_by_company_db = await user_repository.save_user(owner_by_company)
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    company = CompanyModel(
        name="Company", is_visible=True, owner_id=owner_by_company_db.id
    )
    company_db = await company_repository.save_company(company)

    response = await test_client.post(
        f"/companies/{company_db.id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"user_id": invited_user_db.id},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    await company_repository.delete_company(company)
    for user in [owner_by_company, invited_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_owner_can_get_invitations_from_company(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    other_company = CompanyModel(
        name="Visible Other Company", is_visible=True, owner_id=other_user_db.id
    )

    for company in [own_company, other_company]:
        await company_repository.save_company(company)

    own_invitation = InvitationModel(
        company_id=own_company.id, user_id=invited_user_db.id
    )
    other_invitation = InvitationModel(
        company_id=other_company.id, user_id=invited_user_db.id
    )

    for invitation in [own_invitation, other_invitation]:
        await invitation_repository.save_invitation(invitation)

    response = await test_client.get(
        f"/companies/{own_company.id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_invitations = response.json()["invitations"]
    company_ids = [invitation["company_id"] for invitation in response_invitations]
    assert own_company.id in company_ids
    assert other_company.id not in company_ids

    for invitation in [own_invitation, other_invitation]:
        await invitation_repository.delete_invitation(invitation)
    for company in [own_company, other_company]:
        await company_repository.delete_company(company)
    for user in [invited_user, other_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_get_invitations_from_company(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    setup_companies,
):
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    company = setup_companies[0]

    invitation = InvitationModel(company_id=company.id, user_id=invited_user_db.id)
    await invitation_repository.save_invitation(invitation)

    response = await test_client.get(
        f"/companies/{company.id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await invitation_repository.delete_invitation(invitation)
    await user_repository.delete_user(invited_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_invitations_for_user(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    owner_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_company_db = await user_repository.save_user(owner_company)
    other_invited_user = UserModel(
        email="invited@mail.com", hashed_password="test12345"
    )
    other_invited_user_db = await user_repository.save_user(other_invited_user)

    company = CompanyModel(
        name="Company", is_visible=False, owner_id=owner_company_db.id
    )

    await company_repository.save_company(company)

    invitation_for_user = InvitationModel(company_id=company.id, user_id=user_id)
    invitation_for_other_user = InvitationModel(
        company_id=company.id, user_id=other_invited_user_db.id
    )

    for invitation in [invitation_for_user, invitation_for_other_user]:
        await invitation_repository.save_invitation(invitation)

    response = await test_client.get(
        f"/users/{user_id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_invitations = response.json()["invitations"]
    users_ids = [invitation["user_id"] for invitation in response_invitations]
    assert user_id in users_ids
    assert other_invited_user_db.id not in users_ids

    for invitation in [invitation_for_user, invitation_for_other_user]:
        await invitation_repository.delete_invitation(invitation)
    await company_repository.delete_company(company)
    for user in [owner_company, other_invited_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_cannot_get_invitations_for_other_user(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    setup_companies,
):
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    company = setup_companies[0]

    invitation = InvitationModel(company_id=company.id, user_id=invited_user_db.id)
    await invitation_repository.save_invitation(invitation)

    response = await test_client.get(
        f"/users/{invited_user_db.id}/invitations/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await invitation_repository.delete_invitation(invitation)
    await user_repository.delete_user(invited_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_owner_can_delete_invitation_from_company(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    own_company = CompanyModel(name="Own Company", is_visible=False, owner_id=user_id)
    await company_repository.save_company(own_company)

    own_invitation = InvitationModel(
        company_id=own_company.id, user_id=invited_user_db.id
    )
    await invitation_repository.save_invitation(own_invitation)

    response = await test_client.delete(
        f"/companies/{own_company.id}/invitations/{own_invitation.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response_invitations = response.json()["message"]
    assert "deleted" in response_invitations

    await company_repository.delete_company(own_company)
    await user_repository.delete_user(invited_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_delete_invitation_from_company(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    owner_by_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_by_company_db = await user_repository.save_user(owner_by_company)
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    company = CompanyModel(
        name="Company", is_visible=True, owner_id=owner_by_company_db.id
    )
    company_db = await company_repository.save_company(company)

    invitation = InvitationModel(company_id=company.id, user_id=invited_user_db.id)
    invitation_db = await invitation_repository.save_invitation(invitation)

    response = await test_client.delete(
        f"/companies/{company_db.id}/invitations/{invitation_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await invitation_repository.delete_invitation(invitation)
    await company_repository.delete_company(company)
    for user in [owner_by_company, invited_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_decline_invitation(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    owner_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_company_db = await user_repository.save_user(owner_company)

    company = CompanyModel(
        name="Company", is_visible=False, owner_id=owner_company_db.id
    )
    company_db = await company_repository.save_company(company)

    invitation = InvitationModel(company_id=company_db.id, user_id=user_id)
    invitation_db = await invitation_repository.save_invitation(invitation)

    response = await test_client.patch(
        f"/users/{user_id}/invitations/{invitation_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "declined"},
    )
    assert response.status_code == status.HTTP_200_OK

    await invitation_repository.delete_invitation(invitation)
    await company_repository.delete_company(company)
    await user_repository.delete_user(owner_company)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_accept_invitation(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    membership_repository,
    user_repository,
    company_repository,
):
    owner = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_db = await user_repository.save_user(owner)

    company = CompanyModel(name="Company", is_visible=True, owner_id=owner_db.id)
    company_db = await company_repository.save_company(company)

    invitation = InvitationModel(company_id=company_db.id, user_id=user_id)
    invitation_db = await invitation_repository.save_invitation(invitation)

    response = await test_client.patch(
        f"/users/{user_id}/invitations/{invitation_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "accepted"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Invitation accepted and membership created."

    membership = await membership_repository.get_membership_by_company_and_user_id(
        company_id=company_db.id, user_id=user_id
    )
    assert membership is not None
    assert membership.company_id == company_db.id
    assert membership.user_id == user_id

    invitation_in_db = (
        await invitation_repository.get_invitation_by_company_and_user_id(
            company_db.id, user_id
        )
    )
    assert invitation_in_db is None

    await membership_repository.delete_membership(membership)
    await company_repository.delete_company(company_db)
    await user_repository.delete_user(owner)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_accept_invitation(
    test_client,
    access_token,
    user_id,
    invitation_repository,
    user_repository,
    company_repository,
):
    owner_company = UserModel(email="owner@mail.com", hashed_password="test12345")
    owner_company_db = await user_repository.save_user(owner_company)
    invited_user = UserModel(email="invited@mail.com", hashed_password="test12345")
    invited_user_db = await user_repository.save_user(invited_user)

    company = CompanyModel(
        name="Company", is_visible=False, owner_id=owner_company_db.id
    )
    company_db = await company_repository.save_company(company)

    invitation = InvitationModel(company_id=company_db.id, user_id=invited_user_db.id)
    invitation_db = await invitation_repository.save_invitation(invitation)

    response = await test_client.patch(
        f"/users/{invited_user_db.id}/invitations/{invitation_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "accepted"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await invitation_repository.delete_invitation(invitation)
    await company_repository.delete_company(company)
    for user in [owner_company, invited_user]:
        await user_repository.delete_user(user)
