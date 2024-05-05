from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship, backref

from app.models.base import BaseModel


class Result(BaseModel):
    __tablename__ = 'results'

    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer)
    company_member_id = Column(Integer, ForeignKey('company_members.id'))
