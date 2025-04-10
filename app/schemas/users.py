from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List


class UserBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class UserUpdateSchema(UserBaseSchema):
    full_name: str | None = Field(None, max_length=255)


class UserListSchema(BaseModel):
    prev_page: str | None
    next_page: str | None
    pages_count: int
    users_count: int
    users: List[UserBaseSchema]


class UserDetailSchema(UserBaseSchema):
    id: str
    is_active: bool
    is_superuser: bool
    full_name: str | None
