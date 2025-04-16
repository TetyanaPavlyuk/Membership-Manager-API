from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List


class UserBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class UserShortSchema(UserBaseSchema):
    full_name: str | None = Field(None, max_length=255)


class UserListSchema(BaseModel):
    pages_count: int
    users_count: int
    users: List[UserBaseSchema]


class UserDetailSchema(UserBaseSchema):
    id: str
    is_active: bool
    is_superuser: bool
    full_name: str | None


class UserUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    full_name: str | None
