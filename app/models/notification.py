from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class CompanyMemberNotification(BaseModel):
    __tablename__ = 'user_notifications'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    company_member_id = Column(Integer, ForeignKey('company_members.id'), nullable=False)

    company_member = relationship("CompanyMember", back_populates="notifications")
