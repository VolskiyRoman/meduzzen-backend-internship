from typing import List, Dict

from pydantic import BaseModel


class ResultSchema(BaseModel):
    company_member_id: int
    quiz_id: int
    score: float
    total_questions: int
    correct_answers: int

    class Config:
        orm_mode = True
        from_attributes = True


class QuizRequest(BaseModel):
    answers: Dict[int, List[str]]


class CompanyRating(BaseModel):
    company_member_id: int
    company_id: int
    rating: int
