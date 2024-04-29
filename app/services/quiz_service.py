from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.enums.invite import InvitationStatus
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizzes_repository import QuizRepository
from app.schemas.companies import CompanySchema
from app.schemas.quizzes import QuizSchema
from app.utils.quizzes import raise_not_enough_permissions


class QuizService:
    def __init__(
            self,
            session: AsyncSession,
            quiz_repository: QuizRepository,
            action_repository: ActionRepository,
            company_repository: CompanyRepository,
    ):
        self.session = session
        self.quiz_repository = quiz_repository
        self.action_repository = action_repository
        self.company_repository = company_repository

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        return company

    @staticmethod
    async def _validate_quiz_data(quiz_data: QuizSchema) -> None:
        if len(quiz_data.questions) < 2 or any(len(question.options) < 2 for question in quiz_data.questions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz must have at least two questions and each question must have at least two options",
            )

    async def create_quiz(self, quiz_data: QuizSchema, company_id: int, current_user_id: int) -> QuizSchema:
        company = await self._get_company_or_raise(company_id)

        if current_user_id != company.owner_id:
            action = await self.action_repository.get_one(user_id=current_user_id)
            if not action or action.status != InvitationStatus.PROMOTED:
                await raise_not_enough_permissions()
        await self._validate_quiz_data(quiz_data)
        await self.quiz_repository.create_quiz(quiz_data)
        quiz_dict = quiz_data.dict(exclude={'questions'})
        question_dicts = [question.dict() for question in quiz_data.questions]
        created_quiz_schema = QuizSchema(**quiz_dict, questions=question_dicts)

        return created_quiz_schema

    async def _validate_quiz(self, quiz_id: int, current_user_id: int, company_id: int) -> QuizSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company = await self._get_company_or_raise(company_id)

        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found",
            )
        if current_user_id != company.owner_id:
            await raise_not_enough_permissions()
        return quiz

    async def delete_quiz(self, quiz_id: int,
                          current_user_id: int,
                          company_id: int) -> dict:
        quiz = await self._validate_quiz(quiz_id, current_user_id, company_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return {"message": "Quiz has been successfully deleted.", "deleted_quiz_id": quiz.id}

    async def update_quiz(self, quiz_id: int,
                          quiz_data: QuizSchema,
                          current_user_id: int,
                          company_id: int) -> QuizSchema:
        quiz = await self._validate_quiz(quiz_id, current_user_id, company_id)
        await self._validate_quiz_data(quiz_data)
        await self.quiz_repository.update_quiz(quiz_id, quiz_data)
        return quiz

