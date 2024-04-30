from typing import List

from sqlalchemy import select

from app.models.user import User
from app.models.action import CompanyAction
from app.enums.invite import InvitationStatus
from app.repositories.base_repository import BaseRepository
from app.schemas.actions import GetActionsResponseSchema


class ActionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=CompanyAction)

    @staticmethod
    async def get_relatives_query(id_: int, status: InvitationStatus, is_company: bool):
        id_column = CompanyAction.company_id if is_company else CompanyAction.user_id
        query = select(CompanyAction, User).join(User, CompanyAction.user_id == User.id).filter(
            id_column == id_, CompanyAction.status == status
        )
        return query
