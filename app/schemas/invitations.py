from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

from app.db.enums import StatusEnum


class InvitationCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str


class InvitationDetailSchema(InvitationCreateSchema):
    id: str
    company_id: str
    status: StatusEnum
    created_at: datetime


class InvitationListSchema(BaseModel):
    invitations: List[InvitationDetailSchema]


class InvitationUpdateStatusSchema(BaseModel):
    status: StatusEnum
