from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RefreshTokenBaseSchema(BaseModel):
    revoked: bool


class RefreshTokenResponseSchema(RefreshTokenBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    token: str
    created_at: datetime
    expires_at: datetime
