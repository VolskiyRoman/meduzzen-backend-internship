from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repositories.company_repository import CompanyRepository
from app.schemas.companies import CompaniesListResponse, CompanySchema
from app.utils.exception.companies import NotOwnerException


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.session = session
        self.repository = repository

    @staticmethod
    def _is_visible_to_user(company: CompanySchema, user_id: int) -> bool:
        return company.visible or user_id == company.owner_id

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        company = await self.repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return company

    async def validate_company(self, current_user_id: int, company_id: int) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        if not await self.repository.is_user_company_owner(current_user_id, company_id):
            raise NotOwnerException()
        return company

    async def create_company(self, data: dict, current_user_id: int) -> CompanySchema:
        return await self.repository.create_company_with_owner(data=data, owner_id=current_user_id)

    async def edit_company(self, data: dict, current_user_id: int, company_id: int) -> CompanySchema:
        if not data.get("name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name is required",
            )
        await self.validate_company(current_user_id, company_id)
        return await self.repository.update_one(company_id, data)

    async def delete_company(self, company_id: int, current_user_id: int) -> dict:
        await self.validate_company(current_user_id, company_id)
        await self.repository.delete_company(company_id)
        return {"message": "Company deleted"}

    async def get_company_by_id(self, company_id: int, user_id: int) -> Optional[CompanySchema]:
        company = await self._get_company_or_raise(company_id)
        if not self._is_visible_to_user(company, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this company",
            )
        return company

    async def get_companies(self, skip: int = 1, limit: int = 10, user_id: int = None) -> CompaniesListResponse:
        companies = await self.repository.get_many(skip=skip, limit=limit)
        visible_companies = [CompanySchema(id=company.id, name=company.name, description=company.description,
                                           visible=self._is_visible_to_user(company, user_id)) for company in
                             companies]
        return CompaniesListResponse(companies=visible_companies)
