from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies.requests import get_request_service
from app.permissions.companies import can_modify_company
from app.permissions.users import can_modify_user
from app.routers.auth import get_current_user
from app.services.requests import RequestService
from app.schemas.requests import (
    RequestDetailSchema,
    RequestListSchema,
    RequestCreateSchema,
    RequestUpdateStatusSchema,
)


request_router = APIRouter(dependencies=[Depends(get_current_user)])


@request_router.get(
    "/users/{user_id}/requests/",
    response_model=RequestListSchema,
    dependencies=[Depends(can_modify_user)],
)
async def get_requests_from_user(
    user_id: str,
    request_service: RequestService = Depends(get_request_service),
) -> RequestListSchema:
    return await request_service.get_requests_from_user(user_id)


@request_router.get(
    "/companies/{company_id}/requests/",
    response_model=RequestListSchema,
    dependencies=[Depends(can_modify_company)],
)
async def get_requests_for_company(
    company_id: str,
    request_service: RequestService = Depends(get_request_service),
) -> RequestListSchema:
    return await request_service.get_requests_for_company(company_id)


@request_router.post(
    "/users/{user_id}/requests/",
    response_model=RequestDetailSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(can_modify_user)],
)
async def create_request(
    user_id: str,
    payload: RequestCreateSchema,
    request_service: RequestService = Depends(get_request_service),
) -> RequestDetailSchema:
    return await request_service.create_request(payload.company_id, user_id)


@request_router.delete(
    "/users/{user_id}/requests/{request_id}/", dependencies=[Depends(can_modify_user)]
)
async def delete_request(
    request_id: str,
    request_service: RequestService = Depends(get_request_service),
) -> JSONResponse:
    result = await request_service.delete_request(request_id)
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=result)


@request_router.patch(
    "/companies/{company_id}/requests/{request_id}/",
    dependencies=[Depends(can_modify_company)],
)
async def accept_or_decline_request(
    request_id: str,
    new_status: RequestUpdateStatusSchema,
    request_service: RequestService = Depends(get_request_service),
):
    return await request_service.change_request_status(request_id, new_status.status)
