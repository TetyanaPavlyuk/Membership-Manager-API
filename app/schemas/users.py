from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        from_attributes: True


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserSignUp(UserBase):
    password: str

    class Config:
        from_attributes: True


class UserUpdate(UserBase):
    password: Optional[str] = None
    full_name: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes: True


class UserList(BaseModel):
    users: List[UserBase]


class UserDetail(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    full_name: Optional[str]

    class Config:
        from_attributes: True

