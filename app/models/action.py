from sqlalchemy import Column, Integer, ForeignKey, Enum
from .base import Base
from app.enums.invite import InvitationStatus, InvitationType


class Action(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    status = Column(Enum(InvitationStatus), nullable=False)
    type = Column(Enum(InvitationType), nullable=False)
