from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

from app.db.enums.status_enum import StatusEnum


class RequestCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: str


class RequestDetailSchema(RequestCreateSchema):
    id: str
    user_id: str
    status: StatusEnum
    created_at: datetime


class RequestListSchema(BaseModel):
    requests: List[RequestDetailSchema]


class RequestUpdateStatusSchema(BaseModel):
    status: StatusEnum
