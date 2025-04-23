from math import ceil
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.db.models.companies import CompanyModel
from app.schemas.companies import (
    CompanyDetailSchema,
    CompanyBaseSchema,
    CompanyListSchema,
    CompanyCreateSchema,
    CompanyUpdateSchema,
)
from app.services.companies import CompanyService
from app.exceptions.exceptions import (
    ItemCreateException,
    ItemDetailException,
    ItemsListException,
    ItemUpdateException,
    ItemDeleteException,
    ItemAlreadyExistException,
    ItemNotFoundException,
    ForbiddenException,
)


@pytest.mark.asyncio
async def test_create_company_success(db_user):
    mock_repository = AsyncMock()

    company_service = CompanyService(mock_repository)

    company_data = CompanyCreateSchema(
        name="Test Company", description="Test Description", is_visible=True
    )

    saved_company = CompanyModel(
        id="3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        name=company_data.name,
        description=company_data.description,
        is_visible=company_data.is_visible,
        owner_id=db_user.id,
    )

    mock_repository.get_company_by_name.return_value = None
    mock_repository.save_company.return_value = saved_company

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        db_company = await company_service.create_company(company_data, db_user)

    assert isinstance(db_company, CompanyDetailSchema)
    assert db_company.id == saved_company.id
    assert db_company.name == company_data.name
    assert db_company.description == company_data.description
    assert db_company.is_visible == company_data.is_visible
    assert db_company.owner_id == saved_company.owner_id
    mock_repository.get_company_by_name.assert_called_once_with(company_data.name)
    mock_repository.save_company.assert_called_once()
    company_to_save = mock_repository.save_company.call_args.args[0]
    assert company_to_save.name == company_data.name
    assert company_to_save.description == company_data.description
    assert company_to_save.is_visible == company_data.is_visible


@pytest.mark.asyncio
async def test_create_company_already_exist(db_user):
    mock_repository = AsyncMock()

    company_service = CompanyService(mock_repository)

    company_data = CompanyCreateSchema(
        name="Test Company", description="Test Description", is_visible=True
    )

    saved_company = CompanyModel(
        id="3f50c3aa-7d24-4ef2-94e9-64e2e904f472",
        name=company_data.name,
        description=company_data.description,
        is_visible=company_data.is_visible,
        owner_id=db_user.id,
    )

    mock_repository.get_company_by_name.return_value = saved_company

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemAlreadyExistException) as exc:
            await company_service.create_company(company_data, db_user)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exist" in exc.value.message
    mock_repository.save_company.assert_not_called()


@pytest.mark.asyncio
async def test_create_company_exception(db_user):
    mock_repository = AsyncMock()

    company_service = CompanyService(mock_repository)

    company_data = CompanyCreateSchema(
        name="Test Company", description="Test Description", is_visible=True
    )

    mock_repository.get_company_by_name.return_value = None
    mock_repository.save_company.return_value = Exception("DB Error")

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemCreateException) as exc:
            await company_service.create_company(company_data, db_user)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_get_companies_success(companies_create_data, db_user):
    mock_repository = AsyncMock()
    companies_count = len(companies_create_data)
    mock_repository.get_companies_count.return_value = companies_count
    mock_repository.get_companies.return_value = [
        CompanyModel(**company_data) for company_data in companies_create_data
    ]
    company_service = CompanyService(mock_repository)
    page = 1
    limit = 5

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        response = await company_service.get_companies(
            page=page, limit=limit, owner_id=db_user.id
        )

    assert isinstance(response, CompanyListSchema)
    assert len(response.companies) == companies_count
    assert response.companies_count == companies_count
    assert response.pages_count == ceil(companies_count / limit)
    for i, company in enumerate(response.companies):
        assert isinstance(company, CompanyBaseSchema)
        assert company.name == companies_create_data[i]["name"]
    mock_repository.get_companies_count.assert_called_once()
    mock_repository.get_companies.assert_called_once_with(
        (page - 1) * limit, limit, db_user.id
    )


@pytest.mark.asyncio
async def test_get_companies_exception(db_user):
    mock_repository = AsyncMock()
    mock_repository.get_companies_count.side_effect = Exception("DB Error")
    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemsListException) as exc:
            await company_service.get_companies(page=1, limit=2, owner_id=db_user.id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()


@pytest.mark.asyncio
async def test_get_company_success():
    mock_repository = AsyncMock()
    company_id = "company-1"
    owner_id = "owner-1"
    company_data = {
        "id": company_id,
        "name": "Test Company",
        "description": "Test Description",
        "is_visible": True,
        "owner_id": owner_id,
    }
    mock_repository.get_company_by_id.return_value = CompanyModel(**company_data)
    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        company = await company_service.get_company(
            company_id=company_id, owner_id=owner_id
        )

    assert isinstance(company, CompanyDetailSchema)
    assert company.id == company_id
    assert company.name == company_data["name"]
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_get_company_not_found():
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = None
    company_service = CompanyService(mock_repository)
    company_id = "company-2"
    owner_id = "owner-2"

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await company_service.get_company(company_id, owner_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_get_company_forbidden():
    company_id = "company-1"
    owner_id = "owner-1"
    company_data = {
        "id": company_id,
        "name": "Test Company",
        "description": "Test Description",
        "is_visible": False,
        "owner_id": "other-owner",
    }
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = CompanyModel(**company_data)
    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ForbiddenException) as exc:
            await company_service.get_company(company_id, owner_id)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_get_company_exception():
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.side_effect = Exception("DB Error.")
    company_service = CompanyService(mock_repository)
    company_id = "company-1"
    owner_id = "owner-1"

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemDetailException) as exc:
            await company_service.get_company(company_id, owner_id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "error" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_update_company_success():
    company_id = "company-1"
    owner_id = "owner-1"
    company_data = {
        "id": company_id,
        "name": "Test Company",
        "description": "Test Description",
        "is_visible": True,
        "owner_id": owner_id,
    }
    company_model = CompanyModel(**company_data)
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = company_model
    mock_repository.get_company_by_name.return_value = None
    mock_repository.save_company = AsyncMock(side_effect=lambda company: company)

    company_service = CompanyService(mock_repository)

    company_update_data = {
        "name": "New Name",
        "description": "New Description",
        "is_visible": False,
    }
    company_update = CompanyUpdateSchema(**company_update_data)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        db_company = await company_service.update_company(company_id, company_update)

    assert db_company.name == company_update_data["name"]
    assert db_company.description == company_update_data["description"]
    assert db_company.is_visible == company_update_data["is_visible"]
    mock_repository.get_company_by_id.assert_called_once_with(company_id)
    mock_repository.save_company.assert_called_once_with(company_model)


@pytest.mark.asyncio
async def test_update_company_not_found():
    company_id = "company-1"
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = None

    company_service = CompanyService(mock_repository)

    company_update_data = {
        "name": "New Name",
        "description": "New Description",
        "is_visible": False,
    }
    company_update = CompanyUpdateSchema(**company_update_data)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await company_service.update_company(company_id, company_update)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_update_company_already_exist():
    company_id = "company-1"
    company_name = "Company Name"
    owner_id = "owner-1"
    company_data = {
        "id": company_id,
        "name": company_name,
        "description": "Test Description",
        "is_visible": True,
        "owner_id": owner_id,
    }
    company_same_name_data = {
        "id": "company-2",
        "name": company_name,
        "description": "Test Description",
        "is_visible": True,
        "owner_id": owner_id,
    }
    company_model = CompanyModel(**company_data)
    company_same_name_model = CompanyModel(**company_same_name_data)
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = company_model
    mock_repository.get_company_by_name.return_value = company_same_name_model

    company_service = CompanyService(mock_repository)

    company_update_data = {
        "name": company_name,
        "description": "New Description",
        "is_visible": False,
    }
    company_update = CompanyUpdateSchema(**company_update_data)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemAlreadyExistException) as exc:
            await company_service.update_company(company_id, company_update)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exist" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)


@pytest.mark.asyncio
async def test_update_company_exception():
    company_id = "company-1"

    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.side_effect = Exception("DB Error.")

    company_service = CompanyService(mock_repository)

    company_update_data = {
        "name": "New Name",
        "description": "New Description",
        "is_visible": False,
    }
    company_update = CompanyUpdateSchema(**company_update_data)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemUpdateException) as exc:
            await company_service.update_company(company_id, company_update)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)
    mock_repository.save_company.assert_not_called()


@pytest.mark.asyncio
async def test_delete_company_success():
    company_id = "company-1"
    owner_id = "owner-1"
    company_data = {
        "id": company_id,
        "name": "Test Company",
        "description": "Test Description",
        "is_visible": True,
        "owner_id": owner_id,
    }
    company_model = CompanyModel(**company_data)
    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = company_model

    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        response = await company_service.delete_company(company_id)

    assert "deleted" in response["message"]
    mock_repository.get_company_by_id.assert_called_once_with(company_id)
    mock_repository.delete_company.assert_called_once_with(company_model)


@pytest.mark.asyncio
async def test_delete_company_not_found():
    company_id = "company-1"

    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.return_value = None

    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemNotFoundException) as exc:
            await company_service.delete_company(company_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)
    mock_repository.delete_company.assert_not_called()


@pytest.mark.asyncio
async def test_delete_company_exception():
    company_id = "company-1"

    mock_repository = AsyncMock()
    mock_repository.get_company_by_id.side_effect = Exception("DB Error.")

    company_service = CompanyService(mock_repository)

    with patch("app.services.companies.async_log", new_callable=AsyncMock):
        with pytest.raises(ItemDeleteException) as exc:
            await company_service.delete_company(company_id)

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "failed to delete" in exc.value.message.lower()
    mock_repository.get_company_by_id.assert_called_once_with(company_id)
    mock_repository.delete_company.assert_not_called()
