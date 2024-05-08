from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class BaseNotification(BaseModel):
    __tablename__ = 'base_notifications'

    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    type = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "notification",
        "polymorphic_on": type,
    }


class UserNotification(BaseNotification):
    __tablename__ = 'user_notifications'

    id = Column(Integer, ForeignKey('base_notifications.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="notifications")

    __mapper_args__ = {
        "polymorphic_identity": "user_notification",
    }
