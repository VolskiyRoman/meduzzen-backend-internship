from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class BaseNotification(BaseModel):
    __abstract__ = True
    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)


class UserNotification(BaseNotification):
    __tablename__ = 'user_notifications'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="notifications")
