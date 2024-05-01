from sqlalchemy import Column, String, Integer, ARRAY, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Quiz(BaseModel):
    __tablename__ = 'quizzes'

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    company_id = Column(ForeignKey('companies.id'), nullable=False)
    is_active = Column(Boolean, default=True)

    questions = relationship('Question', back_populates='quiz', cascade='all, delete-orphan')


class Question(BaseModel):
    __tablename__ = 'questions'

    question_text = Column(String(1000), nullable=False)
    correct_answer = Column(ARRAY(String(255)), nullable=False)
    options = Column(ARRAY(String(255)), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    quiz = relationship('Quiz', back_populates='questions')
