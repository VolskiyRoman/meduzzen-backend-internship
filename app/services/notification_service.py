from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.repositories.company_repository import CompanyRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.notifications import NotificationSchema


class NotificationService:
    def __init__(
            self,
            session: AsyncSession,
            notification_repository: NotificationRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.company_repository = company_repository
        self.user_repository = user_repository

    async def get_my_notifications(self, current_user_id: int) -> List[NotificationSchema]:
        unread_notifications = await self.notification_repository.get_unread_notifications_for_user(current_user_id)

        notification_schemas = [
            NotificationSchema(
                id=field.id,
                text=field.text,
                is_read=field.is_read,
                user_id=field.user_id
            )
            for field in unread_notifications
        ]

        return notification_schemas

    async def mark_as_read(self, current_user_id: int, notification_id: int) -> NotificationSchema:
        notification = await self.notification_repository.get_one(id=notification_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Notification not found")
        if notification.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Not enough permissions")
        await self.notification_repository.mark_notification_as_read(notification)
        return NotificationSchema(
            id=notification.id,
            text=notification.text,
            is_read=notification.is_read,
            user_id=notification.user_id
        )

    async def mark_as_read_all(self, current_user_id: int) -> List[NotificationSchema]:
        notifications = await self.notification_repository.get_unread_notifications_for_user(current_user_id)
        await self.notification_repository.mark_notifications_as_read_all(current_user_id)
        notification_schemas = [
            NotificationSchema(
                id=notification.id,
                text=notification.text,
                is_read=True,
                user_id=notification.user_id
            )
            for notification in notifications
        ]

        return notification_schemas
