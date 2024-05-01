from pydantic import BaseModel
from typing import List


class QuestionSchema(BaseModel):
    question_text: str
    correct_answer: List[str]
    options: List[str]


class QuizSchema(BaseModel):
    name: str
    description: str
    frequency_days: int
    questions: List[QuestionSchema]


class QuizUpdateSchema(BaseModel):
    name: str
    description: str
    frequency_days: int


class QuizResponseSchema(BaseModel):
    name: str
    description: str
    frequency_days: int
