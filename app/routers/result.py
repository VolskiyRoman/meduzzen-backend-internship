from fastapi import APIRouter, Depends

from app.schemas.results import ResultSchema, QuizRequest, ExportedFile
from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.result_service import ResultService
from app.utils.call_services import get_result_service

router = APIRouter(tags=["Result"])


@router.post("/create", response_model=ResultSchema)
async def create_result(quiz_id: int,
                        quiz_request: QuizRequest,
                        current_user: UserSchema = Depends(AuthService.get_current_user),
                        result_service: ResultService = Depends(get_result_service)) -> ResultSchema:
    current_user_id = current_user.id
    return await result_service.create_result(quiz_id=quiz_id,
                                              current_user_id=current_user_id,
                                              quiz_request=quiz_request)


@router.get("/my/company/rating", response_model=float)
async def get_company_rating(company_id: int,
                             current_user: UserSchema = Depends(AuthService.get_current_user),
                             result_service: ResultService = Depends(get_result_service)) -> float:
    current_user_id = current_user.id
    return await result_service.get_company_rating(company_id, current_user_id)


@router.get("/my/global_rating", response_model=float)
async def get_global_rating(current_user: UserSchema = Depends(AuthService.get_current_user),
                            result_service: ResultService = Depends(get_result_service)) -> float:
    current_user_id = current_user.id
    return await result_service.get_global_rating(current_user_id)


@router.get("/export/company", response_model=ExportedFile)
async def get_export_company(company_id: int,
                             file_format: str,
                             current_user: UserSchema = Depends(AuthService.get_current_user),
                             result_service: ResultService = Depends(get_result_service)) -> ExportedFile:
    current_user_id = current_user.id
    return await result_service.company_answers_list(company_id, file_format, current_user_id)


@router.get("/export/user", response_model=ExportedFile)
async def get_export_user(company_id: int,
                          user_id: int,
                          file_format: str,
                          current_user: UserSchema = Depends(AuthService.get_current_user),
                          result_service: ResultService = Depends(get_result_service)) -> ExportedFile:
    current_user_id = current_user.id
    return await result_service.user_answers_list(company_id, user_id, file_format, current_user_id)


@router.get("/export/me", response_model=ExportedFile)
async def get_export_company(file_format: str,
                             current_user: UserSchema = Depends(AuthService.get_current_user),
                             result_service: ResultService = Depends(get_result_service)) -> ExportedFile:
    current_user_id = current_user.id
    return await result_service.my_answers_list(current_user_id, file_format)



