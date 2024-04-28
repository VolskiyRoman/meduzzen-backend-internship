from sqlalchemy import select

from app.repositories.base_repository import BaseRepository
from app.db.models import Company, User


class CompanyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Company)

    async def get_owned_companies(self, user_id: int):
        stmt = select(Company).join(User).filter(User.id == user_id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result]
