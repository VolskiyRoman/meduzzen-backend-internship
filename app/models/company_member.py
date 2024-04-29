from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
from app.enums.invite import MemberStatus


class CompanyMember(Base):
    __tablename__ = 'company_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    role = Column(Enum(MemberStatus), nullable=False)

    company = relationship("Company", back_populates="members")
