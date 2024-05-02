from typing import List

from sqlalchemy import select
from sqlalchemy.orm import session

from app.models.result import Result
from app.repositories.base_repository import BaseRepository


class ResultRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Result)
