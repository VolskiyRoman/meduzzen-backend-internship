from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_async_session
from app.repositories.action_repository import ActionRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.quizzes_repository import QuizRepository
from app.schemas.quizzes import QuizSchema
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.quiz_service import QuizService

router = APIRouter(tags=["Quizzes"])


async def get_quizzes_service(session: AsyncSession = Depends(get_async_session)) -> QuizService:
    action_repository = ActionRepository(session)
    company_repository = CompanyRepository(session)
    quiz_repository = QuizRepository(session)
    return QuizService(session=session,
                       quiz_repository=quiz_repository,
                       action_repository=action_repository,
                       company_repository=company_repository)


@router.post("/create", response_model=QuizSchema)
async def create_quiz(quiz_data: QuizSchema,
                      company_id: int,
                      current_user: UserSchema = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quizzes_service)) -> QuizSchema:
    current_user_id = current_user.id
    return await quiz_service.create_quiz(quiz_data=quiz_data, current_user_id=current_user_id, company_id=company_id)


@router.delete("/delete", response_model=dict)
async def delete_quiz(quiz_id: int,
                      company_id: int,
                      current_user: UserSchema = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quizzes_service)) -> dict:
    current_user_id = current_user.id
    return await quiz_service.delete_quiz(quiz_id=quiz_id, current_user_id=current_user_id, company_id=company_id)


@router.patch("/update", response_model=QuizSchema)
async def update_quiz(quiz_data: QuizSchema,
                      quiz_id: int,
                      company_id: int,
                      current_user: UserSchema = Depends(AuthService.get_current_user),
                      quiz_service: QuizService = Depends(get_quizzes_service)) -> QuizSchema:
    current_user_id = current_user.id
    return await quiz_service.update_quiz(quiz_data=quiz_data,
                                          quiz_id=quiz_id,
                                          current_user_id=current_user_id,
                                          company_id=company_id)
