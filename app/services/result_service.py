import csv
import json
import os
from datetime import timedelta, datetime
from typing import List, Optional
import pytz

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.result import Result
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizzes_repository import QuizRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.user_repository import UserRepository
from app.schemas.actions import CompanyMemberSchema
from app.schemas.companies import CompanySchema
from app.schemas.results import ResultSchema, QuizRequest, ExportedFile
from app.services.redis_service import redis_service
from app.utils.export_data import export_redis_data


class ResultService:
    def __init__(
            self,
            session: AsyncSession,
            quiz_repository: QuizRepository,
            company_repository: CompanyRepository,
            user_repository: UserRepository,
            result_repository: ResultRepository,
    ):
        self.session = session
        self.quiz_repository = quiz_repository
        self.company_repository = company_repository
        self.user_repository = user_repository
        self.result_repository = result_repository

    async def _validate_is_company_member(self, user_id: int, company_id: int) -> CompanyMemberSchema:
        member = await self.company_repository.get_company_member(user_id, company_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are is not member of company"
            )
        return member

    @staticmethod
    async def get_last_result(results: List[Result]) -> Optional[Result]:
        if results:
            utc = pytz.UTC
            return max(results, key=lambda x: x.created_date.astimezone(utc))
        else:
            return None

    async def create_result(self, quiz_id: int, current_user_id: int, quiz_request: QuizRequest) -> ResultSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if quiz is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found")
        member = await self._validate_is_company_member(current_user_id, company_id)
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)
        results = await self.result_repository.get_many(company_member_id=member.id)
        last_result = await self.get_last_result(results)

        if last_result and datetime.utcnow().replace(tzinfo=pytz.UTC) - last_result.created_date < timedelta(hours=48):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can't create a new result within 48 hours of the last one."
            )

        redis_result = {
            'user_id': current_user_id,
            'company_id': company_id,
            'quiz_id': quiz_id,
            'questions': []
        }
        total_questions = 0
        correct_answers = 0
        for question in questions:
            total_questions += 1
            answer = quiz_request.answers.get(question.id)

            question_data = {
                'question': question.question_text,
                'user_answer': answer,
                'is_correct': answer == question.correct_answer
            }
            redis_result['questions'].append(question_data)

            is_correct = set(answer) == set(question.correct_answer)
            if is_correct:
                correct_answers += 1
        score = correct_answers / total_questions
        rounded_score = round(score, 2)

        result = Result(
            company_member_id=member.id,
            quiz_id=quiz_id,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score=rounded_score
        )

        result_schema = ResultSchema.from_orm(result)

        result = await self.result_repository.create_one(result_schema.dict())

        key = f"quiz_result:{current_user_id}:{company_id}:{quiz_id}:{result.id}"
        serialized_result = json.dumps(redis_result)
        expiration_time_seconds = timedelta(hours=48).total_seconds()
        await redis_service.redis_set(key, serialized_result, int(expiration_time_seconds))
        return ResultSchema.from_orm(result)

    async def get_company_rating(self, current_user_id: int, company_id: int) -> float:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        member = await self._validate_is_company_member(current_user_id, company.id)
        results = await self.result_repository.get_many(company_member_id=member.id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't have any results"
            )

        average_score = await self.result_repository.calculate_rating(member.id)

        return average_score

    async def get_global_rating(self, current_user_id: int) -> float:
        members = await self.user_repository.get_company_members_by_user_id(current_user_id)
        if not members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not a member of companies"
            )
        total_average_score = 0
        total_count = 0
        for member in members:
            results = await self.result_repository.get_many(company_member_id=member.id)
            if results:
                average_score = await self.result_repository.calculate_rating(member.id)
                total_average_score += average_score
                total_count += 1
        if total_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No company ratings found"
            )
        global_average_score = total_average_score / total_count
        return global_average_score

    async def _validate_export(self, company_id: int, current_user_id: int) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not await self.company_repository.is_user_company_owner(current_user_id, company.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to export this company to this user"
            )
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company

    @staticmethod
    async def _check_export_format(file_format: str) -> None:
        if file_format not in ['json', 'csv']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File format not supported"
            )

    async def company_answers_list(self, company_id: int, file_format: str, current_user_id: int) -> ExportedFile:
        await self._validate_export(company_id, current_user_id)
        query = f"quiz_result:*:{company_id}:*"
        return await export_redis_data(query=query, file_format=file_format)

    async def user_answers_list(self, company_id: int, user_id: int, file_format: str, current_user_id: int) -> ExportedFile:
        await self._validate_export(company_id, current_user_id)
        user = await self.user_repository.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        query = f"quiz_result:{user_id}:{company_id}:*"
        return await export_redis_data(query=query, file_format=file_format)

    async def my_answers_list(self, current_user_id, file_format) -> ExportedFile:
        await self._check_export_format(file_format)
        await self.user_repository.get_one(id=current_user_id)
        query = f"quiz_result:{current_user_id}:*:*"
        return await export_redis_data(query=query, file_format=file_format)
