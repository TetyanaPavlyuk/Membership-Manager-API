from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional


class UserBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class UserSignInSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str


class UserSignUpSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(UserBaseSchema):
    full_name: Optional[str] = Field(None, max_length=255)


class UserListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prev_page: Optional[str]
    next_page: Optional[str]
    pages_count: int
    users_count: int
    users: List[UserBaseSchema]


class UserDetailSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_superuser: bool
    full_name: Optional[str]
