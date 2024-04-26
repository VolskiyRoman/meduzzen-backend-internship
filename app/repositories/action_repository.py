from app.repositories.base_repository import BaseRepository
from app.db.models import Invitation


class ActionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Invitation)