from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.enums.invite import MemberStatus
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizzes_repository import QuizRepository
from app.schemas.companies import CompanySchema
from app.schemas.quizzes import QuizSchema, QuizUpdateSchema


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
        member = await self.company_repository.get_company_member(current_user_id, company_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )
        if member.role not in [MemberStatus.OWNER, MemberStatus.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        await self._validate_quiz_data(quiz_data)
        await self.quiz_repository.create_quiz(quiz_data, company_id=company_id)
        quiz_dict = quiz_data.dict(exclude={'questions'})
        question_dicts = [question.dict() for question in quiz_data.questions]
        created_quiz_schema = QuizSchema(**quiz_dict, questions=question_dicts, company_id=company_id)
        return created_quiz_schema

    async def _validate_quiz(self, quiz_id: int, current_user_id: int) -> QuizSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found",
            )
        company_id = quiz.company_id
        await self._get_company_or_raise(company_id)
        await self.company_repository.is_user_company_owner(current_user_id, company_id)
        return quiz

    async def delete_quiz(self, quiz_id: int,
                          current_user_id: int) -> dict:
        quiz = await self._validate_quiz(quiz_id, current_user_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return {"message": "Quiz has been successfully deleted.", "deleted_quiz_id": quiz.id}

    async def update_quiz(self, quiz_id: int,
                          quiz_data: QuizSchema,
                          current_user_id: int) -> QuizUpdateSchema:
        await self._validate_quiz(quiz_id, current_user_id)
        quiz_data_dict = quiz_data.dict(exclude_unset=True)
        updated_quiz = await self.quiz_repository.update_one(quiz_id, quiz_data_dict)
        return updated_quiz

