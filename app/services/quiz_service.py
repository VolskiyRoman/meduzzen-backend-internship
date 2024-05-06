from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.enums.invite import MemberStatus
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.quizzes_repository import QuizRepository
from app.schemas.companies import CompanySchema
from app.schemas.quizzes import QuizSchema, QuizUpdateSchema, QuestionSchema, QuizResponseSchema


class QuizService:
    def __init__(
            self,
            session: AsyncSession,
            quiz_repository: QuizRepository,
            action_repository: ActionRepository,
            company_repository: CompanyRepository,
            notification_repository: NotificationRepository,
    ):
        self.session = session
        self.quiz_repository = quiz_repository
        self.action_repository = action_repository
        self.company_repository = company_repository
        self.notification_repository = notification_repository

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
        min_questions = 2
        min_options = 2
        if len(quiz_data.questions) < min_questions or any(
                len(question.options) < min_options for question in quiz_data.questions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quiz must have at least {min_questions} "
                       f"questions and each question must have at least {min_options} options",
            )
        for question in quiz_data.questions:
            if not question.correct_answer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"At least one correct answer is required for question '{question.question_text}'"
                )

            for answer in question.correct_answer:
                if answer not in question.options:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Correct answer '{answer}' "
                               f"for question '{question.question_text}' is not in the options."
                    )

    async def create_quiz(self, quiz_data: QuizSchema, company_id: int, current_user_id: int) -> QuizSchema:
        company = await self._get_company_or_raise(company_id)
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
        members = await self.company_repository.get_company_members(company_id)
        await self.notification_repository.create_notifications_for_members(members, quiz_data.name, company.name)

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

    async def delete_quiz(self, quiz_id: int, current_user_id: int) -> QuizResponseSchema:
        quiz = await self._validate_quiz(quiz_id, current_user_id)
        await self.quiz_repository.delete_quiz(quiz_id)
        return QuizResponseSchema(
            name=quiz.name,
            description=quiz.description,
            frequency_days=quiz.frequency_days
        )

    async def update_quiz(self, quiz_id: int,
                          quiz_data: QuizUpdateSchema,
                          current_user_id: int) -> QuizUpdateSchema:
        await self._validate_quiz(quiz_id, current_user_id)
        quiz_data_dict = quiz_data.dict(exclude_unset=True)
        updated_quiz = await self.quiz_repository.update_one(quiz_id, quiz_data_dict)
        return updated_quiz

    async def _handle_is_active(self, quiz_id: int) -> None:
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)
        if len(questions) < 2:
            await self.quiz_repository.toggle_quiz_active_status(quiz_id, False)
        else:
            await self.quiz_repository.toggle_quiz_active_status(quiz_id, True)

    async def delete_question(self, question_id: int, current_user_id: int) -> QuestionSchema:
        question = await self.quiz_repository.get_question_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        quiz_id = question.quiz_id
        await self._validate_quiz(quiz_id, current_user_id)
        await self.quiz_repository.delete_question(question_id)
        await self._handle_is_active(quiz_id)

        question_schema = QuestionSchema(
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            options=question.options
        )

        return question_schema

    async def add_question(self, question_data: QuestionSchema, quiz_id: int, current_user_id: int) -> QuestionSchema:
        await self._validate_quiz(quiz_id, current_user_id)
        question = await self.quiz_repository.create_question(question_data, quiz_id)
        await self._handle_is_active(quiz_id)

        question_schema = QuestionSchema(
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            options=question.options
        )
        return question_schema

    async def get_quizzes(self, company_id: int) -> List[QuizResponseSchema]:
        quizzes = await self.quiz_repository.get_many(company_id=company_id)
        quiz_responses = [
            QuizResponseSchema(
                name=quiz.name,
                description=quiz.description,
                frequency_days=quiz.frequency_days
            )
            for quiz in quizzes
        ]
        return quiz_responses
