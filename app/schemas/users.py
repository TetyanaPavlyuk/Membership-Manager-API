from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class UserBaseSchema(BaseModel):
    email: EmailStr

    class Config:
        from_attributes: True


class UserSignInSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes: True


class UserSignUpSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(UserBaseSchema):
    full_name: Optional[str] = Field(None, max_length=255)


class UserListSchema(BaseModel):
    prev_page: Optional[str]
    next_page: Optional[str]
    pages_count: int
    users_count: int
    users: List[UserBaseSchema]

    class Config:
        from_attributes: True


class UserDetailSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_superuser: bool
    full_name: Optional[str]
