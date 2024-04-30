from typing import List, Optional

from pydantic import BaseModel


class CompanySchema(BaseModel):
    id: int
    name: str
    description: str
    visible: bool

    class Config:
        orm_mode = True
        from_attributes = True


class CompanyCreateRequest(BaseModel):
    name: str
    description: str
    visible: Optional[bool] = True


class CompanyUpdateRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    visible: Optional[bool]


class CompaniesListResponse(BaseModel):
    companies: List[CompanySchema]


class CompanyDetailResponse(CompanySchema):
    owner_id: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Company A",
                "description": "Description A",
                "visible": True,
                "owner_id": 123
            }
        }