from pydantic import BaseModel
from typing import List


class OptionSchema(BaseModel):
    option_text: str


class QuestionSchema(BaseModel):
    question_text: str
    correct_answer: str
    options: List[OptionSchema]


class QuizSchema(BaseModel):
    name: str
    description: str
    frequency_days: int
    questions: List[QuestionSchema]


class QuizUpdateSchema(BaseModel):
    name: str
    description: str
    frequency_days: int


class OptionResponseSchema(BaseModel):
    id: int
    option_text: str
    question_id: int
