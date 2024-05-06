from typing import List

from sqlalchemy import select

from app.models.company_member import CompanyMember
from app.models.notification import CompanyMemberNotification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=CompanyMemberNotification)

    async def create_notifications_for_members(self, members: List[CompanyMember], quiz_name: str,
                                               company_name: str) -> None:
        notifications = [
            CompanyMemberNotification(
                text=f"In {company_name} company, a new quiz '{quiz_name}' has been created. Take it now!",
                company_member_id=member.id
            )
            for member in members
        ]

        self.session.add_all(notifications)
        await self.session.commit()

    async def get_unread_notifications_for_user(self, user_id: int) -> List[CompanyMemberNotification]:
        query = (
            select(CompanyMemberNotification)
            .join(CompanyMember)
            .filter(
                CompanyMemberNotification.is_read == False,
                CompanyMember.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
