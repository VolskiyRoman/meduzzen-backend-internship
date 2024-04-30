from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint

from app.enums.invite import MemberStatus
from .base import BaseModel


class CompanyMember(BaseModel):
    __tablename__ = 'company_members'

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MemberStatus), nullable=False)
