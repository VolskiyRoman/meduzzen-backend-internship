from typing import List

from fastapi import APIRouter, Depends

from app.schemas.users import UserSchema
from app.services.auth_service import AuthService
from app.services.result_service import ResultService
from app.utils.call_services import get_result_service

router = APIRouter(tags=["Analytics"])


@router.get("/my_quiz_results", response_model=dict)
async def get_my_quiz_results(quiz_id: int,
                              current_user: UserSchema = Depends(AuthService.get_current_user),
                              result_service: ResultService = Depends(get_result_service)) -> dict:
    current_user_id = current_user.id
    return await result_service.my_quiz_results(current_user_id=current_user_id,
                                                quiz_id=quiz_id)


@router.get("/my_quiz_latest_results", response_model=dict)
async def get_my_quizzes_latest_results(current_user: UserSchema = Depends(AuthService.get_current_user),
                                        result_service: ResultService = Depends(get_result_service)) -> dict:
    current_user_id = current_user.id
    return await result_service.my_quizzes_latest_results(current_user_id=current_user_id)


@router.get("/company_members_results", response_model=dict)
async def get_company_results(company_id: int,
                              current_user: UserSchema = Depends(AuthService.get_current_user),
                              result_service: ResultService = Depends(get_result_service)) -> dict:
    current_user_id = current_user.id
    return await result_service.company_members_results(current_user_id, company_id)


@router.get("/company_member_results", response_model=dict)
async def get_company_results_one_user(company_id: int,
                                       company_member_id: int,
                                       current_user: UserSchema = Depends(AuthService.get_current_user),
                                       result_service: ResultService = Depends(get_result_service)) -> dict:
    current_user_id = current_user.id
    return await result_service.company_member_results(company_id, company_member_id, current_user_id)


@router.get("/company_member_result_last", response_model=dict)
async def get_company_result_last(company_id: int,
                                  current_user: UserSchema = Depends(AuthService.get_current_user),
                                  result_service: ResultService = Depends(get_result_service)) -> dict:
    current_user_id = current_user.id
    return await result_service.company_members_result_last(company_id, current_user_id)
