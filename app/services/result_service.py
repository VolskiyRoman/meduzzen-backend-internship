import json
from datetime import timedelta, datetime

import pytz
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.enums.file_format import FileFormat
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

    async def create_result(self, quiz_id: int, current_user_id: int, quiz_request: QuizRequest) -> ResultSchema:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if quiz is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found")
        member = await self._validate_is_company_member(current_user_id, company_id)
        questions = await self.quiz_repository.get_questions_by_quiz_id(quiz_id)
        last_result = await self.result_repository.get_last_result_for_user(current_user_id)

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

    async def _get_company_or_raise(self, company_id: int) -> CompanySchema:
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return company

    async def get_company_rating(self, current_user_id: int, company_id: int) -> float:
        company = await self._get_company_or_raise(company_id)
        member = await self._validate_is_company_member(current_user_id, company.id)
        results = await self.result_repository.get_many(company_member_id=member.id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't have any results"
            )

        average_score = await self.result_repository.calculate_rating(member.id)

        return average_score

    @staticmethod
    async def _check_is_user_in_companies(company_members):
        if not company_members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not a member of companies"
            )

    async def get_global_rating(self, current_user_id: int) -> float:
        members = await self.user_repository.get_company_members_by_user_id(current_user_id)
        await self._check_is_user_in_companies(members)
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
    async def _check_export_format(file_format: FileFormat) -> None:
        if file_format not in [FileFormat.JSON, FileFormat.CSV]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File format not supported"
            )

    async def company_answers_list(self, company_id: int, file_format: FileFormat, current_user_id: int) -> ExportedFile:
        await self._validate_export(company_id, current_user_id)
        query = f"quiz_result:*:{company_id}:*"
        return await export_redis_data(query=query, file_format=file_format)

    async def user_answers_list(self, company_id: int, user_id: int, file_format: FileFormat, current_user_id: int) -> ExportedFile:
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

    @staticmethod
    async def _make_chart_data(results: list) -> dict:
        chart_data = {}
        current_total_questions = 0
        current_correct_answers = 0
        for result in results:
            current_total_questions += result.total_questions
            current_correct_answers += result.correct_answers
            chart_data[result.created_date] = current_correct_answers / current_total_questions

        return chart_data

    async def my_quiz_results(self, current_user_id, quiz_id: int) -> dict:
        quiz = await self.quiz_repository.get_one(id=quiz_id)
        company_id = quiz.company_id
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        member = await self._validate_is_company_member(current_user_id, company_id)
        results = await self.result_repository.get_many(company_member_id=member.id, quiz_id=quiz_id)
        chart_data = await self._make_chart_data(results)
        return chart_data

    async def my_quizzes_latest_results(self, current_user_id: int) -> dict:
        results = await self.result_repository.get_latest_results_for_company_member(current_user_id)
        latest_results = {}
        for result in results:
            latest_results[result.quiz_id] = result.created_date.isoformat()
        return latest_results

    async def _validate_company_owner_analytics(self, current_user_id: int, company_id: int) -> None:
        if not await self.company_repository.is_user_company_owner(current_user_id, company_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to get this data"
            )

    async def company_members_results(self, current_user_id: int, company_id: int) -> dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_analytics(current_user_id, company_id)
        company = await self.company_repository.get_one(id=company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        results = await self.company_repository.get_company_members_result_data(company_id)

        member_results = {}
        for result in results:
            member_id = result.company_member_id
            if member_id not in member_results:
                member_results[member_id] = []
            member_results[member_id].append(result)

        chart_data = {}
        for member_id, member_result in member_results.items():
            chart_data[member_id] = await self._make_chart_data(member_result)

        return chart_data

    async def company_member_results(self, company_id: int, company_member_id, current_user_id: int) -> dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_analytics(current_user_id, company_id)
        member = await self.company_repository.get_company_member(company_member_id, company_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company member not found"
            )
        results = await self.result_repository.get_many(company_member_id=member.id)
        chart_data = await self._make_chart_data(results)
        return chart_data

    async def company_members_result_last(self, company_id: int, current_user_id: int) -> dict:
        await self._get_company_or_raise(company_id)
        await self._validate_company_owner_analytics(current_user_id, company_id)

        latest_results = await self.result_repository.get_latest_results_for_company(company_id)
        results_dict = {}

        for result in latest_results:
            user_id = result.company_member_id
            if user_id not in results_dict:
                results_dict[user_id] = {}
            results_dict[user_id][result.quiz_id] = result.created_date

        return results_dict

