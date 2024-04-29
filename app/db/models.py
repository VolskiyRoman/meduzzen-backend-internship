from sqlalchemy import Enum

from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.enums.invite import InvitationStatus

Base: DeclarativeMeta = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())


class User(BaseModel):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    companies_owned = relationship('Company', back_populates='owner')


class Company(BaseModel):
    __tablename__ = 'companies'

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='companies_owned')

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    visible = Column(Boolean, default=True)


class Action(BaseModel):
    __tablename__ = 'actions'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    status = Column(Enum(InvitationStatus), nullable=False)


class Quiz(BaseModel):
    __tablename__ = 'quizzes'

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    frequency_days = Column(Integer, nullable=False)

    questions = relationship('Question', back_populates='quiz', cascade='all, delete-orphan')


class Question(BaseModel):
    __tablename__ = 'questions'

    question_text = Column(String(1000), nullable=False)
    correct_answer = Column(String(255), nullable=False)
    options = Column(ARRAY(String), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    quiz = relationship('Quiz', back_populates='questions')
