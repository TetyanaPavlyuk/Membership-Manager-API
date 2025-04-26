import pytest

from fastapi import status

from app.db.models import RequestModel, UserModel, CompanyModel


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_create_request(
    test_client,
    access_token,
    user_id,
    setup_companies,
    request_repository,
):
    company = setup_companies[0]

    response = await test_client.post(
        f"/users/{user_id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"company_id": company.id},
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["company_id"] == company.id
    assert response_data["user_id"] == user_id

    request = await request_repository.get_request_by_id(response_data["id"])
    await request_repository.delete_request(request)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_create_request(
    test_client, access_token, user_id, user_repository, setup_companies
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    company = setup_companies[0]

    response = await test_client.post(
        f"/users/{other_user_db.id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"company_id": company.id},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_requests_from_user(
    test_client,
    access_token,
    user_id,
    setup_companies,
    request_repository,
    user_repository,
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    company = setup_companies[0]

    own_request = RequestModel(company_id=company.id, user_id=user_id)
    other_request = RequestModel(company_id=company.id, user_id=other_user_db.id)

    for request in [own_request, other_request]:
        await request_repository.save_request(request)

    response = await test_client.get(
        f"/users/{user_id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["requests"]
    user_ids = [request["user_id"] for request in response_data]
    assert user_id in user_ids
    assert other_user_db.id not in user_ids

    for request in [own_request, other_request]:
        await request_repository.delete_request(request)
    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_cannot_get_requests_from_other_user(
    test_client,
    access_token,
    user_id,
    setup_companies,
    request_repository,
    user_repository,
):
    other_user = UserModel(email="other@mail.com", hashed_password="test12345")
    other_user_db = await user_repository.save_user(other_user)

    company = setup_companies[0]

    request = RequestModel(company_id=company.id, user_id=other_user_db.id)
    await request_repository.save_request(request)

    response = await test_client.get(
        f"/users/{other_user_db.id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await request_repository.delete_request(request)
    await user_repository.delete_user(other_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_requests_for_company(
    test_client,
    access_token,
    user_id,
    request_repository,
    user_repository,
    setup_companies,
    company_repository,
):
    company = CompanyModel(name="Company", is_visible=False, owner_id=user_id)
    company_db = await company_repository.save_company(company)
    other_company = setup_companies[0]

    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    other_requested_user = UserModel(
        email="requested_other@mail.com", hashed_password="test12345"
    )
    other_requested_user_db = await user_repository.save_user(other_requested_user)

    request_for_company = RequestModel(
        company_id=company_db.id, user_id=requested_user_db.id
    )
    request_for_other_company = RequestModel(
        company_id=other_company.id, user_id=other_requested_user_db.id
    )

    for request in [request_for_company, request_for_other_company]:
        await request_repository.save_request(request)

    response = await test_client.get(
        f"/companies/{company_db.id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["requests"]

    companies_ids = [request["company_id"] for request in response_data]
    assert company_db.id in companies_ids
    assert other_company.id not in companies_ids

    users_ids = [request["user_id"] for request in response_data]
    assert requested_user_db.id in users_ids
    assert other_requested_user_db.id not in users_ids

    for request in [request_for_company, request_for_other_company]:
        await request_repository.delete_request(request)
    await company_repository.delete_company(company)
    for user in [requested_user, other_requested_user]:
        await user_repository.delete_user(user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_get_requests_for_company(
    test_client,
    access_token,
    user_id,
    request_repository,
    user_repository,
    setup_companies,
):
    company = setup_companies[0]

    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    request = RequestModel(company_id=company.id, user_id=requested_user_db.id)
    await request_repository.save_request(request)

    response = await test_client.get(
        f"/companies/{company.id}/requests/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await request_repository.delete_request(request)
    await user_repository.delete_user(requested_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_user_can_delete_request(
    test_client, access_token, user_id, request_repository, setup_companies
):
    company = setup_companies[0]

    request = RequestModel(company_id=company.id, user_id=user_id)
    request_db = await request_repository.save_request(request)

    response = await test_client.delete(
        f"/users/{user_id}/requests/{request_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response_data = response.json()["message"]
    assert "deleted" in response_data


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_delete_request(
    test_client,
    access_token,
    user_id,
    request_repository,
    user_repository,
    setup_companies,
):
    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    company = setup_companies[0]

    request = RequestModel(company_id=company.id, user_id=requested_user_db.id)
    request_db = await request_repository.save_request(request)

    response = await test_client.delete(
        f"/users/{requested_user_db.id}/requests/{request_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await request_repository.delete_request(request)
    await user_repository.delete_user(requested_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_company_owner_can_decline_request(
    test_client,
    access_token,
    user_id,
    request_repository,
    user_repository,
    company_repository,
):
    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    company = CompanyModel(name="Company", is_visible=False, owner_id=user_id)
    company_db = await company_repository.save_company(company)

    request = RequestModel(company_id=company_db.id, user_id=requested_user_db.id)
    request_db = await request_repository.save_request(request)

    response = await test_client.patch(
        f"/companies/{company_db.id}/requests/{request_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "declined"},
    )
    assert response.status_code == status.HTTP_200_OK

    await request_repository.delete_request(request)
    await company_repository.delete_company(company)
    await user_repository.delete_user(requested_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_company_owner_can_accept_request(
    test_client,
    access_token,
    user_id,
    request_repository,
    membership_repository,
    user_repository,
    company_repository,
):
    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    company = CompanyModel(name="Company", is_visible=True, owner_id=user_id)
    company_db = await company_repository.save_company(company)

    request = RequestModel(company_id=company_db.id, user_id=requested_user_db.id)
    request_db = await request_repository.save_request(request)

    response = await test_client.patch(
        f"/companies/{company_db.id}/requests/{request_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "accepted"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Request accepted and membership created."

    membership = await membership_repository.get_membership_by_company_and_user_id(
        company_id=company_db.id, user_id=requested_user_db.id
    )
    assert membership is not None
    assert membership.company_id == company_db.id
    assert membership.user_id == requested_user_db.id

    request_in_db = await request_repository.get_request_by_company_and_user_id(
        company_db.id, requested_user_db.id
    )
    assert request_in_db is None

    await membership_repository.delete_membership(membership)
    await company_repository.delete_company(company_db)
    await user_repository.delete_user(requested_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_other_user_cannot_accept_request(
    test_client,
    access_token,
    user_id,
    request_repository,
    user_repository,
    setup_companies,
):
    requested_user = UserModel(email="requested@mail.com", hashed_password="test12345")
    requested_user_db = await user_repository.save_user(requested_user)

    company = setup_companies[0]

    request = RequestModel(company_id=company.id, user_id=requested_user_db.id)
    request_db = await request_repository.save_request(request)

    response = await test_client.patch(
        f"/companies/{company.id}/requests/{request_db.id}/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"status": "accepted"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    await request_repository.delete_request(request)
    await user_repository.delete_user(requested_user)
