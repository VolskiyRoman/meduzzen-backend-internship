from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizzes_repository import QuizRepository
from app.repositories.result_repository import ResultRepository
from app.repositories.user_repository import UserRepository
from app.services.action_service import ActionService
from app.services.auth_service import AuthService
from app.services.company_service import CompanyService
from app.services.quiz_service import QuizService
from app.services.result_service import ResultService
from app.services.user_service import UserService


async def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(session=session, repository=user_repository)


async def get_result_service(session: AsyncSession = Depends(get_async_session)) -> ResultService:
    result_repository = ResultRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)
    quizzes_repository = QuizRepository(session)
    return ResultService(session=session,
                         result_repository=result_repository,
                         company_repository=company_repository,
                         user_repository=user_repository,
                         quiz_repository=quizzes_repository)


async def get_quizzes_service(session: AsyncSession = Depends(get_async_session)) -> QuizService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    quiz_repository = QuizRepository(session)
    return QuizService(session=session,
                       quiz_repository=quiz_repository,
                       action_repository=action_repository,
                       company_repository=company_repository)


async def get_company_service(session: AsyncSession = Depends(get_async_session)) -> CompanyService:
    company_repository = CompanyRepository(session)
    return CompanyService(session=session, repository=company_repository)


async def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(session=session, repository=user_repository)


async def get_action_service(session: AsyncSession = Depends(get_async_session)) -> ActionService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    user_repository = UserRepository(session)
    return ActionService(session=session,
                         action_repository=action_repository,
                         company_repository=company_repository,
                         user_repository=user_repository)
