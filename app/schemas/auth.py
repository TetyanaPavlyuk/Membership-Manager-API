from pydantic import BaseModel, EmailStr, field_validator
from app.exceptions.exceptions import ItemCreateException
import re


class RegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ItemCreateException(
                "password", "Password must be at least 8 characters long"
            )
        if not re.search(r"[A-Z]", value):
            raise ItemCreateException(
                "password", "Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", value):
            raise ItemCreateException(
                "password", "Password must contain at least one lowercase letter"
            )
        if not re.search(r"\d", value):
            raise ItemCreateException(
                "password", "Password must contain at least one digit"
            )
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", value):
            raise ItemCreateException(
                "password", "Password must contain at least one special character"
            )
        return value


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
