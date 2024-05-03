from typing import List

from sqlalchemy import select, func
from sqlalchemy.orm import session

from app.models.result import Result
from app.repositories.base_repository import BaseRepository


class ResultRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Result)

    async def calculate_rating(self, company_member_id: int) -> float:
        total_score_query = (
            select(func.sum(self.model.score))
            .filter(self.model.company_member_id == company_member_id)
        )

        total_results_query = (
            select(func.count(self.model.id))
            .filter(self.model.company_member_id == company_member_id)
        )
        total_score = await self.session.execute(total_score_query)
        total_results = await self.session.execute(total_results_query)

        total_score_value = total_score.scalars().first() or 0.0
        total_results_value = total_results.scalars().first() or 0

        average_score = total_score_value / total_results_value if total_results_value > 0 else 0.0
        return average_score

