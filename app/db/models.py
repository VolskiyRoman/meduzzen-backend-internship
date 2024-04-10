from sqlalchemy import MetaData, Integer, Column, String

from app.db.connection import Base

metadata = MetaData()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    is_admin = Column(Integer, nullable=False)
