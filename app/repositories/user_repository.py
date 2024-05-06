from typing import List

from sqlalchemy import select

from app.models.company_member import CompanyMember
from app.repositories.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=User)

    async def get_user_username(self, user_id: int) -> str:
        query = select(User).where(User.id == user_id)
        user = await self.session.execute(query)
        user_obj = user.scalar_one()
        return user_obj.username

    async def get_company_members_by_user_id(self, user_id: int) -> List[CompanyMember]:
        query = select(CompanyMember).where(CompanyMember.user_id == user_id)
        members = await self.session.execute(query)
        return members.scalars().all()

    async def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        query = select(User).where(User.id.in_(user_ids))
        users = await self.session.execute(query)
        return users.scalars().all()