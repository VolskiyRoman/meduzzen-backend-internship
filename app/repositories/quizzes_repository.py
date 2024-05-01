from sqlalchemy import delete

from app.repositories.base_repository import BaseRepository
from app.models.quiz import Quiz, Question
from app.schemas.quizzes import QuizSchema


class QuizRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, model=Quiz)

    async def create_quiz(self, quiz_data: QuizSchema, company_id: int) -> QuizSchema:
        quiz_dict = quiz_data.dict(exclude={'questions'})
        quiz = await self.create_one(dict(**quiz_dict, company_id=company_id))

        for question_data in quiz_data.questions:
            question = Question(
                quiz_id=quiz.id,
                question_text=question_data.question_text,
                correct_answer=[question_data.correct_answer],
                options=[option.option_text for option in question_data.options]
            )
            self.session.add(question)

        await self.session.commit()
        return quiz

    async def delete_quiz(self, quiz_id: int) -> None:
        query = delete(Question).where(Question.quiz_id == quiz_id)
        await self.session.execute(query)
        await self.session.commit()
        await self.delete_one(quiz_id)
