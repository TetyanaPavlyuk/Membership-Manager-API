import pytest

from app.db.models import CompanyModel, UserModel
from app.tests.conftest import companies_create_data


@pytest.mark.asyncio(loop_scope="session")
async def test_save_company(company_repository, user_repository, companies_create_data):
    user = UserModel(email="test@mail.com", hashed_password="test12345")
    db_user = await user_repository.save_user(user)
    companies = [
        CompanyModel(owner_id=db_user.id, **company_data)
        for company_data in companies_create_data
    ]
    saved_companies = [
        await company_repository.save_company(company) for company in companies
    ]

    assert saved_companies[0].name == companies_create_data[0]["name"]
    assert saved_companies[1].name == companies_create_data[1]["name"]
    assert saved_companies[0].description == companies_create_data[0]["description"]
    assert saved_companies[1].description == companies_create_data[1]["description"]
    assert saved_companies[0].is_visible == companies_create_data[0]["is_visible"]
    assert saved_companies[1].is_visible is True
    assert saved_companies[0].owner_id == db_user.id
    assert saved_companies[1].owner_id == db_user.id

    for company in saved_companies:
        await company_repository.delete_company(company)
    await user_repository.delete_user(db_user)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_companies_count(
    company_repository, setup_companies, companies_create_data
):
    companies_count = await company_repository.get_companies_count(
        setup_companies[0].owner_id
    )
    assert companies_count == len(companies_create_data)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_companies(
    company_repository, setup_companies, companies_create_data
):
    companies_list = await company_repository.get_companies(
        0, 10, setup_companies[0].owner_id
    )
    assert [company.name for company in companies_list] == [
        company_data["name"] for company_data in companies_create_data
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_company_by_name(
    company_repository, setup_companies, companies_create_data
):
    name = companies_create_data[0]["name"]
    company = await company_repository.get_company_by_name(name)
    assert company.name == name


@pytest.mark.asyncio(loop_scope="session")
async def test_get_company_by_id(
    company_repository, setup_companies, companies_create_data
):
    company_name = companies_create_data[0]["name"]
    company = await company_repository.get_company_by_name(company_name)
    test_company = await company_repository.get_company_by_id(company.id)
    assert test_company.name == company_name


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_company(
    company_repository, setup_companies, companies_create_data
):
    company_name = companies_create_data[0]["name"]
    company = await company_repository.get_company_by_name(company_name)
    await company_repository.delete_company(company)
    deleted_company = await company_repository.get_company_by_id(company.id)
    assert deleted_company is None
