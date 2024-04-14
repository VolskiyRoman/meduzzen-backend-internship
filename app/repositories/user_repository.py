from app.db.models import User
from app.repositories.base_repository import BaseRepository
from app.db.connection import async_session_maker


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)


user_repository = UserRepository()
