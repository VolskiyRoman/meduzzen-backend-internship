from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Company(Base):
    __tablename__ = 'companies'
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    visible = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="companies")

    members = relationship("CompanyMember", back_populates="company", cascade="all, delete")
