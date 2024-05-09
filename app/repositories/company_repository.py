from typing import List

from fastapi import HTTPException
from sqlalchemy import select, delete, join
from sqlalchemy.exc import NoResultFound
from starlette import status

from app.enums.invite import MemberStatus
from app.models.company import Company
from app.models.company_member import CompanyMember
from app.models.result import Result
from app.repositories.base_repository import BaseRepository
from app.schemas.actions import CompanyMemberSchema
from app.schemas.companies import CompanySchema


class CompanyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Company)

    async def create_company_with_owner(self, data: dict, owner_id: int) -> CompanySchema:
        company = await self.create_one(data=data)
        company_member_data = {
            "user_id": owner_id,
            "company_id": company.id,
            "role": MemberStatus.OWNER
        }
        await self.create_company_member(company_member_data)

        return company

    async def create_company_member(self, data: dict) -> CompanyMemberSchema:
        company_member = CompanyMember(**data)
        self.session.add(company_member)
        await self.session.commit()
        company_member_schema = CompanyMemberSchema.from_orm(company_member)

        return company_member_schema

    async def is_user_company_owner(self, user_id: int, company_id: int) -> bool:
        query = select(CompanyMember).filter(
            CompanyMember.user_id == user_id,
            CompanyMember.company_id == company_id,
            CompanyMember.role == MemberStatus.OWNER
        )
        company_owner = await self.session.execute(query)
        return company_owner.scalar()

    async def delete_company(self, company_id: int) -> None:
        await self._delete_company_members(company_id)
        await self.delete_one(model_id=company_id)

    async def _delete_company_members(self, company_id: int) -> None:
        query = delete(CompanyMember).where(CompanyMember.company_id == company_id)
        await self.session.execute(query)
        await self.session.commit()

    async def delete_company_member(self, company_id: int, user_id) -> None:
        query = delete(CompanyMember).where(CompanyMember.company_id == company_id,
                                            CompanyMember.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_company_member(self, user_id: int, company_id: int):
        query = select(CompanyMember).filter(
            CompanyMember.user_id == user_id,
            CompanyMember.company_id == company_id,
        )
        company_member = await self.session.execute(query)
        return company_member.scalar_one_or_none()

    async def get_user_company_members(self, user_id: int):
        query = select(CompanyMember).filter(
            CompanyMember.user_id == user_id,
        )
        company_members = await self.session.execute(query)
        return company_members.scalars().all()

    async def update_company_member(self, company_member: CompanyMemberSchema, role: MemberStatus) -> None:
        member = await self.get_company_member(company_member.user_id, company_member.company_id)
        member.role = role
        await self.session.commit()

    async def get_admins(self, company_id: int) -> List[CompanyMember]:
        query = select(CompanyMember).filter(
            CompanyMember.company_id == company_id,
            CompanyMember.role == MemberStatus.ADMIN
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_company_members_result_data(self, company_id: int) -> List[Result]:
        query = (
            select(Result)
            .select_from(join(CompanyMember, Result, CompanyMember.id == Result.company_member_id))
            .where(CompanyMember.company_id == company_id)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_company_members(self, company_id: int) -> List[CompanyMember]:
        query = select(CompanyMember).filter(CompanyMember.company_id == company_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_company_member_by_id(self, company_member_id: int) -> CompanyMember:
        query = select(CompanyMember).filter(CompanyMember.id == company_member_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
