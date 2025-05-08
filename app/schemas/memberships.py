from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class MembershipCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    company_id: str


class MembershipDetailSchema(MembershipCreateSchema):
    id: str
    created_at: datetime


class MembershipsListSchema(BaseModel):
    pages_count: int
    memberships_count: int
    memberships: List[MembershipDetailSchema]
