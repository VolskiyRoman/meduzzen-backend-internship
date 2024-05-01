from sqlalchemy import select

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
