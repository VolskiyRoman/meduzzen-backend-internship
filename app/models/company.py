from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel


class Company(BaseModel):
    __tablename__ = 'companies'

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    visible = Column(Boolean, default=True)

    actions = relationship("CompanyAction", backref="company", cascade="all, delete")
