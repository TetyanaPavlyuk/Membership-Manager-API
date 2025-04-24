from pydantic import BaseModel, Field, ConfigDict
from typing import List


class CompanyBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    is_visible: bool = True


class CompanyCreateSchema(CompanyBaseSchema):
    pass


class CompanyDetailSchema(CompanyBaseSchema):
    id: str
    owner_id: str


class CompanyListSchema(BaseModel):
    pages_count: int
    companies_count: int
    companies: List[CompanyBaseSchema]


class CompanyUpdateSchema(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    is_visible: bool | None = None
