from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status
from app.repositories.company_repository import CompanyRepository
from app.schemas.companies import CompanySchema


class CompanyService:
    def __init__(self, session: AsyncSession, repository: CompanyRepository):
        self.session = session
        self.repository = repository

    @staticmethod
    def _is_visible_to_user(company: CompanySchema, user_id: int) -> bool:
        if company.visible:
            return True
        elif user_id == company.owner_id:
            return True
        else:
            return False

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        company = await self.repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return company

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
                detail="You are not available to view this company",
            )
        return company

    async def get_companies(self, skip: int = 1, limit: int = 10, user_id: int = None) -> dict:
        companies = await self.repository.get_many(skip=skip, limit=limit)
        visible_companies = [company for company in companies if self._is_visible_to_user(company, user_id)]
        return {"companies": visible_companies}
