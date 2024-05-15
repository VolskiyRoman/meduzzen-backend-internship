from typing import List

from fastapi import HTTPException
from sqlalchemy import delete, select
from starlette import status

from app.repositories.base_repository import BaseRepository
from app.models.quiz import Quiz, Question
from app.schemas.quizzes import QuizSchema, QuestionSchema


class QuizRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Quiz)

    async def create_quiz(self, quiz_data: QuizSchema, company_id: int) -> QuizSchema:
        quiz_dict = quiz_data.dict(exclude={'questions'})
        quiz = await self.create_one(dict(**quiz_dict, company_id=company_id))

        questions = [
            Question(
                quiz_id=quiz.id,
                question_text=question_data.question_text,
                correct_answer=question_data.correct_answer,
                options=question_data.options
            )
            for question_data in quiz_data.questions
        ]

        self.session.add_all(questions)
        await self.session.commit()
        return quiz

    async def delete_quiz(self, quiz_id: int) -> None:
        query = delete(Question).where(Question.quiz_id == quiz_id)
        await self.session.execute(query)
        await self.session.commit()
        await self.delete_one(quiz_id)

    async def delete_question(self, question_id: int) -> None:
        query = delete(Question).where(Question.id == question_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_question_by_id(self, question_id: int) -> Question:
        query = await self.session.execute(select(Question).filter(Question.id == question_id))
        return query.scalar_one_or_none()

    async def toggle_quiz_active_status(self, quiz_id: int, new_status: bool) -> None:
        quiz = await self.get_one(id=quiz_id)
        quiz.is_active = new_status
        await self.session.commit()

    async def get_questions_by_quiz_id(self, quiz_id: int) -> List[Question]:
        query = select(Question).filter(Question.quiz_id == quiz_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_question(self, question_data: QuestionSchema, quiz_id: int) -> Question:
        question = Question(
            quiz_id=quiz_id,
            question_text=question_data.question_text,
            correct_answer=question_data.correct_answer,
            options=question_data.options
        )
        self.session.add(question)
        await self.session.commit()
        return question
