from pydantic import BaseModel, EmailStr

from app.schemas.users import UserDetailSchema


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class RegisterResponseSchema(BaseModel):
    user: UserDetailSchema


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
