import functools
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repositories.company_repository import CompanyRepository
from app.schemas.companies import CompanySchema, CompaniesListResponse, BaseCompanySchema


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.session = session
        self.repository = repository

    @staticmethod
    def _is_visible_to_user(company: CompanySchema, user_id: int) -> bool:
        return company.visible or user_id == company.owner_id

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        print(f"Fetching company with ID: {company_id}")
        company = await self.repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return company

    def require_company_owner(self, func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            company_id = kwargs.get('company_id')
            company = await self._get_company_or_raise(company_id)
            if user_id != company.owner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to edit this company",
                )

            return await func(*args, **kwargs)

        return wrapper

    @staticmethod
    async def check_company_owner(user_id: int, company_owner_id) -> None:
        if user_id != company_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to edit this company",
            )
        return

    async def create_company(self, data: dict, current_user_id: int) -> CompanySchema:
        data["owner_id"] = current_user_id
        return await self.repository.create_one(data=data)

    async def edit_company(self, data: dict, current_user_id: int, company_id: int) -> CompanySchema:
        if not data.get("name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name is required",
            )
        company = await self._get_company_or_raise(company_id)
        await self.check_company_owner(current_user_id, company.owner_id)
        return await self.repository.update_one(company_id, data)

    async def delete_company(self, company_id: int, current_user_id: int) -> CompanySchema:
        company = await self._get_company_or_raise(company_id)
        await self.check_company_owner(current_user_id, company.owner_id)
        return await self.repository.delete_one(company_id)

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
        visible_companies = [BaseCompanySchema(id=company.id, name=company.name, description=company.description,
                                               visible=self._is_visible_to_user(company, user_id)) for company in
                             companies]
        return CompaniesListResponse(companies=visible_companies)
