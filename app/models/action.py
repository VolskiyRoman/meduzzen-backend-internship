from sqlalchemy import Column, Integer, ForeignKey, Enum

from app.enums.invite import InvitationStatus, InvitationType
from .base import BaseModel


class CompanyAction(BaseModel):
    __tablename__ = 'actions'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    status = Column(Enum(InvitationStatus), nullable=False)
    type = Column(Enum(InvitationType), nullable=False)
