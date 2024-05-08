from typing import List

from sqlalchemy import select, update

from app.models.notification import UserNotification, BaseNotification
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=UserNotification)

    async def create_notifications_for_users(self, users: List[User], quiz_name: str,
                                             company_name: str) -> None:
        notifications = []

        for user in users:
            notification = UserNotification(
                text=f"In {company_name} company, a new quiz '{quiz_name}' has been created. Take it now!",
                user_id=user.id
            )
            notifications.append(notification)

        if notifications:
            self.session.add_all(notifications)
            await self.session.commit()

    async def get_unread_notifications_for_user(self, user_id: int) -> List[UserNotification]:
        query = (
            select(UserNotification)
            .filter(
                UserNotification.is_read == False,
                UserNotification.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def mark_notification_as_read(self, notification: UserNotification) -> None:
        notification.is_read = True
        await self.session.commit()

    async def mark_notifications_as_read_all(self, user_id: int) -> None:
        await self.session.execute(
            update(BaseNotification)
            .where(UserNotification.user_id == user_id)
            .values(is_read=True)
        )
        await self.session.commit()
