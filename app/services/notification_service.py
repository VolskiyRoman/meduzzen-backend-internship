from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repositories.company_repository import CompanyRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notifications import NotificationSchema


class NotificationService:
    def __init__(
            self,
            session: AsyncSession,
            notification_repository: NotificationRepository,
            company_repository: CompanyRepository,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.company_repository = company_repository

    async def get_my_notifications(self, current_user_id: int) -> List[NotificationSchema]:
        unread_notifications = await self.notification_repository.get_unread_notifications_for_user(current_user_id)

        notification_schemas = [
            NotificationSchema(
                id=field.id,
                text=field.text,
                is_read=field.is_read,
                company_member_id=field.company_member_id
            )
            for field in unread_notifications
        ]

        return notification_schemas

    async def mark_as_read(self, current_user_id: int, notification_id: int) -> NotificationSchema:
        notification = await self.notification_repository.get_one(id=notification_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Notification not found")
        member_id = notification.company_member_id
        member = await self.company_repository.get_company_member_by_id(member_id)
        if member.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not enough permissions")
        notification.is_read = True
        await self.notification_repository.update_one(notification.id, {"is_read": True})
        return notification


