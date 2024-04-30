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

    async def get_relatives(self,
                            id_: int,
                            status: InvitationStatus,
                            is_company: bool) -> List[GetActionsResponseSchema]:
        id_column = CompanyAction.company_id if is_company else CompanyAction.user_id

        query = (
            select(CompanyAction, User)
            .join(User, CompanyAction.user_id == User.id)
            .filter(id_column == id_, CompanyAction.status == status)
        )
        result = await self.session.execute(query)
        actions = [
            GetActionsResponseSchema(id=action.id, user_id=user.id, user_username=user.username)
            for action, user in result.fetchall()
        ]
        return actions
