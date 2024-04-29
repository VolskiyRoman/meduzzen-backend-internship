from app.repositories.base_repository import BaseRepository
from app.db.models import Company


class CompanyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Company)
